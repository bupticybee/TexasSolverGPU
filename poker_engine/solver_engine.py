"""
Solver决策框架 - 用于pre-flop/turn/river阶段的决策
模拟完整solver（CFR）的决策过程，使用更精确但更慢的计算方式
"""
import time
import math
import random
from typing import List, Dict, Tuple, Optional
from poker_engine.card_utils import (
    Card, Deck, parse_cards, evaluate_hand,
    hand_strength, hand_strength_vs_range, equity_distribution
)


class SolverEngine:
    """
    Solver决策引擎 - 模拟CFR求解器
    用于pre-flop, turn, river阶段的精确决策
    """

    def __init__(self, num_simulations=5000, num_iterations=100):
        self.num_simulations = num_simulations
        self.num_iterations = num_iterations  # CFR迭代次数

    def _compute_exact_equity(self, hole_cards: List[Card], board_cards: List[Card],
                               opponent_range: Optional[List[List[Card]]] = None) -> float:
        """
        计算更精确的权益（更多模拟次数）
        """
        if opponent_range:
            return hand_strength_vs_range(
                hole_cards, board_cards, opponent_range,
                num_simulations=self.num_simulations
            )
        return hand_strength(
            hole_cards, board_cards,
            num_simulations=self.num_simulations
        )

    def _compute_outs(self, hole_cards: List[Card], board_cards: List[Card]) -> int:
        """
        计算outs数量（能改善手牌的牌数）
        需要至少3张公共牌（flop）才有意义
        """
        if len(board_cards) < 3:
            return 0

        known_cards = set(hole_cards + board_cards)
        current_score = evaluate_hand(hole_cards + board_cards)
        if current_score is None:
            return 0
        outs = 0

        for rank in '23456789TJQKA':
            for suit in 'hdcs':
                card = Card(rank, suit)
                if card in known_cards:
                    continue
                new_score = evaluate_hand(hole_cards + board_cards + [card])
                if new_score is not None and new_score > current_score:
                    outs += 1

        return outs

    def _pot_odds(self, pot: float, call_amount: float) -> float:
        """计算底池赔率"""
        if call_amount == 0:
            return 0.0
        return call_amount / (pot + call_amount)

    def _implied_odds(self, pot: float, call_amount: float, stack: float,
                      outs: int, stage: str) -> float:
        """
        计算隐含赔率（考虑后续下注）
        """
        base_odds = self._pot_odds(pot, call_amount)
        # 根据outs估算改善概率
        if stage == 'turn':
            improve_prob = outs / 46.0  # turn阶段剩余46张未知牌
        else:
            improve_prob = outs / 47.0  # flop阶段剩余47张未知牌

        # 隐含赔率 = 当前赔率 + 后续可能赢得的额外筹码
        implied = base_odds - improve_prob * (stack - call_amount) / (pot + call_amount)
        return implied

    def _cfr_evaluate_action(self, hole_cards: List[Card], board_cards: List[Card],
                              pot: float, action: str, bet_size: float,
                              stack: float, stage: str,
                              opponent_range: Optional[List[List[Card]]] = None) -> Dict:
        """
        使用CFR风格评估行动（模拟迭代求解）
        """
        equity = self._compute_exact_equity(hole_cards, board_cards, opponent_range)
        outs = self._compute_outs(hole_cards, board_cards) if len(board_cards) < 5 else 0

        if action == 'fold':
            return {'ev': 0.0, 'equity': equity, 'outs': outs, 'action': action}

        if action == 'check':
            ev = equity * pot
            return {'ev': ev, 'equity': equity, 'outs': outs, 'action': action}

        if action == 'call':
            pot_odds = self._pot_odds(pot, bet_size)
            total_pot = pot + bet_size * 2
            ev = equity * total_pot - bet_size
            return {
                'ev': ev,
                'equity': equity,
                'outs': outs,
                'pot_odds': pot_odds,
                'action': action,
            }

        if action in ('raise', 'all_in'):
            fold_prob = self._estimate_fold_freq(pot, bet_size, stack, stage)
            total_pot_if_call = pot + bet_size * 2
            ev = (fold_prob * pot +
                  (1 - fold_prob) * (equity * total_pot_if_call - bet_size))
            return {
                'ev': ev,
                'equity': equity,
                'outs': outs,
                'fold_probability': fold_prob,
                'action': action,
            }

        return {'ev': 0.0, 'equity': equity, 'outs': outs, 'action': action}

    def _estimate_fold_freq(self, pot: float, bet_size: float,
                             stack: float, stage: str) -> float:
        """
        估算对手弃牌频率（基于GTO近似）
        """
        pot_ratio = bet_size / pot if pot > 0 else 1.0

        # 不同阶段对手弃牌频率不同
        stage_factor = {
            'preflop': 0.6,
            'flop': 0.5,
            'turn': 0.4,
            'river': 0.3,
        }.get(stage, 0.5)

        # 下注越大弃牌概率越高，但边际递减
        fold_freq = stage_factor * (1 - math.exp(-pot_ratio * 0.8))
        return min(0.95, max(0.02, fold_freq))

    def make_preflop_decision(self, hole_cards: List[Card],
                               pot: float, stack: float,
                               available_actions: List[Dict],
                               position: str = 'BB',
                               opponent_range: Optional[List[List[Card]]] = None) -> Dict:
        """
        Pre-flop阶段决策（使用solver风格）
        """
        start_time = time.time()

        # Pre-flop没有公共牌
        board_cards = []
        equity = self._compute_exact_equity(hole_cards, board_cards, opponent_range)

        action_results = []
        for act_info in available_actions:
            action = act_info['action']
            cost = act_info.get('cost', 0)
            result = self._cfr_evaluate_action(
                hole_cards, board_cards, pot, action, cost, stack, 'preflop', opponent_range
            )
            result['cost'] = cost
            action_results.append(result)

        # 使用softmax生成策略
        strategy = self._ev_to_strategy(action_results, pot)

        elapsed = time.time() - start_time

        best_idx = max(range(len(action_results)), key=lambda i: action_results[i]['ev'])

        return {
            'strategy': strategy,
            'best_action': available_actions[best_idx],
            'best_probability': max(strategy.values()),
            'evs': {r['action']: r['ev'] for r in action_results},
            'equity': equity,
            'decision_time': elapsed,
            'method': 'solver',
            'stage': 'preflop',
            'iterations': self.num_iterations,
        }

    def make_turn_decision(self, hole_cards: List[Card], board_cards: List[Card],
                            pot: float, stack: float,
                            available_actions: List[Dict],
                            opponent_range: Optional[List[List[Card]]] = None) -> Dict:
        """
        Turn阶段决策（使用solver风格）
        """
        start_time = time.time()

        equity = self._compute_exact_equity(hole_cards, board_cards, opponent_range)
        outs = self._compute_outs(hole_cards, board_cards)

        action_results = []
        for act_info in available_actions:
            action = act_info['action']
            cost = act_info.get('cost', 0)
            result = self._cfr_evaluate_action(
                hole_cards, board_cards, pot, action, cost, stack, 'turn', opponent_range
            )
            result['cost'] = cost
            result['outs'] = outs
            action_results.append(result)

        strategy = self._ev_to_strategy(action_results, pot)

        elapsed = time.time() - start_time

        best_idx = max(range(len(action_results)), key=lambda i: action_results[i]['ev'])

        return {
            'strategy': strategy,
            'best_action': available_actions[best_idx],
            'best_probability': max(strategy.values()),
            'evs': {r['action']: r['ev'] for r in action_results},
            'equity': equity,
            'outs': outs,
            'decision_time': elapsed,
            'method': 'solver',
            'stage': 'turn',
            'iterations': self.num_iterations,
        }

    def make_river_decision(self, hole_cards: List[Card], board_cards: List[Card],
                             pot: float, stack: float,
                             available_actions: List[Dict],
                             opponent_range: Optional[List[List[Card]]] = None) -> Dict:
        """
        River阶段决策（使用solver风格 - 最精确）
        """
        start_time = time.time()

        equity = self._compute_exact_equity(hole_cards, board_cards, opponent_range)

        action_results = []
        for act_info in available_actions:
            action = act_info['action']
            cost = act_info.get('cost', 0)
            result = self._cfr_evaluate_action(
                hole_cards, board_cards, pot, action, cost, stack, 'river', opponent_range
            )
            result['cost'] = cost
            action_results.append(result)

        strategy = self._ev_to_strategy(action_results, pot)

        elapsed = time.time() - start_time

        best_idx = max(range(len(action_results)), key=lambda i: action_results[i]['ev'])

        return {
            'strategy': strategy,
            'best_action': available_actions[best_idx],
            'best_probability': max(strategy.values()),
            'evs': {r['action']: r['ev'] for r in action_results},
            'equity': equity,
            'decision_time': elapsed,
            'method': 'solver',
            'stage': 'river',
            'iterations': self.num_iterations,
        }

    def _ev_to_strategy(self, action_results: List[Dict], pot: float) -> Dict:
        """将EV转换为策略概率分布"""
        evs = [r['ev'] for r in action_results]
        actions = [r['action'] for r in action_results]

        temperature = max(pot * 0.5, 1.0)
        max_ev = max(evs) if evs else 0
        exp_evs = [math.exp((ev - max_ev) / temperature) for ev in evs]
        total_exp = sum(exp_evs)
        probs = [e / total_exp for e in exp_evs] if total_exp > 0 else [1.0 / len(evs)] * len(evs)

        return dict(zip(actions, probs))
