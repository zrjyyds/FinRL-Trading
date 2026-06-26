import pandas as pd
import pytest

from learning.src.sample_data import generate_news, generate_prices
from learning.src.time_alignment import (
    compute_news_available_at,
    filter_available_news,
    get_next_trading_date,
    market_close_timestamp,
    market_open_timestamp,
    trading_dates_from_prices,
    validate_event_timeline,
)


def test_next_trading_date_and_timeline():
    prices = generate_prices()
    dates = trading_dates_from_prices(prices)
    nxt = get_next_trading_date(dates[0], dates)
    assert nxt > dates[0]
    signal = market_close_timestamp(dates[0])
    execution = market_open_timestamp(nxt)
    validate_event_timeline(signal, signal, execution)


def test_news_after_close_available_next_trading_day():
    prices = generate_prices()
    dates = trading_dates_from_prices(prices)
    published = market_close_timestamp(dates[0]) + pd.Timedelta(hours=1)
    available = compute_news_available_at(published, dates)
    assert available == market_open_timestamp(dates[1])


def test_invalid_timeline_rejected():
    with pytest.raises(ValueError):
        validate_event_timeline("2024-01-03T10:00:00-05:00", "2024-01-02T16:00:00-05:00", "2024-01-03T09:30:00-05:00")


def test_filter_available_news():
    news = generate_news()
    signal = news["available_at"].iloc[10]
    usable = filter_available_news(news, signal)
    assert pd.to_datetime(usable["available_at"], utc=True).max() <= pd.Timestamp(signal).tz_convert("UTC")
