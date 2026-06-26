# 量化金融模块审计

## 1. 总览

结论：项目真实实现了股票和 ETF 价格、基本面、新闻、机器学习选股、组合权重、风险控制、回测、模拟/实盘 Alpaca 交易接口；但期货、加密货币、宏观经济、行业中性化、严格滑点、成交量限制、T+1 等模块未发现完整实现。

零基础解释：量化金融模块就是把数据、模型、策略、回测和交易连起来的一套流程。

## 2. 数据模块

| 项目 | 是否存在 | 证据 | 完成程度 | 零基础解释 | 风险或限制 |
|---|---|---|---|---|---|
| 行情数据获取 | 是 | `src/data/data_fetcher.py`，`FMPFetcher.get_price_data` | 部分实现 | 获取股票每天开高低收和成交量 | 默认 FMP，联网且可能需要 API Key |
| 股票数据 | 是 | `get_sp500_components`、`fetch_sp500_tickers` | 部分实现 | 股票列表和价格 | 主要围绕美国股票 |
| 指数数据 | 是 | 配置中 `SPY`、`QQQ`、`^GSPC`、`^VIX` | 部分实现 | 指数用于基准和市场状态 | 来源依赖 FMP/yfinance/CSV |
| 期货数据 | 未发现 | 无期货专用模块 | 未实现 | 期货是带保证金的合约 | 不适合作为期货教学 |
| 加密货币数据 | 未发现 | 无 crypto/binance 模块 | 未实现 | 加密货币是数字资产 | 未实现 |
| 宏观经济数据 | 未发现 | 无宏观数据源 | 未实现 | 利率、通胀等宏观变量 | 未实现 |
| 新闻数据 | 是 | `FMPFetcher.get_news` | 部分实现 | 新闻可用于情绪因子 | 需要 FMP，可能调用 OpenAI |
| 财务报表数据 | 是 | `get_fundamental_data`、`fetch_and_store_fundamentals.py` | 部分实现 | 财报数据用于基本面因子 | 需要 FMP 或本地缓存 |
| OHLCV 数据 | 是 | `price_data` 表字段 open/high/low/close/volume | 完整实现 | 开高低收成交量是价格基础数据 | 复权和停牌处理有限 |

专业词：成交量（Volume）。

零基础解释：成交量是一段时间内交易了多少股，常用于判断市场活跃度。

## 3. 数据清洗与特征工程

| 项目 | 是否存在 | 证据 | 完成程度 | 输入 | 输出 | 风险或限制 |
|---|---|---|---|---|---|---|
| 数据清洗 | 是 | `DataProcessor._clean_fundamental_data`、`_clean_price_data` | 部分实现 | CSV | 清洗后的 DataFrame | 规则较基础 |
| 缺失值处理 | 是 | `DataProcessor._handle_missing_values` | 部分实现 | fundamental DataFrame | 中位数填充 | 按 sector 填充，若缺 sector 可能失败 |
| 异常值处理 | 是 | `ml_bucket_selection.py` 中 winsorize 逻辑 | 部分实现 | 因子列 | 截尾后的因子 | 非全局模块化 |
| 复权处理 | 是 | `adj_close`、`fix_adj_close.py` | 部分实现 | yfinance/FMP 价格 | adj_close_q | 依赖外部数据 |
| 技术指标 | 是 | `DataProcessor._add_technical_indicators` | 部分实现 | 价格数据 | SMA、RSI、MACD | MACD 实现可能存在 pandas 对齐风险 |
| 基本面因子 | 是 | `DataStore.FUNDAMENTAL_COLS`、`FMPFetcher.get_fundamental_data` | 部分实现 | 财报接口 | 多个估值/盈利/杠杆因子 | 因子定义依赖 FMP 字段 |
| 动量因子 | 是 | `ml_bucket_selection.py` 的 `MOMENTUM_COLS` | 部分实现 | 历史价格/财报 | ret_1q 等 | 需确认时间对齐 |
| 价值因子 | 是 | `pe`、`ps`、`pb`、`peg` | 部分实现 | 财报 | 估值因子 | 数据质量依赖 FMP |
| 质量因子 | 是 | `roe`、`gross_margin` 等 | 部分实现 | 财报 | 质量/盈利因子 | 财报滞后需要严格处理 |
| 情绪因子 | 是 | `news_articles.sentiment` | 部分实现 | 新闻 + OpenAI | sentiment/confidence | 未发现严格新闻时间对齐回测 |
| 因子标准化 | 是 | `StandardScaler` | 部分实现 | 特征矩阵 | 标准化特征 | 若全数据提前标准化会泄漏；部分脚本先分割后 fit |
| 行业中性化 | 未发现严格实现 | 仅有 sector/bucket 和行业分组 | 未实现/部分实现 | 行业字段 | 分桶结果 | 不是统计意义的行业中性化 |

