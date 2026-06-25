# 待确认草稿区

> 每次对话开始时检查，有内容则第一件事列出请主公决策

---

（空 — 2026-06-23 已清空：6-10 至 6-22 共 12 批草稿全部经主公逐批审核处理完毕。处理摘要见 cowork_log.md 同日"review_drafts批N"行。）

---

## [草稿] 2026-06-23 深度审核（3 sessions：96b24987 / abd8d2eb / f95f94af）

### 🤖 本次自动写入摘要（4 分，已直接写入正式文件）
- **[评分:4]** knowledge_base「permissions.deny 禁止特定工具触发」→ 已写入 reference/knowledge_base.md「MCP 与系统设计」区块

### 🗑️ 本次自动丢弃摘要（1 分，未保留）
- 共 3 条 1 分候选被 AI 自判低价值丢弃（f95f94af=已全提交4cc349f/96b24987=7条极简/abd8d2eb产出已入5a86386）

---

## [草稿] 2026-06-23 深度审核·第二批（3 sessions：41968649 / dab72bb5 / 9893fc2f）

### 🤖 本次自动写入摘要（4-5 分，已直接写入正式文件）
- **[评分:5]** feedback「文档为AI而写总纲」→ 已写入 memory/feedback_docs_for_ai.md（含读者二分判据+系统内文档标准+脚本四段写法）
- **[评分:5]** FERC信号漏确认闭环修复 → 已写入 trading/notes/趋势追踪档案.md(CEG 6/23更正行+修订区) + 趋势观察池.md(E1两阶段) + scripts/ferc_watch.py(逻辑说明)
- **[评分:4]** 信号作战表(给AI看的信号→动作SOP) → 已新建 trading/notes/信号作战表.md + 登记INDEX.md/cron_jobs.md
- **[评分:4]** friction「收工git授权失灵+token被hook清」→ 已写入 friction_log.md（根因待查留两问）

### 🗑️ 本次自动丢弃摘要（1 分，未保留）
- 2 条 1 分候选丢弃：41968649=周报HTML渲染修复(已历史完成入提交)/dab72bb5=三实例runner核验(已完成工作的核验,2小尾巴已入be4aaf5)

### 📌 留主公决策（非草稿，已记 CURRENT_SESSION）
- P9 两待决策：① NAND/光模块是否加轻量哨兵 ② 通知是否改三级分级（🔴出手即时/🟡事件当天/⚪周检心跳）

## [草稿] 2026-06-24 深度审核

### Friction 建议补记（0条）
（本场 2 条假问题 friction 已实时记入 friction_log，无需补）

### Playbook 建议更新（0处）
（playbooks/p9_trading.md 本场已直接更新账号实时查口径）

### CLAUDE.md 规则建议（1处）
- **[评分:3]** CLAUDE.md 白名单补 `friction_log_archive.md`：本场(及 6/24 00:38 AA 场)发现收工归档 friction 时，改 `friction_log.md`(白名单内)放行但写 `friction_log_archive.md`(白名单写的是目录 `archive/`,不含根目录的 `friction_log_archive.md`)被任务守卫拦。两者同性质(收工高频归档操作),建议白名单加 `friction_log_archive.md` 给同等权限。需主公确认是否改 CLAUDE.md。

---

## [草稿] 2026-06-25 深度审核（本场=重启+收工，复核昨日大会话 bcfbf1ac）

### ⚠️ 上一条草稿状态复核（重要）
- 上面「CLAUDE.md 白名单补 `friction_log_archive.md`」**hook 层已自动解决**：6/24 20:53 的 D 修复已把 `system_file_guard.sh:27` 白名单从 `friction_log.md` 改成子串 `friction_log`，子串匹配同时覆盖 `friction_log.md` + `friction_log_archive.md`，task 守卫不再拦归档文件。
- **但残留一处文档↔实现不一致**：`~/.claude/CLAUDE.md:29` 文字白名单仍写 `friction_log.md`（人读文档），与 hook 实际放行的 `friction_log`（含 archive）不符。
  - **[评分:3]** 建议：把 `~/.claude/CLAUDE.md:29` 白名单文字 `friction_log.md` 改成 `friction_log*`（或注明"含 archive"），让人读文档与 hook 行为一致（符合 feedback_doc_single_source）。需主公确认。这是**唯一仍需处理项**，原"补白名单"诉求已由 D 技术解决。

### 其他类别
- INSIGHTS/Friction/Playbook/文档对齐/MEMORY清理：本场无新增。昨日大会话的洞察（先读代码再诊断、自我更正、停手防数据丢失）均为已有 memory 规则的再次印证，无新规则可写。F 检查 MEMORY.md 无废弃孤儿（🗄️ 两条为有意保留）。

---

### 🤖 本次自动写入摘要（4-5 分，已直接写入正式文件）
- **[评分:5]** Feedback 文档纪律 `feedback_doc_single_source` → 已写入 memory/（会变的别写死+状态类就地覆盖禁新旧并存；治"文档更新追不上"）
- **[评分:4]** Feedback `feedback_cleanup_temp_data` 扩展"临时脚本"纳入 → 已写入 memory/（主公 6/24 点名）
