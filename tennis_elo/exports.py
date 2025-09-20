from typing import List, Dict
from .models import players_db

def export_player_elo_history_to_dict(player_name: str, include_start_point: bool = False) -> List[Dict[str, object]]:
    p = (players_db.get(player_name)
         or next((v for k,v in players_db.items() if k.lower()==player_name.lower()), None)
         or next((v for k,v in players_db.items() if player_name.lower() in k.lower()), None))
    if not p:
        raise ValueError("Player not found")
    out: List[Dict[str, object]] = []
    if include_start_point and p.history:
        d0 = p.history[0].date
        out.append({"date": (d0.date().isoformat() if d0 else ""), "elo": 500.0})
    for ev in p.history:
        out.append({"date": (ev.date.date().isoformat() if ev.date else ""), "elo": round(ev.new_elo, 2)})
    return out
