from typing import Optional
from .models import Player, RatingEvent, players_db, START_ELO
from .models import players_db as db

# Basic +/-5
WIN_POINTS = 5.0
LOSS_POINTS = -5.0

def ensure_player(name: str) -> Player:
    name = name.strip()
    if not name:
        raise ValueError("Player name is empty after stripping.")
    if name not in db:
        db[name] = Player(name=name)
    return db[name]

def record_match_basic(p1: str, p2: str, winner: str,
                       date=None, tournament="", surface="", rnd="") -> None:
    a = ensure_player(p1); b = ensure_player(p2)
    winner = winner.strip()
    if winner == p1:
        a.elo += WIN_POINTS; a.wins += 1
        b.elo += LOSS_POINTS; b.losses += 1
        a.history.append(RatingEvent(date, b.name, "W", WIN_POINTS, a.elo, (tournament, surface, rnd)))
        b.history.append(RatingEvent(date, a.name, "L", LOSS_POINTS, b.elo, (tournament, surface, rnd)))
    elif winner == p2:
        b.elo += WIN_POINTS; b.wins += 1
        a.elo += LOSS_POINTS; a.losses += 1
        b.history.append(RatingEvent(date, a.name, "W", WIN_POINTS, b.elo, (tournament, surface, rnd)))
        a.history.append(RatingEvent(date, b.name, "L", LOSS_POINTS, a.elo, (tournament, surface, rnd)))
    else:
        raise ValueError("winner must equal p1 or p2")

# Proper Elo
K_DEFAULT = 32.0
ELO_SCALE = 400.0

def expected_score(r_a: float, r_b: float, scale: float = ELO_SCALE) -> float:
    return 1.0 / (1.0 + 10.0 ** ((r_b - r_a) / scale))

def record_match_elo(p1: str, p2: str, winner: str,
                     date=None, tournament="", surface="", rnd="",
                     K: float = K_DEFAULT, scale: float = ELO_SCALE) -> None:
    a = ensure_player(p1); b = ensure_player(p2)
    Ea = expected_score(a.elo, b.elo, scale); Eb = 1.0 - Ea
    if winner == p1:
        Sa, Sb = 1.0, 0.0
    elif winner == p2:
        Sa, Sb = 0.0, 1.0
    else:
        raise ValueError("winner must equal p1 or p2")
    da = K * (Sa - Ea); dbb = K * (Sb - Eb)
    a.elo += da; b.elo += dbb
    if Sa == 1.0:
        a.wins += 1; b.losses += 1
        a.history.append(RatingEvent(date, b.name, "W", da, a.elo, (tournament, surface, rnd)))
        b.history.append(RatingEvent(date, a.name, "L", dbb, b.elo, (tournament, surface, rnd)))
    else:
        b.wins += 1; a.losses += 1
        b.history.append(RatingEvent(date, a.name, "W", dbb, b.elo, (tournament, surface, rnd)))
        a.history.append(RatingEvent(date, b.name, "L", da, a.elo, (tournament, surface, rnd)))
