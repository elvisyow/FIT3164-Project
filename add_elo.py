import pandas as pd

# Load your dataset
df = pd.read_csv("./Data/atp_tennis_clean.csv")

# Player dictionary: {player: (wins, losses, elo)}
players = {}

# Elo settings
DEFAULT_ELO = 500
ELO_WIN = 5
ELO_LOSS = -5

def ensure_player(player):
    """Ensure a player exists in the hashmap, else add them."""
    if player not in players:
        players[player] = (0, 0, DEFAULT_ELO)

def win(player):
    """Update player stats for a win (immutably)."""
    wins, losses, elo = players[player]
    players[player] = (wins + 1, losses, elo + ELO_WIN)

def loss(player):
    """Update player stats for a loss (immutably)."""
    wins, losses, elo = players[player]
    players[player] = (wins, losses + 1, elo + ELO_LOSS)

# New columns to store Elo ratings after each match
p1_elos = []
p2_elos = []

# Process matches row by row
for _, row in df.iterrows():
    p1, p2, winner = row["Player_1"], row["Player_2"], row["Winner"]

    # Ensure both players exist
    ensure_player(p1)
    ensure_player(p2)

    # Apply win/loss updates
    if winner == p1:
        win(p1)
        loss(p2)
    else:
        win(p2)
        loss(p1)

    # Record the updated Elo ratings of both players
    p1_elos.append(players[p1][2])
    p2_elos.append(players[p2][2])

# Add Elo columns to the dataframe
df["Player_1_Elo"] = p1_elos
df["Player_2_Elo"] = p2_elos

# Save new CSV with Elo ratings
df.to_csv("./Data/atp_tennis_with_elo.csv", index=False)

print("Finished! File saved as ./Data/atp_tennis_with_elo.csv")
