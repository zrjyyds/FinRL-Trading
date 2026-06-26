"""生成和加载 Phase 1 离线合成教学数据。"""

from __future__ import annotations

from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

NY_TZ = ZoneInfo("America/New_York")
TICKERS = ["AAA", "BBB", "CCC", "DDD", "EEE"]
RANDOM_SEED = 42


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def data_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "data"


def generate_prices(random_seed: int = RANDOM_SEED) -> pd.DataFrame:
    """生成价格数据。

    收盘价（Close）
    零基础解释：收盘价是某个交易日最后形成的价格。
    """

    rng = np.random.default_rng(random_seed)
    dates = pd.bdate_range("2024-01-02", periods=300)
    rows = []
    phase = np.r_[np.full(100, 0.0018), np.full(100, -0.0012), np.full(100, 0.0002)]
    ticker_bias = {
        "AAA": 0.0008,
        "BBB": -0.0001,
        "CCC": 0.0004,
        "DDD": -0.0004,
        "EEE": 0.0000,
    }

    for idx, ticker in enumerate(TICKERS):
        price = 30.0 + idx * 12.0
        for day_i, day in enumerate(dates):
            noise = rng.normal(0, 0.012 + idx * 0.001)
            ret = phase[day_i] + ticker_bias[ticker] + noise
            prev_close = price
            close = max(2.0, prev_close * (1.0 + ret))
            open_px = max(2.0, prev_close * (1.0 + rng.normal(0, 0.004)))
            high = max(open_px, close) * (1.0 + abs(rng.normal(0.003, 0.002)))
            low = min(open_px, close) * (1.0 - abs(rng.normal(0.003, 0.002)))
            volume = int(rng.integers(180_000, 1_500_000))
            rows.append(
                {
                    "date": day.strftime("%Y-%m-%d"),
                    "ticker": ticker,
                    "open": round(open_px, 4),
                    "high": round(max(high, open_px, close, low), 4),
                    "low": round(min(low, open_px, close, high), 4),
                    "close": round(close, 4),
                    "volume": volume,
                }
            )
            price = close

    df = pd.DataFrame(rows).sort_values(["date", "ticker"]).reset_index(drop=True)
    return df


def _next_business_open(ts: pd.Timestamp) -> pd.Timestamp:
    next_day = (ts + pd.offsets.BDay(1)).normalize()
    return pd.Timestamp(next_day.date()).replace(hour=9, minute=30, tzinfo=NY_TZ)


def _available_at(published_at: pd.Timestamp) -> pd.Timestamp:
    if published_at.weekday() >= 5:
        return _next_business_open(published_at)
    market_close = published_at.replace(hour=16, minute=0, second=0, microsecond=0)
    if published_at <= market_close:
        return published_at
    return _next_business_open(published_at)


def generate_news(random_seed: int = RANDOM_SEED) -> pd.DataFrame:
    """生成合成新闻。

    情绪分类（Sentiment Classification）
    零基础解释：把新闻分为正面、中性和负面三类。
    """

    rng = np.random.default_rng(random_seed + 7)
    price_dates = pd.bdate_range("2024-01-02", periods=300)
    templates = {
        "positive": [
            ("订单增长", "management reports stronger demand and improved backlog"),
            ("成本改善", "operating costs improved while customer retention stayed firm"),
            ("产品进展", "new product tests show steady adoption in a teaching scenario"),
        ],
        "neutral": [
            ("例行更新", "management repeats prior guidance without material change"),
            ("会议纪要", "the company shares a routine operational update"),
            ("行业观察", "sector conditions remain mixed in this synthetic note"),
        ],
        "negative": [
            ("需求放缓", "management flags softer demand and delayed customer orders"),
            ("成本压力", "input costs rose and margins may face pressure"),
            ("执行风险", "a project delay creates uncertainty in this teaching scenario"),
        ],
    }
    labels = ["positive", "neutral", "negative"]
    rows = []
    article_id = 1
    for ticker in TICKERS:
        for i in range(32):
            label = labels[(i + TICKERS.index(ticker)) % 3]
            title_key, body = templates[label][i % 3]
            base_day = pd.Timestamp(price_dates[int(rng.integers(0, len(price_dates)))])
            if i % 10 == 0:
                published = base_day + pd.Timedelta(days=5)
            hour = [10, 14, 17, 20][i % 4]
            published = pd.Timestamp(base_day.date()).replace(hour=hour, minute=int(rng.integers(0, 50)), tzinfo=NY_TZ)
            available = _available_at(published)
            rows.append(
                {
                    "article_id": f"N{article_id:04d}",
                    "ticker": ticker,
                    "published_at": published.isoformat(),
                    "available_at": available.isoformat(),
                    "title": f"{ticker} {title_key} 教学新闻",
                    "body": f"This is synthetic education-only text: {body}. It is not investment advice.",
                    "source": "synthetic_learning_news",
                    "expected_label": label,
                }
            )
            article_id += 1
    return pd.DataFrame(rows).sort_values(["available_at", "ticker", "article_id"]).reset_index(drop=True)


def generate_company_notes() -> pd.DataFrame:
    rows = []
    sections = {
        "business": "The synthetic company sells teaching products and has no real securities meaning.",
        "risk": "The synthetic note reminds learners that model output can be wrong.",
        "data": "The dataset is deterministic and intended for offline classroom experiments.",
    }
    for ticker in TICKERS:
        for section, text in sections.items():
            rows.append({"ticker": ticker, "section": section, "text": f"{ticker}: {text}"})
    return pd.DataFrame(rows)


def write_sample_data(base_dir: Path | None = None) -> None:
    target = base_dir or data_dir()
    target.mkdir(parents=True, exist_ok=True)
    generate_prices().to_csv(target / "sample_prices.csv", index=False)
    generate_news().to_csv(target / "sample_news.csv", index=False)
    generate_company_notes().to_csv(target / "sample_company_notes.csv", index=False)


def load_prices() -> pd.DataFrame:
    return pd.read_csv(data_dir() / "sample_prices.csv")


def load_news() -> pd.DataFrame:
    return pd.read_csv(data_dir() / "sample_news.csv")


def load_company_notes() -> pd.DataFrame:
    return pd.read_csv(data_dir() / "sample_company_notes.csv")


if __name__ == "__main__":
    write_sample_data()

