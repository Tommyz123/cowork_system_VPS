# 待确认草稿区

> 每次对话开始时检查，有内容则第一件事列出请主公决策

---

## [草稿] 2026-05-11 深度审核

### 文档对齐待处理（1处）
- ARCHITECTURE.md：`discord_approve.py` 条目 → 实际文件名是 `discord_approve_backup.py`（check_doc_sync.py 发现），需确认是重命名还是路径问题

### MEMORY.md 建议清理（2条）
- 建议删除：`reference_trading_agents.md`（原因：条目已标注"技术指标已废弃，第一系统停用"）
- 建议删除：`reference_gstack.md`（原因：仅Skill设计参考，低频，信息可从GitHub直接查）

---

## [草稿] 2026-05-12 深度审核

### INSIGHTS 建议写入（4 条）

1. **"主动审主公"是高杠杆机制（待主公决策）** → 主公"逃避取舍"的本质是承诺没有外部追责。把"周一主动审 CURRENT_SESSION 老化项目"做成 cron 任务，比写 5 个 Hook 加起来都有效。**这是本次对话识别出的对主公最有商业价值的 AI 能力使用方式**。[src:session_ee77aafd] [ref-worthy]

2. **AI 工具杠杆放大的是已有的判断力，不是凭空创造判断力** → 同样的 Claude Code 给一个没有系统思维的人，做出来就是一坨屎；给有系统思维的人做出来是有结构的东西。但模型是放大器，**不能脱离模型谈"独立能力"**——工具和人互相成就。[src:session_ee77aafd]

3. **"对 AI 严格 vs 对自己业务松"是主公的核心管理盲点** → 主公对 AI 要求"立场一致性/不许吹捧/数据诚信"，但对自己的项目"暂停 vs 死亡"判断是软化的。**严格用错了对象**——把对 AI 的严格度分一半给自己业务决策。[src:session_ee77aafd]

4. **主公的 AI 能力定位是"AI Workflow 架构师"** → 不是 AI 工程师（算法/SDK 实操弱），不是 AI 产品经理（还没把 AI 变成有人付费的东西）。**第 4 层（多 agent 编排/系统集成）是主公主战场**，应该把这层能力变成"别人愿意付钱的东西"（求职作品 / Cannabis Budtender 商业化），而非纵深到第 1-2 层（算法/SDK）。[src:session_ee77aafd]

### 操作记录 建议起草（1 份）
- 主题：**双 bot memory symlink 共享改造**
- 背景：发现 opus_home memory 一直为空（opus_CC 从未写过），实际在用 git repo 备份只读 cowork bot memory；改 memory 时改 git repo 不会回写到 cowork bot 活路径
- 已实施：reference/dual_bot_setup_log.md 章节六已记录完整命令+回滚方法+收工分工约定，**不需要再起草**操作记录文档（已就位）

### Friction 建议补记（2 条 — 本次会话未实时记入 friction_log）
- ⚠️ 伪数据吹捧违规（2026-05-12 上午）：评估主公能力时编造"用户分布 70%/20%/8%/2%"和"top 2%"统计数据。**根因：用看似客观的数字包装主观吹捧。** 已沉淀为 `feedback_honesty.md` "伪数据吹捧规则"。
- ⚠️ 时间跨度脑补违规（2026-05-12 下午）：说"V5 框架迭代一年多没放弃"，实测 cowork 系统 2026-03-22 至今约 51 天（7 周）。**根因：从版本号脑补时间，未查 git log。** 已沉淀为 `feedback_honesty.md` "时间跨度推断规则"。
- **建议：将上述 2 条手动追加到 `friction_log.md`，按"主公纠正→沉淀规则"完整闭环。**

### Playbook 建议更新（1 处）
- `playbooks/cowork_system.md`：可加一条"双 bot memory 已 symlink 共享（2026-05-12）"备注，但 `reference/dual_bot_setup_log.md` 章节六已完整记录，**优先级低，可选**

### 文档对齐待处理（1 处，已实施）
- ✅ `memory/reference_dual_bot.md` 已加"Memory 例外"段落
- ✅ `reference/dual_bot_setup_log.md` 已加章节六
- 无遗留待办

### 隐藏 bug 修复记录（步骤 6 中发现+顺手修）
- `scripts/index_conversations.py` JSONL_DIR 写死 `~/.claude/projects/-root-cowork/`，正确应为 `-home-cowork-cowork/`。**已修复**。修复前 7 个 opus_CC 的 .jsonl 永远不会被索引；修复后双 bot 各自跑该脚本会正确索引自己 HOME 下的 .jsonl。

