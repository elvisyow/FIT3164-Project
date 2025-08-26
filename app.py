from flask import Flask, redirect, url_for, render_template, request, jsonify
import Data.hashmap as hashmap

app = Flask(__name__)

hashmap.load_csv_basic("Data/atp_tennis.csv")

@app.route('/')
def players():
    # Get the top 10 players from your function
    top10 = hashmap.top_n(20)   # returns list of player objects

    # Extract just their names
    names = [p.name for p in top10]

    return render_template("headtohead.html", players=names)

if __name__ == "__main__":
    app.run(debug = True)




