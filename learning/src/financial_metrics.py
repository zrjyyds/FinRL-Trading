"""基础金融指标。"""

from __future__ import annotations

import numpy as np
import pandas as pd


def simple_returns(prices: pd.Series) -> pd.Series:
    """简单收益率（Simple Return）。

    零基础解释：简单收益率等于本期价格除以上期价格再减 1。
    """

    if prices is None or len(prices) < 2:
        return pd.Series(dtype=float)
    return pd.Series(prices, dtype=float).pct_change().dropna()


def log_returns(prices: pd.Series) -> pd.Series:
    """对数收益率（Log Return）。

    零基础解释：对数收益率用价格比值的自然对数表示收益。
    """

    if prices is None or len(prices) < 2:
        return pd.Series(dtype=float)
    s = pd.Series(prices, dtype=float)
    return np.log(s / s.shift(1)).dropna()


def cumulative_return(returns: pd.Series) -> float:
    """累计收益率（Cumulative Return）。

    零基础解释：累计收益率表示从开始到结束总共涨跌多少。
    """

    if returns is None or len(returns) == 0:
        return 0.0
    r = pd.Series(returns, dtype=float).dropna()
    if len(r) == 0:
        return 0.0
    return float((1.0 + r).prod() - 1.0)


def annualized_return(returns: pd.Series, periods_per_year: int = 252) -> float:
    """年化收益率（Annualized Return）。

    零基础解释：把一段时间的收益换算成一年大约是多少。
    """

    if returns is None or len(returns) == 0:
        return 0.0
    r = pd.Series(returns, dtype=float).dropna()
    if len(r) == 0:
        return 0.0
    total = (1.0 + r).prod()
    return float(total ** (periods_per_year / len(r)) - 1.0)


def annualized_volatility(returns: pd.Series, periods_per_year: int = 252) -> float:
    """年化波动率（Annualized Volatility）。

    零基础解释：把日收益波动换算成一年的波动程度。
    """

    if returns is None or len(returns) < 2:
        return 0.0
    r = pd.Series(returns, dtype=float).dropna()
    if len(r) < 2:
        return 0.0
    return float(r.std(ddof=1) * np.sqrt(periods_per_year))


def maximum_drawdown(values: pd.Series) -> float:
    """最大回撤（Maximum Drawdown，MDD）。

    零基础解释：资金从历史最高点跌到之后最低点的最大跌幅。
    """

    if values is None or len(values) == 0:
        return 0.0
    s = pd.Series(values, dtype=float).dropna()
    if len(s) == 0:
        return 0.0
    running_max = s.cummax()
    drawdown = s / running_max - 1.0
    return float(drawdown.min())


def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0, periods_per_year: int = 252) -> float:
    """夏普比率（Sharpe Ratio）。

    零基础解释：衡量每承担一单位波动风险，获得了多少超额收益。
    """

    if returns is None or len(returns) < 2:
        return 0.0
    r = pd.Series(returns, dtype=float).dropna()
    if len(r) < 2:
        return 0.0
    vol = annualized_volatility(r, periods_per_year)
    if vol == 0:
        return 0.0
    ann = annualized_return(r, periods_per_year)
    return float((ann - risk_free_rate) / vol)
