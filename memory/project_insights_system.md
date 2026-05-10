---
name: project_insights_system
description: INSIGHTS双轨设计：缓冲区+knowledge_base永久参考库的架构决策背景
type: project
originSessionId: 5c7836eb-106d-4460-b97f-2e692a4e1082
---
INSIGHTS.md 改为临时捕获缓冲区，reference/knowledge_base.md 为已审核永久参考库。

**Why:** 原设计 INSIGHTS.md 作为永久存储导致健康检查噪音（≥10条触发报警但条目长期有效不需要处理）；双轨分离后，INSIGHTS只做短暂缓存，审核后迁入knowledge_base，保持INSIGHTS始终接近空。

**How to apply:**
- 遇报错/环境问题 → 先查 `reference/knowledge_base.md`，有已知解决方案直接用
- 新经验/洞察 → 先写 INSIGHTS.md（缓冲区）
- 健康检查触发≥10条 → 审核INSIGHTS，有价值迁入knowledge_base，无价值删除
- knowledge_base.md 按领域分类（WSL环境/MCP与系统设计/外部集成等）
