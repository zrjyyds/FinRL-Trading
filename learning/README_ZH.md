# 大语言模型 + 量化金融同步入门

这套课程学习如何同时理解量化金融和大语言模型（Large Language Model，LLM）。
零基础解释：大语言模型是能处理文字输入并生成文字输出的模型，本课程默认使用离线 Mock 模型。

## 为什么两条线可以同时学

量化金融需要把价格、新闻、财报等信息变成数字；自然语言处理（Natural Language Processing，NLP）可以把新闻文字变成结构化信号。
零基础解释：NLP 是让程序处理人类语言文本的技术。

本课程每一课都包含：
- 一个量化金融知识点。
- 一个大语言模型知识点。
- 一个离线可运行实验。
- 一个可观察输出或图表。

## 八课顺序

| 课程 | 量化知识 | 大语言模型知识 |
|---|---|---|
| 01 市场数据与输入输出 | 价格、股票代码、OHLCV | Prompt、消息结构、Token |
| 02 做多做空与结构化输出 | 买入、卖出、做多、做空 | JSON、JSON Schema、Pydantic |
| 03 收益风险与新闻情绪分类 | 收益率、波动率、最大回撤 | 情绪分析、Mock Provider |
| 04 回测时间轴与新闻时间对齐 | 信号日、成交日、未来数据泄漏 | Context Window、available_at |
| 05 动量因子与提示词工程 | 20 日动量、横截面排序 | Prompt Engineering、Temperature |
| 06 情绪因子与大模型风险 | 情绪因子、滚动聚合 | Hallucination、Prompt Injection |
| 07 动量情绪联合策略 | 月度调仓、费用、滑点 | Provider 边界、模型不直接交易 |
| 08 消融实验与综合评价 | 消融实验、指标对比 | RAG 概念、TF-IDF 检索 |

开盘价、最高价、最低价、收盘价和成交量（Open, High, Low, Close and Volume，OHLCV）
零基础解释：OHLCV 是描述一天交易行情的五个基础字段。

## Windows PowerShell 环境安装

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

不需要 WSL、Docker、Git Bash、GPU 或 API Key。

## 数据声明

所有数据都是教学用合成数据。AAA、BBB、CCC、DDD、EEE 不是投资建议，也不是可交易建议。

## 安全声明

本课程不执行真实交易，不执行模拟盘交易，不连接券商接口，不调用真实大模型。

应用程序编程接口（Application Programming Interface，API）
零基础解释：API 是程序连接外部服务的接口，本课程默认不调用外部 API。

Codex 登录不等于项目拥有 OpenAI API Key。未来如需接入 OpenAI 兼容接口，需要用户显式配置环境变量，并保持默认关闭。

## 遇到错误如何检查解释器

```powershell
python --version
py -0p
python -c "import sys; print(sys.executable)"
```

学完后可以进入下一阶段：把离线 Mock LLM 替换成可选在线 Provider、扩展更多因子、增加更严格的回测测试。
