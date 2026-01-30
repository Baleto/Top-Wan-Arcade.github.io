from __future__ import annotations
from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import random

from engines.blackjack_engine import BlackjackLiteEngine, build_deck, hand_total
from stats_store import load_stats, save_stats, inc, setmax

app = Flask(__name__)
CORS(app)  # dev-friendly (later restrict origins)

engine = BlackjackLiteEngine()

# In-memory session (simple). Later: per-user sessions / JWT / database.
CURRENT = {
    "state": None,
    "rng": None,
    "streak": 0,
}

@app.get("/api/blackjack/state")
def get_state():
    st = CURRENT["state"]
    if not st:
        return jsonify({"active": False})
    reveal = (st.phase != "player_turn")
    return jsonify({"active": True, "data": st.public_view(reveal_dealer=reveal)})


@app.post("/api/blackjack/new")
def new_round():
    seed = int(time.time() * 1000) ^ random.randint(1, 1_000_000)
    round_id = str(seed)

    st = engine.start_round(round_id=round_id, seed=seed)

    # store rng/deck for this round
    rng = random.Random(seed)
    deck = build_deck(rng)
    # burn the 4 initial cards that were dealt (2 player, 2 dealer)
    deck.pop(); deck.pop(); deck.pop(); deck.pop()

    CURRENT["state"] = st
    CURRENT["deck"] = deck

    # Handle stats if resolved immediately (naturals)
    if st.phase == "resolved":
        stats = load_stats()
        if st.result == "player":
            inc(stats, "bj_user_wins")
            inc(stats, "bj_blackjacks")  # natural win
            CURRENT["streak"] += 1
        elif st.result == "dealer":
            inc(stats, "bj_cpu_wins")
            CURRENT["streak"] = 0
        setmax(stats, "bj_best_streak", CURRENT["streak"])
        save_stats(stats)

    reveal = (st.phase != "player_turn")
    return jsonify(st.public_view(reveal_dealer=reveal))


@app.post("/api/blackjack/hit")
def hit():
    st = CURRENT["state"]
    if not st:
        return jsonify({"error": "No active round."}), 400

    deck = CURRENT["deck"]
    if not deck:
        return jsonify({"error": "Deck empty."}), 400

    card = deck.pop()
    st = engine.hit(st, card)
    CURRENT["state"] = st

    if st.phase == "resolved":
        stats = load_stats()
        if st.result == "player":
            inc(stats, "bj_user_wins")
            CURRENT["streak"] += 1
        elif st.result == "dealer":
            inc(stats, "bj_cpu_wins")
            CURRENT["streak"] = 0
        setmax(stats, "bj_best_streak", CURRENT["streak"])
        save_stats(stats)

    reveal = (st.phase != "player_turn")
    return jsonify(st.public_view(reveal_dealer=reveal))


@app.post("/api/blackjack/stand")
def stand():
    st = CURRENT["state"]
    if not st:
        return jsonify({"error": "No active round."}), 400

    deck = CURRENT["deck"]
    draws = []
    # Dealer may need multiple cards; we pass a list, engine stops at 17+
    # We'll just provide a generous chunk.
    for _ in range(10):
        if deck:
            draws.append(deck.pop())

    st = engine.stand_and_resolve(st, dealer_draws=draws)
    CURRENT["state"] = st

    stats = load_stats()
    if st.result == "player":
        inc(stats, "bj_user_wins")
        CURRENT["streak"] += 1
    elif st.result == "dealer":
        inc(stats, "bj_cpu_wins")
        CURRENT["streak"] = 0
    # push: streak unchanged
    setmax(stats, "bj_best_streak", CURRENT["streak"])
    save_stats(stats)

    return jsonify(st.public_view(reveal_dealer=True))


@app.get("/api/blackjack/stats")
def stats():
    return jsonify(load_stats())


if __name__ == "__main__":
    app.run(debug=True, port=5050)
