# 官方插件参考：enterprise-search

> 来源：https://github.com/anthropics/knowledge-work-plugins/tree/main/enterprise-search
> 性质：**纯参考方法论**，未安装/未配置。用得上时手动借鉴其 skill 的套路与输出模板。
> 与主公业务相关度：低 — 跨系统企业搜索

**官方连接器(MCP)**：slack, notion, guru, atlassian, asana, google calendar, gmail
> ⚠️ 我们环境未连这些工具；Alpine IQ 不在官方连接器内 → 不能即插即用，只借方法论。

## Skills（5个）

### `digest`
Generate a daily or weekly digest of activity across all connected sources. Use when catching up after time away, starting the day and wanting a summary of mentions and action items, or reviewing a week's decisions and document updates grouped by project.

### `knowledge-synthesis`
Combines search results from multiple sources into coherent, deduplicated answers with source attribution. Handles confidence scoring based on freshness and authority, and summarizes large result sets effectively.

### `search`
Search across all connected sources in one query. Trigger with "find that doc about...", "what did we decide on...", "where was the conversation about...", or when looking for a decision, document, or discussion that could live in chat, email, cloud storage, or a project tracker.

### `search-strategy`
Query decomposition and multi-source search orchestration. Breaks natural language questions into targeted searches per source, translates queries into source-specific syntax, ranks results by relevance, and handles ambiguity and fallback strategies.

### `source-management`
Manages connected MCP sources for enterprise search. Detects available sources, guides users to connect new ones, handles source priority ordering, and manages rate limiting awareness.
