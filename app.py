from flask import Flask, render_template, request, jsonify
import tennis_elo as elo

app = Flask(__name__)


# Homepage
@app.route("/")
def home():
    return render_template("homepage.html")

@app.route("/rankings")
def rankings():
    return render_template("rankings.html")

@app.route("/headtohead")
def headtohead():
    names = [p.name for p in elo.top_n(10)]
    return render_template("headtohead.html", players=names)

@app.route("/comparisons")
def comparisons():
    return render_template("comparisons.html")

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