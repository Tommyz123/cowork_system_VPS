# 官方插件参考：small-business

> 来源：https://github.com/anthropics/knowledge-work-plugins/tree/main/small-business
> 性质：**纯参考方法论**，未安装/未配置。用得上时手动借鉴其 skill 的套路与输出模板。
> 与主公业务相关度：⭐ 中 — 小生意运营全套（现金流/营销/客户/合同），跟大麻零售店运营贴近

**官方连接器(MCP)**：quickbooks, paypal, hubspot, canva, docusign, slack, stripe, square, gmail, google calendar, google drive
> ⚠️ 我们环境未连这些工具；Alpine IQ 不在官方连接器内 → 不能即插即用，只借方法论。

## Skills（31个）

### `business-pulse`
>

### `call-list`
Ranks the top-5 leads most worth calling today, supplies talking points from email history, blocks time on the calendar, and drafts follow-up messages. Accepts optional count and date arguments.

### `canva-creator`
>

### `cash-flow-snapshot`
>

### `close-month`
Closes the month — reconciles QB vs payment processors, flags gaps, writes P&L narrative, exports close packet. Accepts optional month and save-to arguments.

### `content-strategy`
>

### `contract-review`
>

### `crm-cleanup`
Scans HubSpot for stale deals, duplicate contacts, and missing fields, then fixes what the owner approves. Accepts optional scope argument for deals, contacts, or all.

### `crm-maintenance`
>

### `customer-pulse`
>

### `customer-pulse-check`
Synthesizes themes from PayPal disputes, HubSpot tickets, and review exports into a top-3 fixable issues list with drafted response templates. Accepts optional since-date argument.

### `friday-brief`
Delivers the Friday end-of-week pulse — revenue vs prior week, top sellers, wins and watches. Accepts optional lookback window of 7 or 14 days.

### `handle-complaint`
Handles an incoming customer complaint end-to-end — pulls context, drafts a response, and suggests an operational fix. Accepts optional email or ticket ID argument.

### `invoice-chase`
>

### `job-post-builder`
>

### `lead-triage`
>

### `margin-analyzer`
>

### `monday-brief`
Generates a one-page Monday morning briefing — cash, sales, pipeline, week ahead, top three to-dos. Accepts optional post destination and save-to arguments.

### `month-end-prep`
>

### `month-heads-up`
Runs on the 25th — shows the next 30-day cash-flow outlook and flags anything that needs attention before month-end. Accepts optional 30 or 60 day horizon.

### `plan-payroll`
Forecasts cash, ranks overdue invoices, and stages PayPal reminders so the owner can confidently run payroll. Accepts optional horizon and payroll-date arguments.

### `price-check`
Produces a margin-by-product table and three pricing-scenario data views so the owner can see the full financial picture before making a pricing decision. Accepts optional product name argument.

### `quarterly-review`
Generates a full QBR narrative — revenue trend, margin trend, customer health, top opportunities and risks — as a presentation-ready PDF or deck. Accepts optional quarter and save-to arguments.

### `review-contract`
Reviews a contract in plain English, surfaces red flags with severity ratings, and produces a marked-up docx/PDF with suggested redlines. Accepts optional file path or DocuSign envelope ID.

### `run-campaign`
Runs an end-to-end marketing campaign — sales analysis, content brief, Canva assets, HubSpot send. Accepts optional lookback and channel arguments.

### `sales-brief`
Surfaces top and bottom sellers, identifies seasonality patterns, and produces a 2-week content brief to push winners and clear slow movers. Accepts optional lookback window of 30, 60, or 90 days.

### `smb-onboard`
>

### `smb-router`
>

### `tax-prep`
Prepares tax-season materials — quarterly estimated tax calculation or year-end 1099 prep — and produces an accountant handoff packet. Accepts optional mode and year arguments.

### `tax-season-organizer`
>

### `ticket-deflector`
>
