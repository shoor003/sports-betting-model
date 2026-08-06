import os
from src.generate_sample_data import generate
from src.data_loader import load_matches
from src.backtest import run_backtest

DATA_PATH = "data/atp_matches_sample.csv"


def main():
    if not os.path.exists(DATA_PATH):
        generate(DATA_PATH)

    matches = load_matches(DATA_PATH)
    print(f"Loaded {len(matches)} matches\n")

    results = run_backtest(matches)

    print("=" * 50)
    print("BACKTEST RESULTS")
    print("=" * 50)
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
    print("TOP 10 ELO RATINGS (end of backtest)")
    print("=" * 50)
    for rank, (player, rating) in enumerate(results["elo"].leaderboard(10), start=1):
        print(f"{rank:>2}. {player:<20} {rating:.0f}")


if __name__ == "__main__":
    main()
