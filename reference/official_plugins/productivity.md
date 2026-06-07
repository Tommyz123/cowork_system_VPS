# 官方插件参考：productivity

> 来源：https://github.com/anthropics/knowledge-work-plugins/tree/main/productivity
> 性质：**纯参考方法论**，未安装/未配置。用得上时手动借鉴其 skill 的套路与输出模板。
> 与主公业务相关度：中 — 任务/日历/记忆管理（参考其 memory-management 设计）

**官方连接器(MCP)**：slack, notion, asana, linear, atlassian, monday, clickup, google calendar, gmail
> ⚠️ 我们环境未连这些工具；Alpine IQ 不在官方连接器内 → 不能即插即用，只借方法论。

## Skills（4个）

### `memory-management`
Two-tier memory system that makes Claude a true workplace collaborator. Decodes shorthand, acronyms, nicknames, and internal language so Claude understands requests like a colleague would. CLAUDE.md for working memory, memory/ directory for the full knowledge base.

### `start`
Initialize the productivity system and open the dashboard. Use when setting up the plugin for the first time, bootstrapping working memory from your existing task list, or decoding the shorthand (nicknames, acronyms, project codenames) you use in your todos.

### `task-management`
Simple task management using a shared TASKS.md file. Reference this when the user asks about their tasks, wants to add/complete tasks, or needs help tracking commitments.

### `update`
Sync tasks and refresh memory from your current activity. Use when pulling new assignments from your project tracker into TASKS.md, triaging stale or overdue tasks, filling memory gaps for unknown people or projects, or running a comprehensive scan to catch todos buried in chat and email.
