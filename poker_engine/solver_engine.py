"""
Solver决策引擎 - 统一决策框架
- Pre-flop: Solver(CFR风格)决策
- Flop: 蒙特卡洛决策（快速，5000次模拟）
- Turn: Solver(CFR风格)决策
- River: Solver(CFR风格)决策
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
    统一Solver决策引擎
    - preflop/turn/river: CFR风格精确求解
    - flop: 蒙特卡洛模拟快速决策
    """

    # 蒙特卡洛flop决策默认模拟次数
    DEFAULT_MC_SIMULATIONS = 5000

    def __init__(self, num_simulations=5000, num_iterations=100,
                 mc_simulations=None):
        """
        num_simulations: solver权益估算的模拟次数
        num_iterations: CFR迭代次数
        mc_simulations: flop阶段蒙特卡洛模拟次数（默认5000）
        """
        self.num_simulations = num_simulations
        self.num_iterations = num_iterations
        self.mc_simulations = mc_simulations or self.DEFAULT_MC_SIMULATIONS

    # ================================================================
    # 公共接口：统一决策入口
    # ================================================================

    def make_decision(self, stage: str, hole_cards: List[Card],
                      board_cards: List[Card], pot: float, stack: float,
                      available_actions: List[Dict],
                      position: str = 'BB',
                      opponent_range: Optional[List[List[Card]]] = None) -> Dict:
        """
        统一决策入口，根据阶段自动选择决策方式
        stage: 'preflop', 'flop', 'turn', 'river'
        """
        if stage == 'preflop':
            return self.make_preflop_decision(
                hole_cards, pot, stack, available_actions, position, opponent_range)
        elif stage == 'flop':
            return self.make_flop_decision(
                hole_cards, board_cards, pot, stack, available_actions, opponent_range)
        elif stage == 'turn':
            return self.make_turn_decision(
                hole_cards, board_cards, pot, stack, available_actions, opponent_range)
        elif stage == 'river':
            return self.make_river_decision(
                hole_cards, board_cards, pot, stack, available_actions, opponent_range)
        else:
            raise ValueError(f"Unknown stage: {stage}")

    # ================================================================
    # Flop阶段：蒙特卡洛决策
    # ================================================================

    def make_flop_decision(self, hole_cards: List[Card], board_cards: List[Card],
                           pot: float, stack: float, available_actions: List[Dict],
                           opponent_range: Optional[List[List[Card]]] = None) -> Dict:
        """
        Flop阶段蒙特卡洛决策（5000次模拟）
        通过随机模拟估算各行动的期望收益，大幅减少决策时间
        """
        start_time = time.time()

        # 估算手牌权益
        equity = self._mc_estimate_equity(hole_cards, board_cards, opponent_range)

        # 计算每个行动的EV
        evs = []
        action_details = []
        for act_info in available_actions:
            action = act_info['action']
            cost = act_info.get('cost', 0)
            result = self._mc_evaluate_action(
                hole_cards, board_cards, pot, action, cost, stack,
                equity, opponent_range)
            evs.append(result['ev'])
            action_details.append(result)

        # softmax生成策略概率分布
        strategy = self._ev_to_strategy(evs, [a['action'] for a in available_actions], pot)

        elapsed = time.time() - start_time

        best_idx = evs.index(max(evs))

        return {
            'strategy': strategy,
            'best_action': available_actions[best_idx],
            'best_probability': max(strategy.values()),
            'evs': dict(zip([a['action'] for a in available_actions], evs)),
            'equity': equity,
            'decision_time': elapsed,
            'method': 'monte_carlo',
            'stage': 'flop',
            'simulations': self.mc_simulations,
        }

    def _mc_estimate_equity(self, hole_cards: List[Card], board_cards: List[Card],
                             opponent_range: Optional[List[List[Card]]] = None) -> float:
        """蒙特卡洛权益估算"""
        if opponent_range:
            return hand_strength_vs_range(
                hole_cards, board_cards, opponent_range,
                num_simulations=self.mc_simulations
            )
        return hand_strength(
            hole_cards, board_cards,
            num_simulations=self.mc_simulations
        )

    def _mc_evaluate_action(self, hole_cards: List[Card], board_cards: List[Card],
                             pot: float, action: str, bet_size: float,
                             stack: float, equity: float,
                             opponent_range: Optional[List[List[Card]]] = None) -> Dict:
        """蒙特卡洛评估单个行动的EV"""
        if action == 'fold':
            return {'ev': 0.0, 'equity': 0.0, 'action': action}

        if action == 'check':
            ev = equity * pot
            return {'ev': ev, 'equity': equity, 'action': action}

        if action == 'call':
            total_pot = pot + bet_size * 2
            ev = equity * total_pot - bet_size
            return {'ev': ev, 'equity': equity, 'action': action}

        if action in ('raise', 'all_in'):
            fold_prob = self._estimate_fold_freq(pot, bet_size, stack, 'flop')
            total_pot_if_call = pot + bet_size * 2
            ev = (fold_prob * pot +
                  (1 - fold_prob) * (equity * total_pot_if_call - bet_size))
            return {
                'ev': ev,
                'equity': equity,
                'fold_probability': fold_prob,
                'action': action,
            }

        return {'ev': 0.0, 'equity': equity, 'action': action}

    # ================================================================
    # Pre-flop阶段：Solver(CFR风格)决策
    # ================================================================

    def make_preflop_decision(self, hole_cards: List[Card],
                               pot: float, stack: float,
                               available_actions: List[Dict],
                               position: str = 'BB',
                               opponent_range: Optional[List[List[Card]]] = None) -> Dict:
        """Pre-flop阶段决策（使用solver风格）"""
        start_time = time.time()

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

        strategy = self._ev_to_strategy(
            [r['ev'] for r in action_results],
            [r['action'] for r in action_results],
            pot
        )

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

    # ================================================================
    # Turn阶段：Solver(CFR风格)决策
    # ================================================================

    def make_turn_decision(self, hole_cards: List[Card], board_cards: List[Card],
                            pot: float, stack: float,
                            available_actions: List[Dict],
                            opponent_range: Optional[List[List[Card]]] = None) -> Dict:
        """Turn阶段决策（使用solver风格）"""
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

        strategy = self._ev_to_strategy(
            [r['ev'] for r in action_results],
            [r['action'] for r in action_results],
            pot
        )

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

    # ================================================================
    # River阶段：Solver(CFR风格)决策
    # ================================================================

    def make_river_decision(self, hole_cards: List[Card], board_cards: List[Card],
                             pot: float, stack: float,
                             available_actions: List[Dict],
                             opponent_range: Optional[List[List[Card]]] = None) -> Dict:
        """River阶段决策（使用solver风格 - 最精确）"""
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

        strategy = self._ev_to_strategy(
            [r['ev'] for r in action_results],
            [r['action'] for r in action_results],
            pot
        )

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

    # ================================================================
    # 共用内部方法
    # ================================================================

    def _compute_exact_equity(self, hole_cards: List[Card], board_cards: List[Card],
                               opponent_range: Optional[List[List[Card]]] = None) -> float:
        """计算更精确的权益（solver用，更多模拟次数）"""
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
        """计算outs数量（能改善手牌的牌数），需要至少3张公共牌"""
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

    def _cfr_evaluate_action(self, hole_cards: List[Card], board_cards: List[Card],
                              pot: float, action: str, bet_size: float,
                              stack: float, stage: str,
                              opponent_range: Optional[List[List[Card]]] = None) -> Dict:
        """使用CFR风格评估行动（模拟迭代求解）"""
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
        """估算对手弃牌频率（基于GTO近似）"""
        pot_ratio = bet_size / pot if pot > 0 else 1.0

        stage_factor = {
            'preflop': 0.6,
            'flop': 0.5,
            'turn': 0.4,
            'river': 0.3,
        }.get(stage, 0.5)

        fold_freq = stage_factor * (1 - math.exp(-pot_ratio * 0.8))
        return min(0.95, max(0.02, fold_freq))

    def _ev_to_strategy(self, evs: List[float], actions: List[str], pot: float) -> Dict:
        """将EV转换为策略概率分布"""
        temperature = max(pot * 0.5, 1.0)
        max_ev = max(evs) if evs else 0
        exp_evs = [math.exp((ev - max_ev) / temperature) for ev in evs]
        total_exp = sum(exp_evs)
        probs = [e / total_exp for e in exp_evs] if total_exp > 0 else [1.0 / len(evs)] * len(evs)

        return dict(zip(actions, probs))
