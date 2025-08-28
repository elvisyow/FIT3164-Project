from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Iterable
from datetime import datetime
from itertools import islice
import csv

START_ELO = 500
WIN_POINTS = 5
LOSS_POINTS = -5

# ---------- Data model ----------

@dataclass
class RatingEvent:
    """
    Immutable snapshot of a single rating update for a player.

    Attributes:
        date: Match date; if unavailable, set to datetime.min.
        opponent: Opponent's display name.
        result: "W" for win, "L" for loss (from this player's perspective).
        delta: Rating change from this match (+5 for win, -5 for loss in this basic system).
        new_elo: Player's Elo immediately AFTER applying 'delta'.
        meta: Tuple of (tournament, surface, round) for light-weight metadata.
    """
    date: datetime
    opponent: str
    result: str        # "W" or "L"
    delta: int
    new_elo: int
    meta: Tuple[str, str, str] = field(default_factory=tuple)  # (tournament, surface, round)

@dataclass
class Player:
    """
    Player state tracked in-memory.

    Attributes:
        name: Display name as used in the CSV.
        elo: Current Elo (starts at START_ELO).
        wins: Number of matches won.
        losses: Number of matches lost.
        history: Chronological list of RatingEvent updates.
    """
    name: str
    elo: int = START_ELO
    wins: int = 0
    losses: int = 0
    history: List[RatingEvent] = field(default_factory=list)

Players = Dict[str, Player]
players_db: Players = {}

# ---------- Helpers ----------

def ensure_player(name: str) -> Player:
    """
    Ensure a Player entry exists for 'name' in the players_db.

    If the player does not exist, create a new Player initialized to START_ELO.

    Args:
        name: Player display name (used as the key).

    Returns:
        The Player object corresponding to 'name'.
    """
    name = name.strip()
    if not name:
        raise ValueError("Player name is empty after stripping.")
    if name not in players_db:
        players_db[name] = Player(name=name)
    return players_db[name]

def record_match_basic(
    p1: str,
    p2: str,
    winner: str,
    date: Optional[datetime] = None,
    tournament: str = "",
    surface: str = "",
    rnd: str = ""
) -> None:
    """
    Apply a single match result to the database using the basic rules:
    - Everyone starts at 500
    - Win = +5 rating and +1 win
    - Loss = -5 rating and +1 loss
    Also appends a RatingEvent to each player's history.

    Args:
        p1: Player 1's display name (as in CSV).
        p2: Player 2's display name (as in CSV).
        winner: Winner's display name; MUST equal p1 or p2.
        date: Match date; if None or invalid, defaults to datetime.min.
        tournament: Tournament name (CSV 'Tournament').
        surface: Court surface (CSV 'Surface').
        rnd: Round label (CSV 'Round').

    Raises:
        ValueError: If 'winner' is not exactly equal to p1 or p2 after stripping.
    """
    p1 = p1.strip()
    p2 = p2.strip()
    winner = winner.strip()
    a = ensure_player(p1)
    b = ensure_player(p2)
    safe_date = date or datetime.min

    if winner == p1:
        a.elo += WIN_POINTS; a.wins += 1
        b.elo += LOSS_POINTS; b.losses += 1
        a.history.append(RatingEvent(safe_date, b.name, "W", WIN_POINTS, a.elo, (tournament, surface, rnd)))
        b.history.append(RatingEvent(safe_date, a.name, "L", LOSS_POINTS, b.elo, (tournament, surface, rnd)))
    elif winner == p2:
        b.elo += WIN_POINTS; b.wins += 1
        a.elo += LOSS_POINTS; a.losses += 1
        b.history.append(RatingEvent(safe_date, a.name, "W", WIN_POINTS, b.elo, (tournament, surface, rnd)))
        a.history.append(RatingEvent(safe_date, b.name, "L", LOSS_POINTS, a.elo, (tournament, surface, rnd)))
    else:
        raise ValueError("winner must equal p1 or p2")

def parse_date(s: str) -> Optional[datetime]:
    """
    Parse a date string from the CSV. Supports day/month/year (e.g., '5/01/2004').
    Returns None if parsing fails.
    """
    s = (s or "").strip()
    if not s:
        return None
    # try dd/mm/yyyy
    try:
        return datetime.strptime(s, "%d/%m/%Y")
    except ValueError:
        pass
    # try yyyy-mm-dd (iso)
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        pass
    return None

def _first_n(iterable: Iterable, n: Optional[int]) -> Iterable:
    """
    Yield at most the first n items from an iterable; if n is None, yield all.

    Args:
        iterable: Any iterable (e.g., csv.DictReader).
        n: Optional limit; if None, do not limit.

    Returns:
        An iterator over up to n items.
    """
    return iterable if n is None else islice(iterable, n)

# ---------- CSV loader ----------

