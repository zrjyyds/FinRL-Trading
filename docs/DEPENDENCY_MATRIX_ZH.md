# Python 依赖审计与分层建议

## 1. 总体结论

结论：当前 `requirements.txt` 把数据处理、机器学习、Web、交易、LLM、测试、文档和可选深度学习混在一起。零基础学习阶段不建议一次性安装全部依赖。

证据：
- 文件：`requirements.txt`
- 文件：`setup.py`
- `setup.py` 中 `extras_require` 进一步声明 `stable-baselines3`、`gymnasium` 等 ML 可选依赖。

专业词：依赖（Dependency）。

零基础解释：依赖是项目运行时需要安装的第三方 Python 包。

## 2. 依赖矩阵

| 依赖名称 | 版本 | 类别 | 用途 | 使用位置 | 核心必需 | GPU | 联网 | Windows/Python 3.11 | 安装风险 | 第一阶段可排除 |
|---|---|---|---|---|---|---|---|---|---|---|
| numpy | >=1.24.0 | 核心基础 | 数组计算 | 多数模块 | 是 | 否 | 否 | 适合 | 低 | 否 |
| pandas | >=2.0.0 | 数据处理 | 表格数据 | 多数模块 | 是 | 否 | 否 | 适合 | 低 | 否 |
| scipy | >=1.11.0 | 数据/优化 | 优化、统计 | `ml_strategy.py`、`backtest_engine.py` | 是 | 否 | 否 | 适合 | 中 | 否 |
| scikit-learn | >=1.3.0 | 传统机器学习 | RF、Scaler、MSE | `ml_strategy.py`、`ml_bucket_selection.py` | 是 | 否 | 否 | 适合 | 低 | 否 |
| lightgbm | >=4.0.0 | 传统机器学习 | LGBM 模型 | `ml_bucket_selection.py` | 否 | 否 | 否 | Windows 可能需轮子 | 中 | 是 |
| xgboost | >=2.0.0 | 传统机器学习 | XGB 模型 | `ml_bucket_selection.py` | 否 | 否 | 否 | 适合 | 中/体积大 | 是 |
| matplotlib | >=3.7.0 | 可视化 | 图表 | 回测、DRL | 否 | 否 | 否 | 适合 | 低 | 是 |
| plotly | >=5.15.0 | 可视化/Web | 交互图 | `src/web` | 否 | 否 | 否 | 适合 | 低 | 是 |
| seaborn | >=0.12.0 | 可视化 | 图表 | 依赖声明 | 否 | 否 | 否 | 适合 | 低 | 是 |
| streamlit | >=1.28.0 | Web 页面 | Dashboard | `src/web/app.py` | 否 | 否 | 可能 | 适合 | 中 | 是 |
| yfinance | >=0.2.0 | 数据下载 | Yahoo 数据 | `deploy.sh`、数据修复脚本 | 否 | 否 | 是 | 适合 | 中 | 是 |
| requests | >=2.31.0 | 数据/API | HTTP 请求 | FMP、Alpaca | 是 | 否 | 是 | 适合 | 低 | 否 |
| python-dotenv | >=1.0.0 | 配置 | 读取 .env | settings、Alpaca | 是 | 否 | 否 | 适合 | 低 | 否 |
| alpaca-py | >=0.13.0 | 交易 | Alpaca SDK | 依赖声明，代码主要用 requests | 否 | 否 | 是 | 适合 | 中 | 是 |
| openai | >=1.40.0 | LLM | 新闻情绪分析 | `data_fetcher.py` | 否 | 否 | 是 | 适合 | 中/费用 | 是 |
| pandas-market-calendars | >=4.3.0 | 交易日历 | NYSE 交易日 | `trading_calendar.py`、data_fetcher | 是 | 否 | 否 | 适合 | 中 | 否 |
| bt | >=1.2.0 | 量化回测 | 回测框架 | `backtest_engine.py` | 是 | 否 | 否 | 需验证 | 中 | 否 |
| pydantic | >=2.5.0 | 配置校验 | Settings 模型 | `settings.py` | 是 | 否 | 否 | 适合 | 低 | 否 |
| pydantic-settings | >=2.1.0 | 配置校验 | BaseSettings | `settings.py` | 是 | 否 | 否 | 适合 | 低 | 否 |
| sqlalchemy | >=2.0.0 | 数据库 | SQL 工具 | 依赖声明 | 否 | 否 | 否 | 适合 | 低 | 是 |
| pathlib | >=1.0.1 | 工具 | 路径 | 标准库已有 | 否 | 否 | 否 | 不建议单独装 | 低 | 是 |
| typing-extensions | >=4.8.0 | 工具 | 类型兼容 | 间接 | 否 | 否 | 否 | 适合 | 低 | 是 |
| lxml | >=4.9.0 | 数据读取 | read_html | 依赖声明 | 否 | 否 | 可能 | Windows 轮子通常可用 | 中 | 是 |
| finnhub | >=2.4.19 | 数据下载 | 未发现使用 | 无核心使用 | 否 | 否 | 是 | 适合 | 中 | 是 |
| pytest | >=7.4.0 | 测试 | 测试框架 | 未发现 tests | 否 | 否 | 否 | 适合 | 低 | 是 |
| pytest-cov | >=4.1.0 | 测试 | 覆盖率 | 未发现 tests | 否 | 否 | 否 | 适合 | 低 | 是 |
| black | >=23.0.0 | 开发工具 | 格式化 | 开发 | 否 | 否 | 否 | 适合 | 低 | 是 |
| flake8 | >=6.1.0 | 开发工具 | Lint | 开发 | 否 | 否 | 否 | 适合 | 低 | 是 |
| mypy | >=1.7.0 | 开发工具 | 类型检查 | 开发 | 否 | 否 | 否 | 适合 | 低 | 是 |
| torch | >=2.0.0 | 深度学习 | DRL 后端 | `rl_model.py`、`fundamental_portfolio_drl.py` | 否 | 可选 | 否 | CPU 版可用但大 | 高/体积大 | 是 |
| sphinx | >=7.2.0 | 文档 | 文档生成 | 依赖声明 | 否 | 否 | 否 | 适合 | 低 | 是 |
| setuptools | >=68.0.0 | 打包 | 安装包 | `setup.py` | 是 | 否 | 否 | 适合 | 低 | 否 |
| wheel | >=0.41.0 | 打包 | 构建 wheel | 打包 | 是 | 否 | 否 | 适合 | 低 | 否 |

