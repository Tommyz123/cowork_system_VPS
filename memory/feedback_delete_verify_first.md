---
name: feedback_delete_verify_first
description: 删除/精简文件内容前，必须先验证目标状态已就绪（信息已在其他地方存在），不能只看要删的文件
type: feedback
---

删除或精简某文件的内容前，必须先确认"接收方"已就绪——即那些信息在其他地方已经存在。

**Why:** 2026-05-02 整理 project_*.md 时，我直接出了"删技术配置"的计划，但没有先读 playbooks/ 确认配置是否已在那里。如果执行了，可能会丢失信息。主公指出这个漏洞后，我自我纠正。

**How to apply:**
- 要删 A 文件的内容 → 先读 B 文件（目标地），确认内容已在 B 里
- B 有 → 可以删 A
- B 没有 → 先补 B，再删 A
- 适用场景：整理 memory/、迁移 playbook、清理 CURRENT_SESSION.md 过期条目等一切"搬迁型"操作
