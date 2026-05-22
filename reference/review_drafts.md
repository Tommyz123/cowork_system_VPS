# 待确认草稿区

> 每次对话开始时检查，有内容则第一件事列出请主公决策

---

## [草稿] 2026-05-22 深度审核

> 审核 session：f80ef6e0（跨日 5/18→5/22，本次收工覆盖前半 P6/P9 修复 + 后半 review_drafts 全清）

### INSIGHTS 建议写入（2条）

1. **P6 ROUTES 排序 = SerpAPI 配额分配机制** [src:f80ef6e0]
   - 直飞路线（JFK→HKG/CAN）原来排在 ROUTES 末位，月度配额耗尽时最先跳过 → 已修复移到最前面
   - 推广原则：ROUTES 排序 = 隐含的优先级声明；高优先路线必须在前，次要路线放后备位置

2. **P9 scanner_picks 重复记录根因** [src:f80ef6e0]
   - UNIQUE(symbol, scan_date) 只防同一天重复，不防跨日重复扫入同一 symbol
   - 修复：write_scanner_picks 前置检查"已有 submitted/filled/open 状态则跳过 INSERT"
   - 在任何 append-only 表里，"逻辑唯一"约束（如"同一活跃持仓只能有一条"）需要应用层检查，不能只靠 DB UNIQUE

### Friction 建议补记（1条）

- **2026-05-22 minor**：采信 review_drafts.md 草稿关于"discord_approve.py 已删"的描述未先验证，准备了错误修改方案（改成 inject_time.sh）；查实后纠正
  - 根因：review_drafts 草稿内容写于 5/18，执行时 5/22，中间 4 天系统变化导致描述过期
  - 教训：review_drafts 草稿执行前必须先 verify 文件实际状态，不能直接采信

### 文档对齐待处理（1处）

- **check_doc_sync.py**：只扫 `cowork/scripts/`，不扫 `~/.claude/hooks/`，导致 `discord_approve.py` 等 hooks 脚本被误报"找不到"。建议加 hooks/ 路径或白名单跳过该文件。

### 维护提醒

- cowork_log.md 322行 > 300行上限 → 需要归档（移前200行至 archive/cowork_log_2026.md）
- INSIGHTS.md 13条 → [ref-worthy] 标记的应迁 knowledge_base.md
- friction 18条 → 建议下次对话跑一次「系统复盘」

### auto_pending 处理建议

[2026-05-11] "收工时整理草稿规则" → **不写入正式 memory**：收工 SKILL.md 步骤5已内嵌该规则（"不直接写入正式文件，存入 review_drafts.md"）。建议清空 auto_pending.md。

### MEMORY.md 废弃检查

扫描完成，无废弃条目。

[src: session f80ef6e0-4363-4121-ac5d-b927f4613745]
