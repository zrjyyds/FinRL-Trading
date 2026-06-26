# 数据源审计

## 1. 全部数据源列表

静态扫描确认或引用的数据源：
- Financial Modeling Prep（FMP）
- Yahoo Finance / yfinance
- Alpaca
- OpenAI
- 本地 CSV
- 本地 SQLite
- WRDS 配置和 README 声明
- Finnhub 依赖声明
- Docker PostgreSQL/Redis 可选服务

未发现真实实现：
- Binance
- Polygon
- Alpha Vantage
- Quandl
- Kaggle
- Hugging Face 数据集

专业词：数据源（Data Source）。

零基础解释：数据源就是股票价格、财报、新闻等数据从哪里来。

## 2. Financial Modeling Prep（FMP）

结论：FMP 是当前核心真实数据源。

证据：
- 文件：`src/data/data_fetcher.py`
- 类：`FMPFetcher`
- 函数：`get_sp500_components`
- 函数：`get_fundamental_data`
- 函数：`get_price_data`
- 函数：`get_news`
- 配置：`src/config/settings.py` 的 `FMPSettings`
- 环境变量：`FMP_API_KEY`

| 审计项 | 结论 |
|---|---|
| 是否需要 API Key | 在线抓取需要 |
| 是否免费 | FMP 通常有免费/付费层，当前无法从代码确认账户方案 |
| 是否会联网 | 会 |
| 是否会自动下载大量数据 | 会，SP500 多股票多端点 |
| 返回字段 | 价格 OHLCV、S&P 500 成分、基本面因子、新闻字段 |
| 是否有缓存 | 有，SQLite `raw_payloads`、`price_data`、`fundamental_data`、`news_articles` |
| 请求失败处理 | 有 try/except，返回空列表或日志警告 |
| 缺失数据处理 | 部分存在 |
| Windows 适合性 | Python requests 可用 |
| 零基础离线适合性 | 不适合在线；适合用已缓存数据 |
| 许可证/商用限制 | 需查看 FMP 条款，当前无法从代码确认 |
| 时间穿越风险 | 财报发布日期和新闻发布时间需严格校验 |

专业词：应用程序编程接口（Application Programming Interface，API）。

零基础解释：API Key 是访问某些数据服务时用来证明身份的密钥。

## 3. Yahoo Finance / yfinance

结论：yfinance 被依赖和多个脚本使用，但不是核心 DataSourceManager 中注册的数据源。

证据：
- 依赖：`requirements.txt` 的 `yfinance>=0.2.0`
- 文件：`deploy.sh` 下载 Adaptive Rotation CSV
- 文件：`src/data/fix_adj_close.py`
- 文件：`src/data/fill_recent_yreturn.py`
- 文件：`src/strategies/ml_bucket_selection.py`

| 审计项 | 结论 |
|---|---|
| 是否需要 API Key | 通常不需要 |
| 是否免费 | 一般免费但非正式 SLA |
| 是否会联网 | 会 |
| 是否会自动下载大量数据 | `deploy.sh` 会批量下载配置中的资产 |
| 返回字段 | OHLCV、调整价格 |
| 是否有缓存 | deploy 下载为 CSV；部分脚本写回 DB |
| 请求失败处理 | 部分 try/except |
| Windows 适合性 | Python 可用 |
| 零基础离线适合性 | 不适合在线；可先准备 CSV |
| 许可证限制 | 需看 Yahoo 使用条款 |
| 时间穿越风险 | 调整价格可能包含后验复权信息，教学中需说明 |

专业词：复权价格（Adjusted Price）。

零基础解释：复权价格会把分红、拆股等影响调整进历史价格里，方便比较长期收益。

## 4. Alpaca

结论：Alpaca 是真实交易和账户数据接口，不是普通行情教学数据源。

证据：
- 文件：`src/trading/alpaca_manager.py`
- 类：`AlpacaManager`
- 函数：`get_account_info`
- 函数：`get_positions`
- 函数：`place_order`
- 函数：`execute_portfolio_rebalance`
- 环境变量：`APCA_API_KEY`、`APCA_API_SECRET`、`APCA_BASE_URL`

