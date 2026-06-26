# 项目架构审计

## 1. 目录结构

核心目录：
- `src/config/`：配置读取。
- `src/data/`：数据源、SQLite 存储、数据处理、补数据脚本。
- `src/backtest/`：基于 `bt` 的回测引擎。
- `src/strategies/`：传统机器学习、深度强化学习脚本、自适应轮动策略。
- `src/trading/`：Alpaca 账户、订单和组合再平衡。
- `src/web/`：Streamlit 页面。
- `examples/`：Notebook 和说明。
- `data/`：压缩数据、基本面 CSV、SP500 历史成分。

零基础解释：架构就是项目不同文件夹各自负责什么。

## 2. 核心模块

### 配置模块

结论：项目使用 Pydantic Settings 读取 `.env` 和环境变量。

证据：
- 文件：`src/config/settings.py`
- 类：`FinRLSettings`
- 类：`AlpacaSettings`
- 类：`FMPSettings`
- 类：`OpenAISettings`
- 函数：`get_config`

完成程度：完整实现。

零基础解释：配置模块统一管理 API Key、数据库路径、日志路径和交易限制。

### 数据模块

结论：真实数据源管理器只注册 FMPFetcher，具备本地优先和离线模式。

证据：
- 文件：`src/data/data_fetcher.py`
- 类：`FMPFetcher`
- 类：`DataSourceManager`
- 函数：`get_data_manager`

完成程度：部分实现。

零基础解释：数据模块负责把股票价格、基本面和新闻转成程序能使用的表格。

### 存储模块

结论：项目使用 SQLite 保存价格、指数成分、原始财报载荷、新闻和基本面因子。

证据：
- 文件：`src/data/data_store.py`
- 类：`DataStore`
- 函数：`_init_database`
- 表：`price_data`
- 表：`sp500_components_details`
- 表：`raw_payloads`
- 表：`news_articles`
- 表：`news_fetch_log`
- 表：`fundamental_data`

完成程度：完整实现。

零基础解释：SQLite 是一个本地数据库文件，可以把下载来的数据存在电脑里。

### 策略模块

结论：策略层有基础接口、机器学习选股、自适应轮动和深度强化学习脚本。

证据：
- 文件：`src/strategies/base_strategy.py`
- 类：`BaseStrategy`
- 文件：`src/strategies/ml_strategy.py`
- 类：`MLStockSelectionStrategy`
- 类：`SectorNeutralMLStrategy`
- 文件：`src/strategies/adaptive_rotation/adaptive_rotation_engine.py`
- 类：`AdaptiveRotationEngine`
- 文件：`src/strategies/rl_model.py`

完成程度：部分实现。

零基础解释：策略模块负责决定买哪些资产、每个资产买多少。

### 回测模块

结论：回测模块基于 `bt` 库实现目标权重回测，并提供基准比较。

证据：
- 文件：`src/backtest/backtest_engine.py`
- 类：`BacktestConfig`
- 类：`BacktestEngine`
- 函数：`run_backtest`
- 函数：`_create_bt_strategy`
- 函数：`_get_benchmark_metrics`

完成程度：部分实现。

零基础解释：回测模块用历史价格模拟策略收益。

### 交易模块

结论：交易模块真实实现 Alpaca 账户、订单、批量订单、取消订单和组合再平衡。

证据：
- 文件：`src/trading/alpaca_manager.py`
- 类：`AlpacaManager`
- 函数：`place_order`
- 函数：`place_orders_batch`
- 函数：`execute_portfolio_rebalance`
- 文件：`src/trading/trade_executor.py`
- 类：`TradeExecutor`

完成程度：完整实现但风险高。

零基础解释：交易模块会和券商接口通信，可能发出真实或模拟订单。

## 3. 模块依赖关系

文本架构图：

```text
.env / 环境变量
→ src/config/settings.py
→ src/data/data_fetcher.py
→ src/data/data_store.py
→ src/strategies/ml_strategy.py 或 src/strategies/adaptive_rotation/
→ 权重 DataFrame / PortfolioWeights
→ src/backtest/backtest_engine.py
→ 回测指标与图表

权重 DataFrame / PortfolioWeights
→ src/trading/alpaca_manager.py
→ Alpaca API
→ 订单 / 持仓 / 账户信息
```

