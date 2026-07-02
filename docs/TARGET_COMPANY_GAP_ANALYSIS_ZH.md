# 目标岗位差距分析：A 股多因子机器学习选股

## 1. 目标画像

目标项目应能清晰展示以下能力：

1. 使用 A 股离线数据构建 point-in-time 股票池。
2. 计算中低频因子，并做去极值、标准化、行业/市值中性化。
3. 用 IC、RankIC 和分组回测评估因子。
4. 用 XGBoost/LightGBM 做横截面收益预测或排序。
5. 使用严格时间切分、滚动训练和独立样本外测试。
6. 构建组合，纳入交易成本、换手、持仓、行业、市值、流动性约束。
7. 输出自动汇总和研究报告，包括模型归因与绩效归因。

## 2. 当前项目基线

当前项目已经不是空白项目。它具备：

- 数据读取、清洗、SQLite 缓存和本地 CSV 基础。
- S&P 500 point-in-time 成分管理思路。
- 基本面、动量和技术指标雏形。
- XGBoost、LightGBM、RandomForest、Stacking 等模型入口。
- bt 回测引擎和简单交易成本设置。
- 配置管理、日志和多份审计文档。

但这些能力大多围绕美股、FMP/Yahoo、FinRL/DRL、Alpaca 交易，不是 A 股量化研究实习岗位最看重的主线。

## 3. 主要差距

| 差距 | 严重度 | 当前表现 | 对目标岗位的影响 | 建议优先级 |
|---|---|---|---|---|
| A 股 point-in-time 数据层缺失 | 高 | 缺 A 股股票池、交易状态、复权、ST、上市退市、披露日统一 schema | 没有可信数据层，后续所有因子和回测都不稳 | P0 |
| 防泄漏测试缺失 | 高 | 有局部 PIT 思路，但全局 winsorize、标签错位、财报披露生效日仍有风险 | 研究结果可能无法被面试官信任 | P0 |
| IC/RankIC 和分组回测缺失 | 高 | 未发现专用因子评价模块 | 无法展示标准量化研究流程 | P0 |
| A 股交易约束缺失 | 高 | 缺停牌、涨跌停、T+1、印花税、无法成交、流动性约束 | 回测可能显著高估 | P1 |
| 因子中性化不足 | 中 | 有 sector bucket，但无行业/市值回归中性化 | 因子解释性和稳健性不足 | P1 |
| 实验配置与结果注册不足 | 中 | 有 adaptive 配置，但不覆盖研究实验 | 结果难复现，无法形成作品集闭环 | P1 |
| 组合归因不足 | 中 | 有 feature importance，但无收益归因 | 难解释策略收益来源 | P2 |
| 研究报告自动化不足 | 中 | 有人工 docs，无自动实验报告 | 面试展示效率不够 | P2 |
| 强化学习主线偏离目标 | 中 | 项目 README 和代码仍有 DRL/交易导向 | 岗位匹配度被稀释 | P2 |

## 4. 数据泄漏与回测风险专项分析

| 风险项 | 是否发现 | 证据或原因 | 处理建议 |
|---|---|---|---|
| 未来函数 | 发现风险 | `create_ml_dataset` 生成 `future_return` 后 merge，需要单测证明特征均早于标签窗口；ML 脚本有全局去极值风险 | 建立 label/feature 时间戳断言 |
| 随机划分时间序列 | 未发现主线使用，但存在风险 | `ml_strategy.py` 导入 `train_test_split`；主流程多为 rolling/time cutoff | 后续测试禁止随机切分用于时间序列 OOS |
| 使用未来股票池 | 部分防护，A 股缺失 | 美股有历史 S&P500 成分；A 股无历史股票池 | 建立 A 股 universe effective_date |
| 财务数据按披露日期生效 | 当前实现存在风险 | 数据库有 `filing_date`、`accepted_date`，但 A 股需 `announce_date`/可交易日生效 | 财报因子必须按披露后下一交易日生效 |
| 忽略停牌和涨跌停 | 发现风险 | 回测审计未发现停牌/涨跌停主线逻辑 | A 股回测必须加入 `is_tradable` 和 limit flags |
| 忽略交易成本 | 部分具备 | 有 flat cost / bt CostModel，但缺 A 股印花税、滑点、无法成交 | 组合 Phase 加入成本模型 |
| 标签与特征时间错位 | 发现风险 | `datadate -> tradedate` 思路存在，但未对所有数据源统一强制 | 增加可复现小样本测试 |
| 训练/验证/测试泄漏 | 发现风险 | StandardScaler 局部正确，但全局填充/截尾可能泄漏；测试集反复评估也会过拟合 | 建立 fit-on-train-only transformer |

## 5. 可保留资产

- `src/data/data_store.py`：可借鉴 SQLite schema、缓存和数据读取模式。
- `src/data/data_processor.py`：可借鉴基础清洗流程，但需要强化时间语义。
- `src/strategies/ml_bucket_selection.py`：可借鉴 XGB/LGBM/Stacking 和 feature importance 输出，但需拆出防泄漏 pipeline。
- `src/backtest/backtest_engine.py`：可借鉴目标权重回测，但 A 股交易约束需补齐。
- `src/strategies/adaptive_rotation/config_loader.py`：可借鉴 YAML/Pydantic 配置与 config hash。
- 现有 `docs/*_ZH.md`：可作为项目学习与审计说明基础。

## 6. 不应作为当前主线的资产

- `src/strategies/rl_model.py`、DRL 训练脚本和 FinRL 相关策略。
- `src/trading/` 下 Alpaca 下单与账户接口。
- `deploy.sh --mode paper` 和任何自动交易流程。
- 在线 FMP/Yahoo/OpenAI 批量抓取流程。

这些代码不删除，作为扩展路线或历史遗留能力保留。

## 7. 最优先三个缺口

1. A 股离线 point-in-time 数据层和可交易股票池。
2. 防泄漏因子/标签流水线与自动测试。
3. IC/RankIC + 分组回测的标准因子评价模块。

## 8. 推荐下一 Phase

推荐进入 `Phase QR-1：A 股离线研究数据层与防泄漏基线`。

该 Phase 不训练大模型，不联网，不下单。目标是先把数据 schema、样本外时间语义、股票池、复权、交易日、财报披露生效日和最小测试样例固定下来。只有 QR-1 验收通过，才允许进入因子评价和 ML 建模。

