from flask import Flask, render_template, request, jsonify
import Data.hashmap as hashmap

app = Flask(__name__)

# Load CSV data
hashmap.load_csv_basic("Data/atp_tennis_clean.csv")


# Route to list top 10 players on homepage
@app.route('/')
def players():
    top10 = hashmap.top_n(10)  # returns list of player objects
    names = [p.name for p in top10]
    return render_template("headtohead.html", players=names)


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
