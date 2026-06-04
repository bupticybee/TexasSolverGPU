"""
蒙特卡洛模拟引擎 - 用于flop阶段的快速决策
通过大量随机模拟来估算各行动的期望收益，替代耗时的完整solver计算
"""
import random
import time
from typing import List, Dict, Tuple, Optional
from poker_engine.card_utils import (
    Card, Deck, parse_cards, evaluate_hand,
    hand_strength, hand_strength_vs_range, equity_distribution
)


class MonteCarloEngine:
    """蒙特卡洛模拟引擎"""

    def __init__(self, num_simulations=2000, num_opponents=1):
        self.num_simulations = num_simulations
        self.num_opponents = num_opponents

    def estimate_equity(self, hole_cards: List[Card], board_cards: List[Card],
                        opponent_range: Optional[List[List[Card]]] = None) -> float:
        """
        估算手牌权益
        hole_cards: 己方手牌
        board_cards: 当前公共牌
        opponent_range: 对手范围（可选）
        """
        if opponent_range:
            return hand_strength_vs_range(
                hole_cards, board_cards, opponent_range,
                num_simulations=self.num_simulations // 2
            )
        return hand_strength(
            hole_cards, board_cards,
            num_simulations=self.num_simulations
        )

    def estimate_equity_batch(self, hands: List[Tuple[List[Card], List[Card]]],
                              opponent_range: Optional[List[List[Card]]] = None) -> List[float]:
        """批量估算多手牌的权益"""
        return [self.estimate_equity(hole, board, opponent_range)
                for hole, board in hands]

    def simulate_action_ev(self, hole_cards: List[Card], board_cards: List[Card],
                           pot: float, action: str, bet_size: float,
                           stack: float, opponent_range: Optional[List[List[Card]]] = None,
                           num_simulations: Optional[int] = None) -> Dict:
        """
        模拟某个行动的期望收益
        action: 'fold', 'check', 'call', 'raise', 'all_in'
        bet_size: 下注金额（对于raise/all_in）
        返回: {
            'ev': 期望收益,
            'equity': 权益,
            'risk_reward': 风险收益比,
            'action': 行动,
            'simulations': 模拟次数
        }
        """
        sims = num_simulations or self.num_simulations

        if action == 'fold':
            return {
                'ev': 0.0,
                'equity': 0.0,
                'risk_reward': 0.0,
                'action': action,
                'simulations': sims,
            }

        equity = self.estimate_equity(hole_cards, board_cards, opponent_range)

        if action == 'check':
            ev = equity * pot
            return {
                'ev': ev,
                'equity': equity,
                'risk_reward': float('inf') if pot > 0 else 0.0,
                'action': action,
                'simulations': sims,
            }

        if action == 'call':
            cost = bet_size
            total_pot = pot + bet_size * 2  # 我方跟注后总池
            ev = equity * total_pot - cost
            risk_reward = cost / (total_pot - cost) if total_pot > cost else 0.0
            return {
                'ev': ev,
                'equity': equity,
                'risk_reward': risk_reward,
                'action': action,
                'simulations': sims,
            }

        if action == 'raise':
            cost = bet_size
            # 简化模型：假设对手有一定概率弃牌
            fold_prob = self._estimate_fold_probability(pot, bet_size, stack)
            total_pot_if_call = pot + bet_size * 2
            # 弃牌收益 + 跟注收益
            ev = (fold_prob * pot +
                  (1 - fold_prob) * (equity * total_pot_if_call - cost))
            risk_reward = cost / total_pot_if_call if total_pot_if_call > 0 else 0.0
            return {
                'ev': ev,
                'equity': equity,
                'risk_reward': risk_reward,
                'action': action,
                'simulations': sims,
                'fold_probability': fold_prob,
            }

        if action == 'all_in':
            cost = stack
            fold_prob = self._estimate_fold_probability(pot, stack, stack)
            total_pot_if_call = pot + stack * 2
            ev = (fold_prob * pot +
                  (1 - fold_prob) * (equity * total_pot_if_call - cost))
            return {
                'ev': ev,
                'equity': equity,
                'risk_reward': stack / total_pot_if_call if total_pot_if_call > 0 else 0.0,
                'action': action,
                'simulations': sims,
                'fold_probability': fold_prob,
            }

        return {'ev': 0.0, 'equity': 0.0, 'action': action, 'simulations': sims}

    def _estimate_fold_probability(self, pot: float, bet_size: float, stack: float) -> float:
        """
        估算对手弃牌概率
        基于下注比例的简化模型
        """
        pot_ratio = bet_size / pot if pot > 0 else 1.0
        # 下注越大，弃牌概率越高
        # 使用sigmoid-like函数
        fold_prob = min(0.9, max(0.05, 1.0 / (1.0 + pot_ratio)))
        return fold_prob

    def make_flop_decision(self, hole_cards: List[Card], board_cards: List[Card],
                           pot: float, stack: float, available_actions: List[Dict],
                           opponent_range: Optional[List[List[Card]]] = None) -> Dict:
        """
        Flop阶段蒙特卡洛决策
        available_actions: [{'action': 'fold', 'cost': 0}, {'action': 'call', 'cost': 5}, ...]
        返回: 最佳行动及其详情
        """
        start_time = time.time()
        best_action = None
        best_ev = float('-inf')
        action_results = []

        for act_info in available_actions:
            action = act_info['action']
            cost = act_info.get('cost', 0)

            result = self.simulate_action_ev(
                hole_cards=hole_cards,
                board_cards=board_cards,
                pot=pot,
                action=action,
                bet_size=cost,
                stack=stack,
                opponent_range=opponent_range,
            )
            result['cost'] = cost
            action_results.append(result)

            if result['ev'] > best_ev:
                best_ev = result['ev']
                best_action = result

        elapsed = time.time() - start_time

        return {
            'best_action': best_action,
            'all_actions': action_results,
            'decision_time': elapsed,
            'method': 'monte_carlo',
            'stage': 'flop',
            'simulations': self.num_simulations,
        }

    def make_flop_decision_with_strategy(self, hole_cards: List[Card],
                                          board_cards: List[Card],
                                          pot: float, stack: float,
                                          available_actions: List[Dict],
                                          opponent_range: Optional[List[List[Card]]] = None) -> Dict:
        """
        Flop阶段蒙特卡洛决策 - 带策略概率分配
        返回每个行动的概率分布（类似solver输出）
        """
        start_time = time.time()

        # 计算每个行动的EV
        evs = []
        for act_info in available_actions:
            action = act_info['action']
            cost = act_info.get('cost', 0)
            result = self.simulate_action_ev(
                hole_cards=hole_cards,
                board_cards=board_cards,
                pot=pot,
                action=action,
                bet_size=cost,
                stack=stack,
                opponent_range=opponent_range,
            )
            evs.append(result['ev'])

        # 使用softmax将EV转换为概率分布
        import math
        temperature = max(pot, 1.0)  # 温度参数，池越大越平滑
        max_ev = max(evs) if evs else 0
        exp_evs = [math.exp((ev - max_ev) / temperature) for ev in evs]
        total_exp = sum(exp_evs)
        probabilities = [e / total_exp for e in exp_evs] if total_exp > 0 else [1.0 / len(evs)] * len(evs)

        strategy = {}
        for act_info, prob in zip(available_actions, probabilities):
            strategy[act_info['action']] = prob

        elapsed = time.time() - start_time

        # 选择最高概率的行动
        best_idx = probabilities.index(max(probabilities))

        return {
            'strategy': strategy,
            'best_action': available_actions[best_idx],
            'best_probability': max(probabilities),
            'evs': dict(zip([a['action'] for a in available_actions], evs)),
            'decision_time': elapsed,
            'method': 'monte_carlo',
            'stage': 'flop',
            'simulations': self.num_simulations,
        }


class FastMonteCarloEngine(MonteCarloEngine):
    """快速蒙特卡洛引擎 - 减少模拟次数以换取速度"""

    def __init__(self, num_simulations=500, num_opponents=1):
        super().__init__(num_simulations, num_opponents)


class PreciseMonteCarloEngine(MonteCarloEngine):
    """精确蒙特卡洛引擎 - 增加模拟次数以换取精度"""

    def __init__(self, num_simulations=5000, num_opponents=1):
        super().__init__(num_simulations, num_opponents)
