# Phase 0 项目审计总报告

## 1. 项目基本信息

结论：当前项目路径为 `D:\FinRL-Trading`，项目名在 `README.md` 中写为 FinRL-X / FinRL Trading，真实代码是一个以量化交易、机器学习选股、回测、自适应轮动和 Alpaca 交易接口为核心的研究型代码库。

证据：
- 文件：`README.md`
- 文件：`setup.py`
- 包名：`finrl_trading`
- 入口声明：`setup.py` 的 `entry_points`

完成程度：部分实现。

零基础解释：项目基本信息说明“这个项目是什么、放在哪里、通过什么入口运行”。

风险或限制：README 的描述比当前代码更完整，不能只按宣传判断功能。

## 2. 当前环境与 Git 状态

结论：
- 当前目录：`D:\FinRL-Trading`
- 当前 Git 分支：`master`
- 最近提交：`e65d6f0 Update ml_bucket_selection.py`
- Phase 0 开始前工作区：干净，`git status --short` 无输出
- 当前 Python：`Python 3.12.4`
- 当前 pip：来自 `D:\jupyter\anaconda\Lib\site-packages\pip`
- PowerShell：`7.5.5`
- 操作系统：`Microsoft Windows 10.0.19045`

证据：
- 命令：`Get-Location`
- 命令：`git branch --show-current`
- 命令：`git log -1 --oneline`
- 命令：`python --version`
- 命令：`python -m pip --version`
- 命令：`$PSVersionTable`

完成程度：已确认。

零基础解释：Git 状态用于确认审计开始前项目是否已有别人改过的文件。

风险或限制：用户要求优先按 Python 3.11 审计，但当前实际环境是 Python 3.12.4，后续安装和运行需要单独验证 Python 3.11。

## 3. 一级目录与缺失目录

已存在：
- `data/`
- `docs/`
- `examples/`
- `figs/`
- `src/`
- `.env.example`
- `.gitignore`
- `deploy.sh`
- `Dockerfile`
- `docker-compose.yml`
- `requirements.txt`
- `setup.py`
- `README.md`
- `ML_STOCK_SELECTION.md`

不存在：
- `.github/`
- `tests/`
- `notebooks/`
- `scripts/`
- 根目录 `config/`
- 根目录 `configs/`
- 根目录 `deployment/`
- 根目录 `trading/`
- 根目录 `backtest/`
- 根目录 `agents/`
- 根目录 `llm/`
- 根目录 `nlp/`
- 根目录 `model/`
- 根目录 `models/`
- `pyproject.toml`
- `setup.cfg`
- `environment.yml`
- `poetry.lock`
- `uv.lock`
- `package.json`

证据：
- 命令：`rg --files`
- 命令：`Test-Path ...`

完成程度：已确认。

零基础解释：目录结构能帮助学习者知道代码从哪里开始看。

## 4. 项目真实定位

结论：当前项目更像“研究代码 + 示例系统 + 部分可运行工具”的集合，不是一个在 Windows 上开箱即用的完整生产交易系统。

证据：
- `src/main.py` 提供 `dashboard/backtest/trade/data/config` 命令。
- `src/web/app.py` 引用 `create_strategy` 和 `EqualWeightStrategy`，但 `src/strategies/base_strategy.py` 没有这些定义。
- `README.md` 声称 FMP、Yahoo Finance、WRDS、LLM sentiment、SQLite cache、Alpaca multi-account，但真实数据源管理器只注册 `FMPFetcher`。
- `requirements.txt` 声明 `openai`，真实调用在 `src/data/data_fetcher.py` 的新闻情绪分析路径中。

完成程度：部分实现。

零基础解释：研究代码通常能展示思路，但不一定所有入口都能直接运行。

风险或限制：学习者如果按 README 一键运行，可能遇到依赖、路径、数据、API Key 和下单风险。

## 5. 已实现功能总览

已在代码中实现：
- FMP 数据源封装：`src/data/data_fetcher.py` 的 `FMPFetcher`
- SQLite 本地存储：`src/data/data_store.py` 的 `DataStore`
- 基本面和价格表结构：`DataStore._init_database`
- 新闻缓存表：`news_articles`、`news_fetch_log`
- OpenAI 新闻情绪分析：`FMPFetcher._annotate_sentiment`
- 传统机器学习选股：`src/strategies/ml_strategy.py`、`src/strategies/ml_bucket_selection.py`
- 自适应多资产轮动：`src/strategies/adaptive_rotation/`
- `bt` 回测引擎：`src/backtest/backtest_engine.py`
- Alpaca 下单封装：`src/trading/alpaca_manager.py`
- 交易执行器：`src/trading/trade_executor.py`
- Streamlit 页面雏形：`src/web/app.py`

