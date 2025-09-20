from flask import Flask, render_template, request, jsonify
import Data.hashmap as hashmap

app = Flask(__name__)

# Load CSV data
hashmap.load_csv_elo("Data/atp_tennis_clean.csv")


# Homepage
@app.route("/")
def home():
    return render_template("homepage.html")


# Rankings page
@app.route("/rankings")
def rankings():
    return render_template("rankings.html")


# Head-to-Head page
@app.route("/headtohead")
def headtohead():
    top10 = hashmap.top_n(10)  # keep your logic here
    names = [p.name for p in top10]
    return render_template("headtohead.html", players=names)


# Comparisons page
@app.route("/comparisons")
def comparisons():
    return render_template("comparisons.html")


# API endpoint to get a player's Elo history
@app.route('/get_elo_history')
def player_timeline():
    player_name = request.args.get("player")
    if not player_name:
        return jsonify({"error": "Player name must be provided"}), 400

    try:
        timeline = hashmap.export_player_elo_history_to_dict(player_name)
    except Exception:
        return jsonify({"error": "Player not found"}), 404

    return jsonify(timeline)


if __name__ == "__main__":
    app.run(debug=True)
