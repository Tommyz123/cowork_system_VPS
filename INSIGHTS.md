# Insights — 临时缓冲区

> **工作流：** 新经验写这里 → 健康检查触发审核 → 有价值的迁入 `reference/knowledge_base.md` → 清空
> 格式：`[YYYY-MM-DD] [项目/领域] 标题 → 内容（一两行，说清楚怎么用）`
> 已审核的稳定参考知识在：`reference/knowledge_base.md`

---






[2026-05-19] [P9/量化数据] OPG 单 Alpaca paper account 实测 fill 率 17%（1/6）→ 5/19 开盘 6 只 OPG 单仅 ASTE filled，5 只 gap up 超 limit 价 expired。影响：15 只满载 × 17% ≈ 2-3 只/次成交，buying_power 长期闲置，sample 累积慢（一年约 8-12 个数据点）。Q3（8/4）扫描预期 2-3 只成交，不要期待满载。[ref-worthy]

[2026-05-19] [cowork系统/架构] 三层索引架构：对话历史 / 平铺索引 / 知识图谱互补不替代 → Layer 1 = cowork.db（对话 FTS5+向量，找过程）；Layer 2 = MEMORY.md/INDEX.md（人工指针，定位文件）；Layer 3 = 知识图谱（节点+边，找规则波及范围，待建）。三者用途不同，不能互相替代。Layer 3 触发条件：2 周内 ≥3 次漏更新关联文件 friction。[ref-worthy]

[2026-05-18] [P9/数据完整性] AI 写的数据需要验证；DB 不一定是真实持仓 → cognitive_scanner.py 设计是只写 DB candidate 不下单，但 status='open' 语义被下游误读为"已成交持仓"。所有自动化数据分析必须有 reconciliation 机制对账外部权威系统（Alpaca 是持仓 SoT，DB 是 thesis SoT）。

[2026-05-18] [P9/研究方法] 红队对抗审核（adversarial review）暴露盲区效果显著 → 让独立 Opus subagent 不知情持仓状态写 bear case，揭示 5 个 Claude 自写 bear thesis 完全没覆盖的角度（地热衰减资本化 / Puna 集中度 / Kenya FX / 储能 merchant 估值 / IRA 政策）。研究框架阶段对每个重要 thesis 跑红队强烈推荐。[ref-worthy]

[2026-05-18] [P9/写作纪律] Thesis 写作纪律：hypothesis 语气 + 范围>单点 → 未验证精确数字（"forward P/S >30x" / "PE <7x"）会随时间漂移失效，不进 thesis 散文只放监测信号；推荐操作用范围（"trim 30-60%"）而非精确百分比。真正分水岭是"可证伪 vs 不可证伪"，不是"简单 vs 聪明"。[ref-worthy]

[2026-05-18] [AI协作/sub-agent] AI 子 agent 任务设计模板 → 3 轮 Opus subagent 质量高的共性：(a) 输出格式严格固定、(b) 反糊弄条款明确（"不许只是 inverse"/"至少 3 layer 5-why"）、(c) Quality bar 标准说明（"读起来像 institutional analyst 而非 Twitter call"）。Prompt 里这 3 点缺一不可。

[2026-05-14] [AI协作/决策] Opus 作为第二意见的正确用法 → 复杂规则/架构决策=先问 Opus，个人倾向/执行细节=直接做。本次 3 处 Opus 独立分析均给出有据可查的推理而非附和，双重验证后置信度明显更高。

[2026-05-14] [cowork系统/规则设计] "不加规则"也是一种决策，需要记录理由 → 摩擦讨论后决定不加规则，理由是"被现有规则覆盖"或"单次违规不够升级"。先问"已有规则为什么没执行"比直接加规则更根本——不是所有摩擦都该变成规则。

[2026-05-12] [P9/trading] price_snapshot skipped=N 是正常行为 → outcome_tracking 里的持仓打标不满30天时，全部 skipped，updated=0，不是bug；当前6个持仓 2026-05-06 打标，30天里程碑最早 2026-06-05 才触发更新

[2026-05-12] [cowork系统/AI协作] "主动审主公"是高杠杆机制 → 主公"逃避取舍"的本质是承诺没有外部追责。把"周一主动审 CURRENT_SESSION 老化项目"做成 cron 任务，比写 5 个 Hook 加起来都有效。这是对主公最有商业价值的 AI 能力使用方式。[ref-worthy]

[2026-05-12] [cowork系统/AI协作] AI 工具杠杆放大的是已有判断力，不是凭空创造 → 同样的 Claude Code 给没有系统思维的人做出来是一坨屎；给有系统思维的人做出来是有结构的东西。工具是放大器，不能脱离模型谈"独立能力"——工具和人互相成就。参照点：纠结"要不要学 SDK 底层"时用这条。

[2026-05-12] [cowork系统/自我认知] "对 AI 严格 vs 对自己业务松"是核心管理盲点 → 对 AI 要求立场一致性/不许吹捧/数据诚信，但对自己项目的"暂停 vs 死亡"判断是软化的。严格用错了对象——把对 AI 的严格度分一半给自己的业务决策。参照点：做项目取舍时用这条。

[2026-05-12] [P8/P12/定位] 主公的 AI 能力定位是"AI Workflow 架构师" → 不是 AI 工程师（算法/SDK 实操弱），不是 AI 产品经理（还没把 AI 变成有人付费的东西）。第 4 层（多 agent 编排/系统集成）是主战场，应把这层能力变成"别人愿意付钱的东西"（求职作品 / Cannabis Budtender 商业化），而非纵深到第 1-2 层（算法/SDK）。