专业词：回测（Backtesting）。

零基础解释：回测就是用历史数据模拟策略过去会赚多少钱，但它不是未来收益保证。

## 6. 部分实现功能

部分实现：
- Web Dashboard：页面存在，但部分导入对象缺失。
- Yahoo Finance：依赖和脚本中使用 `yfinance`，但核心 `DataSourceManager` 没有注册 YahooFetcher。
- WRDS：配置存在，真实数据源实现未发现。
- 深度强化学习：存在训练脚本，但依赖外部 `finrl` 包和本地数据路径，且训练步数较大。
- LLM：只实现新闻情绪分析辅助，不是完整大语言模型交易系统。

专业词：大语言模型（Large Language Model，LLM）。

零基础解释：大语言模型是能读写自然语言文本的模型，例如用于分析新闻情绪。

## 7. 仅文档声明或依赖声明功能

仅文档或依赖声明：
- README 中的 LLM-ready 和 agentic AI 架构，目前没有完整智能体交易系统。
- README 中的 WRDS 数据源，当前代码未发现 WRDSFetcher。
- `requirements.txt` 中的 `finnhub`，未发现核心使用位置。
- `setup.py` extras 中的 `stable-baselines3`，主 requirements 未包含，真实 RL 脚本却导入外部 FinRL。

专业词：智能体（Agent）。

零基础解释：智能体通常指能根据任务自主调用工具或做决策的软件组件。

## 8. 未实现或无法确认功能

未发现完整实现：
- 本地大型语言模型推理
- 检索增强生成（Retrieval-Augmented Generation，RAG）
- 向量数据库（Vector Database）
- 结构化 JSON Schema 校验
- Function calling / tool calling 框架
- 行业中性化的严格统计实现
- 期货数据和期货保证金
- 加密货币数据
- 宏观经济数据
- 财报文本分析和公告分析
- 实盘交易二次确认和全局安全开关
- 单元测试目录

零基础解释：未发现实现表示静态代码扫描没有看到对应入口、类或函数。

## 9. 主要运行入口

入口：
- 命令行主入口：`src/main.py`
- 自适应轮动入口：`src/strategies/run_adaptive_rotation_strategy.py`
- ML 分桶选股入口：`src/strategies/ml_bucket_selection.py`
- 基本面数据抓取：`src/data/fetch_and_store_fundamentals.py`
- 回测引擎脚本入口：`src/backtest/backtest_engine.py`
- 交易执行脚本入口：`src/trading/trade_executor.py`
- Alpaca 管理脚本入口：`src/trading/alpaca_manager.py`
- Web 页面入口：`src/web/app.py`
- Bash 部署入口：`deploy.sh`

风险等级最高的入口：
- `deploy.sh --mode paper`
- `python src/trading/trade_executor.py`
- `python src/main.py trade`
- `src/web/app.py` 的 Live Trading 下单表单

## 10. Windows 兼容性结论

结论：基础静态学习可以在 Windows 上完成；但 `deploy.sh` 是 Bash 脚本，使用 `python3/pip3/find/grep/date/mkdir -p` 等 Linux/macOS 风格命令，不适合直接在纯 PowerShell 中执行。

证据：
- 文件：`deploy.sh`
- 文件：`Dockerfile`
- 文件：`README.md`

完成程度：Windows 支持不完整。

零基础解释：PowerShell 和 Bash 是两种不同命令行，命令写法不完全一样。

## 11. 零基础适用性结论

结论：项目适合作为“量化金融 + 大语言模型”双线学习项目的底座，但不适合作为零基础第一天直接运行的项目。需要 Phase 1 增加独立 `learning/` 教学层、离线样例数据、Mock LLM、禁交易安全开关和精简依赖。

专业词：模拟模型（Mock Model）。

零基础解释：Mock 模型是不调用真实付费服务、只返回固定或规则化结果的假模型。

## 12. 总体审计结论

当前项目真实包含量化数据、机器学习、回测、轮动策略、交易执行和有限 LLM 情绪分析能力，但工程完整性、Windows 入口、安全隔离、测试覆盖和教学友好性不足。

当前未进入 Phase 1。