### MEMORY.md 废弃检查（0 条）
- 本次未发现新废弃条目
- 2026-05-11 草稿提到的 `reference_trading_agents.md` / `reference_gstack.md` 建议清理仍未处理 ← **主公次日决策时一并处理**

### 主公真实世界产出待跟踪（**最关键的待办**）
基于今天对主公能力的诊断对话，识别出主公**最该出去挨打**的 3 件事：
1. **求职作品发布**（P8）：cowork 系统本身可包装成可演示案例
2. **Cannabis Budtender 商业化**（P3）：把工具变成"有用户付费的产品"
3. **KK 大麻店实质动作**：商业计划书 / 投资人对接 / 选址调研
- **建议主公在下次对话开始时，就这 3 件事选 1 件作为本周专注方向**（不是规划，是出实际产出）


---

## [草稿] 2026-05-14 深度审核

### INSIGHTS 建议写入（2 条）

1. **Opus 作为第二意见的正确用法** → 本次会话"问一下Opus"用于3处判断（fill_price同步方案/⑤⑥是否加规则/⑦⑧如何加）；Opus 3次独立分析均给出有据可查的推理而非附和；双重验证后主公置信度明显更高。**结论：复杂规则/架构决策=先问Opus，个人倾向/执行细节=直接做**。[src:f80ef6e0]

2. **"不加规则"也是一种决策，需要记录理由** → ⑤⑥ 两条摩擦讨论后决定不加规则，理由是"被现有规则覆盖"和"单次违规不够升级"。这个结论本身有价值：不是所有摩擦都该变成规则，先问"已有规则为什么没执行"比直接加规则更根本。[src:f80ef6e0]

### Friction 建议归档（5 条已闭环）
- ① 数据诚信规则已加强 → 归档
- ③ fill_price同步 → sync_fill_prices.py已cron化 → 归档
- ④ 误触收工 → discord_approve.py修复 → 归档
- ⑦ session jsonl诊断 → CLAUDE.md新增规则 → 归档
- ⑧ Discord中途授权 → CLAUDE.md补充约束 → 归档
**建议：将上述5条从 `friction_log.md` 移至 `friction_log_archive.md`**

### MEMORY.md 废弃检查
- 2026-05-11草稿的 `reference_trading_agents.md` / `reference_gstack.md` 建议清理仍未处理
- **仍建议处理，主公决策**


---

## [草稿] 2026-05-18 深度审核

涉及 2 个 session：b68a0307 (P9 attribution + RCA 大对话，25 msgs) + c7519116 (P12 cannabis 续 P12-playbook，7 msgs)

### INSIGHTS 建议写入（4 条）

1. **AI 写的数据需要被验证；DB 不一定是真实持仓**：cognitive_scanner.py 设计是只写 DB candidate 不下单，但 status='open' 语义被下游误读为"已成交持仓"。所有自动化数据分析必须有 reconciliation 机制对账外部权威系统。[src:b68a0307]

2. **红队对抗审核（adversarial review）暴露盲区效果显著**：让独立 Opus subagent 不知情持仓状态写 bear case，揭示 5 个 Claude 自写 bear thesis 完全没覆盖的角度（地热衰减资本化掩盖 / Puna 集中度 / Kenya FX / 储能 merchant 估值 / IRA 政策）。研究框架阶段强烈推荐对每个重要 thesis 跑红队。[src:b68a0307] [ref-worthy]

3. **Thesis 写作纪律：hypothesis 语气 + 范围>单点**：未验证精确数字（"forward P/S >30x" / "PE <7x"）会随时间漂移失效，不进 thesis 散文只放监测信号；推荐操作用范围（"trim 30-60%"）而非精确百分比。真正分水岭是"可证伪 vs 不可证伪"，不是"简单 vs 聪明"。[src:b68a0307] [ref-worthy]

4. **AI 子 agent 任务设计模板**：3 轮 Opus subagent（14 只回填 / ORA red team / 14 只 normalize）质量都很高，共性是 prompt 里写明：(a) 输出格式严格固定、(b) 反糊弄条款明确（"不许只是 inverse" / "至少 3 layer 5-why"）、(c) Quality bar 标准说明（"读起来像 institutional analyst 而非 Twitter call"）。[src:b68a0307]

