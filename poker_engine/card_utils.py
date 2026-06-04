"""
扑克牌基础工具模块：牌面表示、手牌评估、牌组管理
"""
import random
from itertools import combinations
from collections import Counter

# 花色和牌面定义
SUITS = ['h', 'd', 'c', 's']  # 红心、方块、梅花、黑桃
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
RANK_VALUES = {r: i for i, r in enumerate(RANKS)}

# 手牌等级
HAND_RANKS = {
    'high_card': 0,
    'one_pair': 1,
    'two_pair': 2,
    'three_of_a_kind': 3,
    'straight': 4,
    'flush': 5,
    'full_house': 6,
    'four_of_a_kind': 7,
    'straight_flush': 8,
}


class Card:
    """扑克牌"""
    __slots__ = ('rank', 'suit', 'value')

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.value = RANK_VALUES[rank]

    def __repr__(self):
        return f"{self.rank}{self.suit}"

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit

    def __hash__(self):
        return hash((self.rank, self.suit))

    def __lt__(self, other):
        return self.value < other.value


class Deck:
    """牌组管理"""

    def __init__(self, excluded_cards=None):
        self.cards = [Card(r, s) for r in RANKS for s in SUITS]
        if excluded_cards:
            self.cards = [c for c in self.cards if c not in excluded_cards]
        random.shuffle(self.cards)
        self._index = 0

    def deal(self, n=1):
        """发n张牌"""
        dealt = self.cards[self._index:self._index + n]
        self._index += n
        return dealt

    def remaining(self):
        return len(self.cards) - self._index


def parse_cards(card_str):
    """解析牌面字符串，如 'AhKd' -> [Card(A,h), Card(K,d)]"""
    cards = []
    i = 0
    while i + 1 < len(card_str):
        rank = card_str[i]
        suit = card_str[i + 1]
        if rank in RANK_VALUES and suit in SUITS:
            cards.append(Card(rank, suit))
        i += 2
    return cards


def evaluate_hand(cards):
    """
    评估手牌中的最佳5张组合
    支持任意数量(>=1)的牌，不足5张时补齐评估
    返回: (hand_rank, tiebreakers) 用于比较大小
    """
    if len(cards) < 5:
        # 不足5张牌，直接评估现有牌的等级
        # 补充虚拟牌使凑够5张，虚拟牌值为-1(最低)
        padded = list(cards) + [Card('2', 'h') for _ in range(5 - len(cards))]
        # 但虚拟牌不应参与真实比较，这里用简化方式
        # 直接返回基于现有牌的评估
        return _evaluate_partial(cards)

    best = None
    for combo in combinations(cards, 5):
        score = _evaluate_five(list(combo))
        if best is None or score > best:
            best = score
    return best


def _evaluate_partial(cards):
    """评估不足5张牌的简化等级（用于pre-flop等场景）"""
    if len(cards) == 0:
        return (HAND_RANKS['high_card'], 0)
    values = sorted([c.value for c in cards], reverse=True)
    counts = Counter(values)
    count_vals = sorted(counts.items(), key=lambda x: (x[1], x[0]), reverse=True)

    if count_vals[0][1] == 4:
        return (HAND_RANKS['four_of_a_kind'], count_vals[0][0])
    if count_vals[0][1] == 3 and len(count_vals) > 1 and count_vals[1][1] >= 2:
        return (HAND_RANKS['full_house'], count_vals[0][0], count_vals[1][0])
    if count_vals[0][1] == 3:
        kickers = sorted([v for v in values if v != count_vals[0][0]], reverse=True)
        return (HAND_RANKS['three_of_a_kind'], count_vals[0][0]) + tuple(kickers)
    if count_vals[0][1] == 2 and len(count_vals) > 1 and count_vals[1][1] == 2:
        pairs = sorted([count_vals[0][0], count_vals[1][0]], reverse=True)
        kicker = [v for v in values if v != pairs[0] and v != pairs[1]]
        return (HAND_RANKS['two_pair'], pairs[0], pairs[1]) + tuple(kicker)
    if count_vals[0][1] == 2:
        kickers = sorted([v for v in values if v != count_vals[0][0]], reverse=True)
        return (HAND_RANKS['one_pair'], count_vals[0][0]) + tuple(kickers)
    return (HAND_RANKS['high_card'],) + tuple(values)