| 审计项 | 结论 |
|---|---|
| 是否需要 API Key | 需要 |
| 是否免费 | 账户服务取决于 Alpaca |
| 是否会联网 | 会 |
| 是否会自动下载大量数据 | 账户/订单数据不大；市场数据接口可联网 |
| 返回字段 | 账户、订单、持仓、行情 |
| 是否有缓存 | 订单日志可写 JSON，但账户数据不缓存 |
| 失败处理 | API 错误抛 RuntimeError |
| Windows 适合性 | requests 可用 |
| 零基础离线适合性 | 不适合 |
| 商用/合规限制 | 需遵守 Alpaca 条款 |
| 时间穿越风险 | 主要是实盘/模拟盘误触发风险 |

专业词：券商（Broker）。

零基础解释：券商是接收买卖订单并连接市场的服务商。

## 5. OpenAI

结论：OpenAI 用于新闻情绪分析，可产生费用。

证据：
- 文件：`src/data/data_fetcher.py`
- 函数：`_annotate_sentiment`
- 配置：`OPENAI_API_KEY`、`OPENAI_MODEL`、`OPENAI_REQUEST_TIMEOUT`

| 审计项 | 结论 |
|---|---|
| 是否需要 API Key | 需要 |
| 是否免费 | 通常按用量计费 |
| 是否会联网 | 会 |
| 是否会自动大量调用 | 逐篇新闻调用，缺成本上限 |
| 返回字段 | sentiment、confidence |
| 是否缓存 | 情绪结果写入 `news_articles` |
| 失败处理 | 捕获异常并 debug 日志 |
| Windows 适合性 | Python SDK 可用 |
| 零基础离线适合性 | 不适合，需 Mock |
| 数据上传风险 | 新闻标题和正文发送给 OpenAI |
| 时间穿越风险 | 新闻发布时间必须对齐回测日期 |

专业词：调用成本（API Cost）。

零基础解释：每次调用付费模型都可能按输入和输出 token 计费。

## 6. 本地 CSV

结论：项目有本地 CSV 数据和脚本输出 CSV。

证据：
- 文件：`data/fundamental_data_full.csv`
- 文件：`data/sp500_historical_constituents.csv`
- 文件：`deploy.sh` 写入 `data/fmp_daily/{SYMBOL}_daily.csv`
- 文件：`src/strategies/ml_bucket_selection.py` 输出 predictions/model_results/feature_importance CSV

完成程度：完整存在。

零基础解释：CSV 是最适合初学者打开和检查的表格文本文件。

风险或限制：`data/finrl_trading.7z` 是压缩文件，Phase 0 未解压；当前无法确认内部数据库内容。

## 7. 本地 SQLite

结论：SQLite 是核心缓存和数据存储。

证据：
- 文件：`src/data/data_store.py`
- 类：`DataStore`
- 默认路径：`data/finrl_trading.db`
- 压缩数据：`data/finrl_trading.7z`

完成程度：完整实现。

专业词：本地数据库（Local Database）。

零基础解释：本地数据库像一个电脑里的表格仓库，适合保存很多历史数据。

风险或限制：仓库当前只有压缩 DB，未运行解压或读取数据库。

## 8. WRDS

结论：WRDS 只有配置和文档声明，未发现真实 WRDS 抓取模块。

证据：
- 文件：`src/config/settings.py`
- 类：`WRDSSettings`
- 文件：`.env.example`
- README 声明：FMP / Yahoo / WRDS
- 未发现：`WRDSFetcher`

完成程度：仅配置/文档声明。

零基础解释：WRDS 是常见的学术金融数据库，通常需要学校或机构账号。

## 9. Finnhub

结论：`requirements.txt` 声明了 `finnhub`，但未发现核心代码使用。

证据：
- 文件：`requirements.txt`
- 搜索：未发现 `import finnhub`

完成程度：仅依赖声明。

## 10. 推荐给零基础使用的数据源

推荐顺序：
1. `data/fundamental_data_full.csv`
2. `data/sp500_historical_constituents.csv`
3. Phase 1 新增小型离线 OHLCV CSV
4. Phase 1 新增 Mock 新闻 CSV

不推荐初学阶段使用：
- FMP 在线接口
- OpenAI 在线接口
- Alpaca 账户接口
- `deploy.sh` 自动下载

当前未进入 Phase 1。
