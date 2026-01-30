from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List, Tuple, Optional
import random

Card = Tuple[str, str]  # (rank, suit)

RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
SUITS = ["♠", "♥", "♦", "♣"]  # display only


def build_deck(rng: random.Random) -> List[Card]:
    deck = [(r, s) for r in RANKS for s in SUITS]
    rng.shuffle(deck)
    return deck


def hand_total(hand: List[Card]) -> int:
    total = 0
    aces = 0
    for r, _ in hand:
        if r in ("J", "Q", "K"):
            total += 10
        elif r == "A":
            total += 11
            aces += 1
        else:
            total += int(r)

    while total > 21 and aces > 0:
        total -= 10
        aces -= 1

    return total


def is_blackjack(hand: List[Card]) -> bool:
    return len(hand) == 2 and hand_total(hand) == 21


@dataclass
class RoundState:
    round_id: str
    deck_seed: int
    player: List[Card]
    dealer: List[Card]
    phase: str  # "player_turn" | "dealer_turn" | "resolved"
    result: Optional[str]  # "player" | "dealer" | "push" | None
    message: str

    @property
    def player_total(self) -> int:
        return hand_total(self.player)

    @property
    def dealer_total(self) -> int:
        return hand_total(self.dealer)

    def public_view(self, reveal_dealer: bool = False) -> dict:
        # Hide dealer[0] until reveal
        dealer_cards = self.dealer.copy()
        if not reveal_dealer and len(dealer_cards) > 0:
            dealer_cards = [("?", "?")] + dealer_cards[1:]

        return {
            "round_id": self.round_id,
            "phase": self.phase,
            "result": self.result,
            "message": self.message,
            "player": self.player,
            "dealer": dealer_cards,
            "player_total": self.player_total,
            "dealer_total": self.dealer_total if reveal_dealer else None,
        }


class BlackjackLiteEngine:
    """
    Stateless-ish engine: each round has its own seed so we can reproduce deck on server.
    For simplicity we keep state in memory in the API (later you can persist).
    """

    def __init__(self) -> None:
        pass

    def start_round(self, round_id: str, seed: int) -> RoundState:
        rng = random.Random(seed)
        deck = build_deck(rng)

        player = [deck.pop(), deck.pop()]
        dealer = [deck.pop(), deck.pop()]

        state = RoundState(
            round_id=round_id,
            deck_seed=seed,
            player=player,
            dealer=dealer,
            phase="player_turn",
            result=None,
            message="Dealing…",
        )

        # Naturals
        p_bj = is_blackjack(player)
        d_bj = is_blackjack(dealer)

        if p_bj and d_bj:
            state.phase = "resolved"
            state.result = "push"
            state.message = "Both have Blackjack! Push."
        elif p_bj:
            state.phase = "resolved"
            state.result = "player"
            state.message = "Blackjack! You win!"
        elif d_bj:
            state.phase = "resolved"
            state.result = "dealer"
            state.message = "Dealer has Blackjack. CPU wins."
        else:
            state.message = "Your move: Hit or Stand."

        return state

    def hit(self, state: RoundState, next_card: Card) -> RoundState:
        if state.phase != "player_turn":
            return state

        state.player.append(next_card)

        pt = state.player_total
        if pt > 21:
            state.phase = "resolved"
            state.result = "dealer"
            state.message = f"Bust at {pt}! CPU wins."
        else:
            state.message = f"You drew {next_card[0]}{next_card[1]} — total {pt}. Hit or Stand?"

        return state

    def stand_and_resolve(self, state: RoundState, dealer_draws: List[Card]) -> RoundState:
        if state.phase != "player_turn":
            return state

        state.phase = "dealer_turn"

        # Dealer reveals + draws to 17+
        for c in dealer_draws:
            if hand_total(state.dealer) >= 17:
                break
            state.dealer.append(c)

        pt = state.player_total
        dt = state.dealer_total

        state.phase = "resolved"
        if dt > 21:
            state.result = "player"
            state.message = f"Dealer busts at {dt}! You win."
        elif pt > dt:
            state.result = "player"
            state.message = f"You win {pt} vs {dt}."
        elif pt < dt:
            state.result = "dealer"
            state.message = f"CPU wins {dt} vs {pt}."
        else:
            state.result = "push"
            state.message = f"Push at {pt}."

        return state
