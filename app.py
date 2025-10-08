from flask import Flask, render_template, request, jsonify
import tennis_elo as elo
from tennis_elo.models import players_db
import os, json, joblib
from sklearn.exceptions import NotFittedError

app = Flask(__name__)


MODEL_PATH = os.getenv("MODEL_PATH", "mlp_model.joblib")
ELOS_JSON  = os.getenv("ELOS_JSON",  "player_elos.json")

mlp_model = None
player_elos_file = {}
START_ELO = 500.0  

def _safe_load_artifacts():
    """Load sklearn pipeline and (optionally) a precomputed Elo json."""
    global mlp_model, player_elos_file
    if os.path.exists(MODEL_PATH):
        try:
            mlp_model = joblib.load(MODEL_PATH)
            print(f"[OK] Loaded model: {MODEL_PATH}")
        except Exception as e:
            print(f"[WARN] Could not load {MODEL_PATH}: {e}")
    else:
        print(f"[WARN] Model not found: {MODEL_PATH}")

    if os.path.exists(ELOS_JSON):
        try:
            with open(ELOS_JSON, "r") as f:
                player_elos_file = json.load(f)
            print(f"[OK] Loaded elos: {ELOS_JSON}")
        except Exception as e:
            print(f"[WARN] Could not load {ELOS_JSON}: {e}")

def get_live_elo(name: str) -> float:
    """Prefer live Elo from players_db; fallback to JSON; else START_ELO."""
    name = (name or "").strip()
    p = players_db.get(name)
    if p:
        return float(p.elo)
    if name in player_elos_file:
        return float(player_elos_file[name])
    return START_ELO



# Homepage
@app.route("/")
@app.route("/home")
def home():
    players = sorted(players_db.values(), key=lambda p: p.elo, reverse=True)
    top3 = players[:3]
    return render_template("homepage.html", top3=top3)

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

# --- ADDED: prediction API for the H2H page ---
@app.route("/api/predict", methods=["POST"])
def api_predict():
    """
    Body example:
    { "p1": "Novak Djokovic", "p2": "Carlos Alcaraz", "surface": "", "round": "" }
    """
    data = request.get_json(force=True) or {}
    p1 = (data.get("p1") or "").strip()
    p2 = (data.get("p2") or "").strip()
    surface = (data.get("surface") or "").strip()
    rnd = (data.get("round") or "").strip()

    if not p1 or not p2:
        return jsonify({"error": "Both p1 and p2 are required"}), 400

    p1_elo = get_live_elo(p1)
    p2_elo = get_live_elo(p2)
    elo_diff = p1_elo - p2_elo

    # Fallback probability if model isn't available
    def elo_expected(a, b, scale=400.0):
        return 1.0 / (1.0 + 10 ** ((b - a) / scale))

    prob = elo_expected(p1_elo, p2_elo)  # default
    if mlp_model is not None:
        try:
            import pandas as pd
            X = pd.DataFrame([{"elo_diff": elo_diff, "surface": surface, "round": rnd}])
            prob = float(mlp_model.predict_proba(X)[:, 1][0])  # P(p1 wins)
        except Exception as e:
            print(f"[WARN] ML predict failed, using Elo prob: {e}")

    predicted = p1 if prob >= 0.5 else p2

    return jsonify({
        "p1": p1, "p2": p2,
        "p1_elo": round(p1_elo, 2),
        "p2_elo": round(p2_elo, 2),
        "elo_diff": round(elo_diff, 2),
        "prob_p1_wins": round(prob, 4),
        "predicted_winner": predicted
    })

if __name__ == "__main__":
    elo.reset_players()
    elo.load_csv_elo("Data/atp_tennis_clean.csv", K=32)
    _safe_load_artifacts()  # <-- ADDED
    app.run(debug=True)
