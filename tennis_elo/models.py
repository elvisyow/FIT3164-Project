from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from datetime import datetime

START_ELO: float = 500.0  # float for proper Elo

@dataclass
class RatingEvent:
    date: Optional[datetime]           # allow None when date missing
    opponent: str
    result: str                        # "W" or "L"
    delta: float                       # Elo change for THIS player
    new_elo: float                     # Elo AFTER this match
    meta: Tuple[str, str, str] = field(default_factory=tuple)  # (tournament, surface, round)

@dataclass
class Player:
    name: str
    elo: float = START_ELO
    wins: int = 0
    losses: int = 0
    history: List[RatingEvent] = field(default_factory=list)

# A dictionary where each key is a player's name (string)
Players = Dict[str, Player]
# Initialize the global player database (hashmap).
players_db: Players = {}

def reset_players() -> None:
    players_db.clear()

def ensure_player(name: str) -> Player:
    name = (name or "").strip()
    if not name:
        raise ValueError("Player name is empty after stripping.")
    if name not in players_db:
        players_db[name] = Player(name=name)
    return players_db[name]
