"""
统一决策管理器 - 通过SolverEngine实现
SolverEngine内部已集成:
- Pre-flop: Solver(CFR风格)决策
- Flop: 蒙特卡洛决策（5000次模拟）
- Turn: Solver(CFR风格)决策
- River: Solver(CFR风格)决策
"""
import time
from typing import List, Dict, Optional
from poker_engine.card_utils import Card, parse_cards
from poker_engine.solver_engine import SolverEngine


class DecisionManager:
    """
    统一决策管理器
    所有阶段通过SolverEngine统一调度:
    - preflop/turn/river: Solver (CFR精确求解)
    - flop: Monte Carlo (5000次模拟快速决策)
    """

    def __init__(self, num_simulations=5000, num_iterations=100,
                 mc_simulations=5000):
        self.solver = SolverEngine(
            num_simulations=num_simulations,
            num_iterations=num_iterations,
            mc_simulations=mc_simulations,
        )
        self.decision_history = []

    def make_decision(self, stage: str, hole_cards: List[Card], board_cards: List[Card],
                      pot: float, stack: float, available_actions: List[Dict],
                      position: str = 'BB',
                      opponent_range: Optional[List[List[Card]]] = None) -> Dict:
        """
        根据阶段做出决策（SolverEngine内部自动选择决策方式）

        stage: 'preflop', 'flop', 'turn', 'river'
        hole_cards: 手牌
        board_cards: 公共牌
        pot: 底池
        stack: 剩余筹码
        available_actions: 可用行动列表
        position: 位置
        opponent_range: 对手范围
        """
        start_time = time.time()

        result = self.solver.make_decision(
            stage=stage,
            hole_cards=hole_cards,
            board_cards=board_cards,
            pot=pot,
            stack=stack,
            available_actions=available_actions,
            position=position,
            opponent_range=opponent_range,
        )

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
                                opponent_range: Optional[List[List[Card]]] = None) -> Dict:
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
