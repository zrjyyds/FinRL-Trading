from learning.src.momentum_factor import compute_momentum, rank_momentum
from learning.src.sample_data import generate_prices


def test_momentum_factor_ranking():
    prices = generate_prices()
    mom = compute_momentum(prices, 20)
    last_date = str(mom["date"].max().date())
    ranked = rank_momentum(mom, last_date, 20)
    assert len(ranked) == 5
    assert ranked["momentum_rank_score"].between(0, 1).all()
    assert ranked["momentum_rank_score"].is_monotonic_decreasing
