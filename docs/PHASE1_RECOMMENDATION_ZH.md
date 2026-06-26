# Phase 1 建议方案

## 1. 目标

Phase 1 建议把当前项目改造成“零基础可运行、默认离线、安全禁交易”的量化金融 + 大语言模型双线学习项目。

本文件只制定方案，不执行。

专业词：大语言模型（Large Language Model，LLM）。

零基础解释：大语言模型可以帮助处理新闻、公告、财报文字，但不能直接当成可靠交易员。

## 2. 建议新增目录结构

```text
learning/
  README_ZH.md
  00_glossary_zh.md
  01_prices_and_returns.ipynb
  02_buy_and_hold_backtest.ipynb
  03_equal_weight_portfolio.ipynb
  04_momentum_factor.ipynb
  05_ml_stock_selection_small.ipynb
  06_mock_llm_sentiment.ipynb
  07_sentiment_plus_momentum.ipynb
  data/
    sample_prices.csv
    sample_news.csv
    sample_fundamentals.csv
  mock/
    mock_llm_provider.py
    mock_broker.py
  utils/
    safe_mode.py
    metrics.py
    mini_backtest.py
tests/
  test_learning_metrics.py
  test_no_trading_in_learning_mode.py
  test_mock_llm_schema.py
```

零基础解释：`learning/` 是把复杂项目拆成小课的目录。

## 3. 建议 Notebook 顺序

1. `01_prices_and_returns.ipynb`
2. `02_buy_and_hold_backtest.ipynb`
3. `03_equal_weight_portfolio.ipynb`
4. `04_momentum_factor.ipynb`
5. `05_ml_stock_selection_small.ipynb`
6. `06_mock_llm_sentiment.ipynb`
7. `07_sentiment_plus_momentum.ipynb`

每个 Notebook 必须：
- 不联网。
- 不需要 API Key。
- 不下单。
- 不训练大型模型。
- 每个专业词首次出现给中文、英文全称和缩写。

## 4. 建议离线样例数据

建议新增小型 CSV：
- 5 只股票。
- 2 年日频价格。
- 20 条新闻。
- 8 个季度基本面。

字段：
- `date`
- `ticker`
- `open`
- `high`
- `low`
- `close`
- `volume`
- `news_time`
- `title`
- `body`
- `sentiment_label`

专业词：开盘价、最高价、最低价、收盘价（Open, High, Low, Close，OHLC）。

零基础解释：OHLC 是一天内价格变化的四个关键点。

## 5. 建议 Mock LLM Provider

接口：

```python
class MockLLMProvider:
    def classify_sentiment(self, title: str, body: str) -> dict:
        return {
            "sentiment": "neutral",
            "confidence": 0.6,
            "reason": "offline mock"
        }
```

要求：
- 不调用 OpenAI。
- 输出固定 JSON。
- 可注入正面/负面关键词规则。
- 可用于单元测试。

专业词：结构化输出（Structured Output）。

零基础解释：结构化输出是让模型返回固定字段，程序才能稳定读取。

## 6. 建议 OpenAI Compatible Provider

Phase 1 只做接口设计，不默认启用真实调用：
- `base_url`
- `api_key`
- `model`
- `timeout`
- `max_tokens`
- `temperature`
- `cost_budget_usd`
- `enabled=false`

专业词：OpenAI 兼容接口（OpenAI-Compatible API）。

零基础解释：OpenAI 兼容接口是不同服务商模仿 OpenAI SDK 格式提供的模型服务。

## 7. 建议结构化输出格式

```json
{
  "sentiment": "positive | neutral | negative",
  "confidence": 0.0,
  "evidence": "short reason",
  "published_at": "YYYY-MM-DD HH:mm:ss",
  "ticker": "AAPL"
}
```

校验规则：
- `sentiment` 必须三选一。
- `confidence` 必须在 0 到 1。
- `published_at` 不得晚于信号生成时间。
- `ticker` 必须在样例股票列表。

专业词：JSON Schema（JavaScript Object Notation Schema）。

零基础解释：JSON Schema 是检查 JSON 字段是否合规的一套规则。

## 8. 建议情绪因子

最小实现：
- 每只股票每天统计新闻情绪分数。
- `positive=1`
- `neutral=0`
- `negative=-1`
- 同一天多条新闻取平均。
- 信号日只能使用信号日前已经发布的新闻。

专业词：情绪因子（Sentiment Factor）。

零基础解释：情绪因子是把新闻好坏转成数字，用作策略输入。

## 9. 建议动量因子

最小实现：
- `momentum_20d = close_today / close_20_days_ago - 1`
- 排名前 2 的股票买入。
- 每月调仓。

专业词：动量因子（Momentum Factor）。

零基础解释：动量因子假设过去一段时间涨得好的资产，短期可能继续强。

## 10. 建议联合策略

简单联合分数：

```text
score = 0.7 * momentum_rank_score + 0.3 * sentiment_score
```

规则：
- 不做空。
- 单只股票最大权重 40%。
- 最多持有 3 只。
- 现金允许存在。
- 信号日和成交日至少相隔 1 个交易日。

专业词：仓位权重（Position Weight）。

零基础解释：仓位权重是某只资产占总资金的比例。

## 11. 建议回测规则

必须明确：
- 信号生成日。
- 可用数据截止时间。
- 成交日。
- 成交价格。
- 交易费用。
- 是否允许小数股。
- 是否允许现金。

最小规则：
- 月末生成信号。
- 下一个交易日开盘买入。
- 交易费用 0.1%。
- 不设滑点或设置固定 0.05% 滑点。

专业词：交易费用（Transaction Cost）。

零基础解释：交易费用是买卖资产时产生的手续费或成本。

## 12. 建议单元测试

测试：
- 收益率计算正确。
- 最大回撤计算正确。
- 信号日不使用未来新闻。
- Mock LLM 输出 schema 正确。
- 学习模式下交易函数必定报错。
- 无 API Key 时 Notebook 可运行。
- 回测结果在固定数据上可复现。

## 13. 建议精简依赖

Phase 1 只建议：

```text
numpy
pandas
matplotlib
scikit-learn
pytest
pydantic
```

暂不使用：
- OpenAI
- Alpaca
- torch
- stable-baselines3
- lightgbm
- xgboost
- streamlit

## 14. Phase 1 预计修改文件

可能新增：
- `learning/`
- `tests/`
- `requirements-learning.txt`
- `docs/LEARNING_MODE_ZH.md`

可能小范围修改：
- `src/trading/alpaca_manager.py` 加安全开关
- `src/trading/trade_executor.py` 加安全开关
- `src/data/data_fetcher.py` 加 LLM 禁用开关

注意：Phase 1 才执行这些修改，本 Phase 0 不执行。

## 15. Phase 1 验收标准

验收：
- 不联网也能完成前 5 个 Notebook。
- 不配置 API Key 也能完成学习。
- 所有学习测试通过。
- 交易函数在学习模式下不可执行。
- Mock LLM 不产生费用。
- 文档解释每个专业词。
- Windows PowerShell 命令可复制运行。

## 16. Phase 1 明确不包含

不包含：
- 实盘交易。
- 模拟下单。
- 强化学习训练。
- 大型模型下载。
- GPU 必需功能。
- 自动投资建议。
- 自动执行交易。
- 真实 API Key。

当前未进入 Phase 1。
