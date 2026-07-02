# A 股多因子研究规范

本规范定义后续主线研究的最小技术标准。任何因子、模型和回测结果，只有满足本规范，才适合进入作品集展示。

## 1. 数据范围

默认研究对象：

- 市场：A 股。
- 频率：日频行情，月频或周频调仓，季度/年度财务数据。
- 策略类型：中低频 long-only 或 long-only 相对基准增强。
- 当前不纳入：实盘交易、模拟盘交易、融资融券、期货、期权、高频订单簿。

## 2. 必需数据表

### 2.1 交易日历 `calendar`

| 字段 | 说明 |
|---|---|
| `trade_date` | 交易日 |
| `is_month_end` | 是否月末调仓候选日 |
| `next_trade_date` | 下一交易日 |

### 2.2 动态股票池 `universe`

| 字段 | 说明 |
|---|---|
| `trade_date` | 生效交易日 |
| `ticker` | 股票代码 |
| `is_member` | 当日是否属于研究股票池 |
| `is_st` | 是否 ST 或风险警示 |
| `listed_days` | 上市天数 |
| `is_delisted` | 是否已退市 |

要求：任何日期只能看到该日期已经生效的股票池，不能使用未来成分。

### 2.3 行情与交易状态 `prices`

| 字段 | 说明 |
|---|---|
| `trade_date` | 交易日 |
| `ticker` | 股票代码 |
| `open`、`high`、`low`、`close` | 未复权价格 |
| `preclose` | 前收盘价 |
| `volume`、`amount` | 成交量和成交额 |
| `adj_factor` | 复权因子 |
| `adj_close` | 复权收盘价 |
| `is_suspended` | 是否停牌 |
| `is_limit_up`、`is_limit_down` | 是否涨停/跌停 |
| `is_tradable` | 是否可成交 |

要求：收益计算使用明确的复权价格；成交模拟使用真实可成交价格和交易状态。

### 2.4 财务数据 `financials`

| 字段 | 说明 |
|---|---|
| `ticker` | 股票代码 |
| `report_period` | 报告期 |
| `announce_date` | 公告日期 |
| `effective_trade_date` | 公告后可用于交易的第一交易日 |
| `field_name` | 财务字段 |
| `value` | 字段值 |

要求：财务字段只能在 `effective_trade_date` 及之后使用。没有公告日期的财务字段不得进入正式研究。

### 2.5 行业与市值 `exposures`

| 字段 | 说明 |
|---|---|
| `trade_date` | 交易日 |
| `ticker` | 股票代码 |
| `industry` | 行业分类 |
| `total_mcap` | 总市值 |
| `float_mcap` | 流通市值 |
| `log_mcap` | 市值对数 |

要求：行业分类需要版本说明；市值字段必须与交易日对齐。

## 3. 因子定义

每个因子必须有元数据：

| 字段 | 说明 |
|---|---|
| `factor_id` | 因子唯一名称 |
| `category` | value、quality、momentum、volatility、liquidity、growth 等 |
| `direction` | 值越大预期收益越高，或越低越好 |
| `frequency` | 日频、周频、月频、季频 |
| `lookback_window` | 回看窗口 |
| `required_fields` | 依赖字段 |
| `effective_lag` | 数据滞后规则 |
| `missing_policy` | 缺失处理 |
| `winsor_policy` | 去极值规则 |
| `neutralize_policy` | 中性化规则 |

## 4. 因子处理流水线

标准顺序：

1. 根据 `trade_date` 和 point-in-time 股票池取当日可用样本。
2. 计算原始因子。
3. 删除不可交易、停牌、上市天数不足和缺少关键字段的样本。
4. 去极值。
5. 标准化。
6. 行业中性化。
7. 市值中性化。
8. 生成最终因子长表。

## 5. 去极值规则

允许的规则：

- 按交易日横截面 1%/99% 分位数截尾。
- MAD 去极值。
- 只使用训练窗口估计边界，再应用到验证/测试窗口。

禁止的规则：

- 使用全样本、全历史、包含测试期的分位数边界处理训练期。
- 先合并标签后再基于未来标签筛样本。

## 6. 标准化规则

默认使用按交易日横截面 z-score：

```text
factor_z = (factor - mean_cross_section) / std_cross_section
```

要求：

- 每个 `trade_date` 独立处理。
- 标准化前后保留样本数量记录。
- 当截面样本过少或方差为 0 时，该日期因子标记为不可用。

## 7. 行业中性化

默认方法：

```text
factor_z = industry_dummies + residual
neutralized_factor = residual
```

要求：

- 每个交易日单独回归。
- 行业样本过少时可合并为 Other 或跳过该日期。
- 输出中记录中性化前后的行业暴露。

## 8. 市值中性化

默认方法：

```text
factor_z = beta0 + beta1 * log_mcap + residual
neutralized_factor = residual
```

可与行业中性化合并：

```text
factor_z = industry_dummies + log_mcap + residual
```

要求：

- `log_mcap` 必须来自当日或当时已知数据。
- 中性化后应检查因子与市值的截面相关性是否下降。

## 9. 标签定义

默认标签：

```text
label_1m = adj_close(t + holding_window) / adj_close(t + execution_lag) - 1
```

要求：

- 因子日期为 `t`。
- 成交日最早为 `t + 1` 或下一个可交易日。
- 标签收益窗口必须晚于因子可见时间。
- 停牌、涨跌停、无法成交样本需单独处理。

## 10. IC 和 RankIC

每个因子至少输出：

- 月度 Pearson IC。
- 月度 Spearman RankIC。
- IC 均值、标准差、ICIR。
- IC t 值。
- IC 胜率。
- 覆盖率。

缺失值处理必须先于 IC 计算，并在结果中记录。

## 11. 分组回测

默认规则：

- 每个调仓日按因子值分成 5 组或 10 组。
- 组内等权。
- 下一期持有收益按样本外收益计算。
- 输出每组年化收益、波动、最大回撤、换手率。
- 输出 Top-Bottom 或 Top-Benchmark 差值。

禁止：

- 用全历史因子表现反向调整因子方向后再报告原始结果。
- 反复查看测试期分组收益后调整处理规则。

## 12. 机器学习特征矩阵

机器学习训练集应包含：

- `trade_date`
- `ticker`
- 因子特征
- 行业和市值暴露
- 样本权重，可选
- 标签 `future_return`

强制要求：

- train、valid、test 按日期切分。
- 所有 transformer 只 fit 训练窗口。
- 验证集用于调参，测试集只做最终报告。
- 输出每次实验的数据版本、参数、随机种子和 git commit。

## 13. 模型归因

XGBoost/LightGBM 至少输出：

- gain/split feature importance。
- permutation importance 或 SHAP 近似解释。
- 不同时间段的特征重要性稳定性。
- 正负样本或 top/bottom 组合的特征暴露对比。

## 14. 最小验收样例

后续每个因子模块必须支持一个极小离线样例：

- 3 到 5 只股票。
- 至少 6 个交易日。
- 至少 2 个调仓日。
- 至少 1 个停牌样本。
- 至少 1 个涨停或跌停样本。
- 至少 1 条财报公告日期晚于报告期的数据。

该样例用于证明没有未来函数、股票池泄漏、财报披露日泄漏和成交约束错误。

