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
