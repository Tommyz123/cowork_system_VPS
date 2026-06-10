# 方法论统一总索引（Skill Methodology Master Index）

> **用途**：一页看全所有「按需调用的方法论资产」。主公做相关工作时，Claude 在此查触发词 → 提醒主公"有现成方法论可用" → 读对应路径套用。
> **性质**：纯逻辑索引（方案②）。两个底层库**物理位置不动**，本文件只做汇总指针，零断链风险。
> **不含**：已配置的自动加载 Skill（保存进度/收工/搜索/整理记忆/系统复盘/auto-rca，在 `~/.claude/skills/`）——那套是常驻工具，不在此索引。
> **建立日期**：2026-06-07 | **维护**：新增方法论 → 在对应区块加一行，带「出处+日期+类型」

---

## 维护规则：新增 / 更新 / 覆盖

**新增**：在对应区块加一行，必带出处三字段（来源 + 记录日期 + 类型）。

**更新覆盖（铁律，按严格度排列）**：
- ✅ **只有「完全同一条方法论」的新版才有资格覆盖旧版** —— 判定同一条：**同名 + 同来源**（同一个东西）。例：官方更新 marketing 插件 → 重抓的新 marketing.md 覆盖旧 marketing.md。
- 🛑 **即使够资格，覆盖前也必须先问主公、得确认才动手** —— 覆盖是删除性动作，不可逆，一律先问。
- ❌ **相似 ≠ 同一，绝不因"看起来差不多/主题相近"就覆盖** —— 相近但非同一的方法论必须**各自保留**，不能把 A 当成 B 的新版盖掉（否则误删本该独立保留的方法论）。
- ⚠️ **拿不准是否同一条 → 不覆盖，问主公。**
- **覆盖动作**（经主公确认后）：直接 Write 替换该文件内容（文件系统自然新盖旧）+ 把对应区块头/该行日期改成当天；精确历史版本靠 `git log 文件名` 查。

---

## 出处规范（新增任何方法论必带）

| 字段 | 说明 |
|------|------|
| **来源** | 仓库URL / 博客链接 / "主公自创" / "某次对话总结" |
| **记录日期** | YYYY-MM-DD，判断是否过时 |
| **类型** | `self`(自有/自创) / `official`(官方权威) / `external`(外部第三方) |

---

## 一、自有方法论（self）— 可执行 SKILL.md

> 物理位置：`cowork/skill_archives/`（不自动加载，读 SKILL.md 按步骤执行）
> 来源：Cowork 自研 V5 框架 | 类型：self | 记录日期：2026-05-23

| 触发关键词 | 路径 | 功能 |
|---|---|---|
| 生成项目计划 / 项目规划 | `skill_archives/project-plan-generator/SKILL.md` | 生成 PROJECT_PLAN.md（9/11/13维度规划）|
| 审核项目计划 | `skill_archives/project-plan-reviewer/SKILL.md` | 审核 PROJECT_PLAN.md 是否符合 SPEC |
| 修复项目计划 | `skill_archives/project-plan-fixer/SKILL.md` | 按审核报告修复 PROJECT_PLAN.md |
| 项目工作流 / 完整规划流程 | `skill_archives/project-workflow/SKILL.md` | 一键 生成+审核+修复 全流程 |
| 生成 TODOLIST / 任务清单 | `skill_archives/todolist-generator/SKILL.md` | 从 PROJECT_PLAN 生成 TODOLIST.md（拓扑排序）|
| 审核 TODOLIST | `skill_archives/todolist-reviewer/SKILL.md` | 审核 TODOLIST.md 是否符合 SPEC |
| 修复 TODOLIST | `skill_archives/todolist-fixer/SKILL.md` | 按审核报告修复 TODOLIST.md |
| 审核系统架构 / 审核架构 | `skill_archives/审核架构/SKILL.md` | cowork 系统架构 7 维度审核 |
| 系统复盘 | `skill_archives/系统复盘/SKILL.md` | friction_log 归类统计 + 复发检测 |

---

## 二、官方参考方法论（official）— 纯文档，不可执行

> 物理位置：`cowork/reference/official_plugins/`（只读方法论，手动套用）
> 来源：github.com/anthropics/knowledge-work-plugins（Anthropic 官方 19.5k★）| 类型：official | 记录日期：2026-06-07
> ⚠️ 不能即插即用：官方连接器(HubSpot/Klaviyo等)我们未连，Alpine IQ 不在其中，只借方法论/输出模板。

