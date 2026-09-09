import os
from src.generate_sample_data import generate
from src.data_loader import load_matches
from src.backtest import run_backtest
from src.evaluate import evaluate_predictions

# Real ATP results for 2023-2024 (source: Tennismylife/TML-Database, same
# schema as Jeff Sackmann's tennis_atp). Falls back to synthetic data if
# this file isn't present.
DATA_PATH = "data/atp_matches_2023_2024.csv"


def main():
    if not os.path.exists(DATA_PATH):
        generate(DATA_PATH)

    matches = load_matches(DATA_PATH)
    print(f"Loaded {len(matches)} real ATP matches (2023-2024)\n")

    # Part 1: accuracy against real outcomes, no simulated odds involved
    eval_results = evaluate_predictions(matches)
    print("=" * 50)
    print("MODEL ACCURACY ON REAL MATCH OUTCOMES")
    print("=" * 50)
    print(f"Matches evaluated:     {eval_results['matches_evaluated']}")
    print(f"Prediction accuracy:   {eval_results['accuracy']*100:.1f}%")
    print(f"Brier score:           {eval_results['brier_score']:.4f}  "
          f"(0 = perfect, 0.25 = coin flip)")
    print()

    # Part 2: betting simulation. Real outcomes, but odds.py still
    # simulates the market side, so treat this as a pipeline demo rather
    # than a real performance number.
    print("=" * 50)
    print("BETTING SIMULATION (real outcomes, simulated market odds)")
    print("=" * 50)
    results = run_backtest(matches)
    print(f"Bets placed:          {results['bets_placed']}")
    print(f"Bets won:             {results['bets_won']}")
    print(f"Hit rate:             {results['hit_rate']*100:.1f}%")
    print()
    print("-- Flat staking (1% of initial bankroll per bet) --")
    print(f"Final bankroll:       ${results['flat_final_bankroll']:.2f}")
    print(f"ROI on amount staked: {results['flat_roi_pct']:.2f}%")
    print()
    print("-- Fractional Kelly staking (25% Kelly) --")
    print(f"Final bankroll:       ${results['kelly_final_bankroll']:.2f}")
    print()

    print("=" * 50)
    print("TOP 10 ELO RATINGS (end of period, from real accuracy model)")
    print("=" * 50)
    for rank, (player, rating) in enumerate(eval_results["elo"].leaderboard(10), start=1):
        print(f"{rank:>2}. {player:<20} {rating:.0f}")


if __name__ == "__main__":
    main()
