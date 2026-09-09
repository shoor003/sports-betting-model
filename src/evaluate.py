"""
Checks the Elo model's raw predictive accuracy against real match
outcomes, no odds or betting involved.

This only needs real results to compare against, not a market, so it's
the one number here that stays honest no matter what. Two metrics:

  - Accuracy: of the matches where the model favored one player, how
    often did they actually win? A coin flip gets ~50%.
  - Brier score: average squared error between the model's stated win
    probability and the actual outcome (1 or 0). 0 is a perfect oracle,
    0.25 is what you get from always guessing 50/50. This measures
    calibration rather than just whether it picked the winner, so a
    model that's 90% confident and wrong gets punished a lot more than
    one that's 55% confident and wrong.
"""

from .elo import EloRatings


def evaluate_predictions(matches):
    elo = EloRatings()

    correct = 0
    total = 0
    brier_sum = 0.0

    for i, m in enumerate(matches):
        winner, loser, level = m["winner"], m["loser"], m["level"]

        # Same alternating assignment as the backtest, so we're not
        # always evaluating from the winner's side.
        if i % 2 == 0:
            player_a, player_b = winner, loser
        else:
            player_a, player_b = loser, winner

        prob_a = elo.win_probability(player_a, player_b)
        predicted_winner = player_a if prob_a >= 0.5 else player_b
        actual_outcome_a = 1.0 if winner == player_a else 0.0

        if predicted_winner == winner:
            correct += 1
        total += 1
        brier_sum += (prob_a - actual_outcome_a) ** 2

        elo.update(winner, loser, level)

    return {
        "matches_evaluated": total,
        "accuracy": correct / total if total else 0.0,
        "brier_score": brier_sum / total if total else 0.0,
        "elo": elo,
    }
