"""
Generates a synthetic dataset of ATP-style tennis matches.

This mimics the column schema used by Jeff Sackmann's public tennis_atp
dataset (tourney_date, winner_name, loser_name, tourney_level, etc.) so
that swapping in real historical data later requires zero code changes
elsewhere in the project -- just replace the CSV.

Real data source (grab manually if you want live data instead of this
synthetic set): https://github.com/JeffSackmann/tennis_atp
Files are named atp_matches_<year>.csv.

Match outcomes are simulated from hidden "true skill" values per player
using the same logistic win-probability formula as Elo, so the Elo
model in elo.py has a real signal to recover instead of just noise.
"""

import csv
import random
from datetime import datetime, timedelta

random.seed(42)

NUM_PLAYERS = 40
NUM_MATCHES = 3000
START_DATE = datetime(2021, 1, 1)
LEVELS = ["G", "M", "A", "A", "A", "F"]  # weighted toward regular tour events

FIRST_NAMES = ["Carlos", "Novak", "Jannik", "Daniil", "Alexander", "Stefanos",
               "Andrey", "Casper", "Holger", "Taylor", "Frances", "Grigor",
               "Felix", "Denis", "Karen", "Hubert", "Lorenzo", "Sebastian",
               "Tommy", "Cameron", "Ben", "Alex", "Nick", "Gael", "Diego",
               "Pablo", "Roberto", "Fabio", "Marin", "Kei", "Milos", "Dominic",
               "Borna", "Cristian", "Jack", "Jordan", "Reilly", "Tallon",
               "Ugo", "Yoshihito"]


def make_player_names():
    surnames = ["Alvarez", "Petrov", "Nakamura", "Silva", "Kowalski", "Dubois",
                "Nilsen", "Costa", "Ivanov", "Muller", "Yamamoto", "Ferreira",
                "Novak", "Weber", "Rossi", "Garcia", "Kim", "Tanaka", "Popov",
                "Novotny", "Andersen", "Wagner", "Moreau", "Santos", "Kuznetsov",
                "Bergstrom", "Larsen", "Herrera", "Fontaine", "Braun", "Sato",
                "Nowak", "Vasquez", "Lindqvist", "Schmidt", "Okafor", "Diallo",
                "Torres", "Hayashi", "Marin"]
    names = [f"{fn} {sn}" for fn, sn in zip(FIRST_NAMES, surnames)]
    return names[:NUM_PLAYERS]


def generate(path: str = "data/atp_matches_sample.csv"):
    players = make_player_names()
    # Hidden true skill, roughly Elo-scaled, that drives simulated outcomes.
    skills = {p: random.gauss(1500, 150) for p in players}

    rows = []
    current_date = START_DATE
    match_id = 1

    for _ in range(NUM_MATCHES):
        p1, p2 = random.sample(players, 2)
        prob_p1 = 1.0 / (1.0 + 10 ** ((skills[p2] - skills[p1]) / 400.0))
        winner, loser = (p1, p2) if random.random() < prob_p1 else (p2, p1)

        level = random.choice(LEVELS)
        # Slight random walk on skill to simulate form changes over a season.
        skills[p1] += random.gauss(0, 8)
        skills[p2] += random.gauss(0, 8)

        current_date += timedelta(days=random.choice([0, 0, 1, 2, 3]))

        rows.append({
            "tourney_date": current_date.strftime("%Y%m%d"),
            "match_num": match_id,
            "tourney_level": level,
            "winner_name": winner,
            "loser_name": loser,
            "winner_rank": max(1, int(round(2200 - skills[winner]) / 4)),
            "loser_rank": max(1, int(round(2200 - skills[loser]) / 4)),
        })
        match_id += 1

    rows.sort(key=lambda r: (r["tourney_date"], r["match_num"]))

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} synthetic matches -> {path}")


if __name__ == "__main__":
    generate()
