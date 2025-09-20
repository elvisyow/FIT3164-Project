import csv
from typing import Optional, Iterable
from itertools import islice
from .parsers import parse_date
from .rating import record_match_elo

def _first_n(iterable: Iterable, n: Optional[int]):
    return iterable if n is None else islice(iterable, n)



def load_csv_elo(path: str, limit_rows: Optional[int] = None, K: float = 32.0) -> None:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in _first_n(reader, limit_rows):
            p1 = (row.get("Player_1") or "").strip()
            p2 = (row.get("Player_2") or "").strip()
            winner = (row.get("Winner") or "").strip()
            if not p1 or not p2 or not winner:
                continue
            record_match_elo(
                p1, p2, winner,
                date=parse_date(row.get("Date") or ""),
                tournament=(row.get("Tournament") or "").strip(),
                surface=(row.get("Surface") or "").strip(),
                rnd=(row.get("Round") or "").strip(),
                K=K
            )
