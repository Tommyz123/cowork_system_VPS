# 待确认草稿区

> 每次对话开始时检查，有内容则第一件事列出请主公决策

---

## [草稿] 2026-06-10 深度审核（memory统一收工 + 4个零散问答session）

> 审核 session：464afa6b（本会话：memory漂移根治+prediction_method落地）+ 422529b2/70876a8f/cd30861d/da60d98b（模型问答/重启确认小session）

### 送审（2-3分，等主公决策）
1. **[评分:3]** 收工 SKILL.md 两处改进建议：①步骤3"memory 备份 cp（原生→cowork/memory）"在 symlink 合一后已无意义（同一文件自拷贝），建议删除该小步；②深度审核 4-5 分自动写入的条目曾同时留在草稿送审区致重复送审（friction 2026-06-09 16:57 实证），建议 SKILL.md 明确"自动写入条目只进🤖摘要区，不进送审编号列表"。改 Skill 需主公点头。[src:464afa6b]
2. **[评分:2]** 问实例"你是什么模型"不可靠，必须查 `$HOME/.claude/settings.json` 的 model 字段：旧 CLI 下实例会否认晚于自己的型号存在（da60d98b 实证：AA 答"没有 Fable 5 这个模型"）。建议入 knowledge_base CLI工具行为区块。[src:da60d98b]

### 🤖 本次自动写入摘要（4-5 分，已在对话中实时写入）
- **[评分:5]** INSIGHTS [ref-worthy]：memory 双目录漂移根治（根因+修法+跨实例断言逐实例实测教训）→ 已写 `INSIGHTS.md`（待迁 knowledge_base）
- **[评分:4]** reference_dual_bot.md：Memory 例外区块更新 + 新实例上线 checklist → 已写入（主公授权）
- **[评分:4]** ARCHITECTURE.md 记忆层 v5：纠正 v4"原生从未写入"误判 → 已写入
- **[评分:4]** friction×2：跨实例断言被纠正 / 草稿重复送审 → 已写 `friction_log.md`

### 🗑️ 本次自动丢弃摘要（1 分，未保留）
- 共 3 条 1 分候选丢弃（模型身份问答细节、重启确认流程复述、与 6-09 已审内容重复的 BB/CC 混淆）
