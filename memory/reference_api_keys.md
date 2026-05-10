---
name: reference_api_keys
description: 所有API key统一存放位置和清单
type: reference
originSessionId: d13aed09-f19a-44e5-81c1-fc0cfee07eea
---
所有API key统一存在 `cowork/config/api_keys.env`（已加.gitignore不追踪）。

**文件路径：** `/mnt/c/Users/zhi89/Desktop/cowork/config/api_keys.env`

**Key清单（2026-05-08更新）：**
- SerpAPI KEY1 — Mac mini价格监控专用
- SerpAPI KEY2 — 机票监控专用（双key容错）
- Gmail（GMAIL_USER / GMAIL_APP_PASSWORD / GMAIL_TO）— 邮件发送
- Discord BOT TOKEN — 各脚本Discord推送
- Voyage — 语义搜索向量化
- OpenAI — 备用LLM
- Anthropic — Claude API
- Tavily — 搜索
- DeepL — 翻译
- DeepSeek — 备用LLM
- Alpaca（ALPACA_API_KEY / ALPACA_SECRET_KEY）— 纸交易账号
- FMP（FMP_API_KEY）— 财务数据（Financial Modeling Prep）；⚠️ Free plan不含新闻端点，仅保留备用
- Finnhub（FINNHUB_API_KEY）— P9新闻采集主力（2026-05-08接入，Free plan含新闻，主公zhitao776@gmail.com注册）

**How to apply:** 涉及任何API调用时，先从此文件读取对应key，不得硬编码。
