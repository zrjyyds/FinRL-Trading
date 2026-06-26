# 大语言模型与自然语言处理模块审计

## 1. 是否真实使用大语言模型

结论：项目真实使用大语言模型（Large Language Model，LLM）的范围仅限于 FMP 新闻情绪分析，未发现完整 LLM 交易智能体、检索增强生成或本地模型推理系统。

证据：
- 文件：`src/data/data_fetcher.py`
- 类：`FMPFetcher`
- 函数：`_init_sentiment_settings`
- 函数：`_get_openai_client`
- 函数：`_annotate_sentiment`
- 函数：`_parse_sentiment_response`
- 配置：`src/config/settings.py` 的 `OpenAISettings`
- 依赖：`requirements.txt` 的 `openai>=1.40.0`

完成程度：部分实现。

零基础解释：大语言模型可以读取新闻文字并输出“正面、中性、负面”等判断。

## 2. 支持的模型提供商

| 提供商 | 是否支持 | 证据 | 完成程度 | 说明 |
|---|---|---|---|---|
| OpenAI | 是 | `from openai import OpenAI`，`OpenAI(api_key=...)` | 部分实现 | 只用于新闻情绪 |
| OpenAI 兼容接口 | 未发现 | 无 base_url 配置 | 未实现 | 不能直接切换兼容服务 |
| 本地模型 | 未发现 | 无本地推理代码 | 未实现 | 无离线 LLM |
| Hugging Face | 依赖未声明 | 无 transformers/datasets | 未实现 | README 提到 AI-native 但无实现 |
| FinGPT | README 图片引用 FinGPT 资产 | 无 FinGPT 代码 | 仅文档/品牌关联 | 未实现 |

专业词：自然语言处理（Natural Language Processing，NLP）。

零基础解释：NLP 是让程序读懂文本，例如新闻标题和正文。

## 3. 大语言模型调用入口

调用链：

```text
fetch_news(...)
→ DataSourceManager.get_news(...)
→ FMPFetcher.get_news(...)
→ FMP 新闻接口
→ FMPFetcher._annotate_sentiment(...)
→ OpenAI chat.completions.create(...)
→ FMPFetcher._parse_sentiment_response(...)
→ DataStore.update_news_sentiment(...)
```

证据：
- 文件：`src/data/data_fetcher.py`
- 函数：`fetch_news`
- 函数：`get_news`
- 函数：`_annotate_sentiment`
- 函数：`_parse_sentiment_response`

完成程度：部分实现。

零基础解释：调用链说明一次新闻情绪分析从哪里开始、经过哪些函数、结果存到哪里。

## 4. 提示词模板

结论：存在硬编码中文提示词，要求模型只返回 JSON。

证据：
- 文件：`src/data/data_fetcher.py`
- 函数：`_annotate_sentiment`
- 内容：要求判断 `positive`、`neutral`、`negative` 并返回 JSON。

完成程度：部分实现。

专业词：提示词（Prompt）。

零基础解释：提示词就是告诉模型“你要做什么、按什么格式回答”的文本。

风险或限制：提示词直接拼接新闻标题和正文，没有专门防提示词注入。

## 5. 新闻情绪分析

结论：项目实现了新闻情绪分析，但只支持三分类，并且缺少严格 JSON Schema 校验。

证据：
- 文件：`src/data/data_fetcher.py`
- 函数：`_annotate_sentiment`
- 函数：`_parse_sentiment_response`
- 字段：`sentiment`
- 字段：`sentiment_confidence`
- 字段：`sentiment_model`
- 表：`news_articles`

完成程度：部分实现。

专业词：情绪分析（Sentiment Analysis）。

零基础解释：情绪分析是判断一条新闻整体偏利好、利空还是中性。

风险或限制：模型输出只通过 `json.loads` 和字符串包含来解析，没有严格字段类型、置信度范围和异常响应校验。

## 6. 财报与公告分析

| 项目 | 是否存在 | 证据 | 完成程度 |
|---|---|---|---|
| 财报数值因子 | 是 | `fundamental_data` 表和 FMP 财报端点 | 部分实现 |
| 财报文本分析 | 未发现 | 无 10-K/10-Q 文本或 LLM 分析函数 | 未实现 |
| 公告分析 | 未发现 | 无公告数据源 | 未实现 |
| 新闻分析 | 是 | `get_news` + `_annotate_sentiment` | 部分实现 |

专业词：财务报表（Financial Statement）。

零基础解释：财务报表是公司定期披露收入、利润、资产、负债等信息的文件。

## 7. 结构化输出和校验

结论：代码要求模型返回 JSON，但没有使用 JSON Schema、Pydantic 模型或函数调用结构化输出。

