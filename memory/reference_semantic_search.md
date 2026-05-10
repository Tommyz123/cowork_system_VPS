---
name: 语义搜索系统位置
description: VoyageAI语义搜索系统技术位置，hybrid模式(FTS5+语义)，API key存放
type: reference
originSessionId: 9d2c8c96-b073-4c5e-ba3b-e71935c35b53
---
VoyageAI 语义搜索已上线于 cowork 系统。

**API Key 位置：** `cowork/scripts/.env` → `VOYAGE_API_KEY`

**关键脚本：**
- `embed_sessions.py` — 生成会话向量
- `embed_messages.py` — 生成消息级向量
- `search_conversations.py` — 默认 hybrid 模式（FTS5 + 语义）

**搜索入口：** `/搜索` Skill（Discord 自然语言触发）

**索引更新机制（重要）：**
- FTS5 关键词索引：`log_session.py` 收工时自动更新，无需手动操作
- 向量索引：`embed_sessions.py`（session级）+ `embed_messages.py`（消息级）需单独跑，否则语义搜索退化
- 收工流程已含向量索引更新步骤，确保两路索引同步
