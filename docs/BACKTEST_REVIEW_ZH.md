# 回测系统审计

## 1. 回测入口

已发现回测入口：
- `src/backtest/backtest_engine.py`
- `BacktestEngine.run_backtest`
- `src/strategies/run_adaptive_rotation_strategy.py`
- `run_backtest`
- `src/strategies/ml_bucket_selection.py`
- `--infer-date` 和 `--ref-date/--end-date` 的历史评估逻辑
- `examples/compare_cost_models.ipynb`

完成程度：部分实现。

零基础解释：回测入口就是运行历史模拟的起点。

## 2. 回测类型

结论：主回测引擎是基于目标权重的向量化/框架式回测，不是完整事件驱动撮合系统。

证据：
- 文件：`src/backtest/backtest_engine.py`
- 函数：`_create_bt_strategy`
- 使用：`bt.algos.WeighTarget`
- 使用：`bt.algos.Rebalance`

完成程度：部分实现。

专业词：事件驱动回测（Event-Driven Backtesting）。

零基础解释：事件驱动回测会模拟每一个订单、成交和市场事件；本项目主要是给定权重后定期再平衡。

## 3. 数据频率

结论：项目同时存在日频价格、季度基本面、周频轮动信号。

证据：
- 日频价格：`DataStore.price_data`，`get_price_data`
- 季度基本面：`fundamental_data.datadate`
- 周频轮动：`run_adaptive_rotation_strategy.py` 默认 `freq="W-FRI"`
- 配置：`AdaptiveRotationConf_v1.2.1.yaml` 的 `rebalance_frequency: weekly`

完成程度：部分实现。

零基础解释：数据频率表示数据是每天、每周还是每季度更新一次。

## 4. 信号生成时间和成交时间

结论：ML 文档强调 `datadate → tradedate`，`ml_bucket_selection.py` 实现了映射；但 `BacktestEngine` 对普通权重信号只在给定日期直接 `RunOnDate` 调仓，无法自动证明所有信号都至少滞后一周期。

证据：
- 文件：`src/strategies/ml_bucket_selection.py`
- 函数：`datadate_to_tradedate`
- 文件：`src/backtest/backtest_engine.py`
- 函数：`_create_bt_strategy`

完成程度：部分实现。

专业词：信号滞后（Signal Lag）。

零基础解释：如果今天收盘后才知道信号，就不能假装今天收盘前已经成交。

风险等级：高。

## 5. 订单、持仓和成交

| 问题 | 当前实现 | 证据 | 结论 |
|---|---|---|---|
| 信号如何转订单 | `bt.algos.WeighTarget` + `Rebalance` | `_create_bt_strategy` | 框架处理 |
| 订单如何转持仓 | `bt` 内部 | `bt.run(backtest)` | 非自研撮合 |
| 是否考虑交易费用 | 是 | `transaction_cost=0.001`，`commissions=lambda ...` | 部分 |
| 是否考虑滑点 | 未发现 | 无 slippage 主线 | 未实现 |
| 成交量限制 | 部分 | 可选 CostModel 需要 volume | 默认未启用 |
| 无法成交 | 未发现 | 无拒单/停牌模拟 | 未实现 |
| 停牌 | 未发现 | 无停牌逻辑 | 未实现 |
| 涨跌停 | 未发现 | 无 limit-up/down 逻辑 | 未实现 |
| 股票 T+1 | 未发现 | 无中国市场 T+1 | 未实现 |
| 做空 | 默认无 | 权重被归一化为非负为主 | 未实现/不主线 |
| 借券费用 | 未发现 | 无 borrow fee | 未实现 |
| 期货保证金 | 未发现 | 无 futures margin | 未实现 |
| 不同交易日历 | 部分 | `pandas_market_calendars`、NYSE | 部分 |

专业词：滑点（Slippage）。

零基础解释：滑点是理想成交价和真实成交价之间的差距。

## 6. 回测绩效指标

已实现指标：
- 总收益：`total_return`
- 年化收益率：`annual_return`
- 年化波动率：`annual_volatility`
- 夏普比率：`sharpe_ratio`
- 索提诺比率：`sortino_ratio`
- 最大回撤：`max_drawdown`
- 偏度、峰度
- 月度辅助指标
- Adaptive 报告中的 Calmar Ratio 和 Win Rate

