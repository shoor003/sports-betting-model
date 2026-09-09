# Tennis Moneyline Prediction & Value-Betting Model

An Elo-based win probability model for ATP tennis, tested against real 2023-2024 match results, plus a walk-forward betting simulation with value-bet detection and two staking strategies (flat vs. fractional Kelly).

## Results (real 2023-2024 ATP data, 6,071 matches)

These numbers come from real match outcomes only, no simulated odds involved:

| Metric | Value |
|---|---|
| Prediction accuracy | 62.1% |
| Brier score | 0.2261 (0 = perfect, 0.25 = coin flip) |

The end-of-period Elo leaderboard lines up with real 2024 rankings too (Sinner, Djokovic, Alcaraz, Zverev at the top).

The betting simulation below (hit rate, ROI, bankroll) still runs against simulated bookmaker odds. See "About the odds data" for why, and what it'd take to make that part real too.

## What this demonstrates
- Building a rating system from historical results (Elo)
- Walk-forward evaluation, no lookahead bias, ratings only use info available before each match
- Evaluating a probabilistic model with real metrics (accuracy, Brier score) instead of just eyeballing it
- Comparing a model's probability estimate to a market's implied probability to find "value" bets
- Bankroll management: flat staking vs. Kelly criterion staking
- Working with real public sports data end to end

## Project structure
```
sports_betting_model/
├── main.py                        # run this
├── data/
│   ├── atp_matches_2023_2024.csv  # real ATP matches, used by default
│   ├── atp_matches_2023.csv
│   └── atp_matches_2024.csv
├── src/
│   ├── elo.py                     # Elo rating engine
│   ├── evaluate.py                # accuracy/Brier score vs. real outcomes
│   ├── odds.py                    # bookmaker odds simulator
│   ├── data_loader.py             # CSV loader (Sackmann-style schema)
│   ├── generate_sample_data.py    # synthetic match generator (fallback)
│   └── backtest.py                # walk-forward betting simulation
└── requirements.txt
```

## Setup
```bash
cd sports_betting_model
pip install -r requirements.txt   # stdlib only, kept for convention
python main.py
```

## About the match data
`data/atp_matches_2023_2024.csv` has real ATP tour results for 2023-2024, pulled from [Tennismylife/TML-Database](https://github.com/Tennismylife/TML-Database), which keeps an actively updated dataset structured after Jeff Sackmann's well-known `tennis_atp` schema (tourney_date, tourney_level, winner_name, loser_name, etc). If the file isn't there, `main.py` falls back to generating synthetic data in the same schema (`src/generate_sample_data.py`) so the project still runs on its own.

## About the odds data
Real historical bookmaker odds aren't freely available without a paid API key, so `src/odds.py` simulates market odds instead: it takes the model's own probability estimate, adds some noise for market imperfection, and applies a ~5% vig. So the accuracy/Brier numbers above are real, but the hit-rate/ROI/bankroll numbers from the betting simulation are more of a pipeline demo than a real-world performance claim.

To make the betting simulation real too, swap `get_market_odds()` in `src/odds.py` for a lookup into an actual odds file (e.g. historical odds from tennis-data.co.uk), keeping the same return shape: `(decimal_odds_a, decimal_odds_b, implied_prob_a, implied_prob_b)`.

## How the betting logic works
1. **Elo model**: every player starts at 1500. After each match, Elo updates based on how surprising the result was, weighted by tournament level (Slams move ratings more than small events).
2. **Market simulation**: bookmaker odds are generated from the model's own probability plus noise plus a ~5% vig.
3. **Value detection**: if a player's model win probability beats the market's implied probability by more than the edge threshold (4%), place a bet on that side.
4. **Staking**: flat bets risk 1% of the starting bankroll each time; Kelly bets risk a bankroll fraction sized to the edge (25% fractional Kelly, to keep variance down).

## Next steps
- Swap in real historical odds data for a genuine out-of-sample ROI number
- Add features beyond Elo (surface-specific ratings, recent form, head-to-head)
- Extend to MLB/NHL moneylines with sport-specific rating systems
- Add a small dashboard for the bankroll curve and which bets got placed
