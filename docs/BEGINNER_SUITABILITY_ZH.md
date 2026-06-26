# 零基础教学适配性审计

## 1. 总体结论

项目适合作为“量化金融 + 大语言模型”双线学习项目的底层素材，但不适合零基础直接从 README 开始运行。主要原因是功能跨度太大、交易接口真实存在、依赖较重、缺少中文教学层、缺少 Mock LLM、缺少安全开关、缺少测试。

零基础解释：零基础教学需要从小数据、小例子、无风险操作开始，而不是直接接触真实券商和复杂模型。

## 2. 学习者需要先懂的概念

| 概念 | 标准写法 | 零基础解释 |
|---|---|---|
| 买入 | 买入（Buy） | 用资金买资产。 |
| 卖出 | 卖出（Sell） | 把资产卖掉换回现金。 |
| 做多 | 做多（Long） | 认为资产会上涨，所以买入持有。 |
| 做空 | 做空（Short） | 认为资产会下跌，通过借入卖出等方式获利。 |
| 开仓 | 开仓（Open Position） | 新建一笔持仓。 |
| 平仓 | 平仓（Close Position） | 结束已有持仓。 |
| 持仓 | 持仓（Position） | 当前账户里持有的资产。 |
| 收益率 | 收益率（Return） | 盈亏占本金的比例。 |
| 波动率 | 波动率（Volatility） | 价格上下波动的剧烈程度。 |
| 最大回撤 | 最大回撤（Maximum Drawdown，MDD） | 资金从最高点跌到之后最低点的最大跌幅。 |
| 因子 | 因子（Factor） | 用来预测收益的变量，如估值、动量。 |
| 回测 | 回测（Backtesting） | 用历史数据模拟策略过去表现。 |
| 滑点 | 滑点（Slippage） | 理论成交价和实际成交价之间的差。 |
| 大语言模型 | 大语言模型（Large Language Model，LLM） | 能处理自然语言文本的模型。 |
| Token | 令牌（Token） | 模型计费和处理文本的基本单位。 |
| Prompt | 提示词（Prompt） | 写给模型的任务说明。 |
| Embedding | 嵌入向量（Embedding） | 把文本变成数字向量，方便检索和计算。 |
| RAG | 检索增强生成（Retrieval-Augmented Generation，RAG） | 先查资料再让模型回答。 |
| API | 应用程序编程接口（Application Programming Interface，API） | 程序调用外部服务的接口。 |

## 3. 项目现有内容从易到难排序

1. 阅读 `data/fundamental_data_full.csv` 和 `sp500_historical_constituents.csv`
2. 阅读 `ML_STOCK_SELECTION.md`
3. 学习 `src/data/data_store.py` 的 SQLite 表结构
4. 学习 `src/data/data_processor.py` 的清洗和特征工程
5. 学习 `src/strategies/ml_bucket_selection.py` 的传统机器学习选股
6. 学习 `src/backtest/backtest_engine.py` 的权重回测
7. 学习 `src/strategies/adaptive_rotation/`
8. 学习 `src/data/data_fetcher.py` 的 FMP 和新闻情绪
9. 学习 `src/trading/` 的 Alpaca 交易接口
10. 学习 `src/strategies/rl_model.py` 和 `fundamental_portfolio_drl.py`

零基础解释：从易到难排序能避免一开始就被 API Key、训练、交易风险卡住。

## 4. 可以立即学习的模块

适合立即阅读：
- `ML_STOCK_SELECTION.md`
- `src/data/data_store.py`
- `src/data/data_processor.py`
- `src/strategies/ml_bucket_selection.py`
- `src/backtest/backtest_engine.py`
- `docs/trading_calendar_guide.md`

条件：
- 只读。
- 不运行联网脚本。
- 不运行训练。
- 不配置 API Key。

## 5. 不适合立即学习的模块

