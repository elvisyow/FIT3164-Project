import csv, os
from typing import Optional, List, Dict
from .models import players_db, START_ELO

def export_players_to_csv(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode="w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Name", "Elo", "Wins", "Losses", "MatchesPlayed"])
        for p in players_db.values():
            w.writerow([p.name, round(p.elo, 2), p.wins, p.losses, p.wins + p.losses])

def resolve_player(name: str):
    return (players_db.get(name)
            or next((v for k,v in players_db.items() if k.lower()==name.lower()), None)
            or next((v for k,v in players_db.items() if name.lower() in k.lower()), None))

def export_player_elo_history_to_csv(player_name: str, path: Optional[str] = None,
                                     include_start_point: bool = True) -> str:
    p = resolve_player(player_name)
    if p is None:
        raise ValueError(f"Player '{player_name}' not found.")
    rows: List[List[str]] = []
    if include_start_point:
        d0 = p.history[0].date if p.history else None
        rows.append([d0.date().isoformat() if d0 else "", str(START_ELO)])
    for ev in p.history:
        rows.append([ev.date.date().isoformat() if ev.date else "", str(round(ev.new_elo, 2))])
    if path is None:
        safe = p.name.replace(" ", "_").replace(".", "")
        path = f"Data/processed/{safe}_elo_history.csv"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode="w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["Date", "Elo"]); w.writerows(rows)
    return path

def export_player_elo_history_to_dict(player_name: str, include_start_point: bool = False) -> List[Dict[str, object]]:
    p = resolve_player(player_name)
    if p is None:
        raise ValueError(f"Player '{player_name}' not found")
    out: List[Dict[str, object]] = []
    if include_start_point:
        d0 = p.history[0].date if p.history else None
        out.append({"date": (d0.date().isoformat() if d0 else ""), "elo": START_ELO})
    for ev in p.history:
        out.append({"date": (ev.date.date().isoformat() if ev.date else ""), "elo": round(ev.new_elo, 2)})
    return out
