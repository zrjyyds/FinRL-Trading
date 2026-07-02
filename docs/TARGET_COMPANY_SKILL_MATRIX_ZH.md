# 目标岗位能力矩阵：量化研究实习方向

本矩阵面向“量化研究实习岗位作品集”重新评估当前项目。当前主线应从 FinRL/强化学习交易系统，调整为 A 股中低频多因子选股、XGBoost/LightGBM、严格样本外回测、组合构建和模型归因。

本轮只做代码库扫描、环境与风险审计、路线规划；未运行训练，未调用付费外部 API，未连接实盘或模拟盘，未发送订单。

## 1. 总体定位

| 维度 | 当前结论 |
|---|---|
| 当前项目主基因 | 美国股票、ETF、FinRL/DRL、Alpaca 交易、FMP/Yahoo 数据、bt 回测 |
| 目标项目主线 | A 股中低频多因子选股研究项目 |
| 当前可复用资产 | 数据存储、基础清洗、ML 选股雏形、回测引擎、配置模式、文档审计基础 |
| 当前不宜继续作为主线 | 强化学习、模拟盘/实盘交易、在线数据抓取、新闻 LLM 情绪 |
| 推荐主线 | 离线 A 股数据层 -> 因子研究 -> IC/分组回测 -> XGBoost/LightGBM -> 组合回测 -> 归因报告 |

## 2. 能力矩阵

状态只使用：已完整具备、部分具备、尚未具备、当前实现存在风险、暂时不需要。

| 能力项 | 状态 | 当前证据 | 主要差距 | 推荐动作 |
|---|---|---|---|---|
| 股票数据读取与清洗 | 部分具备 | `src/data/data_fetcher.py`、`src/data/data_processor.py`、`src/data/data_store.py` | 主要面向 FMP/Yahoo/美股；缺 A 股标准字段、交易状态、复权字段规范 | 建立离线 A 股 CSV/Parquet schema 和读取测试 |
| 动态股票池 | 部分具备 | `data/sp500_historical_constituents.csv`、`get_sp500_at` 相关逻辑 | 只有 S&P 500 point-in-time 思路；缺 A 股上市、退市、ST、指数成分、可交易状态历史 | 新增 A 股 point-in-time universe 表 |
| 前复权或后复权处理 | 部分具备 | `adj_close`、`prccd / ajexdi`、`src/data/fix_adj_close.py` | 复权策略未面向 A 股明确；未统一区分价格回测价格和收益计算价格 | 制定前复权/后复权使用规范和单测 |
| 因子计算 | 部分具备 | 基本面比率、动量列、技术指标、`ML_STOCK_SELECTION.md` | 缺研究级因子库、因子元数据、截面计算和缓存 | 建立 `factor_id/date/ticker/value` 长表规范 |
| 因子去极值 | 当前实现存在风险 | `src/strategies/ml_bucket_selection.py` 中 winsorize 逻辑 | 存在全样本分位数截尾风险，可能把验证/推理期分布信息带入训练 | 改为按日期或训练窗口估计，不在本轮改代码 |
| 因子标准化 | 部分具备 | `StandardScaler` 在 ML 脚本中使用 | 缺按交易日横截面 z-score；缺训练窗口 fit 后 transform 的统一约束 | 在因子流水线定义横截面标准化 |
| 行业中性化 | 部分具备 | sector bucket、sector-neutral selection | 不是标准回归残差中性化；缺 A 股行业分类版本管理 | 实现按日期对行业哑变量回归取残差 |
| 市值中性化 | 尚未具备 | 未发现完整市值中性化流水线 | 缺流通市值/总市值字段和回归残差处理 | 引入市值字段，做 log_mcap 中性化 |
| IC 和 RankIC | 尚未具备 | 未发现专用 IC/RankIC 模块 | 缺因子有效性核心评价 | 新增 Spearman/Pearson IC、月度汇总、t 值 |
| 分组回测 | 尚未具备 | 有 bucket ranking/backtest 思路，但非标准因子分组回测 | 缺 quintile/decile 分组、组间收益、多空组合 | 新增按日期分组和 OOS 分组收益 |
| 多因子组合 | 部分具备 | 多特征 ML、Stacking、bucket ensemble | 缺显式多因子合成规则、IC 加权、等权因子、模型预测因子 | 先做线性多因子，再做 ML 预测分数 |
| XGBoost | 部分具备 | `XGBRegressor` 可选导入、requirements 相关依赖 | 不是 A 股研究主线，缺统一训练/验证/测试协议 | 在后续 Phase 做离线小样本可复现实验 |
| LightGBM | 部分具备 | `LGBMRegressor` 可选导入、requirements 相关依赖 | 同上，缺 A 股横截面排序任务配置 | 建立 LGBM baseline 和 feature importance |
| 时间序列切分 | 部分具备 | `val_cutoff`、rolling training、walk-forward | 缺强制禁止随机切分的测试和研究配置 | 后续所有实验必须以日期切分 |
| 滚动训练 | 部分具备 | `MLStockSelectionStrategy._rolling_train_all_date`、adaptive walk-forward | 与目标 A 股月频/周频选股未完全对齐 | 实现 train-window/valid-window/test-window 可配置 |
| 防止数据泄漏 | 当前实现存在风险 | 有 point-in-time 成分和 datadate/tradedate 思路 | 全局去极值、财报披露日、标签错位、反复使用测试集风险仍需测试 | 先建立防泄漏检查清单和单测 |
| 交易成本 | 部分具备 | `BacktestConfig.transaction_cost`、`bt.core.CostModel` | 缺 A 股佣金、印花税、滑点、涨跌停无法成交 | 后续组合回测加入成本模型 |
| 组合约束 | 部分具备 | `max_weight_per_stock`、adaptive portfolio builder、min-variance | 缺 A 股行业、市值、流动性、换手率约束 | 新增组合优化/约束配置 |
| 绩效归因 | 尚未具备 | 有 feature importance 输出 | 缺组合收益归因、行业/风格/个股贡献、换手成本归因 | 后续生成归因表和报告图 |
| 实验配置管理 | 部分具备 | adaptive YAML/Pydantic config、settings | 不是统一研究实验配置；缺 run id、数据版本、结果目录约定 | 建立 `configs/research/*.yaml` 规范 |
| 结果自动汇总 | 部分具备 | ML 脚本输出 CSV/Excel/dashboard | 缺统一 experiment registry 和 OOS 指标汇总 | 新增结果 manifest、summary CSV |
| 研究报告生成 | 尚未具备 | 已有人工审计文档 | 缺自动从实验结果生成 Markdown/HTML/PDF 报告 | 后续 Phase 生成研究报告模板 |
| 强化学习 | 暂时不需要 | `src/strategies/rl_model.py`、FinRL 相关模块 | 与当前目标岗位主线不匹配，训练耗时且不稳定 | 保留为扩展路线，不删除、不作为当前主线 |
| 实盘/模拟盘交易 | 暂时不需要 | `src/trading/`、Alpaca、`deploy.sh --mode paper` | 当前作品集不需要下单能力，且有误触发风险 | 学习主线禁用交易入口 |

