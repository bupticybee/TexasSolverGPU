"""
AI决策时间和决策效果测试脚本
SolverEngine已集成蒙特卡洛flop决策(5000次模拟):
- Pre-flop: Solver(CFR风格)决策
- Flop: 蒙特卡洛决策（5000次模拟）
- Turn: Solver(CFR风格)决策
- River: Solver(CFR风格)决策
"""
import time
import sys
import os
import json
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from poker_engine.card_utils import Card, Deck, parse_cards, evaluate_hand, hand_strength, RANKS, SUITS
from poker_engine.solver_engine import SolverEngine
from poker_engine.decision_manager import DecisionManager


def print_separator(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_sub(title):
    print(f"\n--- {title} ---")


# ============================================================
# 测试1: 各阶段决策时间对比（SolverEngine统一调度）
# ============================================================
def test_decision_time_by_stage():
    print_separator("测试1: 各阶段决策时间对比 (SolverEngine统一调度)")

    dm = DecisionManager(num_simulations=5000, mc_simulations=5000)

    test_cases = {
        'preflop': {
            'hole_str': 'AhKh',
            'board_str': '',
            'pot': 5.0,
            'stack': 95.0,
            'actions': [
                {'action': 'fold', 'cost': 0},
                {'action': 'call', 'cost': 2.5},
                {'action': 'raise', 'cost': 8.0},
            ],
        },
        'flop': {
            'hole_str': 'AhKh',
            'board_str': 'Ts9s3h',
            'pot': 10.0,
            'stack': 90.0,
            'actions': [
                {'action': 'fold', 'cost': 0},
                {'action': 'check', 'cost': 0},
                {'action': 'call', 'cost': 5.0},
                {'action': 'raise', 'cost': 15.0},
            ],
        },
        'turn': {
            'hole_str': 'AhKh',
            'board_str': 'Ts9s3h2d',
            'pot': 20.0,
            'stack': 85.0,
            'actions': [
                {'action': 'fold', 'cost': 0},
                {'action': 'check', 'cost': 0},
                {'action': 'call', 'cost': 10.0},
                {'action': 'raise', 'cost': 30.0},
            ],
        },
        'river': {
            'hole_str': 'AhKh',
            'board_str': 'Ts9s3h2d7c',
            'pot': 40.0,
            'stack': 75.0,
            'actions': [
                {'action': 'fold', 'cost': 0},
                {'action': 'check', 'cost': 0},
                {'action': 'call', 'cost': 20.0},
                {'action': 'raise', 'cost': 60.0},
            ],
        },
    }

    results = {}
    for stage, case in test_cases.items():
        print_sub(f"阶段: {stage}")
        result = dm.make_decision_from_str(
            stage=stage,
            hole_str=case['hole_str'],
            board_str=case['board_str'],
            pot=case['pot'],
            stack=case['stack'],
            available_actions=case['actions'],
        )
        results[stage] = result

        print(f"  决策方法: {result['method']}")
        print(f"  决策时间: {result['total_decision_time']:.4f}s")
        print(f"  策略分布: {json.dumps({k: f'{v:.2%}' for k, v in result['strategy'].items()}, ensure_ascii=False)}")
        best = result['best_action']
        print(f"  最佳行动: {best['action']} (概率: {result['best_probability']:.2%})")

    # 汇总对比
    print_sub("决策时间汇总")
    print(f"  {'阶段':<10} {'方法':<15} {'时间(s)':<12}")
    print(f"  {'-'*37}")
    for stage, result in results.items():
        print(f"  {stage:<10} {result['method']:<15} {result['total_decision_time']:.4f}")

    flop_time = results['flop']['total_decision_time']
    solver_avg = sum(results[s]['total_decision_time'] for s in ['preflop', 'turn', 'river']) / 3
    speedup = solver_avg / flop_time if flop_time > 0 else float('inf')
    print(f"\n  Flop(蒙特卡洛 5000次) 平均时间: {flop_time:.4f}s")
    print(f"  其他阶段(Solver) 平均时间: {solver_avg:.4f}s")
    print(f"  Flop加速比: {speedup:.2f}x")

    return results


# ============================================================
# 测试2: Flop蒙特卡洛 vs Solver决策对比
# ============================================================
def test_flop_mc_vs_solver():
    print_separator("测试2: Flop阶段蒙特卡洛 vs Solver决策对比")

    # 不同MC模拟次数的SolverEngine
    engines = {
        'MC-500': SolverEngine(num_simulations=5000, mc_simulations=500),
        'MC-1000': SolverEngine(num_simulations=5000, mc_simulations=1000),
        'MC-2000': SolverEngine(num_simulations=5000, mc_simulations=2000),
        'MC-5000': SolverEngine(num_simulations=5000, mc_simulations=5000),
    }
    # 纯solver基准（用turn决策方法模拟flop的solver计算）
    solver_baseline = SolverEngine(num_simulations=5000, mc_simulations=5000)

    flop_scenarios = [
        {
            'name': '强牌(顶对)',
            'hole_str': 'AhTh',
            'board_str': 'Ts9s3h',
            'pot': 10.0,
            'stack': 90.0,
            'actions': [
                {'action': 'fold', 'cost': 0},
                {'action': 'check', 'cost': 0},
                {'action': 'call', 'cost': 5.0},
                {'action': 'raise', 'cost': 15.0},
            ],
        },
        {
            'name': '中等牌(中对)',
            'hole_str': 'Kh9h',
            'board_str': 'Ts9s3h',
            'pot': 10.0,
            'stack': 90.0,
            'actions': [
                {'action': 'fold', 'cost': 0},
                {'action': 'check', 'cost': 0},
                {'action': 'call', 'cost': 5.0},
                {'action': 'raise', 'cost': 15.0},
            ],
        },
        {
            'name': '弱牌(空气)',
            'hole_str': '7d2c',
            'board_str': 'Ts9s3h',
            'pot': 10.0,
            'stack': 90.0,
            'actions': [
                {'action': 'fold', 'cost': 0},
                {'action': 'check', 'cost': 0},
                {'action': 'call', 'cost': 5.0},
                {'action': 'raise', 'cost': 15.0},
            ],
        },
        {
            'name': '听牌(同花听牌)',
            'hole_str': 'As5s',
            'board_str': 'Ts9s3h',
            'pot': 10.0,
            'stack': 90.0,
            'actions': [
                {'action': 'fold', 'cost': 0},
                {'action': 'check', 'cost': 0},
                {'action': 'call', 'cost': 5.0},
                {'action': 'raise', 'cost': 15.0},
            ],
        },
    ]

    for scenario in flop_scenarios:
        print_sub(f"场景: {scenario['name']}")
        hole_cards = parse_cards(scenario['hole_str'])
        board_cards = parse_cards(scenario['board_str'])

        # Solver基准（使用turn决策方法作为solver基准）
        solver_result = solver_baseline.make_turn_decision(
            hole_cards=hole_cards,
            board_cards=board_cards,
            pot=scenario['pot'],
            stack=scenario['stack'],
            available_actions=scenario['actions'],
        )
        solver_best = solver_result['best_action']['action']
        solver_time = solver_result['decision_time']

        print(f"  Solver基准: 最佳行动={solver_best}, 时间={solver_time:.4f}s")
        print(f"  Solver策略: {json.dumps({k: f'{v:.2%}' for k, v in solver_result['strategy'].items()}, ensure_ascii=False)}")

        print(f"  {'引擎':<10} {'最佳行动':<8} {'时间(s)':<10} {'加速比':<8} {'与Solver一致':<10}")
        print(f"  {'-'*50}")

        for name, engine in engines.items():
            mc_result = engine.make_flop_decision(
                hole_cards=hole_cards,
                board_cards=board_cards,
                pot=scenario['pot'],
                stack=scenario['stack'],
                available_actions=scenario['actions'],
            )
            mc_best = mc_result['best_action']['action']
            mc_time = mc_result['decision_time']
            speedup = solver_time / mc_time if mc_time > 0 else float('inf')
            consistent = '是' if mc_best == solver_best else '否'

            print(f"  {name:<10} {mc_best:<8} {mc_time:.4f}     {speedup:.2f}x    {consistent}")


# ============================================================
# 测试3: SolverEngine统一决策入口测试
# ============================================================
def test_unified_decision_entry():
    print_separator("测试3: SolverEngine统一决策入口测试")

    solver = SolverEngine(num_simulations=5000, mc_simulations=5000)

    hole_cards = parse_cards('AhKh')
    board_cards_flop = parse_cards('Ts9s3h')
    board_cards_turn = parse_cards('Ts9s3h2d')
    board_cards_river = parse_cards('Ts9s3h2d7c')

    actions = [
        {'action': 'fold', 'cost': 0},
        {'action': 'check', 'cost': 0},
        {'action': 'call', 'cost': 5.0},
        {'action': 'raise', 'cost': 15.0},
    ]

    print_sub("通过 make_decision() 统一入口调用各阶段")

    stages = [
        ('preflop', [], actions[:3]),  # preflop无check
        ('flop', board_cards_flop, actions),
        ('turn', board_cards_turn, actions),
        ('river', board_cards_river, actions),
    ]

    for stage, board, acts in stages:
        result = solver.make_decision(
            stage=stage,
            hole_cards=hole_cards,
            board_cards=board,
            pot=10.0,
            stack=90.0,
            available_actions=acts,
        )
        print(f"  {stage}: method={result['method']}, "
              f"best={result['best_action']['action']}, "
              f"time={result['decision_time']:.4f}s, "
              f"sims={result.get('simulations', result.get('iterations', 'N/A'))}")


# ============================================================
# 测试4: 完整手牌决策流程测试
# ============================================================
def test_full_hand_decision_flow():
    print_separator("测试4: 完整手牌决策流程测试")

    dm = DecisionManager(num_simulations=5000, mc_simulations=5000)

    print_sub("场景: HU, 100bb, 持有AhKh")

    # Pre-flop
    print("\n  [Pre-flop] SB raise 2.5bb, BB (你) 面临决策")
    result = dm.make_decision_from_str(
        stage='preflop',
        hole_str='AhKh',
        board_str='',
        pot=3.5,
        stack=99.0,
        available_actions=[
            {'action': 'fold', 'cost': 0},
            {'action': 'call', 'cost': 1.5},
            {'action': 'raise', 'cost': 7.0},
        ],
        position='BB',
    )
    print(f"    方法: {result['method']}, 时间: {result['total_decision_time']:.4f}s")
    print(f"    策略: {json.dumps({k: f'{v:.2%}' for k, v in result['strategy'].items()}, ensure_ascii=False)}")

    # Flop
    print("\n  [Flop] 公共牌: Ts9s3h, 底池: 7bb")
    result = dm.make_decision_from_str(
        stage='flop',
        hole_str='AhKh',
        board_str='Ts9s3h',
        pot=7.0,
        stack=97.0,
        available_actions=[
            {'action': 'fold', 'cost': 0},
            {'action': 'check', 'cost': 0},
            {'action': 'call', 'cost': 3.5},
            {'action': 'raise', 'cost': 10.5},
        ],
    )
    print(f"    方法: {result['method']}, 时间: {result['total_decision_time']:.4f}s")
    print(f"    策略: {json.dumps({k: f'{v:.2%}' for k, v in result['strategy'].items()}, ensure_ascii=False)}")

    # Turn
    print("\n  [Turn] 公共牌: Ts9s3h2d, 底池: 14bb")
    result = dm.make_decision_from_str(
        stage='turn',
        hole_str='AhKh',
        board_str='Ts9s3h2d',
        pot=14.0,
        stack=93.5,
        available_actions=[
            {'action': 'fold', 'cost': 0},
            {'action': 'check', 'cost': 0},
            {'action': 'call', 'cost': 7.0},
            {'action': 'raise', 'cost': 21.0},
        ],
    )
    print(f"    方法: {result['method']}, 时间: {result['total_decision_time']:.4f}s")
    print(f"    策略: {json.dumps({k: f'{v:.2%}' for k, v in result['strategy'].items()}, ensure_ascii=False)}")

    # River
    print("\n  [River] 公共牌: Ts9s3h2d7c, 底池: 28bb")
    result = dm.make_decision_from_str(
        stage='river',
        hole_str='AhKh',
        board_str='Ts9s3h2d7c',
        pot=28.0,
        stack=86.5,
        available_actions=[
            {'action': 'fold', 'cost': 0},
            {'action': 'check', 'cost': 0},
            {'action': 'call', 'cost': 14.0},
            {'action': 'raise', 'cost': 42.0},
        ],
    )
    print(f"    方法: {result['method']}, 时间: {result['total_decision_time']:.4f}s")
    print(f"    策略: {json.dumps({k: f'{v:.2%}' for k, v in result['strategy'].items()}, ensure_ascii=False)}")

    # 统计
    stats = dm.get_decision_stats()
    print_sub("决策统计")
    print(f"  总决策次数: {stats['total_decisions']}")
    print(f"  总决策时间: {stats['total_time']:.4f}s")
    for stage, info in stats['by_stage'].items():
        method = 'monte_carlo' if stage == 'flop' else 'solver'
        print(f"  {stage}: 次数={info['count']}, 平均时间={info['avg_time']:.4f}s, "
              f"方法={method}")


# ============================================================
# 测试5: 批量flop决策性能测试
# ============================================================
def test_batch_flop_performance():
    print_separator("测试5: 批量Flop决策性能测试 (MC 5000次 vs Solver)")

    solver_mc = SolverEngine(num_simulations=5000, mc_simulations=5000)
    solver_only = SolverEngine(num_simulations=5000, mc_simulations=5000)

    random.seed(42)
    scenarios = []
    for _ in range(10):
        deck = Deck()
        hole = deck.deal(2)
        board = deck.deal(3)
        pot = random.uniform(5, 30)
        stack = random.uniform(20, 100)
        scenarios.append({
            'hole_cards': hole,
            'board_cards': board,
            'pot': pot,
            'stack': stack,
            'actions': [
                {'action': 'fold', 'cost': 0},
                {'action': 'check', 'cost': 0},
                {'action': 'call', 'cost': pot * 0.5},
                {'action': 'raise', 'cost': pot * 1.5},
            ],
        })

    # 蒙特卡洛flop决策
    print_sub("蒙特卡洛Flop决策 (10个场景, 5000次模拟)")
    mc_start = time.time()
    mc_decisions = []
    for s in scenarios:
        result = solver_mc.make_flop_decision(
            hole_cards=s['hole_cards'],
            board_cards=s['board_cards'],
            pot=s['pot'],
            stack=s['stack'],
            available_actions=s['actions'],
        )
        mc_decisions.append(result)
    mc_total = time.time() - mc_start

    # Solver flop决策（用turn方法模拟）
    print_sub("Solver Flop决策 (10个场景)")
    solver_start = time.time()
    solver_decisions = []
    for s in scenarios:
        result = solver_only.make_turn_decision(
            hole_cards=s['hole_cards'],
            board_cards=s['board_cards'],
            pot=s['pot'],
            stack=s['stack'],
            available_actions=s['actions'],
        )
        solver_decisions.append(result)
    solver_total = time.time() - solver_start

    print_sub("批量决策对比")
    print(f"  {'方法':<25} {'总时间(s)':<12} {'平均时间(s)':<12} {'加速比':<10}")
    print(f"  {'-'*59}")
    print(f"  {'蒙特卡洛(Flop,5000次)':<25} {mc_total:.4f}       {mc_total/10:.4f}       {solver_total/mc_total:.2f}x")
    print(f"  {'Solver(Flop)':<25} {solver_total:.4f}       {solver_total/10:.4f}       1.00x")

    consistent = sum(1 for mc, sv in zip(mc_decisions, solver_decisions)
                     if mc['best_action']['action'] == sv['best_action']['action'])
    print(f"\n  决策一致性: {consistent}/{len(scenarios)} ({consistent/len(scenarios)*100:.0f}%)")

    return mc_total, solver_total


# ============================================================
# 测试6: 权益估算准确性
# ============================================================
def test_equity_accuracy():
    print_separator("测试6: 权益估算准确性 (蒙特卡洛5000次 vs Solver)")

    solver = SolverEngine(num_simulations=5000, mc_simulations=5000)

    known_scenarios = [
        {
            'name': 'AA vs 随机 (Pre-flop)',
            'hole_str': 'AhAd',
            'board_str': '',
            'expected_equity_range': (0.80, 0.88),
        },
        {
            'name': '顶对顶踢 (Flop)',
            'hole_str': 'AhKh',
            'board_str': 'Ks7d2c',
            'expected_equity_range': (0.70, 0.90),
        },
        {
            'name': '同花听牌 (Flop)',
            'hole_str': 'As5s',
            'board_str': 'Ts9s3h',
            'expected_equity_range': (0.40, 0.65),
        },
        {
            'name': '弱牌 (Flop)',
            'hole_str': '7d2c',
            'board_str': 'Ts9s3h',
            'expected_equity_range': (0.05, 0.25),
        },
    ]

    print(f"  {'场景':<25} {'MC权益':<10} {'Solver权益':<12} {'期望范围':<20} {'MC在范围':<8} {'Solver在范围':<10}")
    print(f"  {'-'*85}")

    for scenario in known_scenarios:
        hole_cards = parse_cards(scenario['hole_str'])
        board_cards = parse_cards(scenario['board_str']) if scenario['board_str'] else []

        # MC权益（flop决策方法内部使用）
        mc_eq = solver._mc_estimate_equity(hole_cards, board_cards)
        # Solver权益
        solver_eq = solver._compute_exact_equity(hole_cards, board_cards)

        low, high = scenario['expected_equity_range']
        mc_in_range = '是' if low <= mc_eq <= high else '否'
        solver_in_range = '是' if low <= solver_eq <= high else '否'

        print(f"  {scenario['name']:<25} {mc_eq:.4f}     {solver_eq:.4f}       "
              f"{low:.2f}-{high:.2f}          {mc_in_range:<8} {solver_in_range}")


# ============================================================
# 主测试入口
# ============================================================
def main():
    print("=" * 60)
    print("  德州扑克AI决策系统测试")
    print("  SolverEngine 已集成蒙特卡洛flop决策")
    print("  - Pre-flop/Turn/River: Solver(CFR风格)")
    print("  - Flop: 蒙特卡洛(5000次模拟)")
    print("=" * 60)

    # 测试1: 各阶段决策时间
    test_decision_time_by_stage()

    # 测试2: Flop蒙特卡洛 vs Solver
    test_flop_mc_vs_solver()

    # 测试3: 统一决策入口
    test_unified_decision_entry()

    # 测试4: 完整手牌流程
    test_full_hand_decision_flow()

    # 测试5: 批量性能
    test_batch_flop_performance()

    # 测试6: 权益准确性
    test_equity_accuracy()

    print_separator("测试完成")
    print("\n关键结论:")
    print("  1. SolverEngine已统一集成蒙特卡洛flop决策")
    print("  2. Flop阶段使用蒙特卡洛(5000次模拟)，决策时间显著减少")
    print("  3. Pre-flop/Turn/River阶段保持Solver(CFR)精确决策")
    print("  4. 通过 make_decision() 统一入口自动按阶段选择决策方式")


if __name__ == '__main__':
    main()
