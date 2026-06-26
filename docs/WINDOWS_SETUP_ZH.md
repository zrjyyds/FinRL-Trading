# Windows 环境审计与后续安装建议

## 1. 当前 Windows 环境

结论：当前系统是 Windows 10 + PowerShell 7.5.5，实际 Python 是 3.12.4；用户要求目标优先按 Python 3.11 审计，因此后续建议新建 Python 3.11 虚拟环境。

证据：
- 当前路径：`D:\FinRL-Trading`
- PowerShell：`7.5.5`
- OS：`Microsoft Windows 10.0.19045`
- Python：`3.12.4`
- pip：Anaconda Python 3.12 环境

专业词：虚拟环境（Virtual Environment，venv）。

零基础解释：虚拟环境是给一个项目单独准备的 Python 包安装空间，避免污染系统环境。

## 2. Windows 环境要求

建议：
- Windows 10 或 Windows 11
- Python 3.11.x
- PowerShell 7 或 Windows PowerShell
- Git
- 可选：Visual Studio Build Tools，仅在某些包缺 wheel 时需要
- 不要求 GPU
- 不要求 Docker
- 不要求真实 API Key

零基础解释：GPU 主要用于深度学习训练，基础回测和机器学习可以用 CPU。

## 3. 不推荐直接执行的命令

Phase 0 和零基础第一阶段不推荐：

```powershell
.\deploy.sh
python src\main.py trade
python src\trading\trade_executor.py
python src\trading\alpaca_manager.py
python src\data\data_fetcher.py
python src\strategies\fundamental_portfolio_drl.py
python src\strategies\rl_model.py
pip install -r requirements.txt
```

原因：
- `deploy.sh` 是 Bash 脚本，且可能安装依赖、下载数据、执行 paper 交易。
- 交易脚本可能连接 Alpaca 并提交订单。
- 数据脚本可能联网抓数据或调用 OpenAI。
- DRL 脚本会进行长时间训练。
- 全量 requirements 会安装过多非入门依赖。

专业词：模拟盘（Paper Trading）。

零基础解释：模拟盘不使用真实资金，但仍然会向券商模拟账户提交订单，学习阶段也应避免误触发。

## 4. Linux/macOS 命令对应 PowerShell

| README/脚本命令 | PowerShell 建议 |
|---|---|
| `python3 -m venv venv` | `py -3.11 -m venv .venv` |
| `source venv/bin/activate` | `.\.venv\Scripts\Activate.ps1` |
| `pip install -r requirements.txt` | 先不要全量安装，改用精简依赖 |
| `cp .env.example .env` | `Copy-Item .env.example .env` |
| `./deploy.sh --help` | 不建议在 PowerShell 直接执行 |
| `mkdir -p data/fmp_daily` | `New-Item -ItemType Directory -Force data\fmp_daily` |

专业词：命令行壳（Shell）。

零基础解释：Shell 是接收命令的程序，PowerShell 和 Bash 写法不同。

## 5. Windows 不兼容点

| 问题 | 证据 | 风险 |
|---|---|---|
| Bash 专属脚本 | `deploy.sh` 使用 `#!/usr/bin/env bash`、`set -euo pipefail` | PowerShell 不能直接运行 |
| Linux 命令 | `find`、`grep`、`wc`、`tr`、`mkdir -p` | 需 Git Bash/WSL 或改写 |
| `python3/pip3` | `deploy.sh` 中大量使用 | Windows 常用 `py` 或 `python` |
| Docker apt-get | `Dockerfile` 使用 `apt-get` | 仅 Docker Linux 容器可用 |
| 写死旧路径 | `ml_strategy.py` 中 `D:\Projects\FinRL-Trading-old\...` | 本机不可复现 |
| Web 导入缺失 | `src/web/app.py` 引用不存在的 `create_strategy` | Dashboard 可能启动失败 |
| 多进程训练 | DRL 脚本设置 spawn | Windows 可用但训练复杂 |
| GPU/CUDA | torch 自动检测 CUDA | 基础学习不需要 |

零基础解释：写死路径就是代码只在作者电脑上的某个目录能运行。

## 6. 路径拼接与编码

较好做法：
- 多数核心代码使用 `Path`、`os.path.join`。
- `settings.py` 使用相对路径配置数据目录。

风险：
- `src/strategies/ml_strategy.py` 的 `__main__` 使用绝对 Windows 旧路径。
- `src/trading/alpaca_manager.py` 有部分中文注释显示乱码，可能存在编码保存问题。
- `deploy.sh` 中 Bash 字符串和 heredoc 不适合 PowerShell。

专业词：文件编码（File Encoding）。

零基础解释：文件编码决定中文在文件中如何保存，编码不一致会出现乱码。

## 7. 能否在纯 Windows PowerShell 中运行

| 目标 | 结论 |
|---|---|
| 完成静态学习 | 可以 |
| 查看 CSV | 可以 |
| 运行最小离线回测 | Phase 1 改造后可以 |
| 运行当前 `deploy.sh` | 不建议 |
| 运行 Web | 当前存在导入问题，需要修复后再试 |
| 无 Docker 学习 | 可以 |
| 无 GPU 学习 | 可以 |
| 无 API Key 学习 | 需要离线样例和 Mock |
| 运行历史回测 | 当前需要先准备数据并验证依赖 |

## 8. 后续 Phase 1 推荐安装命令

本阶段不要实际执行，以下仅为建议：

```powershell
cd D:\FinRL-Trading
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install numpy pandas scipy scikit-learn matplotlib requests python-dotenv pydantic pydantic-settings pandas-market-calendars bt pytest
```

如果 `bt` 安装失败，Phase 1 可先用手写最小回测替代。

## 9. 无 API Key 运行方案

建议：
- 使用 `data/fundamental_data_full.csv`
- 使用 `data/sp500_historical_constituents.csv`
- 新增小型离线 `learning/data/sample_prices.csv`
- 新增 Mock LLM Provider
- 所有在线数据源默认关闭

专业词：离线样例数据（Offline Sample Data）。

零基础解释：离线样例数据是不联网也能读取的小数据文件，适合初学者反复练习。

## 10. 常见安装错误

可能问题：
- Python 版本不是 3.11。
- Anaconda 环境和 venv 混用。
- LightGBM 缺少编译环境。
- torch 下载很大或 GPU 版本不匹配。
- `bt` 依赖与 Python 版本兼容问题。
- PowerShell 执行策略阻止激活脚本。

PowerShell 激活脚本若被拦截，可在用户确认后使用：

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

当前未执行任何安装。
