"""
Elo rating system for tennis players.

Standard chess-style Elo, adapted for tennis. Every player starts at
BASE_RATING. After each match, the winner gains points and the loser
loses points, scaled by how surprising the result was (K-factor) and
by match importance (Grand Slams move ratings more than small events).
"""

BASE_RATING = 1500
K_FACTOR = 32

# Multiplier applied to K based on tournament level, so a Grand Slam
# upset moves the needle more than a small 250-level event.
LEVEL_K_MULTIPLIER = {
    "G": 1.5,   # Grand Slam
    "M": 1.25,  # Masters 1000
    "A": 1.0,   # Other tour-level
    "D": 0.75,  # Davis Cup
    "F": 1.1,   # Tour Finals
}


class EloRatings:
    def __init__(self, base_rating: float = BASE_RATING, k_factor: float = K_FACTOR):
        self.base_rating = base_rating
        self.k_factor = k_factor
        self.ratings = {}

    def get(self, player: str) -> float:
        return self.ratings.get(player, self.base_rating)

    def win_probability(self, player_a: str, player_b: str) -> float:
        """Probability that player_a beats player_b, per the Elo formula."""
        rating_a = self.get(player_a)
        rating_b = self.get(player_b)
        return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400.0))

    def update(self, winner: str, loser: str, level: str = "A") -> None:
        """Update ratings after a match. Call win_probability() BEFORE this
        if you need the pre-match odds for backtesting."""
        prob_winner = self.win_probability(winner, loser)
        k = self.k_factor * LEVEL_K_MULTIPLIER.get(level, 1.0)

        winner_rating = self.get(winner)
        loser_rating = self.get(loser)

        self.ratings[winner] = winner_rating + k * (1 - prob_winner)
        self.ratings[loser] = loser_rating - k * (1 - prob_winner)

    def leaderboard(self, top_n: int = 20):
        return sorted(self.ratings.items(), key=lambda x: x[1], reverse=True)[:top_n]
