---
name: project_cowork_roadmap
description: Cowork系统定位、多agent架构路线图和发展方向（2026-05-08更新）
type: project
originSessionId: 7c28c936-b9d6-4c38-900c-13e6e9aec5ed
---

**系统终极定位（2026-05-08确认）：**
Cowork = 主公的"项目管家/私人助理"，不是multi-agent调度器。扩展方向围绕"管理主公所有项目"（trading/求职/contract/内容/财务等），不是工程化炫技。当前完成度约60-70%，缺跨项目关联/决策辅助/时间管理三块。VPS 4GB永远够这个定位，不需要multi-agent。

**Why:** 主公明确定位，防止过度工程化。
**How to apply:** 评估新功能/新自动化时，先问"这是否服务于管项目"，否则不做。
**多agent架构路线图（2026-04-20主公确认）：**
1. 先修 Codex login（已完成）
2. 验证我+Codex协作（已测试通过）
3. 加主动推送（任务完成自动通知Discord）
4. Mac mini上线（24/7在线）
5. 再扩展其他agent

**Why:** 逐步添加，每步验证稳定再加下一个，稳比快重要。

**How to apply:** 有人提议加新agent或新自动化时，先确认当前阶段是否稳定，按路线图顺序推进。路线图可灵活调整，我有更好判断时主动提出讨论，主公认可后再改。不主动建议加固定子agent，除非主公遇到真实痛点（等待30分钟以上的任务）。当前我+Codex两层够用（2026-04-20确认）。

---

**Codex审核给出的3个发展方向（优先级顺序）：**
1. **自动任务监控**：cron任务加heartbeat+失败推送Discord，5个任务都没有失败通知
2. **关键规则代码化**：把高风险规则从Markdown变成Hook脚本
3. **统一项目状态层**：projects.json替代纯Markdown，等Mac mini后做

**Why:** Codex独立审核CLAUDE.md和CURRENT_SESSION.md后给出的判断，和主公讨论后认可。

**How to apply:** 推进cowork系统优化时按此优先级，不要颠倒顺序。
