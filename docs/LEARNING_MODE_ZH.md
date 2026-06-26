# Phase 1 学习模式说明

本阶段新增的 `learning/` 是独立中文教学层，不依赖原项目的交易、真实行情、真实大模型或部署入口。

大语言模型（Large Language Model，LLM）
零基础解释：大语言模型是能处理自然语言输入并生成文本输出的模型，本学习层默认只使用离线 Mock，不调用真实模型。

应用程序编程接口（Application Programming Interface，API）
零基础解释：API 是程序连接外部服务的接口，本学习层默认不连接外部 API。

## 安全边界

默认规则：
- 不联网。
- 不读取 `.env`。
- 不调用 OpenAI 或其他收费模型。
- 不调用 Alpaca 或任何券商接口。
- 不下载行情。
- 不训练深度学习模型。
- 不训练强化学习模型。
- 不导入原项目交易模块。

## Windows PowerShell 安装

```powershell
Set-Location D:\FinRL-Trading
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-learning.txt
python -m pytest learning\tests -q
python -m jupyter lab
```

如果本机没有 Python 3.11，可以先用当前 Python 运行教学层，但最终建议按 Python 3.11 验证。

## 在线 Provider

`requirements-learning-online.txt` 只为未来可选在线实验准备。本阶段不安装、不调用、不要求 API Key。

OpenAI 兼容接口（OpenAI-Compatible API）
零基础解释：OpenAI 兼容接口是不同服务商使用类似 OpenAI SDK 格式提供模型服务。

## 声明

所有数据都是合成教学数据。所有结果只用于学习，不构成投资建议，不代表任何策略未来一定赚钱。
