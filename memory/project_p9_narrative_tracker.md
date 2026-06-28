---
name: project_p9_narrative_tracker
description: P9 公司叙事追踪系统（建仓前研究跟踪）—— 2026-06-27 上线，VST 试点等 8/6 财报第一次对答案
metadata: 
  node_type: memory
  type: project
  originSessionId: c84032e9-d1ee-4bda-98cd-671b54a6273c
---

P9 新子系统「公司叙事追踪」（2026-06-27 主公提"新闻追踪"→CC/Codex 两轮对抗审核后落地）。是「主题累积研究 Loop」的**公司粒度分支**。

**核心哲学（不可动）**：「新闻不是资产，假设才是资产。绑不到任何假设的信息不准进档案。」防止沦为"勤奋新闻笔记库"。判断是否笔记库的唯一标准=改变过决策没有。

**它补的空白**：现有 thesis_monitor/scanner_picks/dossier_autowrite 全围绕"已建仓持仓票"，这套补"**建仓前/观察期**对象的持续假设追踪+关注点演化+对答案"。
**边界铁律**：对象一旦真建仓 → 假设追踪移交 thesis_monitor/scanner_picks（status 置 `已移交持仓监控`），本系统只管建仓前。防 4 套打架。

**结构**：trading.db 4 表（narrative_hypotheses 假设 / narrative_evidence 证据(绑假设id) / narrative_weekly_checkins 周记 / narrative_discard_log）。脚本 `narrative_dossier.py`(手动录入CLI) + `narrative_earnings_watch.py`(每天08:00 cron财报哨兵,从假设表解析追踪票不硬编码,临近5天Discord提醒)。

**当前状态**：VST 1 只试点（假设A核心=AI电力需求含核电观察点 / 假设C次要=量vs价，均信心3、复看 2026-08-06）。先跑 6-8 周验流程，**结论限定"工作流值不值得扩展"非"系统有效"**，通过再铺 3 只。**8/6 VST 财报=第一次对答案+把"待核实"阈值用真实数据补准**。

跑法：CC 每周扫新闻绑假设更信心发一行周记，关键节点(假设触发/失效)才拉主公做真决策。方案全文 `trading/notes/新闻追踪方案_2026-06-27.md`。与 [[project_p9_trading]] 同库不同表；承袭 [[feedback_tracking_facts_only]] 分层 + [[feedback_data_driven_no_hardcode]]。
