---
name: feedback_token_economy
description: 系统优化方案必须算token经济账，真正省token的优先级反直觉
type: feedback
originSessionId: f80ef6e0-4363-4121-ac5d-b927f4613745
---
**评估任何系统优化方案时，必须算 token 经济账（4个维度）：**

1. 输入 token 进 context（方案执行时读了多少文件？）
2. 输出 token 进对话（方案产出了多少内容进 context？）
3. LLM 调用消耗（claude --print 每次跑多少 token？）
4. 替代了多少现有浪费（能省的比花的多吗？）

**真正省 token 的优先级（反直觉）：**

| 方案 | 月节省估算 |
|------|-----------|
| 开新对话纪律（避免长对话） | 1-2M/月 |
| 搜索 Skill 升级（减少重复读文件） | 200-500K/月 |
| 知识图谱（减少漏更新） | 100-200K/月 |
| LLM 语义检查（如 claude --print 分析文档） | **净增** 50-150K/月 |

最大的节省不在"聪明工具"，在"开新对话"这个纪律。

**Why:** 2026-05-21 评估 CodeGraph G 方案时，"3-4h 工时"看起来便宜，但算了 token 账发现 claude --print 输出进 context 是净增成本，不是节省。

**How to apply:**
- 任何涉及 claude --print / LLM 调用的"自动化"方案，先算 token 净增/净减
- 优先推"减少读文件次数"的方案，而非"更聪明地读文件"的方案
