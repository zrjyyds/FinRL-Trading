# 安全与交易风险审计

## 1. 总体结论

项目真实包含 Alpaca 下单、组合再平衡、账户查询、订单日志、paper 模式部署脚本和 Web 下单表单。零基础学习阶段必须默认禁用所有交易入口。

专业词：实盘交易（Live Trading）。

零基础解释：实盘交易会使用真实账户和真实资金买卖资产。

## 2. 实盘交易入口

| 文件 | 类/函数 | 如何被调用 | 默认是否启用 | 风险等级 |
|---|---|---|---|---|
| `src/trading/alpaca_manager.py` | `AlpacaManager.place_order` | 代码直接调用 | 否，但无全局禁用 | 严重 |
| `src/trading/alpaca_manager.py` | `execute_portfolio_rebalance` | 权重再平衡 | 否，但可被脚本调用 | 严重 |
| `src/trading/trade_executor.py` | `TradeExecutor.execute_strategy` | `python src/trading/trade_executor.py` 或导入 | 否 | 严重 |
| `src/main.py` | `trade` 命令 | `python src/main.py trade` | 用户触发 | 严重 |
| `src/web/app.py` | Live Trading 表单 | Streamlit 页面点击 | 用户触发 | 高 |
| `deploy.sh` | `--mode paper` | Bash 脚本 | 用户触发 | 高 |

证据：
- 文件：`src/trading/alpaca_manager.py`
- 函数：`place_order`
- 函数：`place_orders_batch`
- 函数：`execute_portfolio_rebalance`
- 文件：`src/trading/trade_executor.py`
- 文件：`deploy.sh`
- 文件：`src/web/app.py`

零基础解释：下单入口是任何可能向券商发送买入或卖出请求的代码。

## 3. 模拟盘交易入口

结论：`deploy.sh --mode paper` 会生成信号后连接 Alpaca paper 账户；如果未传 `--dry-run`，会调用 `execute_portfolio_rebalance`。

证据：
- 文件：`deploy.sh`
- 片段：`--mode paper`
- 片段：`manager.execute_portfolio_rebalance(... dry_run=dry_run ...)`
- 检查：如果 `account.is_paper` 为 False 会拒绝

完成程度：完整实现。

风险等级：高。

零基础解释：模拟盘虽然不花真钱，但会真实改变模拟账户持仓，初学阶段也应避免。

## 4. 危险函数清单

绝对不能在学习阶段调用：
- `AlpacaManager.place_order`
- `AlpacaManager.place_orders_batch`
- `AlpacaManager.cancel_order`
- `AlpacaManager.cancel_all_orders`
- `AlpacaManager.execute_portfolio_rebalance`
- `TradeExecutor.execute_strategy`
- `TradeExecutor.execute_portfolio_rebalance`
- `create_trade_executor_from_env`
- `create_alpaca_account_from_env`
- `performance_analyzer.main`

风险等级：严重。

专业词：组合再平衡（Portfolio Rebalance）。

零基础解释：组合再平衡是把当前持仓调整到目标权重，可能产生一批买卖订单。

## 5. 危险脚本清单

绝对不能在学习阶段运行：
- `deploy.sh`
- `python src/main.py trade`
- `python src/trading/trade_executor.py`
- `python src/trading/alpaca_manager.py`
- `python src/trading/performance_analyzer.py`
- `python src/data/data_fetcher.py`
- `python src/data/fetch_and_store_fundamentals.py`
- `python src/data/backfill_historical_sp500.py`
- `python src/data/fix_adj_close.py`
- `python src/data/fill_recent_yreturn.py`
- `python src/strategies/fundamental_portfolio_drl.py`
- `python src/strategies/rl_model.py`

理由：
- 可能联网。
- 可能写数据。
- 可能调用 OpenAI。
- 可能调用 Alpaca。
- 可能训练模型。

## 6. API Key 风险

结论：`.env` 已被 `.gitignore` 忽略，存在 `.env.example`，未在静态扫描中发现真实密钥内容。

证据：
- 文件：`.gitignore`
- 行为：忽略 `.env`
- 文件：`.env.example`
- 文件：`src/config/settings.py`
- 类型：`SecretStr`

