from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from datetime import datetime

START_ELO = 500.0  # float now

@dataclass
class RatingEvent:
    date: Optional[datetime]            # allow None for missing dates
    opponent: str
    result: str                         # "W" or "L"
    delta: float
    new_elo: float
    meta: Tuple[str, str, str] = field(default_factory=tuple)  # (tournament, surface, round)

@dataclass
class Player:
    name: str
    elo: float = START_ELO
    wins: int = 0
    losses: int = 0
    history: List[RatingEvent] = field(default_factory=list)

Players = Dict[str, Player]
players_db: Players = {}

def reset_players() -> None:
    players_db.clear()
