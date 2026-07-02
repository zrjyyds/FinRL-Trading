# 量化研究作品集蓝图

本蓝图描述项目完成后的目标形态。目标不是展示“能下单”，而是展示“能严谨完成一个可复现的量化研究项目”。

## 1. 项目一句话定位

一个面向量化研究实习岗位的 A 股中低频多因子选股研究项目：从 point-in-time 数据层、因子清洗、IC/RankIC、分组回测，到 XGBoost/LightGBM 样本外建模、组合构建、交易成本和归因报告。

## 2. 推荐作品集结构

```text
FinRL-Trading/
  configs/
    research/
      a_share_factor_baseline.yaml
      xgb_lgbm_oos.yaml
  data/
    README_DATA_ZH.md
    sample_a_share/
      calendar.csv
      universe.csv
      prices.csv
      financials.csv
      exposures.csv
      tradability.csv
  docs/
    TARGET_COMPANY_SKILL_MATRIX_ZH.md
    TARGET_COMPANY_GAP_ANALYSIS_ZH.md
    QUANT_RESEARCH_ROADMAP_ZH.md
    FACTOR_RESEARCH_SPEC_ZH.md
    BACKTEST_ANTI_LEAKAGE_CHECKLIST_ZH.md
    PORTFOLIO_PROJECT_BLUEPRINT_ZH.md
    RESEARCH_REPORT_ZH.md
  reports/
    experiments/
      run_id/
        config.yaml
        summary.csv
        factor_ic.csv
        group_backtest.csv
        portfolio_metrics.csv
        attribution.csv
        figures/
  src/
    research/
      data_schema.py
      factor_pipeline.py
      factor_eval.py
      ml_oos.py
      portfolio_backtest.py
      attribution.py
      report.py
  tests/
    research/
      test_no_lookahead.py
      test_point_in_time_universe.py
      test_factor_pipeline.py
      test_ic_rankic.py
      test_portfolio_constraints.py
```

说明：以上是目标蓝图，不代表本轮已经创建这些代码目录。本轮只创建规划文档。

## 3. 最终展示能力

| 展示模块 | 面试官能看到什么 |
|---|---|
| 数据层 | 你知道量化研究最先要解决 point-in-time 和数据质量 |
| 因子工程 | 你会做去极值、标准化、行业/市值中性化，而不只是堆技术指标 |
| 因子评价 | 你会用 IC、RankIC、分组回测判断因子是否有效 |
| 机器学习 | 你会用 XGBoost/LightGBM 做严格样本外横截面预测 |
| 回测 | 你理解交易成本、停牌、涨跌停、换手和组合约束 |
| 归因 | 你能解释收益来自哪里，而不是只给一张净值曲线 |
| 工程化 | 你能用配置、测试、结果注册和报告生成保证复现 |

## 4. 主线实验设计

### 4.1 Baseline 1：单因子研究

- 输入：A 股离线价格、股票池、行业、市值、基础财务字段。
- 因子：动量、反转、波动、换手、估值、盈利质量。
- 输出：IC、RankIC、分组收益、因子覆盖率。
- 目标：证明研究流程正确，不追求收益最大化。

### 4.2 Baseline 2：线性多因子

- 输入：通过 QR-3 筛选后的因子池。
- 方法：等权因子、IC 加权因子、Ridge regression。
- 输出：多因子 score、分组回测、组合回测。
- 目标：建立可解释 baseline。

### 4.3 Baseline 3：XGBoost/LightGBM

- 输入：标准化与中性化后的因子矩阵。
- 方法：按时间切分训练、验证、测试；滚动训练。
- 输出：OOS 预测分数、feature importance、SHAP 或替代归因。
- 目标：展示机器学习能力和过拟合控制。

### 4.4 Portfolio：组合构建

- 输入：因子或模型 score。
- 方法：top-N、行业约束、市值约束、单票上限、换手约束。
- 成本：佣金、印花税、滑点、无法成交。
- 输出：净值、超额收益、风险指标、归因。

## 5. 结果报告模板

最终报告建议包含：

1. 研究问题。
2. 数据范围与 point-in-time 规则。
3. 因子定义和处理流程。
4. 防泄漏检查结果。
5. IC/RankIC 和分组回测。
6. 模型训练与样本外协议。
7. 组合构建与交易成本。
8. 绩效指标与归因。
9. 失败案例和限制。
10. 下一步改进。

## 6. 不展示或弱展示内容

当前阶段不把以下内容作为主线卖点：

- 强化学习收益。
- 自动下单和 Alpaca 交易。
- OpenAI 新闻情绪。
- 在线抓取数据的规模。
- 未经防泄漏测试的回测曲线。

## 7. 强化学习扩展路线

原 FinRL/DRL 代码保留，但重新定位为：

- 主线完成后的扩展实验。
- 用于比较传统多因子组合和 RL 权重调整。
- 只允许离线、小规模、无交易环境。
- 必须与等权、风险平价、均值方差、ML score 组合进行对照。

不允许：

- 把 RL 作为当前主线。
- 用 RL 回测收益替代因子研究闭环。
- 运行耗时训练作为普通验收步骤。
- 连接 Alpaca 或发送订单。

## 8. 推荐 README 展示口径

后续 README 可调整为：

```text
本项目从 FinRL-Trading 代码库出发，保留原有强化学习与交易模块作为扩展能力，
当前主线聚焦 A 股中低频多因子选股研究。项目强调 point-in-time 数据处理、
防止未来函数、IC/RankIC、分组回测、XGBoost/LightGBM 样本外建模、
组合约束、交易成本和归因报告。
```

本轮不修改 README，只记录推荐口径。

## 9. 作品集验收标准

第一版作品集应满足：

- 能离线运行最小样例测试。
- 有明确数据 schema 和防泄漏清单。
- 有至少 10 个基础因子。
- 有 IC/RankIC 和分组回测。
- 有 XGBoost/LightGBM OOS 对比。
- 有交易成本后的组合净值。
- 有模型归因和绩效归因。
- 有一份完整研究报告。

## 10. 推荐下一 Phase

推荐下一 Phase 是 `Phase QR-1：A 股离线研究数据层与防泄漏基线`。

优先完成可信数据层，再做因子、模型和组合。否则后续收益结果即使好看，也难以解释和防守。