| 插件 | 相关度 | 用途 | 路径 |
|---|---|---|---|
| data | ⭐高 | SQL/可视化/统计/仪表盘（可套 Alpine IQ·market.db）| `reference/official_plugins/data.md` |
| legal | ⭐高 | 合同审查/NDA分类/合规/风险/签署（legal_library）| `reference/official_plugins/legal.md` |
| marketing | ⭐高 | 文案/活动/品牌审核/SEO/效果报告/邮件序列（可套 Alpine IQ）| `reference/official_plugins/marketing.md` |
| sales | ⭐中 | 客户调研/通话准备/外联/竞品情报/做物料 | `reference/official_plugins/sales.md` |
| small-business | ⭐中 | 现金流/发票/利润/营销/合同/CRM/报税（31skill最全，贴近大麻零售店）| `reference/official_plugins/small-business.md` |
| cowork-plugin-management | ⭐参考 | 教你自建组织专属插件 | `reference/official_plugins/cowork-plugin-management.md` |
| customer-support | 中 | 工单/客户研究 | `reference/official_plugins/customer-support.md` |
| product-management | 中 | 写spec/路线图/竞品（SaaS化）| `reference/official_plugins/product-management.md` |
| productivity | 中 | 任务/日历/记忆管理 | `reference/official_plugins/productivity.md` |
| finance/operations/engineering/design/human-resources/enterprise-search/bio-research | 低 | 专业职能（详见各 .md）| `reference/official_plugins/` |

> 官方插件完整索引（含「主动提醒触发点」清单）：`reference/official_plugins/INDEX.md`

---

## 三、外部方法论（external）— 预留

> 物理位置：`cowork/reference/external_methodology/`（暂未创建，首次添加时建）
> 以后从博客/书/他人处看到的成熟方法论入此，必带出处规范三字段。

（暂无）

---

## 三.5、预测方法论（self，引擎已落地）

> 来源：通读 MiroFish 仓库 + 主公与 Claude 对话拆解 | 类型：self | 记录日期：2026-06-08（铁律文档 2026-06-09 落地）
> ✅ **通用引擎已落地**：六步流水线已实现为可复用脚本，换题目不改代码。✅ 正式铁律文档 `reference/prediction_method.md` 已写（2026-06-09）。

| 触发关键词 | 路径 | 内容 |
|---|---|---|
| 做预测 / 预测走向 / 涌现推演 / 复刻MiroFish | `prediction_engine/predict.py` + `README.md` | **通用预测引擎**：输入facts+问题→自动跑六步出预测报告。用法见README。订阅版零API费 |
| 预测标准 / 预测铁律 / 跑预测前必读 | `reference/prediction_method.md` | **七条铁律+六步骨架+能力边界+实跑检查清单**（做任何预测前必读） |
| 预测原理/拆坑 | `reference/mirofish_拆解笔记.md` | MiroFish 六步涌现流水线+代码出处+10个坑拆解+订阅版替换表 |

---

## 四、其他方法论去哪找（指路，不在此物理收录）

> 本索引专管「成套·可主动调用的 skill 形态方法论」。系统里还有大量**零散方法论**，它们各有归宿和自己的索引，**保持原位、不搬进来**（避免一条方法论多处记导致过期不同步）。需要时去下表对应位置查：

| 方法论类型 | 位置 | 调用方式 |
|---|---|---|
| 技术踩坑/解法（工具报错/环境问题）| `reference/knowledge_base.md` | 遇报错先查 |
| 写脚本规范 | `reference/script_standards.md` | 写/改脚本前读 |
| 各项目协作打法/启动套路 | `playbooks/<项目名>.md` | frontmatter triggers 自动路由 |
| 主公教我的做事方法（被动内化的规矩，如金字塔教学法/proposal先验证痛点）| `memory/` 的 `feedback_*.md`（索引在 MEMORY.md）| 我做事时自动遵守，非点名调用 |
| 临时未审核洞察 | `INSIGHTS.md` | 审核后迁入 knowledge_base |

> **区别**：本索引(一~三区)=**主动调用**的成套流程（你点名"用XX"）；上表=**被动内化/按需查阅**的零散方法论。两者定位不同，故分开管，逻辑上从这一个入口都能找到去向。

---

## 主动提醒触发点（给未来 Claude）

主公做以下工作时，主动提醒"有现成方法论可借鉴" + 给路径：

- **规划新项目/拆任务** → self 区：项目规划 + TODOLIST 系列
- **Alpine IQ 营销分析/活动归因/漏斗** → official：marketing.md + data.md
- **大麻法律/合同/合规** → official：legal.md
- **写营销文案/邮件/落地页** → official：marketing.md
- **客户开发/竞品调研/求职外联** → official：sales.md
- **大麻零售店日常运营**（现金流/客户/合同）→ official：small-business.md
- **审核 cowork 系统架构 / 复盘** → self：审核架构 / 系统复盘
- **想自建 Cowork 插件 / SaaS规划** → official：cowork-plugin-management.md / product-management.md
