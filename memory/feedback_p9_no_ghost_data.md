---
name: P9 数据完整性铁律 — 不允许 ghost data
description: P9 scanner_picks status 必须对齐真实 broker 状态；扫描后立即自动下单（研究阶段）或 candidate→approve→filled（真钱阶段）
type: feedback
originSessionId: 0d07266c-759a-4496-87e2-e643a71c00e1
---
P9 系统数据完整性铁律：**scanner_picks.status 必须反映真实 broker 状态，不允许 DB 单边记录"已入场"但 Alpaca 没有实际持仓**。

**Why**：2026-05-18 ghost positions 事件——5/11 那批 8 只 scanner_picks 标 `status='open'` 但 swing 账户从未真实下单（cognitive_scanner.py 当时 by design 不下单，主公需手动操作，但当时无明确提醒），导致所有下游 alpha 计算 / weekly_review / ORA case study 基于"14 只都真实持仓"的错误前提运行一周。RCA 锁到根因：**状态语义模糊（'open' 在 P9 设计里=watchlist，在金融业=已成交）+ 缺少 DB-Alpaca reconciliation + 信任 DB 而非 broker + scanner 不下单但用 'open' 状态写入**。

**How to apply**:

1. **研究阶段（当前状态 2026-05-19 起）→ cognitive_scanner 扫描后自动下单 + reconciler 同步真实状态**：
   - scanner 写入时 `status='submitted', cohort='auto_pending'` + 同时 alpaca place_order opg 单到 swing
   - **次日 9:45 EDT sync_fill_prices.py reconciler 按 Alpaca 实际 status 更新**：
     - filled → status='filled' / cohort='auto_filled' + 回填 fill 字段
     - expired/canceled/rejected → 同名状态（DB-broker 一致，下游自动过滤）
   - 4 层 sanity check（每只 notional 上限 / 单次扫描数量上限 / dedup 同 ticker / buying_power 充足）— 具体数值见 feedback_p9_auto_execute（2026-05-30 起每只 $1000 / 上限 30 只）
   - **永远禁止**：INSERT 时硬编码 'filled' 假设 broker 100% 成交（2026-05-19 OPG 1/6 实测 fill 率证伪此假设；RCA: trading/rca/2026_05_19_opg_expired_anti_pattern_recurrence.md）
   - 详见 [feedback_p9_auto_execute.md](feedback_p9_auto_execute.md)

2. **真钱阶段（未来切换时）→ 必须重新启用 approve gate**：
   - 恢复 'candidate' 状态值 + 重新实现 submit_pending_picks 类机制
   - 不能假设主公"会看到 Discord 推送自动下单" — 必须有显式 reply approve TICKER

3. **状态字段规则**（永久铁律）：
   - 真实持仓查询用 `status IN ('filled', 'filled_late')`（13 处下游脚本已统一）
   - 状态字段一律用领域明确词：candidate / filled / filled_late / auto_filled / partially_filled / closed / cancelled / invalidated / skipped / expired
   - 禁用 'open' / 'pending' 这种在不同上下文含义不同的词

4. **SoT 信任模型**（永久铁律）：
   - DB 是 thesis/attribution 的 SoT；Alpaca 是真实持仓的 SoT
   - 任何"持仓数量/fill_price/实际敞口"分析必须从 Alpaca 拉，DB 是缓存
   - 任何"thesis/bear thesis/cohort/verdict"分析必须从 DB 拉，Alpaca 没这些

5. **每周 data integrity check**：weekly_review 第一段必须做 DB filled+filled_late+auto_filled count vs Alpaca position count 对账，不一致就阻止 review 输出

6. **反模式根治铁律（2026-05-19 更新）**：识别反模式后，**数据层修复 ≠ 流程修复**。必须把"代码层改造"列为 P0/P1 任务，否则同款问题会以新形态复发（5/18 ghost positions 修了数据没修流程，5/19 自动下单流程立刻以 OPG expired 形态复发，相隔 24h）。所有 INSERT DB 状态的代码点必检：status 是否反映 broker 实际状态？异步执行用中间态（submitted/pending）+ reconciler 后续更新。
