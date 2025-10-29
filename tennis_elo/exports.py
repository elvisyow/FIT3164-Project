from typing import List, Dict
from .models import players_db

def export_player_elo_history_to_dict(player_name: str, include_start_point: bool = False) -> List[Dict[str, object]]:
    # Attempt to retrieve the player object from the players_db dictionary
    # 1. Exact name match
    # 2. Case-insensitive name match
    # 3. Partial substring match (case-insensitive)
    p = (players_db.get(player_name)
         or next((v for k, v in players_db.items() if k.lower() == player_name.lower()), None)
         or next((v for k, v in players_db.items() if player_name.lower() in k.lower()), None))
    # If no player was found after all matching attempts, raise an error
    if not p:
        raise ValueError("Player not found")
    # Initialize the output list, which will store dictionaries of date–Elo pairs
    out: List[Dict[str, object]] = []
    # If requested, include the player's starting Elo (default = 500)
    # This adds an initial point to the timeline before any recorded matches
    if include_start_point and p.history:
        d0 = p.history[0].date  # Get date of first recorded match
        out.append({"date": (d0.date().isoformat() if d0 else ""), "elo": 500.0})
    # Iterate through the player's match history
    for ev in p.history:
        # Append each match's date (in ISO format) and corresponding new Elo rating
        out.append({
            "date": (ev.date.date().isoformat() if ev.date else ""),
            "elo": round(ev.new_elo, 2)
        })
    # Return the complete Elo timeline as a list of dictionaries
    return out