# 官方插件参考：sales

> 来源：https://github.com/anthropics/knowledge-work-plugins/tree/main/sales
> 性质：**纯参考方法论**，未安装/未配置。用得上时手动借鉴其 skill 的套路与输出模板。
> 与主公业务相关度：⭐ 中 — 客户调研/外联/竞品情报（求职+客户开发）

**官方连接器(MCP)**：slack, hubspot, close, clay, zoominfo, notion, atlassian, fireflies, apollo, outreach, google calendar, gmail, similarweb
> ⚠️ 我们环境未连这些工具；Alpine IQ 不在官方连接器内 → 不能即插即用，只借方法论。

## Skills（9个）

### `account-research`
Research a company or person and get actionable sales intel. Works standalone with web search, supercharged when you connect enrichment tools or your CRM. Trigger with "research [company]", "look up [person]", "intel on [prospect]", "who is [name] at [company]", or "tell me about [company]".

### `call-prep`
Prepare for a sales call with account context, attendee research, and suggested agenda. Works standalone with user input and web research, supercharged when you connect your CRM, email, chat, or transcripts. Trigger with "prep me for my call with [company]", "I'm meeting with [company] prep me", "call prep [company]", or "get me ready for [meeting]".

### `call-summary`
Process call notes or a transcript — extract action items, draft follow-up email, generate internal summary. Use when pasting rough notes or a transcript after a discovery, demo, or negotiation call, drafting a customer follow-up, logging the activity for your CRM, or capturing objections and next steps for your team.

### `competitive-intelligence`
Research your competitors and build an interactive battlecard. Outputs an HTML artifact with clickable competitor cards and a comparison matrix. Trigger with "competitive intel", "research competitors", "how do we compare to [competitor]", "battlecard for [competitor]", or "what's new with [competitor]".

### `create-an-asset`
Generate tailored sales assets (landing pages, decks, one-pagers, workflow demos) from your deal context. Describe your prospect, audience, and goal — get a polished, branded asset ready to share with customers.

### `daily-briefing`
Start your day with a prioritized sales briefing. Works standalone when you tell me your meetings and priorities, supercharged when you connect your calendar, CRM, and email. Trigger with "morning briefing", "daily brief", "what's on my plate today", "prep my day", or "start my day".

### `draft-outreach`
Research a prospect then draft personalized outreach. Uses web research by default, supercharged with enrichment and CRM. Trigger with "draft outreach to [person/company]", "write cold email to [prospect]", "reach out to [name]".

### `forecast`
Generate a weighted sales forecast with best/likely/worst scenarios, commit vs. upside breakdown, and gap analysis. Use when preparing a quarterly forecast call, assessing gap-to-quota from a pipeline CSV, deciding which deals to commit vs. call upside, or checking pipeline coverage against your number.

### `pipeline-review`
Analyze pipeline health — prioritize deals, flag risks, get a weekly action plan. Use when running a weekly pipeline review, deciding which deals to focus on this week, spotting stale or stuck opportunities, auditing for hygiene issues like bad close dates, or identifying single-threaded deals.