专业词：因子（Factor）。

零基础解释：因子是一个用来解释或预测收益的变量，比如估值、动量、质量。

## 4. 标签与数据集划分

| 项目 | 是否存在 | 证据 | 完成程度 | 零基础解释 | 风险 |
|---|---|---|---|---|---|
| 标签生成 | 是 | `DataProcessor.create_ml_dataset` 的 `future_return`，`ML_STOCK_SELECTION.md` 的 `y_return` | 部分实现 | 标签是模型要预测的未来收益 | 需要防止未来数据泄漏 |
| 训练集/验证集/测试集划分 | 是 | `ml_bucket_selection.py` 的 `val_cutoff`、`val_quarters` | 部分实现 | 用过去训练，用后面验证 | 没有独立测试目录证明 |
| 点时成分过滤 | 是 | `get_sp500_at` 相关逻辑，`sp500_historical_constituents.csv` | 部分实现 | 避免使用未来股票池 | 需运行验证，不在 Phase 0 执行 |

专业词：未来数据泄漏（Look-Ahead Bias）。

零基础解释：未来数据泄漏就是在历史回测时偷偷用了当时还不知道的信息。

## 5. 机器学习模块

| 模型 | 中文名称 | 文件 | 用途 | 输入 | 输出 | CPU 可行性 | 完成程度 |
|---|---|---|---|---|---|---|---|
| LinearRegression | 线性回归（Linear Regression） | `src/strategies/ml_strategy.py` | 基线预测 | 基本面和价格特征 | 收益预测 | 可 | 部分实现 |
| Ridge | 岭回归（Ridge Regression） | `ml_bucket_selection.py` | 单模型和 Stacking 元模型 | 标准化特征 | 收益预测 | 可 | 完整实现 |
| RandomForest | 随机森林（Random Forest，RF） | `ml_strategy.py`、`ml_bucket_selection.py` | 选股预测 | 因子 | 预测收益 | 可但较慢 | 完整实现 |
| XGBoost | 极端梯度提升（Extreme Gradient Boosting，XGBoost） | `ml_bucket_selection.py` | 候选模型 | 因子 | 预测收益 | 可 | 可选依赖 |
| LightGBM | 轻量梯度提升机（Light Gradient Boosting Machine，LightGBM） | `ml_bucket_selection.py` | 候选模型 | 因子 | 预测收益 | 可 | 可选依赖 |
| ExtraTrees | 极端随机树（Extra Trees） | `ml_bucket_selection.py` | 候选模型 | 因子 | 预测收益 | 可 | 完整实现 |
| HistGradientBoosting | 直方图梯度提升（Histogram Gradient Boosting） | `ml_bucket_selection.py` | 候选模型 | 因子 | 预测收益 | 可 | 完整实现 |
| Stacking | 堆叠集成（Stacking Ensemble） | `ml_bucket_selection.py` | 集成模型 | 多模型预测 | 预测收益 | 可 | 完整实现 |
| SVM/SVR | 支持向量机（Support Vector Machine，SVM） | `src/strategies/rl_model.py` | 导入但非主线 | 未明确 | 未明确 | 可 | 仅导入/旧代码 |

零基础解释：机器学习模型会从历史样本中学习“哪些特征可能对应更高未来收益”。

## 6. 深度学习和强化学习模块

| 项目 | 是否存在 | 证据 | 完成程度 | 状态空间 | 动作空间 | 奖励函数 | 是否适合零基础立即运行 |
|---|---|---|---|---|---|---|---|
| 深度神经网络（Deep Neural Network，DNN） | 间接存在 | `torch` 依赖、Stable-Baselines 路径 | 依赖/间接 | 未单独定义 | 未单独定义 | 未单独定义 | 否 |
| 长短期记忆网络（Long Short-Term Memory，LSTM） | 未发现 | 无 LSTM 类/函数 | 未实现 | 无 | 无 | 无 | 否 |
| Transformer | 未发现 | 无 Transformer 训练代码 | 未实现 | 无 | 无 | 无 | 否 |
| 强化学习（Reinforcement Learning，RL） | 是 | `src/strategies/rl_model.py` | 部分实现 | `state_space` 参数 | `action_space=stock_dimension` | FinRL 环境内部 | 否 |
| 深度强化学习（Deep Reinforcement Learning，DRL） | 是 | `DRLAgent`、`StockPortfolioEnv` | 部分实现 | 协方差/技术指标 | 组合权重 | 环境收益 | 否 |
| PPO | 是 | `train_ppo` | 部分实现 | FinRL 环境 | 权重动作 | 环境收益 | 否 |
| DDPG | 是 | `train_ddpg` | 部分实现 | FinRL 环境 | 权重动作 | 环境收益 | 否 |
| TD3 | 是 | `train_td3` | 函数存在但主流程注释 | FinRL 环境 | 权重动作 | 环境收益 | 否 |
| SAC | 是 | `train_sac` | 函数存在但主流程注释 | FinRL 环境 | 权重动作 | 环境收益 | 否 |
| A2C | 是 | `train_a2c` | 部分实现 | FinRL 环境 | 权重动作 | 环境收益 | 否 |
| Stable-Baselines3 | 是 | `stable_baselines3.common.vec_env`、`setup.py extras` | 依赖/部分实现 | 由 FinRL 包装 | 由 FinRL 包装 | 由 FinRL 包装 | 否 |
| Ray RLlib | 未发现 | 无 rllib 命中 | 未实现 | 无 | 无 | 无 | 否 |
| PyTorch | 是 | `torch` | 依赖/设备选择 | 训练后端 | 模型参数 | 模型训练 | 否 |
| TensorFlow | 仅环境变量 | `TF_CPP_MIN_LOG_LEVEL` | 仅痕迹 | 无 | 无 | 无 | 否 |

