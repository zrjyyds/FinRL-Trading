import numpy as np
import pandas as pd

from learning.src.financial_metrics import (
    annualized_return,
    annualized_volatility,
    cumulative_return,
    log_returns,
    maximum_drawdown,
    sharpe_ratio,
    simple_returns,
)


def test_returns_small_hand_check():
    prices = pd.Series([100.0, 110.0, 121.0])
    rets = simple_returns(prices)
    assert np.allclose(rets.values, [0.1, 0.1])
    assert np.allclose(log_returns(prices).values, [np.log(1.1), np.log(1.1)])
    assert abs(cumulative_return(rets) - 0.21) < 1e-9


def test_empty_single_and_zero_volatility():
    assert simple_returns(pd.Series([1.0])).empty
    assert annualized_return(pd.Series(dtype=float)) == 0.0
    assert annualized_volatility(pd.Series([0.01])) == 0.0
    assert sharpe_ratio(pd.Series([0.01, 0.01, 0.01])) == 0.0


def test_maximum_drawdown_hand_check():
    values = pd.Series([100, 120, 90, 150])
    assert abs(maximum_drawdown(values) - (-0.25)) < 1e-9