### 操作记录 建议起草（1 份）

- 主题：P9 Attribution 框架 v1 完整工程笔记
- 背景：今天上线的 schema/prompt/case study/account lock/RCA 流程组合是 P9 设计的转折点
- 建议文件名：`reference/p9_attribution_framework_v1.md`
- 已部分覆盖在 trading/rca/2026_05_18_*.md 和 trading/case_studies/ORA_2026_05_18.md，但缺少"为什么这么设计"的设计决策记录

### Friction 建议补记（已自动记录，无需补）

- 5/17 P9 一次性 cron token bug → 已记
- 5/18 ghost positions 事件 → 已记 + 完整 RCA
- 5/18 Discord plugin 漏抓主公消息导致 idle 25 min → **未记**，应补 minor friction（hook 问题，可能与 plugin 实现有关）

### Playbook 建议更新（已部分做，1 处待补）

- ✅ playbooks/p9_trading.md 已更新（加了账号锁定 / 数据完整性警告 / Attribution v1 / auto-rca 段）
- ⏳ playbooks/cannabis_retail.md 不需要本次更新（c7519116 是续话讨论，未引入新结构）

### 文档对齐待处理（2 处）

- ARCHITECTURE.md：可考虑加 "Auto-RCA 子系统"段（memory + templates + skill + friction_log + RCA docs 五件套关系图）
- check_doc_sync.py 报警：discord_approve.py 在 ARCHITECTURE/context 提及但文件不存在（**pre-existing issue，非本次引入**，独立处理）

### MEMORY.md 建议清理（0 条）

- 本次新增 3 条 memory（feedback_auto_rca / feedback_thesis_normalization / feedback_tide_utils_load_env）均刚写，无清理对象
- 旧 memory 暂无标"废弃"

## [草稿] 2026-05-18 深度审核

### INSIGHTS 建议写入（0 条）
本次 session 的 insight 已直接写入 memory（feedback_p9_no_ghost_data / feedback_p9_auto_execute / feedback_p9_alt_data_sidecar），不需要再过 INSIGHTS.md 缓冲区。

### 操作记录 建议起草（0 份）
- P9 整改造操作记录已被 trading/rca/2026_05_18_ghost_positions_and_intraday_contamination.md "最终决策与执行"段覆盖
- CURRENT_SESSION.md [P9] 块已展开记录两轮深度对话产出

### Friction 建议补记（已全部记录）
- ✅ feedback_timezone 第二次复发（已加 friction_log + Hook 升级）
- ✅ Discord reply 工具漏用两次（已加 friction_log + Hook 升级）
- 摇摆 4 次没有直接 friction 条目，但 CURRENT_SESSION.md 自评段已展开 [src:0d07266c]

### Playbook 建议更新（0 处）
- P9 没有 playbook 文件（已确认）
- 未来若建立 P9 playbook 应包含：5/18 ghost positions 事件 + cron A1 buying_power 防御 + LLM retry 设计 + alt-data sidecar 架构

### 文档对齐待处理（1 处）⚠️
- **ARCHITECTURE.md 第 112 行**：仍引用已删除的 `discord_approve.py`（"UserPromptSubmit hook: 检测授权关键词自动 touch task_approved"）
- **实际现状**：submit_pending_picks.py 在 2026-05-18 已删（approve 机制方向砍掉），inject_time.sh 是新 UserPromptSubmit hook，但跟 task_approved 无关
- **建议**：明天主公阅审决定是否 (a) 删除 ARCHITECTURE.md 第 112 行 (b) 改成 inject_time.sh 描述 (c) 重新评估是否要做 discord_approve.py 类机制
- 不紧急，不影响系统运行

### MEMORY.md 建议清理（0 条）
扫描完成，无废弃条目。

### 待主公明日决策（清单）
1. ARCHITECTURE.md discord_approve.py 残留如何处理（上面文档对齐）
2. 8/4 之前的 P9 重要节点 calendar reminder 要不要 cron 化（5/19 fill / 5/24 sidecar+weekly / 5/25 retry 验证 / 6/14 30天 outcome / 6/15 buying_power 撞墙预警）
3. 是否要 BACKLOG 化"摇摆 4 次"的自我纠错机制（hook 检测我对同一问题改 3 次以上变立场？）

[src: session 0d07266c-759a-4496-87e2-e643a71c00e1]