不适合初学者直接运行：
- `src/trading/alpaca_manager.py`
- `src/trading/trade_executor.py`
- `deploy.sh`
- `src/data/data_fetcher.py` 的 `__main__`
- `src/strategies/rl_model.py`
- `src/strategies/fundamental_portfolio_drl.py`
- `src/web/app.py` 的 Live Trading 页面

原因：
- 可能联网。
- 可能下单。
- 可能训练很久。
- 可能需要 API Key。
- 可能在 Windows 下不兼容。

## 6. 专业词解释不足

README 和代码中常见问题：
- 大量使用 ML、DRL、PPO、SAC、A2C、MDD、PnL、API 等缩写。
- 英文文档为主，中文零基础解释不足。
- README 对架构描述偏高层，初学者难以对应到函数。
- Notebook 可能直接进入完整工作流，缺少小型数字例子。

专业词：近端策略优化（Proximal Policy Optimization，PPO）。

零基础解释：PPO 是一种强化学习算法，用来训练模型在环境中选择动作。

## 7. 数字案例、图表、Notebook

| 项目 | 当前状态 |
|---|---|
| 数字案例 | `ML_STOCK_SELECTION.md` 有 AMD 的 y_return 示例，较好 |
| 图表 | `figs/` 有结果图，但偏论文/展示 |
| Notebook | `examples/` 有 ipynb，但未作为零基础课程拆分 |
| 离线样例数据 | 有较大 CSV 和压缩包，但缺小型教学数据 |
| Mock LLM | 没有 |
| Mock Broker | 没有 |

零基础解释：数字案例能让学习者用几个数手算，确认自己理解公式。

## 8. 无 API Key、无 GPU、无实盘可行性

| 条件 | 当前可行性 |
|---|---|
| 无 API Key 学习 | 可阅读；运行需要离线样例改造 |
| 无 GPU 学习 | 基础 ML 和回测可以；DRL 不建议 |
| 不接触实盘学习 | 可以，但必须避开交易模块 |
| 无 Docker 学习 | 可以 |
| 纯 PowerShell 学习 | 需要替代 `deploy.sh` |

专业词：图形处理器（Graphics Processing Unit，GPU）。

零基础解释：GPU 是加速模型训练的硬件，第一阶段不需要。

## 9. 哪些部分适合作为第一课

建议第一课：
1. 股票价格表的含义：date、open、high、low、close、volume。
2. 单只股票收益率计算。
3. 买入并持有策略。
4. 等权组合。
5. 最大回撤和夏普比率。
6. 用离线 CSV 做最小回测。

不建议第一课：
- 强化学习。
- Alpaca 交易。
- OpenAI API。
- FMP 大规模抓取。
- Docker 部署。

## 10. 需要重新制作的中文教学层

建议新增：
- `learning/00_glossary_zh.md`
- `learning/01_prices_and_returns.ipynb`
- `learning/02_buy_and_hold_backtest.ipynb`
- `learning/03_equal_weight_portfolio.ipynb`
- `learning/04_simple_momentum_factor.ipynb`
- `learning/05_ml_stock_selection_small.ipynb`
- `learning/06_mock_llm_sentiment.ipynb`
- `learning/07_sentiment_plus_momentum.ipynb`
- `learning/data/`
- `learning/mock/`

专业词：教学层（Learning Layer）。

零基础解释：教学层是专门给初学者准备的简化代码和说明，不直接暴露复杂生产模块。

## 11. 是否适合作为双线主项目

结论：适合，但需要改造。

适合原因：
- 有真实量化数据结构。
- 有机器学习选股。
- 有回测。
- 有新闻情绪的 LLM 雏形。
- 有交易接口可作为高级安全案例。

缺少内容：
- LLM 主线太弱。
- 无 Mock LLM。
- 无结构化输出校验。
- 无初学者离线数据。
- 无安全开关。
- 无测试。
- 无 Windows PowerShell 学习命令。

当前未进入 Phase 1。
