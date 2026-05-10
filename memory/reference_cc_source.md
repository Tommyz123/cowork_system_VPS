---
name: reference_cc_source
description: Claude Code 源码架构研究笔记位置——已探索 Hook/权限/工具/多智能体/压缩/记忆等模块，含对主公系统的具体建议
type: reference
---

详细研究笔记在：`/mnt/c/Users/zhi89/Desktop/cowork/research/cc_source_insights.md`

**已覆盖的模块：**
Hook 系统（stdin JSON机制）、权限模型、ToolSearch延迟加载、工具注册、协调器模式、Stop Hooks后处理、SessionMemory自动提取、对话压缩三层策略、成本追踪、Memory四分类、QueryEngine会话管理、extractMemories、autoDream

**对主公系统最重要的结论：**
- Stop Hook 可解决日志漏记（优先级高）
- 记忆相关性过滤可节省 token（优先级高）
- 协调器模式适合多项目并发（优先级中）
- SQLite MCP 适合 marketing 项目（优先级中）

**2026-04-01 新增借鉴（已落地到 CLAUDE.md）：**
- extractMemories 双写互斥 → 收工前检查是否已整理记忆
- MEMORY.md 200行/25KB硬限制 → 我们加了180行预警
- cursor 追踪（lastMemoryMessageUuid）→ last_memory_sync 时间戳
- autoDream lock 文件 mtime 即状态 → 留作将来自动整理记忆参考

**QueryEngine 分析结论：** 架构不适合直接借鉴（代码层设计），但"轮级 vs 会话级状态分离"思想有参考价值；对话内临时状态靠对话上下文即可，无需落文件。

**Hook 关键坑：** 数据通过 stdin 传 JSON，不是环境变量；修改 settings.json 触发 Discord MCP 重启