证据：
- 文件：`src/backtest/backtest_engine.py`
- 函数：`_calculate_comprehensive_metrics`
- 函数：`_backfill_short_period_metrics`
- 函数：`_calculate_basic_metrics`
- 文件：`src/strategies/run_adaptive_rotation_strategy.py`
- 函数：`_generate_performance_report`

专业词：损益（Profit and Loss，PnL）。

零基础解释：损益就是某段时间内赚了多少钱或亏了多少钱。

## 7. 基准策略

结论：支持 SPY、QQQ 买入并持有基准。

证据：
- 文件：`src/backtest/backtest_engine.py`
- 配置：`BacktestConfig.benchmark_tickers`
- 函数：`_get_benchmark_metrics`
- 策略：`bt.algos.RunOnce`、`WeighEqually`、`Rebalance`

完成程度：完整实现。

零基础解释：基准是用来比较策略好坏的参照物，例如买入 SPY 后一直持有。

## 8. 未来数据泄漏检查

已做防护：
- ML 文档明确 `datadate → tradedate → trade_price → y_return`
- `ml_bucket_selection.py` 有 `DATADATE_TO_TRADEDATE_MAP`
- 使用 SP500 历史成分 CSV 做 point-in-time 过滤
- `StandardScaler` 在 `run_bucket` 中先对训练集 `fit_transform`，再对验证和推理 `transform`

证据：
- 文件：`ML_STOCK_SELECTION.md`
- 文件：`src/strategies/ml_bucket_selection.py`
- 函数：`datadate_to_tradedate`
- 数据：`data/sp500_historical_constituents.csv`

仍有风险：
- `DataProcessor.create_ml_dataset` 使用 `merge_asof(... direction='backward')` 和 `future_return`，需要隔离测试验证时间语义。
- Adaptive performance report 对权重日期到下一权重日期的收益计算较粗糙。
- `ml_bucket_selection.py` 的 `--ref-date/--end-date` 会下载实际收益，若用于调参可能造成测试集反复使用。

专业词：幸存者偏差（Survivorship Bias）。

零基础解释：幸存者偏差是只看现在还存在的股票，而忽略历史上退市或被剔除的股票。

## 9. 回测可能虚高的全部原因

风险清单：
1. 默认回测缺少滑点，真实成交通常更差。
2. 默认回测缺少成交量约束，大资金不一定能按价格成交。
3. 停牌、涨跌停、无法成交未建模。
4. 普通权重信号直接 `RunOnDate`，不自动强制信号滞后一日。
5. 部分 Web 回测使用随机样例数据，不代表真实回测。
6. Adaptive 快速风控和止损在回测中部分只是“记录/调整说明”，不是完整订单级成交。
7. 如果反复用测试期选择 alpha、模型、参数，会形成过拟合。
8. 新闻情绪若未来接入回测，必须严格按新闻发布时间对齐，否则会使用未来新闻。
9. 当前缺少单元测试证明交易费用、最大回撤、调仓日期、数据泄漏检查正确。
10. README 展示收益结果当前无法从静态代码确认可复现。

专业词：过拟合（Overfitting）。

零基础解释：过拟合是策略太贴合过去数据，未来反而可能表现很差。

## 10. 单元测试

结论：未发现 `tests/` 目录，未发现系统化 pytest/unittest 测试。

证据：
- 命令：`Test-Path tests` 返回 `False`
- 文件：部分模块 `if __name__ == "__main__"` 下有手写测试或样例

完成程度：测试系统未实现。

零基础解释：单元测试是用小规模自动检查证明某个函数没有明显错误。

## 11. 是否适合作为教学回测

结论：适合作为 Phase 1 教学回测的素材，但需要先简化：
- 只使用离线 CSV。
- 只做买入并持有、等权、简单动量三个策略。
- 明确交易日、信号日、成交日。
- 手写小型回测与 `bt` 结果对照。
- 禁用 Alpaca 和 OpenAI。

当前未进入 Phase 1。