零基础解释：强化学习会让模型通过“试错”学习动作，但训练耗时长、结果不稳定。

## 7. 策略信号、组合权重与风险控制

| 项目 | 是否存在 | 证据 | 完成程度 | 风险 |
|---|---|---|---|---|
| 交易信号生成 | 是 | `generate_weights`、`AdaptiveRotationEngine.run` | 部分实现 | 信号时间需验证 |
| 做多信号 | 是 | 选中正预测收益股票，长仓权重 | 部分实现 | 无做空 |
| 做空信号 | 未发现主线实现 | 注释中有 short_dict 但未启用 | 未实现 | 无 |
| 仓位生成 | 是 | `PortfolioWeights`、`allocate_weights` | 部分实现 | 需验证约束 |
| 投资组合权重 | 是 | `weight_signals`、`weights.weights` | 完整实现 | 权重可直接下单 |
| 调仓逻辑 | 是 | `bt.algos.RunOnDate`、Adaptive weekly | 部分实现 | 执行滞后不总是明确 |
| 交易费用 | 是 | `transaction_cost=0.001`、`transaction_cost_pct=0.001` | 部分实现 | 费用模型简单 |
| 滑点 | 未发现显式实现 | 无 slippage 主线 | 未实现 | 回测可能偏乐观 |
| 最大持仓限制 | 是 | 配置 `max_weight_per_stock`、Adaptive `max_assets` | 部分实现 | 需运行验证 |
| 止损 | 是 | `risk_manager.py` | 完整实现 | 回测中 fast/stop 调整未完整反映成交 |
| 止盈 | 未发现 | 无 take-profit | 未实现 | 无 |
| 风险管理 | 是 | `RiskManager`、交易前检查 | 部分实现 | 缺少全局禁交易开关 |

专业词：投资组合（Portfolio）。

零基础解释：投资组合是一篮子资产及其每个资产的资金占比。

## 8. 回测与绩效指标

| 项目 | 是否存在 | 证据 | 完成程度 |
|---|---|---|---|
| 历史回测 | 是 | `BacktestEngine.run_backtest`、`run_adaptive_rotation_strategy.py --backtest` | 部分实现 |
| 买入并持有基准 | 是 | `_get_benchmark_metrics` 中 BuyHold | 部分实现 |
| 策略基准指数 | 是 | 默认 `SPY`、`QQQ` | 完整实现 |
| 年化收益率 | 是 | `annual_return` | 完整实现 |
| 年化波动率 | 是 | `annual_volatility` | 完整实现 |
| 夏普比率 | 是 | `sharpe_ratio` | 完整实现 |
| 最大回撤 | 是 | `_calculate_max_drawdown` | 完整实现 |
| 胜率 | 是 | Adaptive performance report | 部分实现 |
| 交易次数 | 部分 | bt trades 为空 DataFrame | 部分实现 |
| 换手率 | 是 | DRL performance 中 turnover | 部分实现 |

专业词：夏普比率（Sharpe Ratio）。

零基础解释：夏普比率衡量每承担一单位波动风险，大约换来多少超额收益。

## 9. 模拟盘与实盘

| 项目 | 是否存在 | 证据 | 完成程度 | 风险 |
|---|---|---|---|---|
| 模拟交易 | 是 | `.env.example` 的 paper URL，`deploy.sh --mode paper` | 完整实现 | 可能真实提交 paper 订单 |
| 实盘交易 | 是 | `AlpacaAccount.base_url` 可配置 | 部分实现 | `AlpacaManager` 不禁止 live URL |

结论：学习阶段应完全禁用 `src/trading/` 下单路径和 `deploy.sh --mode paper`。
