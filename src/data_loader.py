"""
Loads ATP match data (Sackmann schema) from CSV, sorted chronologically.
Works identically whether the CSV is synthetic sample data or a real
file downloaded from https://github.com/JeffSackmann/tennis_atp
"""

import csv


def load_matches(path: str):
    matches = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            matches.append({
                "date": row["tourney_date"],
                "level": row.get("tourney_level", "A"),
                "winner": row["winner_name"],
                "loser": row["loser_name"],
            })
    # Ensure chronological order -- critical for a walk-forward backtest,
    # since we can only bet using information available before the match.
    matches.sort(key=lambda m: m["date"])
    return matches
