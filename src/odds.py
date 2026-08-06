"""
Simulates bookmaker moneyline odds for a match.

Real historical odds (e.g. from tennis-data.co.uk or The Odds API) aren't
freely fetchable from this environment, so this module generates
realistic odds instead: it takes a "true" win probability, adds noise to
represent the market's own imperfect model, then bakes in a bookmaker
margin (vig). This is what your betting edge exists inside of -- a
model that just reproduces the bookmaker's noise has zero edge; a model
that's closer to the true probability than the market is where ROI
comes from.

Swap this out for a real odds feed by replacing get_market_odds() with
a lookup into your odds CSV/API response -- keep the same return shape.
"""

import random

VIG = 0.05  # typical sportsbook overround, ~5%
MARKET_NOISE_STD = 0.04  # how far the "market" probability drifts from truth


def get_market_odds(true_prob_a: float):
    """
    Given the TRUE probability that player A wins, simulate what a
    bookmaker's moneyline odds would look like for both players.
    Returns (decimal_odds_a, decimal_odds_b, implied_prob_a, implied_prob_b).
    """
    noisy_prob_a = min(0.98, max(0.02, true_prob_a + random.gauss(0, MARKET_NOISE_STD)))

    # Apply vig: bookmaker inflates both implied probabilities so they
    # sum to > 1 (that sum-over-100% is the house edge).
    total_vig_prob = 1 + VIG
    implied_a = noisy_prob_a * total_vig_prob / (noisy_prob_a + (1 - noisy_prob_a))
    implied_b = (1 - noisy_prob_a) * total_vig_prob / (noisy_prob_a + (1 - noisy_prob_a))

    decimal_odds_a = 1 / implied_a
    decimal_odds_b = 1 / implied_b

    return decimal_odds_a, decimal_odds_b, implied_a, implied_b
