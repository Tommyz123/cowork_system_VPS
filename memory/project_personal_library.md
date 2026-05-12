---
name: P10 个人文件库
description: cowork 个人AI助理文件检索系统，索引简历/租约/财务/证书/cannabis文件，可通过Discord语音直接检索发送
type: project
originSessionId: 18c93b3f-7be5-4c38-8fe8-4915ad9e1e5a
---
P10 个人文件库 — 将静态个人文件内容索引化，通过自然语言检索并发送到 Discord。

**Why:** 求职用（快速找简历）+ 个人助理升级（文件不用找，直接说）；基于 gbrain/llm_wiki 思路的两层架构（文件库 + 项目库）

**How to apply:** 主公说"发我XXX简历/租约/证书"时，直接调用 `personal/search_personal.py` 检索并发 Discord；按分类建议索引范围

## 数据库分层架构（2026-04-25确立）
四库各自独立，不互相混存：
- `cowork.db` — 对话历史（session/messages）
- `personal.db` — 个人静态文件索引
- `trading.db` — 量化交易数据
- `market.db` — 大麻市场数据

## 当前状态（2026-04-25）
阶段1-4完成：267文件已索引；阶段5-8暂停，OCR已就绪，进度见 CURRENT_SESSION.md [P10]
