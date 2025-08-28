from tennis_elo.models import reset_players
from tennis_elo.loaders import load_csv_basic, load_csv_elo
from tennis_elo.exports import export_player_elo_history_to_csv

CSV_IN = "Data/processed/atp_tennis_clean.csv"     
NAME   = "Nadal R."                         

# --- OLD TEST SYSTEM (±5) ---
reset_players()
load_csv_basic(CSV_IN)  # uses your record_match_basic
hist_basic = "Data/processed/nadal_history_basic.csv"
export_player_elo_history_to_csv(NAME, hist_basic, include_start_point=False)

# --- PROPER ELO ---
reset_players()
load_csv_elo(CSV_IN, K=32)  # uses proper Elo
hist_proper = "Data/processed/nadal_history_proper.csv"
export_player_elo_history_to_csv(NAME, hist_proper, include_start_point=False)



import pandas as pd
import matplotlib.pyplot as plt

basic = pd.read_csv(hist_basic, parse_dates=["Date"])
proper = pd.read_csv(hist_proper, parse_dates=["Date"])

# drop missing dates (if any) and sort
basic = basic.dropna(subset=["Date"]).sort_values("Date")
proper = proper.dropna(subset=["Date"]).sort_values("Date")

# if multiple matches on the same date, take the LAST Elo of that day
basic = basic.groupby("Date", as_index=False).last().rename(columns={"Elo": "Elo_basic"})
proper = proper.groupby("Date", as_index=False).last().rename(columns={"Elo": "Elo_proper"})

# outer-join so we see both lines across all dates
combo = pd.merge(basic, proper, on="Date", how="outer").sort_values("Date")

# plot
plt.figure(figsize=(10,5))
plt.plot(combo["Date"], combo["Elo_basic"], marker="o", linestyle="-", label="Old test Elo (±5)")
plt.plot(combo["Date"], combo["Elo_proper"], marker="o", linestyle="-", label="Proper Elo")
plt.title(f"{NAME} — Elo over time (comparison)")
plt.xlabel("Date"); plt.ylabel("Elo rating")
plt.legend(); plt.grid(True)
plt.tight_layout()
plt.show()