def load_csv_basic(path: str, limit_rows: Optional[int] = None) -> None:
    """
    Load and apply matches from the big CSV using the basic +5/-5 rules.

    CSV columns expected (as per your sample):
        "Tournament","Date","Series","Court","Surface","Round","Best of",
        "Player_1","Player_2","Winner","Rank_1","Rank_2","Pts_1","Pts_2",
        "Odd_1","Odd_2","Score"

    Only these are used by this loader:
        "Tournament", "Date", "Surface", "Round", "Player_1", "Player_2", "Winner"

    Args:
        path: Filesystem path to the CSV.
        limit_rows: If provided, only process the first N rows (useful for smoke tests).

    Side effects:
        Mutates players_db by updating (or creating) Player entries and appending history events.
    """
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in _first_n(reader, limit_rows):
            # Extract and sanitize
            p1 = (row.get("Player_1") or "").strip()
            p2 = (row.get("Player_2") or "").strip()
            winner = (row.get("Winner") or "").strip()
            if not p1 or not p2 or not winner:
                # Skip malformed rows
                continue

            date = parse_date(row.get("Date") or "")
            tournament = (row.get("Tournament") or "").strip()
            surface = (row.get("Surface") or "").strip()
            rnd = (row.get("Round") or "").strip()

            # Apply the match
            record_match_basic(
                p1, p2, winner,
                date=date,
                tournament=tournament,
                surface=surface,
                rnd=rnd
            )

# ---------- Utilities & tests ----------

def top_n(n: int = 10) -> List[Player]:
    """
    Return the top-n players by current Elo.

    Args:
        n: Number of players to return.

    Returns:
        A list of Player objects sorted by Elo descending, length <= n.
    """
    return sorted(players_db.values(), key=lambda p: p.elo, reverse=True)[:n]

def reset_players() -> None:
    """
    Clear the in-memory player database (useful for tests).
    """
    players_db.clear()

def test_basic_three_matches() -> None:
    """
    Minimal unit test over three matches to confirm +5/-5 updates and history logging.
    """
    reset_players()
    record_match_basic("Nadal", "Federer", winner="Nadal")
    record_match_basic("Nadal", "Djokovic", winner="Djokovic")
    record_match_basic("Federer", "Djokovic", winner="Federer")

    assert players_db["Nadal"].elo == 500 and players_db["Nadal"].wins == 1 and players_db["Nadal"].losses == 1
    assert players_db["Federer"].elo == 500 and players_db["Federer"].wins == 1 and players_db["Federer"].losses == 1
    assert players_db["Djokovic"].elo == 500 and players_db["Djokovic"].wins == 1 and players_db["Djokovic"].losses == 1
    assert len(players_db["Nadal"].history) == 2

def export_players_to_csv(path: str = "eerr.csv") -> None:
    """
    Export current player snapshots to CSV.
    Columns: Name, Elo, Wins, Losses, MatchesPlayed
    """
    with open(path, mode="w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Name", "Elo", "Wins", "Losses", "MatchesPlayed"])
        for p in players_db.values():
            w.writerow([p.name, p.elo, p.wins, p.losses, p.wins + p.losses])
    print(f"✅ Exported {len(players_db)} players to {path}")

def resolve_player(name: str) -> Optional[Player]:
    """
    Best-effort resolver: exact match first, then case-insensitive,
    then substring (case-insensitive). Returns the Player or None.
    """
    if name in players_db:
        return players_db[name]
    lower = name.lower()
    # case-insensitive exact
    for k in players_db.keys():
        if k.lower() == lower:
            return players_db[k]
    # substring search
    for k in players_db.keys():
        if lower in k.lower():
            return players_db[k]
    return None

def export_player_elo_history_to_csv(player_name: str, path: Optional[str] = None,
                                     include_start_point: bool = True) -> str:
    """
    Export (date, elo) timeline for a single player so frontend can plot.
    - If dates are missing, events carry datetime.min; you may filter those.
    - include_start_point=True adds an initial row representing the pre-match Elo.

    Columns: Date, Elo
    """
    p = resolve_player(player_name)
    if p is None:
        raise ValueError(f"Player '{player_name}' not found in players_db.")

    rows: List[List[str]] = []
    # optional starting anchor at START_ELO (before any matches)
    if include_start_point:
        # Use a safe artificial date just before first event if available
        first_date = p.history[0].date if p.history else datetime.min
        start_date = (first_date if first_date != datetime.min else datetime(1, 1, 1))
        rows.append([start_date.date().isoformat(), str(START_ELO)])

    # append each event’s (date, new_elo)
    for ev in p.history:
        # if date is datetime.min, write empty to let FE handle as “unknown”
        date_str = "" if ev.date == datetime.min else ev.date.date().isoformat()
        rows.append([date_str, str(ev.new_elo)])

    # default filename if not provided
    if path is None:
        safe = p.name.replace(" ", "_").replace(".", "")
        path = f"data19082025_{safe}_elo_history.csv"

    with open(path, mode="w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Date", "Elo"])
        w.writerows(rows)

    print(f"✅ Exported Elo history for '{p.name}' with {len(rows)} rows to {path}")
    return path



reset_players()
load_csv_basic("Data/atp_tennis_clean.csv")
export_players_to_csv("data19082025.csv")
export_player_elo_history_to_csv("Nadal R.")
 