专业词：图形处理器（Graphics Processing Unit，GPU）。

零基础解释：GPU 常用于加速深度学习训练，但基础量化学习不需要 GPU。

## 3. 重点依赖检查

| 重点依赖 | 当前状态 |
|---|---|
| torch | requirements 中声明，DRL 脚本使用；第一阶段应排除 |
| tensorflow | requirements 未声明，仅 `TF_CPP_MIN_LOG_LEVEL` 痕迹 |
| stable-baselines3 | requirements 未声明，`setup.py` extras 和脚本间接依赖 FinRL |
| ray | 未发现 |
| xgboost | requirements 声明并可选使用 |
| lightgbm | requirements 声明并可选使用 |
| catboost | 未发现 |
| alpaca-py | requirements 声明，但主要交易代码用 requests |
| openai | requirements 声明并真实用于情绪分析 |
| transformers | 未发现 |
| datasets | 未发现 |
| accelerate | 未发现 |
| bitsandbytes | 未发现 |
| streamlit | requirements 声明，Web 使用 |
| sphinx | requirements 声明 |
| jupyter/notebook/ipykernel | requirements 未声明，但 examples 有 ipynb |

专业词：强化学习（Reinforcement Learning，RL）。

零基础解释：强化学习让模型通过奖励和惩罚学习动作，通常训练成本高。

## 4. 依赖冲突和 Windows 风险

风险：
- `pathlib>=1.0.1` 在现代 Python 中通常不需要安装。
- `torch` 体积大，Windows CPU/GPU 安装路径不同。
- `lightgbm` 在部分 Windows 环境可能遇到编译或 OpenMP 问题。
- `bt` 依赖链需要在 Python 3.11 单独验证。
- `alpaca-py` 和代码中 `requests` 手写 Alpaca API 并存，可能造成认知混乱。
- `setup.py` 过滤 torch/tensorflow 的逻辑与 `requirements.txt` 不一致。

零基础解释：依赖冲突是不同包要求的版本互相不兼容，导致安装或运行失败。

## 5. 建议依赖分层

本阶段只提出拆分建议，不实际拆分文件。

### requirements-core.txt

```text
numpy
pandas
scipy
scikit-learn
requests
python-dotenv
pydantic
pydantic-settings
pandas-market-calendars
bt
setuptools
wheel
```

### requirements-quant.txt

```text
yfinance
bt
pandas-market-calendars
lxml
```

### requirements-ml.txt

```text
scikit-learn
xgboost
lightgbm
```

### requirements-llm.txt

```text
openai
```

### requirements-deep-learning.txt

```text
torch
gymnasium
stable-baselines3
finrl
```

注意：`finrl` 当前未在 requirements 中声明，但 RL 代码导入它。

### requirements-trading.txt

```text
alpaca-py
requests
python-dotenv
```

### requirements-dev.txt

```text
pytest
pytest-cov
black
flake8
mypy
```

### requirements-docs.txt

```text
sphinx
sphinx-rtd-theme
myst-parser
```

## 6. 第一阶段最小环境建议

建议 Phase 1 只安装：

```text
numpy
pandas
scikit-learn
matplotlib
requests
python-dotenv
pydantic
pydantic-settings
pandas-market-calendars
bt
pytest
```

不安装：
- `torch`
- `openai`
- `alpaca-py`
- `streamlit`
- `xgboost`
- `lightgbm`
- `sphinx`

当前未进入 Phase 1。