## 3. 与目标岗位 JD 的对应关系

| 岗位能力 | 当前可展示程度 | 说明 |
|---|---|---|
| Python 数据处理 | 中 | 有 pandas、SQLite、CSV 数据流，但需转为 A 股离线研究样式 |
| 因子研究 | 低到中 | 有基础因子来源，但缺 IC、RankIC、分组回测和中性化闭环 |
| 机器学习建模 | 中 | 有 XGB/LGBM/RF/Stacking 代码，但需严格样本外和可复现实验 |
| 回测严谨性 | 低到中 | 有 bt 回测和成本雏形，但缺 A 股交易约束与防泄漏测试 |
| 组合构建 | 中 | 有权重生成思路，但缺行业、市值、换手、流动性约束 |
| 研究表达 | 中 | 文档基础较好；还缺自动报告和可展示图表 |
| 工程规范 | 中 | 有配置、日志、模块化；缺测试体系和研究结果注册 |

## 4. 当前最适合展示的部分

- 已有数据/回测/ML 模块可作为“项目基础设施扫描与重构起点”展示。
- `ML_STOCK_SELECTION.md` 中的 datadate -> tradedate -> y_return 思路可作为 point-in-time 标签设计参考。
- adaptive rotation 的 YAML/Pydantic 配置可作为后续实验配置管理参考。
- 已有中文审计文档可证明项目具备风险意识和工程化整理能力。

## 5. 当前不建议展示为主线的部分

- 强化学习收益表现。
- Alpaca paper/live trading。
- 依赖在线 FMP/Yahoo/OpenAI 的一键脚本。
- 未经防泄漏测试的 ML 回测收益。

