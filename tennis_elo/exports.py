import csv
from typing import Optional, List
from .models import players_db, START_ELO

def export_players_to_csv(path: str) -> None:
    with open(path, mode="w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Name", "Elo", "Wins", "Losses", "MatchesPlayed"])
        for p in players_db.values():
            w.writerow([p.name, round(p.elo, 2), p.wins, p.losses, p.wins + p.losses])
    print(f"✅ Exported {len(players_db)} players to {path}")

def export_player_elo_history_to_csv(player_name: str, path: Optional[str] = None,
                                     include_start_point: bool = True) -> str:
    # simple resolver
    p = players_db.get(player_name) or next((v for k,v in players_db.items() if k.lower()==player_name.lower() or player_name.lower() in k.lower()), None)
    if p is None:
        raise ValueError(f"Player '{player_name}' not found.")
    rows: List[List[str]] = []
    if include_start_point:
        first_date = p.history[0].date if p.history else None
        start_label = (first_date.date().isoformat() if first_date else "")
        rows.append([start_label, str(START_ELO)])
    for ev in p.history:
        date_str = ev.date.date().isoformat() if ev.date else ""
        rows.append([date_str, str(round(ev.new_elo, 2))])
    if path is None:
        safe = p.name.replace(" ", "_").replace(".", "")
        path = f"data19082025_{safe}_elo_history.csv"
    with open(path, mode="w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["Date", "Elo"]); w.writerows(rows)
    print(f"✅ Exported Elo history for '{p.name}' to {path}")
    return path
