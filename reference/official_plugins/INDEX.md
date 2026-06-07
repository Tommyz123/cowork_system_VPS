# 官方 knowledge-work-plugins 参考索引

> 来源：https://github.com/anthropics/knowledge-work-plugins（Anthropic 官方，19.5k★）
> 抓取日期：2026-06-07 | 共 16 个插件 / 140 个 skill
> **性质：纯参考方法论，未安装、未配置。** 每个 .md 存该插件全部 skill 的 name+description。
>
> **使用方式**：主公做相关工作时，Claude 主动提醒「官方 X 插件有现成方法论可借鉴」→ 读对应 .md → 手动套用其 skill 套路/输出模板。
> **不能即插即用**：官方连接器(HubSpot/Klaviyo等)我们未连，Alpine IQ 不在其中；只借方法论，不借工具。

## 按相关度排序

| 插件 | 相关度 | 用途 | skill数 |
|------|------|------|------|
| [data](./data.md) | ⭐高 | SQL/仪表盘/数据解读(可套Alpine IQ·market.db) | 10 |
| [legal](./legal.md) | ⭐高 | legal_library大麻法律:合同/NDA/合规/风险 | 9 |
| [marketing](./marketing.md) | ⭐高 | P3/P12营销·内容·活动效果(可套Alpine IQ) | 8 |
| [sales](./sales.md) | ⭐中 | 客户调研/外联/竞品(求职+客户开发) | 9 |
| [small-business](./small-business.md) | ⭐中 | 小生意运营全套,贴近大麻零售店 | 31 |
| [cowork-plugin-management](./cowork-plugin-management.md) | ⭐参考 | 教你自建组织专属插件,对照自研Skill | 2 |
| [customer-support](./customer-support.md) | 中 | 工单/客户研究(未来零售客服) | 5 |
| [product-management](./product-management.md) | 中 | 写spec/路线图/竞品(SaaS化) | 8 |
| [productivity](./productivity.md) | 中 | 任务/日历/记忆管理 | 4 |
| [bio-research](./bio-research.md) | 低 | 生命科学R&D(无关) | 6 |
| [design](./design.md) | 低 | 设计评审/用研/无障碍 | 7 |
| [engineering](./engineering.md) | 低 | 代码审查/架构/部署 | 10 |
| [enterprise-search](./enterprise-search.md) | 低 | 跨系统企业搜索 | 5 |
| [finance](./finance.md) | 低 | 会计/对账/财报 | 8 |
| [human-resources](./human-resources.md) | 低 | 招聘/薪酬/绩效 | 9 |
| [operations](./operations.md) | 低 | 流程/容量/合规追踪 | 9 |

## 主动提醒触发点（给未来 Claude）

- 主公做 **Alpine IQ 营销分析/活动归因/漏斗** → 提醒看 `marketing.md`(performance-report/campaign-plan) + `data.md`
- 主公做 **大麻法律/合同/合规** → 提醒看 `legal.md`(review-contract/compliance-check/triage-nda)
- 主公写 **营销文案/邮件/落地页** → 提醒看 `marketing.md`(content-creation/email-sequence)
- 主公做 **客户开发/竞品调研/求职外联** → 提醒看 `sales.md`(account-research/draft-outreach/competitive-intelligence)
- 主公做 **大麻零售店日常运营**（现金流/客户/合同/营销）→ 提醒看 `small-business.md`
- 主公想 **自建/重构 Cowork 自己的插件** → 提醒看 `cowork-plugin-management.md`
- 主公做 **SaaS产品规划**（spec/路线图）→ 提醒看 `product-management.md`

## 看 skill 全文
本索引只存 name+description。需要某 skill 的**完整 Body(执行步骤/模板)** → 抓 `https://github.com/anthropics/knowledge-work-plugins/blob/main/<插件>/skills/<skill名>/SKILL.md`