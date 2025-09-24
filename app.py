from flask import Flask, render_template, request, jsonify
import tennis_elo as elo
from tennis_elo.models import players_db

app = Flask(__name__)


# Homepage
@app.route("/")
def home():
    return render_template("homepage.html")

@app.route("/rankings")
def rankings():
    sort_key = request.args.get("sort") or "elo_desc"

    players = list(players_db.values())

    def matches(p): return (p.wins or 0) + (p.losses or 0)
    if sort_key == "elo_asc":
        players.sort(key=lambda p: p.elo)
    elif sort_key == "matches_desc":
        players.sort(key=lambda p: matches(p), reverse=True)
    else:
        players.sort(key=lambda p: p.elo, reverse=True)

    ranked = []
    for i, p in enumerate(players, start=1):
        ranked.append({
            "rank": i,
            "name": p.name,
            "elo": round(p.elo, 2),
            "wins": p.wins,
            "losses": p.losses,
            "matches": matches(p),
        })

    return render_template("rankings.html", players=ranked, sort=sort_key)

@app.route("/headtohead")
def headtohead():
    names = [p.name for p in elo.top_n(10)]
    return render_template("headtohead.html", players=names)

@app.route("/comparisons")
def comparisons():
    names = [p.name for p in elo.top_n(10)]
    return render_template("comparisons.html", players=names)

@app.route("/get_elo_history")
def player_timeline():
    player_name = request.args.get("player")
    if not player_name:
        return jsonify({"error": "Player name must be provided"}), 400
    try:
        timeline = elo.export_player_elo_history_to_dict(player_name)
    except Exception:
        return jsonify({"error": "Player not found"}), 404
    return jsonify(timeline)

if __name__ == "__main__":
    elo.reset_players()
    elo.load_csv_elo("Data/atp_tennis_clean.csv", K=32)
    app.run(debug=True)