"""
统一决策管理器 - 根据游戏阶段选择决策方式
- Pre-flop: Solver决策
- Flop: 蒙特卡洛决策（快速）
- Turn: Solver决策
- River: Solver决策
"""
import time
from typing import List, Dict, Optional
from poker_engine.card_utils import Card, parse_cards
from poker_engine.monte_carlo_engine import MonteCarloEngine, FastMonteCarloEngine, PreciseMonteCarloEngine
from poker_engine.solver_engine import SolverEngine


class DecisionManager:
    """
    统一决策管理器
    根据游戏阶段自动选择决策引擎:
    - preflop: Solver (精确)
    - flop: Monte Carlo (快速)
    - turn: Solver (精确)
    - river: Solver (精确)
    """

    def __init__(self, mc_simulations=2000, solver_simulations=5000, solver_iterations=100):
        self.mc_engine = MonteCarloEngine(num_simulations=mc_simulations)
        self.fast_mc_engine = FastMonteCarloEngine(num_simulations=mc_simulations // 4)
        self.solver_engine = SolverEngine(
            num_simulations=solver_simulations,
            num_iterations=solver_iterations
        )
        self.decision_history = []

    def make_decision(self, stage: str, hole_cards: List[Card], board_cards: List[Card],
                      pot: float, stack: float, available_actions: List[Dict],
                      position: str = 'BB',
                      opponent_range: Optional[List[List[Card]]] = None,
                      fast_mode: bool = False) -> Dict:
        """
        根据阶段选择决策引擎并做出决策

        stage: 'preflop', 'flop', 'turn', 'river'
        hole_cards: 手牌
        board_cards: 公共牌
        pot: 底池
        stack: 剩余筹码
        available_actions: 可用行动列表
        position: 位置
        opponent_range: 对手范围
        fast_mode: 是否使用快速模式
        """
        start_time = time.time()

        if stage == 'flop':
            # Flop阶段使用蒙特卡洛
            engine = self.fast_mc_engine if fast_mode else self.mc_engine
            result = engine.make_flop_decision_with_strategy(
                hole_cards=hole_cards,
                board_cards=board_cards,
                pot=pot,
                stack=stack,
                available_actions=available_actions,
                opponent_range=opponent_range,
            )
        elif stage == 'preflop':
            # Pre-flop使用solver
            result = self.solver_engine.make_preflop_decision(
                hole_cards=hole_cards,
                pot=pot,
                stack=stack,
                available_actions=available_actions,
                position=position,
                opponent_range=opponent_range,
            )
        elif stage == 'turn':
            # Turn使用solver
            result = self.solver_engine.make_turn_decision(
                hole_cards=hole_cards,
                board_cards=board_cards,
                pot=pot,
                stack=stack,
                available_actions=available_actions,
                opponent_range=opponent_range,
            )
        elif stage == 'river':
            # River使用solver
            result = self.solver_engine.make_river_decision(
                hole_cards=hole_cards,
                board_cards=board_cards,
                pot=pot,
                stack=stack,
                available_actions=available_actions,
                opponent_range=opponent_range,
            )
        else:
            raise ValueError(f"Unknown stage: {stage}")

        total_time = time.time() - start_time
        result['total_decision_time'] = total_time

        # 记录决策历史
        self.decision_history.append({
            'stage': stage,
            'method': result['method'],
            'decision_time': total_time,
            'best_action': result.get('best_action', {}),
        })

        return result

    def make_decision_from_str(self, stage: str, hole_str: str, board_str: str,
                                pot: float, stack: float, available_actions: List[Dict],
                                position: str = 'BB',
                                opponent_range: Optional[List[List[Card]]] = None,
                                fast_mode: bool = False) -> Dict:
        """
        从字符串解析牌面并做决策
        hole_str: 如 'AhKd'
        board_str: 如 'Ts9s3h'
        """
        hole_cards = parse_cards(hole_str)
        board_cards = parse_cards(board_str) if board_str else []
        return self.make_decision(
            stage=stage,
            hole_cards=hole_cards,
            board_cards=board_cards,
            pot=pot,
            stack=stack,
            available_actions=available_actions,
            position=position,
            opponent_range=opponent_range,
            fast_mode=fast_mode,
        )

    def get_decision_stats(self) -> Dict:
        """获取决策统计信息"""
        if not self.decision_history:
            return {'total_decisions': 0}

        by_stage = {}
        by_method = {}
        total_time = 0

        for d in self.decision_history:
            stage = d['stage']
            method = d['method']
            dt = d['decision_time']

            by_stage.setdefault(stage, {'count': 0, 'total_time': 0, 'times': []})
            by_stage[stage]['count'] += 1
            by_stage[stage]['total_time'] += dt
            by_stage[stage]['times'].append(dt)

            by_method.setdefault(method, {'count': 0, 'total_time': 0})
            by_method[method]['count'] += 1
            by_method[method]['total_time'] += dt

            total_time += dt

        # 计算各阶段平均时间
        for stage, info in by_stage.items():
            info['avg_time'] = info['total_time'] / info['count']
            info['min_time'] = min(info['times'])
            info['max_time'] = max(info['times'])

        return {
            'total_decisions': len(self.decision_history),
            'total_time': total_time,
            'by_stage': by_stage,
            'by_method': by_method,
        }

    def clear_history(self):
        """清除决策历史"""
        self.decision_history = []
