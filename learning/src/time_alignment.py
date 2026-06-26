"""回测时间轴和新闻可用时间。"""

from __future__ import annotations

from datetime import datetime, time
from zoneinfo import ZoneInfo

import pandas as pd

NY_TZ = ZoneInfo("America/New_York")
MARKET_OPEN = time(9, 30)
MARKET_CLOSE = time(16, 0)


def ensure_ny_timestamp(value: str | datetime | pd.Timestamp) -> pd.Timestamp:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        ts = ts.tz_localize(NY_TZ)
    return ts.tz_convert(NY_TZ)


def trading_dates_from_prices(prices: pd.DataFrame) -> list[pd.Timestamp]:
    dates = pd.to_datetime(prices["date"]).drop_duplicates().sort_values()
    return [pd.Timestamp(d).normalize() for d in dates]


def get_next_trading_date(current_date: str | datetime | pd.Timestamp, trading_dates: list[pd.Timestamp]) -> pd.Timestamp:
    """获取下一可交易日期。

    未来数据泄漏（Look-Ahead Bias）
    零基础解释：回测时使用当时还不知道的信息，就是未来数据泄漏。
    """

    cur = pd.Timestamp(current_date).tz_localize(None).normalize()
    for day in sorted(pd.Timestamp(d).tz_localize(None).normalize() for d in trading_dates):
        if day > cur:
            return day
    raise ValueError("no next trading date available")


def market_close_timestamp(day: str | datetime | pd.Timestamp) -> pd.Timestamp:
    date = pd.Timestamp(day).date()
    return pd.Timestamp(datetime.combine(date, MARKET_CLOSE), tz=NY_TZ)


def market_open_timestamp(day: str | datetime | pd.Timestamp) -> pd.Timestamp:
    date = pd.Timestamp(day).date()
    return pd.Timestamp(datetime.combine(date, MARKET_OPEN), tz=NY_TZ)


def compute_news_available_at(published_at: str | datetime | pd.Timestamp, trading_dates: list[pd.Timestamp]) -> pd.Timestamp:
    published = ensure_ny_timestamp(published_at)
    day = published.normalize()
    trading_norm = {pd.Timestamp(d).normalize() for d in trading_dates}
    if day in trading_norm and published.time() <= MARKET_CLOSE:
        return published
    next_day = get_next_trading_date(day, trading_dates)
    return market_open_timestamp(next_day)


def validate_event_timeline(
    available_at: str | datetime | pd.Timestamp,
    signal_timestamp: str | datetime | pd.Timestamp,
    execution_timestamp: str | datetime | pd.Timestamp,
) -> None:
    available = ensure_ny_timestamp(available_at)
    signal = ensure_ny_timestamp(signal_timestamp)
    execution = ensure_ny_timestamp(execution_timestamp)
    if not (available <= signal < execution):
        raise ValueError("timeline must satisfy available_at <= signal_timestamp < execution_timestamp")


def filter_available_news(news: pd.DataFrame, signal_timestamp: str | datetime | pd.Timestamp) -> pd.DataFrame:
    signal = ensure_ny_timestamp(signal_timestamp)
    df = news.copy()
    df["available_at"] = pd.to_datetime(df["available_at"], utc=True).dt.tz_convert(NY_TZ)
    return df[df["available_at"] <= signal].copy()


def monthly_signal_schedule(prices: pd.DataFrame) -> pd.DataFrame:
    """生成月末收盘后信号和下一交易日开盘成交时间。"""

    dates = trading_dates_from_prices(prices)
    date_df = pd.DataFrame({"date": dates})
    last_days = date_df.groupby(date_df["date"].dt.to_period("M"))["date"].max().tolist()
    rows = []
    for signal_day in last_days[:-1]:
        execution_day = get_next_trading_date(signal_day, dates)
        rows.append(
            {
                "signal_date": signal_day.strftime("%Y-%m-%d"),
                "signal_timestamp": market_close_timestamp(signal_day).isoformat(),
                "execution_date": execution_day.strftime("%Y-%m-%d"),
                "execution_timestamp": market_open_timestamp(execution_day).isoformat(),
            }
        )
    return pd.DataFrame(rows)

