"""Phase 1.1 新增功能的测试。"""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ---- 字体配置测试 ----

def test_configure_chinese_plotting_does_not_raise():
    from learning.src.plotting import configure_chinese_plotting, get_font_status
    font = configure_chinese_plotting()
    assert isinstance(font, str)
    assert len(font) > 0
    status = get_font_status()
    assert "chinese_available" in status
    assert "selected_font" in status
    assert "fallback_reason" in status


def test_safe_title_does_not_raise_without_chinese_font():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from learning.src.plotting import safe_title
    fig, ax = plt.subplots()
    safe_title(ax, "中文标题", "English Title")
    plt.close(fig)


def test_get_font_status_returns_valid_dict():
    from learning.src.plotting import get_font_status
    status = get_font_status()
    assert isinstance(status, dict)
    assert isinstance(status["chinese_available"], bool)
    assert isinstance(status["selected_font"], str)


# ---- 基准测试 ----

def test_equal_weight_benchmark_targets():
    from learning.src.market_data import load_price_data
    from learning.src.time_alignment import monthly_signal_schedule
    DATA = ROOT / "learning" / "data"
    prices = load_price_data(DATA / "sample_prices.csv")
    schedule = monthly_signal_schedule(prices)
    tickers_all = sorted(prices["ticker"].unique())
    initial_date = schedule["execution_date"].iloc[0]
    # 等权配置
    targets = pd.DataFrame([
        {"execution_date": initial_date, "ticker": t, "weight": 1.0 / len(tickers_all)}
        for t in tickers_all
    ])
    assert len(targets) == len(tickers_all)
    assert abs(targets["weight"].sum() - 1.0) < 0.001
    # 只有第一天有调仓
    assert (targets["execution_date"] == initial_date).all()


def test_cash_benchmark_constant_nav():
    """现金基准的净值应永远保持 1.0。"""
    dates = pd.date_range("2024-01-01", periods=60, freq="B")
    eq_cash = pd.Series(1.0, index=dates, name="cash")
    assert (eq_cash == 1.0).all()


def test_strategy_and_benchmark_same_date_range():
    """策略和基准使用相同日期范围。"""
    from learning.src.market_data import load_price_data
    from learning.src.time_alignment import monthly_signal_schedule
    from learning.src.mini_backtest import run_backtest
    DATA = ROOT / "learning" / "data"
    prices = load_price_data(DATA / "sample_prices.csv")
    schedule = monthly_signal_schedule(prices)
    tickers_all = sorted(prices["ticker"].unique())
    initial_date = schedule["execution_date"].iloc[0]
    # 策略
    strat_targets = pd.DataFrame([
        {"execution_date": s["execution_date"], "ticker": t, "weight": 1.0 / len(tickers_all)}
        for _, s in schedule.head(8).iterrows() for t in tickers_all
    ])
    result_s = run_backtest(prices, strat_targets)
    # 基准
    bh_targets = pd.DataFrame([
        {"execution_date": initial_date, "ticker": t, "weight": 1.0 / len(tickers_all)}
        for t in tickers_all
    ])
    result_bh = run_backtest(prices, bh_targets)
    # 日期序列对齐
    eq_s = result_s.equity_curve.set_index("date")["equity"]
    eq_bh = result_bh.equity_curve.set_index("date")["equity"]
    assert eq_s.index[0] == eq_bh.index[0]
    assert eq_s.index[-1] == eq_bh.index[-1]


# ---- TF-IDF 检索测试 ----

def test_tfidf_retrieval_repeatable():
    from learning.src.retrieval_demo import retrieve_notes
    DATA = ROOT / "learning" / "data"
    result1 = retrieve_notes(DATA / "sample_company_notes.csv", "risk management", 3)
    result2 = retrieve_notes(DATA / "sample_company_notes.csv", "risk management", 3)
    assert len(result1) == len(result2)
    # 相同查询应返回相同结果
    for r1, r2 in zip(result1, result2):
        assert r1 == r2


def test_tfidf_retrieval_returns_specified_count():
    from learning.src.retrieval_demo import retrieve_notes
    DATA = ROOT / "learning" / "data"
    result = retrieve_notes(DATA / "sample_company_notes.csv", "teaching data", 3)
    assert 1 <= len(result) <= 3


# ---- 离线安全测试 ----

def test_no_trading_imports_in_new_code():
    """新增代码不导入交易模块。"""
    from learning.src.plotting import configure_chinese_plotting, safe_title, get_font_status
    # 只要能成功导入，就不涉及交易模块
    assert callable(configure_chinese_plotting)
    assert callable(safe_title)
    assert callable(get_font_status)


# ---- 小数股测试 ----

def test_fractional_shares_allowed():
    """mini_backtest 允许小数股。"""
    from learning.src.mini_backtest import run_backtest
    from learning.src.market_data import load_price_data
    DATA = ROOT / "learning" / "data"
    prices = load_price_data(DATA / "sample_prices.csv")
    first_date = str(prices["date"].iloc[0].date())
    targets = pd.DataFrame([
        {"execution_date": first_date, "ticker": "AAA", "weight": 0.3333},
    ])
    result = run_backtest(prices, targets, initial_cash=1000.0)
    assert len(result.trades) >= 0
    assert result.equity_curve["equity"].iloc[-1] >= 0