证据：
- 文件：`src/data/data_fetcher.py`
- 函数：`_parse_sentiment_response`
- 行为：`json.loads(content)` 后手工读取 `sentiment` 和 `confidence`

完成程度：部分实现。

专业词：结构化输出（Structured Output）。

零基础解释：结构化输出就是让模型按固定字段回答，方便程序可靠读取。

风险或限制：模型回答额外文字、错误 JSON、置信度异常时，可能被弱解析逻辑误判。

## 8. Temperature、超时、重试、最大 Token

| 配置 | 是否存在 | 证据 | 完成程度 |
|---|---|---|---|
| Temperature | 是 | `_annotate_sentiment` 设置 `temperature=0.1` | 完整 |
| 最大 Token | 是 | `_annotate_sentiment` 设置 `max_tokens=60` | 完整 |
| 超时配置 | 配置存在 | `OpenAISettings.request_timeout` | 配置存在但调用未传入 | 部分 |
| 重试 | 未发现 | 无 retry/backoff | 未实现 |
| 成本记录 | 未发现 | 无 token/cost 统计 | 未实现 |
| 缓存 | 是 | `news_articles` 表缓存 sentiment | 部分实现 |

专业词：令牌（Token）。

零基础解释：Token 是模型计费和处理文本时使用的基本单位，近似为词或词片段。

## 9. 调用成本与重复调用风险

结论：项目会缓存新闻与情绪结果，但在 `force_refresh=True` 或缓存缺失时，可能对多篇新闻逐条调用 OpenAI，缺少成本上限。

证据：
- 文件：`src/data/data_fetcher.py`
- 函数：`get_news`
- 函数：`_annotate_sentiment`
- 表：`news_fetch_log`
- 表：`news_articles`

完成程度：部分实现。

风险等级：中。

零基础解释：如果很多新闻都调用付费模型，费用可能累积。

## 10. 离线 Mock 与回退机制

结论：没有独立 Mock LLM；OpenAI 不可用时会跳过情绪分析，不会报错中断。

证据：
- 文件：`src/data/data_fetcher.py`
- 函数：`_get_openai_client`
- 函数：`_annotate_sentiment`
- 日志：`OpenAI client unavailable, skip sentiment analysis`

完成程度：部分实现。

专业词：回退机制（Fallback）。

零基础解释：回退机制是在外部服务不可用时换一种更安全的处理方式。

## 11. LLM 输出是否直接影响交易

结论：当前无法从静态代码确认新闻情绪已经直接进入交易权重或下单流程。项目有新闻情绪缓存字段，但 ML 选股主线的特征列未包含 `sentiment`。

证据：
- 文件：`src/strategies/ml_bucket_selection.py`
- 常量：`FEATURE_COLS`
- 常量：`MOMENTUM_COLS`
- 未包含：`sentiment`

完成程度：未接入交易主线。

风险等级：低到中。

零基础解释：如果模型输出直接变成交易指令，错误回答就可能导致错误下单；目前未发现这种直连。

## 12. 提示词注入、幻觉和未来新闻风险

| 风险 | 是否存在 | 证据 | 风险等级 | 说明 |
|---|---|---|---|---|
| 提示词注入 | 可能存在 | 新闻正文直接进入 prompt | 中 | 新闻内容可能诱导模型偏离任务 |
| 幻觉风险 | 存在 | 无事实校验 | 中 | 模型可能输出不可靠情绪 |
| 未来新闻泄漏 | 可能存在 | 未发现回测中严格按新闻发布时间对齐 | 高 | 历史回测若使用未来新闻会虚高 |
| 成本失控 | 可能存在 | 无 cost cap | 中 | 多新闻逐条调用 |
| 输出校验不足 | 存在 | 弱 JSON 解析 | 中 | 无 schema |

专业词：提示词注入（Prompt Injection）。

零基础解释：提示词注入是外部文本试图操纵模型，让它不按原规则回答。

## 13. 多智能体和真实交易工具

结论：未发现多智能体（Multi-Agent）实现；未发现 LLM 智能体可直接调用真实交易工具。

证据：
- 搜索关键词：`agent`、`multi-agent`、`tool calling`
- 结果：无完整框架实现。

完成程度：未实现。

零基础解释：多智能体是多个模型角色协作完成任务，比如分析师、风控员、交易员。

## 14. 离线学习可行性

结论：LLM 部分当前不适合零基础离线学习，因为没有 Mock Provider；但可以在 Phase 1 添加规则情绪模型或固定 JSON 返回。

建议：
- 新增 `learning/llm/mock_provider.py`
- 新增固定新闻样例 CSV
- 新增情绪 JSON Schema
- 默认禁用真实 OpenAI 调用
- 加成本预算参数

当前未进入 Phase 1。
