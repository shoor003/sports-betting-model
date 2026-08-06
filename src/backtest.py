"""
Walk-forward backtest of an Elo-based tennis moneyline model.

For every match, in chronological order:
  1. Compute each player's win probability from CURRENT Elo (pre-match --
     no lookahead).
  2. Simulate bookmaker odds for the match.
  3. If the model thinks a player's true win chance is meaningfully
     higher than the market's implied probability, place a bet (value
     betting).
  4. Settle the bet based on the actual result.
  5. Update Elo ratings with the result, then move to the next match.

Two staking strategies are compared:
  - Flat staking: bet a fixed % of INITIAL bankroll every time.
  - Kelly staking: bet a fraction of CURRENT bankroll sized by edge size
    (fractional Kelly to control variance).
"""

from .elo import EloRatings
from .odds import get_market_odds

EDGE_THRESHOLD = 0.04   # only bet when model edge exceeds this vs. market
KELLY_FRACTION = 0.25   # fractional Kelly to reduce variance
FLAT_STAKE_PCT = 0.01   # 1% of initial bankroll per flat bet


def kelly_stake(prob_win: float, decimal_odds: float) -> float:
    """Returns the Kelly-optimal fraction of bankroll to stake (can be 0)."""
    b = decimal_odds - 1  # net odds
    edge = prob_win * b - (1 - prob_win)
    fraction = edge / b if b > 0 else 0
    return max(0.0, fraction)


def run_backtest(matches, starting_bankroll: float = 1000.0):
    elo = EloRatings()

    flat_bankroll = starting_bankroll
    kelly_bankroll = starting_bankroll
    flat_stake = starting_bankroll * FLAT_STAKE_PCT

    bets_placed = 0
    bets_won = 0
    total_staked_flat = 0.0
    bankroll_curve = []  # (match_index, flat_bankroll, kelly_bankroll)

    for i, m in enumerate(matches):
        winner, loser, level = m["winner"], m["loser"], m["level"]

        # Randomly assign winner/loser to "player_a"/"player_b" slots so we
        # don't always evaluate from the winner's side (that would leak
        # the outcome into which side we bet).
        if i % 2 == 0:
            player_a, player_b = winner, loser
        else:
            player_a, player_b = loser, winner

        model_prob_a = elo.win_probability(player_a, player_b)
        odds_a, odds_b, implied_a, implied_b = get_market_odds(model_prob_a)

        edge_a = model_prob_a - implied_a
        edge_b = (1 - model_prob_a) - implied_b

        bet_side, bet_prob, bet_odds, edge = None, None, None, None
        if edge_a > EDGE_THRESHOLD and edge_a >= edge_b:
            bet_side, bet_prob, bet_odds, edge = player_a, model_prob_a, odds_a, edge_a
        elif edge_b > EDGE_THRESHOLD:
            bet_side, bet_prob, bet_odds, edge = player_b, 1 - model_prob_a, odds_b, edge_b

        if bet_side is not None:
            bets_placed += 1
            won = (bet_side == winner)
            if won:
                bets_won += 1

            # Flat staking settlement
            total_staked_flat += flat_stake
            flat_bankroll += flat_stake * (bet_odds - 1) if won else -flat_stake

            # Kelly staking settlement
            k_frac = kelly_stake(bet_prob, bet_odds) * KELLY_FRACTION
            k_stake = kelly_bankroll * k_frac
            kelly_bankroll += k_stake * (bet_odds - 1) if won else -k_stake

        elo.update(winner, loser, level)
        bankroll_curve.append((i, flat_bankroll, kelly_bankroll))

    return {
        "bets_placed": bets_placed,
        "bets_won": bets_won,
        "hit_rate": bets_won / bets_placed if bets_placed else 0.0,
        "flat_final_bankroll": flat_bankroll,
        "flat_roi_pct": (flat_bankroll - starting_bankroll) / total_staked_flat * 100
                        if total_staked_flat else 0.0,
        "kelly_final_bankroll": kelly_bankroll,
        "elo": elo,
        "bankroll_curve": bankroll_curve,
    }