def _evaluate_five(cards):
    """评估5张牌的等级"""
    values = sorted([c.value for c in cards], reverse=True)
    suits = [c.suit for c in cards]
    is_flush = len(set(suits)) == 1

    # 检查顺子
    is_straight = False
    straight_high = 0
    unique_vals = sorted(set(values), reverse=True)
    if len(unique_vals) == 5:
        if unique_vals[0] - unique_vals[4] == 4:
            is_straight = True
            straight_high = unique_vals[0]
        # A-2-3-4-5 (wheel)
        if unique_vals == [12, 3, 2, 1, 0]:
            is_straight = True
            straight_high = 3  # 5高顺子

    counts = Counter(values)
    count_vals = sorted(counts.items(), key=lambda x: (x[1], x[0]), reverse=True)

    if is_straight and is_flush:
        return (HAND_RANKS['straight_flush'], straight_high)
    if count_vals[0][1] == 4:
        kicker = [v for v in values if v != count_vals[0][0]][0]
        return (HAND_RANKS['four_of_a_kind'], count_vals[0][0], kicker)
    if count_vals[0][1] == 3 and count_vals[1][1] == 2:
        return (HAND_RANKS['full_house'], count_vals[0][0], count_vals[1][0])
    if is_flush:
        return (HAND_RANKS['flush'],) + tuple(values)
    if is_straight:
        return (HAND_RANKS['straight'], straight_high)
    if count_vals[0][1] == 3:
        kickers = sorted([v for v in values if v != count_vals[0][0]], reverse=True)
        return (HAND_RANKS['three_of_a_kind'], count_vals[0][0]) + tuple(kickers)
    if count_vals[0][1] == 2 and count_vals[1][1] == 2:
        pairs = sorted([count_vals[0][0], count_vals[1][0]], reverse=True)
        kicker = [v for v in values if v != pairs[0] and v != pairs[1]][0]
        return (HAND_RANKS['two_pair'], pairs[0], pairs[1], kicker)
    if count_vals[0][1] == 2:
        kickers = sorted([v for v in values if v != count_vals[0][0]], reverse=True)
        return (HAND_RANKS['one_pair'], count_vals[0][0]) + tuple(kickers)
    return (HAND_RANKS['high_card'],) + tuple(values)


def hand_strength(hole_cards, board_cards, num_simulations=1000):
    """
    蒙特卡洛估算手牌强度（胜率）
    返回: 胜率 (0~1)
    """
    known_cards = set(hole_cards + board_cards)
    wins = 0
    ties = 0

    for _ in range(num_simulations):
        deck = Deck(excluded_cards=known_cards)
        # 补全公共牌到5张
        remaining_board = 5 - len(board_cards)
        sim_board = board_cards + deck.deal(remaining_board)
        # 发对手2张牌
        opp_hole = deck.deal(2)

        my_score = evaluate_hand(hole_cards + sim_board)
        opp_score = evaluate_hand(opp_hole + sim_board)

        if my_score > opp_score:
            wins += 1
        elif my_score == opp_score:
            ties += 1

    return (wins + ties * 0.5) / num_simulations


def hand_strength_vs_range(hole_cards, board_cards, opponent_range, num_simulations=500):
    """
    蒙特卡洛估算手牌对阵对手范围的胜率
    opponent_range: 对手可能手牌列表 [[Card, Card], ...]
    """
    known_cards = set(hole_cards + board_cards)
    wins = 0
    ties = 0
    total = 0

    for _ in range(num_simulations):
        # 从对手范围中随机选一手牌
        opp_hole = random.choice(opponent_range)
        # 确保对手牌不与已知牌冲突
        if any(c in known_cards for c in opp_hole):
            continue

        current_known = known_cards | set(opp_hole)
        deck = Deck(excluded_cards=current_known)
        remaining_board = 5 - len(board_cards)
        sim_board = board_cards + deck.deal(remaining_board)

        my_score = evaluate_hand(hole_cards + sim_board)
        opp_score = evaluate_hand(opp_hole + sim_board)

        if my_score > opp_score:
            wins += 1
        elif my_score == opp_score:
            ties += 1
        total += 1

    if total == 0:
        return 0.5
    return (wins + ties * 0.5) / total


def equity_distribution(hole_cards, board_cards, num_simulations=1000):
    """
    计算手牌的详细权益分布
    返回: {
        'win': 胜率,
        'tie': 平局率,
        'lose': 败率,
        'hand_type': 最可能的手牌类型
    }
    """
    known_cards = set(hole_cards + board_cards)
    wins = 0
    ties = 0
    hand_types = Counter()

    for _ in range(num_simulations):
        deck = Deck(excluded_cards=known_cards)
        remaining_board = 5 - len(board_cards)
        sim_board = board_cards + deck.deal(remaining_board)
        opp_hole = deck.deal(2)

        my_score = evaluate_hand(hole_cards + sim_board)
        opp_score = evaluate_hand(opp_hole + sim_board)

        # 记录手牌类型
        hand_rank_name = [k for k, v in HAND_RANKS.items() if v == my_score[0]][0]
        hand_types[hand_rank_name] += 1

        if my_score > opp_score:
            wins += 1
        elif my_score == opp_score:
            ties += 1

    losses = num_simulations - wins - ties
    most_likely_hand = hand_types.most_common(1)[0][0] if hand_types else 'unknown'

    return {
        'win': wins / num_simulations,
        'tie': ties / num_simulations,
        'lose': losses / num_simulations,
        'hand_type': most_likely_hand,
    }
