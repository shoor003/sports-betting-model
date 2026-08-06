# Tennis Moneyline Value-Betting Model

A walk-forward backtest of an Elo-based win-probability model against
simulated bookmaker odds, with value-bet detection and two staking
strategies (flat vs. fractional Kelly).

## What this demonstrates
- Building a rating system from historical results (Elo)
- Walk-forward backtesting (no lookahead bias -- ratings only use
  information available *before* each match)
- Comparing a model's probability estimate to a market's implied
  probability to find "value" bets
- Bankroll management: flat staking vs. Kelly criterion staking
- Working with tabular sports data in the same schema as a real public
  dataset

## Project structure
```
sports_betting_model/
├── main.py                    # run this
├── data/
│   └── atp_matches_sample.csv # auto-generated on first run
├── src/
│   ├── elo.py                 # Elo rating engine
│   ├── odds.py                # bookmaker odds simulator
│   ├── data_loader.py         # CSV loader (Sackmann schema)
│   ├── generate_sample_data.py# synthetic match generator
│   └── backtest.py            # walk-forward backtest logic
└── requirements.txt
```

## Setup
```bash
cd sports_betting_model
pip install -r requirements.txt   # stdlib only, but kept for convention
python main.py
```

## Important: about the data
Real historical tennis odds aren't freely downloadable via API without
a paid key, so this project ships with a **synthetic match generator**
(`src/generate_sample_data.py`) that produces data in the *exact same
column schema* as Jeff Sackmann's real public ATP dataset. Match
outcomes are simulated from hidden skill ratings using the same
logistic formula as Elo, so the model has genuine signal to recover --
this isn't just random noise dressed up as a project.

**To use real match history instead:**
1. Go to https://github.com/JeffSackmann/tennis_atp and download any
   `atp_matches_<year>.csv` file (e.g. `atp_matches_2023.csv`)
2. Drop it into `data/`
3. Change `DATA_PATH` in `main.py` to point to that file

The loader already expects that schema, so no other code changes are
needed.

**To add real odds** (optional upgrade): replace `get_market_odds()` in
`src/odds.py` with a lookup into a real odds file, e.g. historical
odds from tennis-data.co.uk, keeping the same return shape
`(decimal_odds_a, decimal_odds_b, implied_prob_a, implied_prob_b)`.

## How the betting logic works
1. **Elo model**: every player starts at 1500. After each match, Elo
   updates based on how surprising the result was, weighted by
   tournament level (Slams move ratings more than small events).
2. **Market simulation**: bookmaker odds are generated from the *true*
   probability plus noise (representing market imperfection) plus a
   ~5% vig (bookmaker margin).
3. **Value detection**: if the model's win probability for a player
   exceeds the market's implied probability by more than the edge
   threshold (4%), a bet is placed on that side.
4. **Staking**: flat bets risk 1% of the *starting* bankroll each time;
   Kelly bets risk a bankroll-fraction sized to the edge (at 25%
   fractional Kelly, to control variance).

## A note on the results
Because the market odds in this version are simulated from the same
underlying probability the Elo model is trying to recover (see
`src/odds.py`), the model has a structural edge by construction. The
ROI/hit-rate numbers this produces demonstrate that the pipeline works
end to end -- they are **not** a claim about real-world betting
performance. Getting a real performance number requires swapping in
actual historical odds (see below).

## Next steps
- Swap in real historical odds data and re-run for genuine out-of-sample
  ROI
- Add more features beyond Elo (surface-specific ratings, recent form,
  head-to-head history)
- Extend to MLB/NHL moneylines with sport-specific rating systems
- Add a Streamlit dashboard showing the bankroll curve over time and
  which bets were placed
- Track calibration (Brier score) to check the probabilities are
  well-calibrated, not just profitable by luck