专业词：应用程序编程接口（Application Programming Interface，API）。

零基础解释：API 是程序和外部服务对话的接口，例如向券商提交订单。

## 4. 数据流

真实可确认的数据流：

```text
FMP 或本地 SQLite/CSV
→ FMPFetcher.get_sp500_components / get_fundamental_data / get_price_data / get_news
→ DataStore 保存 price_data / fundamental_data / news_articles
→ DataProcessor 或 ML 脚本生成特征
→ MLStockSelectionStrategy 或 ml_bucket_selection.py 训练/预测
→ 目标股票与权重
→ BacktestEngine.run_backtest 或 AlpacaManager.execute_portfolio_rebalance
→ 回测结果或订单结果
```

完成程度：部分实现。

风险或限制：`src/data/data_fetcher.py` 的 `__main__` 会抓取 NVDA 新闻并在 `analyze_sentiment=True` 时调用 OpenAI，不应在 Phase 0 运行。

## 5. 模型训练流

传统机器学习训练流：

```text
fundamental_data 表 / fundamental_data_full.csv
→ 选择 FEATURE_COLS 和 MOMENTUM_COLS
→ 缺失值填充 / winsorize / 标准化
→ RandomForest / XGBoost / LightGBM / HistGradientBoosting / ExtraTrees / Ridge / Stacking
→ 验证集 MSE 选模型
→ 训练集 + 验证集重训
→ inference 预测
→ CSV / XLSX 输出
```

证据：
- 文件：`src/strategies/ml_bucket_selection.py`
- 函数：`build_models`
- 函数：`run_bucket`
- 参数：`--val-cutoff`
- 参数：`--infer-date`

专业词：均方误差（Mean Squared Error，MSE）。

零基础解释：MSE 衡量预测值和真实值差距，越小通常越好。

## 6. 回测流

```text
权重信号
→ BacktestEngine._prepare_price_data_for_bt
→ 对齐交易日并前向填充权重
→ bt.algos.WeighTarget
→ bt.algos.Rebalance
→ bt.run
→ 收益、波动、夏普、最大回撤
```

证据：
- 文件：`src/backtest/backtest_engine.py`
- 类：`BacktestEngine`
- 函数：`run_backtest`
- 函数：`_calculate_comprehensive_metrics`

专业词：最大回撤（Maximum Drawdown，MDD）。

零基础解释：最大回撤是资金从历史高点跌到之后低点的最大跌幅。

## 7. 大语言模型调用流

```text
FMP 新闻
→ FMPFetcher.get_news
→ DataStore.get_news_articles 检查缓存
→ FMPFetcher._annotate_sentiment
→ OpenAI chat.completions.create
→ _parse_sentiment_response
→ DataStore.update_news_sentiment
```

证据：
- 文件：`src/data/data_fetcher.py`
- 函数：`get_news`
- 函数：`_annotate_sentiment`
- 函数：`_parse_sentiment_response`

完成程度：部分实现。

专业词：自然语言处理（Natural Language Processing，NLP）。

零基础解释：自然语言处理是让程序处理新闻、公告等文字材料。

## 8. 模拟或实盘交易流

```text
目标权重
→ AlpacaManager.execute_portfolio_rebalance
→ get_positions / get_portfolio_value
→ 生成 sell_orders 和 buy_orders
→ place_orders_batch
→ place_order
→ POST /v2/orders
```

证据：
- 文件：`src/trading/alpaca_manager.py`
- 函数：`execute_portfolio_rebalance`
- 函数：`place_order`

完成程度：完整实现。

风险或限制：`AlpacaAccount.is_paper` 仅用 `base_url` 是否包含 `paper` 判断，安全性不足。

## 9. README 与真实代码一致性

一致处：
- 目标权重接口真实存在。
- FMP、SQLite、bt、Alpaca、机器学习选股真实存在。
- 自适应轮动策略真实存在。

不一致处：
- README 写 Yahoo / WRDS 多源，但真实数据管理器只注册 FMP。
- README 写完整 Web 与 live trading，Web 中存在缺失导入和样例随机数据。
- README 写 LLM-ready，但真实 LLM 仅新闻情绪分析，不是完整 LLM 交易系统。

当前无法从静态代码确认：README 中展示的历史回测收益是否可由当前代码和数据复现。
