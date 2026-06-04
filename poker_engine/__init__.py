"""
poker_engine 包初始化

SolverEngine 已集成蒙特卡洛flop决策:
- Pre-flop: Solver(CFR风格)决策
- Flop: 蒙特卡洛决策（默认5000次模拟）
- Turn: Solver(CFR风格)决策
- River: Solver(CFR风格)决策
"""
from poker_engine.card_utils import Card, Deck, parse_cards, evaluate_hand, hand_strength
from poker_engine.solver_engine import SolverEngine
from poker_engine.decision_manager import DecisionManager

__all__ = [
    'Card', 'Deck', 'parse_cards', 'evaluate_hand', 'hand_strength',
    'SolverEngine', 'DecisionManager',
]
