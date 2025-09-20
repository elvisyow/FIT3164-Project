from typing import Optional
from .models import RatingEvent, Player, players_db, ensure_player, START_ELO

# proper Elo
K_DEFAULT = 32.0
ELO_SCALE = 400.0

def expected_score(r_a: float, r_b: float, scale: float = ELO_SCALE) -> float:
    return 1.0 / (1.0 + 10.0 ** ((r_b - r_a) / scale))

def record_match_elo(p1: str, p2: str, winner: str,
                     date=None, tournament="", surface="", rnd="",
                     K: float = K_DEFAULT, scale: float = ELO_SCALE) -> None:
    p1 = p1.strip(); p2 = p2.strip(); winner = winner.strip()
    a = ensure_player(p1); b = ensure_player(p2)
    Ea = expected_score(a.elo, b.elo, scale); Eb = 1.0 - Ea
    if winner == p1:
        Sa, Sb = 1.0, 0.0
    elif winner == p2:
        Sa, Sb = 0.0, 1.0
    else:
        raise ValueError("winner must equal p1 or p2")
    da = K * (Sa - Ea); db = K * (Sb - Eb)
    a.elo += da; b.elo += db
    if Sa == 1.0:
        a.wins += 1; b.losses += 1
        a.history.append(RatingEvent(date, b.name, "W", da, a.elo, (tournament, surface, rnd)))
        b.history.append(RatingEvent(date, a.name, "L", db, b.elo, (tournament, surface, rnd)))
    else:
        b.wins += 1; a.losses += 1
        b.history.append(RatingEvent(date, a.name, "W", db, b.elo, (tournament, surface, rnd)))
        a.history.append(RatingEvent(date, b.name, "L", da, a.elo, (tournament, surface, rnd)))

def top_n(n: int = 10):
    return sorted(players_db.values(), key=lambda p: p.elo, reverse=True)[:n]