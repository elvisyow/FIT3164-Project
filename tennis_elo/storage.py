import json
from dataclasses import asdict
from datetime import datetime
from .models import players_db, Player, RatingEvent

def save_players_db(path: str = "players_db.json") -> None:
    serializable = {k: asdict(v) for k, v in players_db.items()}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2, default=str)

def load_players_db(path: str = "players_db.json") -> None:
    global players_db
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    players_db = {}
    for name, pdata in raw.items():
        hist = []
        for ev in pdata["history"]:
            d = ev["date"]
            date_val = datetime.fromisoformat(d) if d and d != "0001-01-01 00:00:00" else None
            hist.append(RatingEvent(date_val, ev["opponent"], ev["result"], ev["delta"], ev["new_elo"], tuple(ev["meta"])))
        players_db[name] = Player(pdata["name"], pdata["elo"], pdata["wins"], pdata["losses"], hist)
