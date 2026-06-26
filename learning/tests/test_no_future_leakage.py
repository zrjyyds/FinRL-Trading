import pandas as pd
import pytest

from learning.src.sample_data import generate_news, generate_prices
from learning.src.time_alignment import filter_available_news, monthly_signal_schedule, validate_event_timeline


def test_future_news_excluded():
    prices = generate_prices()
    news = generate_news()
    schedule = monthly_signal_schedule(prices)
    signal = schedule.iloc[0]["signal_timestamp"]
    usable = filter_available_news(news, signal)
    assert (pd.to_datetime(usable["available_at"], utc=True) <= pd.Timestamp(signal).tz_convert("UTC")).all()
    future = news[pd.to_datetime(news["available_at"], utc=True) > pd.Timestamp(signal).tz_convert("UTC")]
    assert len(future) > 0


def test_after_close_news_not_allowed_before_signal():
    with pytest.raises(ValueError):
        validate_event_timeline(
            "2024-01-02T17:00:00-05:00",
            "2024-01-02T16:00:00-05:00",
            "2024-01-03T09:30:00-05:00",
        )


def test_execution_after_signal():
    prices = generate_prices()
    schedule = monthly_signal_schedule(prices)
    row = schedule.iloc[0]
    assert pd.Timestamp(row["signal_timestamp"]) < pd.Timestamp(row["execution_timestamp"])
