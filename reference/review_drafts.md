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

## [草稿] 2026-06-10 深度审核（session e8643b8d，P9审核+方向定案）

### INSIGHTS 建议写入（2条）
1. **[评分:4]** LLM打分系统必须给硬数据约束，否则编分+通胀 → P9实锤：prompt要求LLM按"分析师覆盖少"打market_lag分但没喂覆盖数数据，结果32个标的全9-11分；6/10补记真实数据后发现15只持仓覆盖5-11个无一冷门=分数是编的。规则：LLM评分维度所需数据必须在输入里，拿不到数据的维度改程序算分或留空，禁止让LLM"从字里行间猜"。适用任何LLM评分/筛选系统（P9/趋势主线/未来agent评审）[src:e8643b8d]（冷启动保守送审，本可5分自动写）
2. **[评分:3]** INSIGHTS已写的"Alpaca OPG部分成交expired陷阱"[ref-worthy] → 建议升入 reference/knowledge_base.md 技术踩坑区块（趋势主线复用对账代码时会再用到）[src:e8643b8d]

### Friction 建议升级（1条）
- **[评分:4]** 连续"没理解"≥2次=优先怀疑答非所问而非讲太难，停下列选项确认问题本身 → 今日实例：主公问"哪个好"我答错对象，连讲2轮简化版无效，第3轮确认才发现答非所问。建议并入 feedback_pacing_and_plain_language.md 作增补条款（friction_log 已记原始记录）[src:e8643b8d]

### 操作记录 建议起草（1份）
- **[评分:3]** 主题：幽灵持仓家族第3次复发RCA（OPG部分成交反向幽灵）/ 背景：按feedback_auto_rca属major应有RCA文件，今日修复时只记了log+playbook未写rca/文件 / 建议文件名：trading/rca/2026_06_10_opg_partial_fill_ghost.md（short模板即可，素材全在cowork_log 6/10条目）

### 收工Skill 建议修复（1处）
- **[评分:3]** 收工SKILL.md步骤4的 `grep -A 25 "本次完成（${TODAY}"` 会命中CURRENT_SESSION.md里**其他项目**同日区块（今日实锤：抓到P2的memory工作，haiku摘要全错，已手动修DB）→ 建议改为先按本次project_ids定位项目块再grep日期

### 文档对齐待处理（1处）
- **[评分:2]** ARCHITECTURE.md：双层结构(趋势主线=独立新系统)暂未登记——建议等趋势手册/系统实际落地后再加章节，现在只有方向定案无实体

### CLAUDE.md 微调建议（1处）
- **[评分:2]** "token操作走token_utils.sh"未写路径(实际在~/.claude/hooks/)，今日猜错一次 → 建议补路径