完成程度：部分实现。

风险等级：中。

零基础解释：API Key 像账号密码一样，泄漏后别人可能使用你的服务额度或账户。

## 7. 绝对不能配置的实盘环境变量

学习阶段不应配置：
- `APCA_API_KEY`
- `APCA_API_SECRET`
- `APCA_BASE_URL` 指向 live trading
- `APCA_PAPER1_API_KEY`
- `APCA_PAPER1_API_SECRET`
- `APCA_PAPER2_API_KEY`
- `APCA_PAPER2_API_SECRET`
- `OPENAI_API_KEY`
- `FMP_API_KEY`
- `WRDS_PASSWORD`

尤其危险：
- `APCA_BASE_URL=https://api.alpaca.markets`

风险等级：严重。

## 8. 日志泄漏风险

结论：项目会记录订单和执行结果到 JSON，可能包含账户名、订单状态、标的、数量和目标权重；未发现日志脱敏机制。

证据：
- 文件：`src/trading/trade_executor.py`
- 函数：`_log_execution`
- 函数：`_log_rebalance`
- 配置：`TRADING_ORDER_LOG_PATH=./logs/orders`
- 文件：`deploy.sh` 写 `execution_{date}.json`

风险等级：中。

专业词：日志脱敏（Log Redaction）。

零基础解释：日志脱敏是把敏感字段隐藏，避免文件被别人看到后泄密。

## 9. 大语言模型费用风险

结论：OpenAI 新闻情绪分析没有成本上限和 token 统计。

证据：
- 文件：`src/data/data_fetcher.py`
- 函数：`_annotate_sentiment`
- 参数：`max_tokens=60`
- 未发现：cost tracking

风险等级：中。

## 10. 数据上传风险

可能上传到第三方：
- FMP：股票代码、日期请求。
- Yahoo Finance：股票代码、日期请求。
- OpenAI：新闻标题和正文。
- Alpaca：订单、账户请求、持仓请求。

未发现上传本地任意文件的代码。

风险等级：中。

## 11. 自动下单风险

结论：`trade_executor.py` 的脚本入口会先 dry-run，再根据市场是否开放和 `USE_OPG` 环境变量决定是否提交。

证据：
- 文件：`src/trading/trade_executor.py`
- 逻辑：`if plan.get("market_open")` 后再次调用 `execute_portfolio_rebalance`
- 逻辑：`USE_OPG=true` 时可提交 OPG

风险等级：严重。

专业词：开盘订单（On-the-Open Order，OPG）。

零基础解释：OPG 是在市场开盘时成交的订单类型，可能在你不看屏幕时执行。

## 12. 模型错误和回测误导风险

风险：
- 模型可能过拟合历史数据。
- 回测缺少滑点、停牌、涨跌停、成交失败。
- README 的收益图不能静态确认复现。
- LLM 情绪若未来接入交易，可能被幻觉或提示词注入影响。

风险等级：高。

## 13. 零基础安全运行边界

允许：
- 阅读代码。
- 阅读 CSV。
- 阅读文档。
- 运行纯离线小脚本。
- 运行明确不联网、不训练、不下单的单元测试。

禁止：
- 配置真实 API Key。
- 运行交易脚本。
- 运行 `deploy.sh`。
- 运行 OpenAI 情绪分析。
- 运行 DRL 训练。
- 批量下载数据。

## 14. 建议安全开关

Phase 1 建议新增：
- `FINRL_LEARNING_MODE=true`
- `FINRL_DISABLE_TRADING=true`
- `FINRL_DISABLE_NETWORK=true`
- `FINRL_DISABLE_LLM=true`
- `FINRL_MAX_ORDER_VALUE=0`
- `FINRL_REQUIRE_CONFIRMATION=true`
- `FINRL_ALLOWED_DATA_MODE=offline`

所有下单函数入口处应检查：

```text
如果 FINRL_DISABLE_TRADING=true，则直接抛出异常，不允许 dry-run 之外的任何订单。
```

当前未进入 Phase 1。
