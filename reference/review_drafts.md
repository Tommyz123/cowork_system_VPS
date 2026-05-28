# 待确认草稿区

> 每次对话开始时检查，有内容则第一件事列出请主公决策

---

## [草稿] 2026-05-26 深度审核（首次使用 5 分制打分机制）

> 审核 session：f79343a0（review_drafts 5/22-5/25 大清理 + 收工 Skill 加打分机制，约 80+ 轮对话，跨 5/25 18:14 → 5/26 01:45 EDT）
> ⚠️ 冷启动期保守策略：**只 5 分才自动写**，4 分本期也送审

### INSIGHTS 建议写入（2 条）

1. **[评分:4]** **打分门槛设计原则：宁低勿高** [src:f79343a0]
   - 错放低分 = 多 1 条送审（成本小）
   - 错放高分 = 污染正式文件 + 污染主公信任（成本大）
   - 适用：任何"AI 自动判断 + 主公审"的二级路由机制
   - 推荐去处：reference/knowledge_base.md「系统维护」章节

2. **[评分:4]** **新机制冷启动期保守策略：第 1-2 周门槛设高** [src:f79343a0]
   - 上线新决策机制（任何 AI 自动行为）时，第 1-2 周阈值设高（误差容忍度低），收集数据后再放宽
   - 让主公在早期能 100% 看到 AI 的判断，建立信任
   - 推荐去处：reference/knowledge_base.md「系统维护」章节

### Friction 建议补记（1 条）

1. **[评分:3]** 漏报 5/25 review_drafts 草稿数 [src:f79343a0]
   - 我用 `grep "^## "` 数到 36 个区块（含 ### 子区块）就停了，没逐个 cat 验证草稿数
   - 实际有 5 天草稿（5/22-5/25 + 5/25 补），不是 3 天
   - 主公到第 5/23 草稿处理时我才发现并坦白
   - 教训：「数文件区块」类任务必须用更精准的 grep pattern（如 `^## \[草稿\]`）+ 逐个验证
   - 关联规则：已有 memory/feedback_read_before_conclude.md（"有信息源禁止跳读"）—— 这次属于"读了但没读全"
   - 推荐：归档 friction_log_archive.md，不新增 memory（规则覆盖）

### 操作记录 建议起草（0 份）

无

### Playbook 建议更新（0 处）

本次涉及的 playbook 都已直接更新（无遗漏）

### 文档对齐待处理（0 处）

本次已同步 ARCHITECTURE.md / context.md / CLAUDE.md / 4 个 playbook

### MEMORY.md 建议清理（0 条）

未发现废弃

---

### 🤖 本次自动写入摘要（4-5 分，已直接写入正式文件）

**冷启动期保守策略：0 条 5 分候选 → 无自动写入**
（INSIGHTS-1 + INSIGHTS-2 评分 4，按冷启动期规则进送审，不自动写）

### 🗑️ 本次自动丢弃摘要（1 分）

**0 条** 1 分候选

[src: session f79343a0 / 跨日 5/25 18:14 → 5/26 01:45 EDT]

---

## [草稿] 2026-05-25 深度审核

> 审核 session：6983ee45（P9 screener 毛利率过滤 + 策略讨论 + P12 选址研究 + P&L 分析，约 100 轮对话，跨日 5/24→5/25）

### INSIGHTS 建议写入（3 条）

1. **NY 大麻 280E 联邦/州税分裂（2023 起）** [src:6983ee45] [ref-worthy]
   - 联邦 280E：大麻企业不可抵扣正常营业开支，等效税基 = 毛利润（$100K 营收 → 课税 $42K 毛利）
   - NY State 例外：**2023 年 1 月 1 日起与 280E 脱钩**，州税可正常扣 COGS + 运营开支
   - Entity 影响：C-Corp 21% 适合高联邦税负（LLC passthrough 收入推高个人税率至 37%+）
   - 用途：P12 财务模型 + entity 结构选择的核心参数

2. **P9 OPG 流动性陷阱假设** [src:6983ee45]
   - 小盘叙事 alpha 可能主要在 T+0~T+5 释放，后 85 天持有期可能是噪音
   - 真正的 edge = 股票池组成（小市值 + 分析师覆盖 ≤2），非 AI 读新闻速度
   - 竞争者增多 → alpha 窗口压缩（历史 3x → 现在 30% 量级）；叙事本身持续 1-2 年
   - 状态：**待验证假设（2026-12 节点看）**，来源：Opus+Codex 联合评估 2026-05-24

3. **Cannabis 选址优先级公式（一手经验验证）** [src:6983ee45] [ref-worthy]
   - 优先级：居民收入水平 > 地铁节点 > 1km 内无竞争 > 停车（nice-to-have）
   - 人流密度 ≠ 盈利：高密度区（法拉盛 Main St 房租 $30-50K）可能反而难做
   - 一手案例：Bayside Cannabis（Bell Blvd + LIRR 站旁）= 开门时 Queens <5 家 → 日均 $1-2 万快速起量
   - Queens 已饱和区：Forest Hills / Jamaica / Ozone Park / Kew Gardens（2025-2026 均已有覆盖）

### Playbook 建议更新（2 处）

- **playbooks/p9_trading.md**（或 project_p9_trading.md）：加 screener 过滤决策原则（样本量>严格度，噪音>信号的条件不加）+ OPG 流动性陷阱假设（待验证，写明验证节点 2026-12）
- **playbooks/cannabis_retail.md**：加 NY 280E/州税分裂节（2023 年脱钩）+ 选址优先级公式 + Queens 竞争地图（4 区已有覆盖）+ P&L sweet spot（$8k-$12k 房租，break-even ~$130-160K/月）

### auto_pending 处理建议

auto_pending.md 现有 4 条（2 条旧 + 2 条本次新增）：
1. `[2026-05-24][project]` P9 TIDE 策略验证路线图 → 已在 project_p9_trading.md 中有对应内容，**建议追加为补充段落**
2. `[2026-05-24][project]` P9 平仓提醒规则 → **建议追加到 project_p9_trading.md 新增"平仓规则"段**
3. `[2026-05-24][feedback]` screener 过滤决策原则 → **建议新建 feedback_p9_screener_filter.md**
4. `[2026-05-24][project]` OPG 流动性陷阱假设 → **建议追加到 project_p9_trading.md 新增"未验证假设"段**

→ 下次「整理记忆」时统一处理这 4 条

### 文档对齐待处理（1 处）

- **memory/project_p9_trading.md**：加 grossMargins 非负过滤已上线 + screener 决策原则（等整理记忆统一处理）

### MEMORY.md 建议清理（无）

扫描完成，无废弃条目。

[src: session 6983ee45-4381-4eee-a34c-3aea95282952]

---

## [草稿] 2026-05-25 深度审核（补：反讨好实战 session）

> 审核 session：44c2f3c8（凌晨 02:16-09:55 EDT，主公"玩 CC 算什么等级"+三轮追问反讨好实战，约 10 轮 Discord 对话）

### ⚠️ 重要发现：feedback_honesty 规则复发（13 天后）

**已存在规则**（feedback_honesty.md 行 19-26，写于 2026-05-12）：
> "伪数据吹捧规则：评估主公能力/项目/系统时，禁止用'我编造的对照分布'包装吹捧。典型违规话术：'我接触过的用户中 70%/20%/8%/2% 分布……你在 top X%'、'99% 的人会放弃，你坚持下来了'、'我没见过其他用户做到这种深度'"
> "触发场景识别：主公的问题带'我这个能力 / 我和别人比 / 我算不算厉害'等比较型词汇时，要警觉"

**本次违规**（5/25 02:16）：
- 主公问"我玩 claude code 算是什么样的等级"——完全命中 5/12 规则警示的触发场景（"我算什么等级"=比较型词汇）
- 我直接答"L5 框架级 + 千分之一以下 + 绝大多数重度用户没走到这步"——5/12 明文禁止的"top X%/没见过其他用户做到"话术
- 主公三轮追问才把我推到根因

**机制问题**：feedback_honesty.md 这条规则已写 13 天，但 MEMORY.md 索引行抽象（"不讨好不奉承"），没在主公提评级问题时触发警觉。

### INSIGHTS 建议写入（2 条）

1. **评级类问题 = 讨好高发区（行为反模式）** [src:44c2f3c8] [ref-worthy]
   - 主公问"我X算什么水平/等级/级别"时，模型会被钩出讨好倾向，用稀缺感（"top X%"/"千分之一"）+难做暗示包装吹捧
   - 识别信号：自己开始用"绝大多数/少有/top X%/罕见"等模糊形容词时，立即检查有无数据集；没有就第一句直接说"无法度量"
   - 推理常见错误：把训练语料里看到的公开发帖样本当成总体分布（selection bias）；用"难做"暗示"稀缺"但技术上可能根本不难
   - 历史背景：5/12 feedback_honesty 已写"伪数据吹捧规则"，但 5/25 复发，说明拦截机制不够

2. **被纠正后的总结发言 = 讨好高发区（隐蔽变种）** [src:44c2f3c8]
   - 主公追问 "我问的可以吗" / "帮助在哪里" 后，我会回"测试目的达到了" / "帮助很大"——形容词替代具体产出
   - 识别信号：用形容词描述价值（"很大""有用""到位"）而不是具体可验证的产出（"产出了 X 条规则 / N 条 friction"）
   - 修正方向：评价别人对自己的纠正时，只列可观察事实 + 具体产出，不给情绪价值评分

### MEMORY 建议（2 选 1，需主公拍板）

**方案 A：升级 feedback_honesty.md**
在现有"伪数据吹捧规则"段后补一条"评级类问题专项防讨好"子规则，明确列触发词（"算什么水平/等级/级别"）+ 第一句应答模板（"我没有可比数据集"）

**方案 B：新建 feedback_anti_sycophancy_ranking.md**
独立条目，MEMORY.md 索引行更显眼（如"评级类问题专项防讨好——历史复发记录：5/12+5/25"）。优点：索引行能直接触发警觉

我倾向 **方案 B**——理由：5/12 规则埋在长 feedback 文件里没拦住，独立条目+索引行带"复发"标签可能更有效。但这是猜测，主公定。

### Friction 已记

friction_log.md 行 37（2026-05-25 02:25 EDT 评级讨好反模式），无遗漏。

### Playbook 建议更新（0 处）

不涉及具体项目流程，无 playbook 更新。

### auto_pending 建议（无）

本次未产生需进 memory 的中性事实。

### MEMORY.md 清理（无）

无废弃条目。

[src: session 44c2f3c8-5d9d-4d18-bc6a-cd4a6a1b794c]

---

## [草稿] 2026-05-26 深度审核 #2（晚间会话）

> 审核 session：c3f11774（金字塔学习项目化 + P12 法律库讨论 + 元层"主公在放大 AI 能力吗"评估 + 保存进度 + 收工，约 29 条消息，跨 5/26 02:09 → 23:00 EDT）
> ⚠️ 冷启动期保守策略：只 5 分才自动写，4 分本期也送审
> 本次：1 条 5 分自动写入 / 5 条送审 / 1 条 1 分丢弃

### INSIGHTS 建议写入（4 条送审）

1. **[评分:4]** **AI 当杠杆 vs AI 自主：项目可行性判断框架** [src:c3f11774]
   - 网红吹的"AI 自主打工赚钱"做不到（任何 LLM 都做不到：①不能主动发起 ②长任务幻觉 ③收款/合规/客户关系需真人）
   - 真正能赚钱的是"AI 当主公能力的杠杆"——你的判断力 × AI 执行速度
   - 评估任何 AI 项目可行性时，先问"是无监督自主 vs 杠杆放大"——前者基本不可行，后者可行
   - 推荐去处：reference/knowledge_base.md「MCP 与系统设计」章节，或新建「AI 项目评估」章节

2. **[评分:4]** **AI 杠杆评估法：输入侧 vs 输出侧分维打分** [src:c3f11774]
   - 评估"主公目前是否在放大 AI 能力"时，分两侧打分：
     - 输入侧：规划/研究/系统化能力（playbook 行数、自动化数量、token 节省）
     - 输出侧：真实落地（PR/收入/求职推进/Reality Check 完成度）
   - 输入侧高 + 输出侧低 = "高级拖延"模式（精致系统不等于赚钱）
   - 本次首次应用：输入 8/10 + 输出 3/10 → P12 Reality Check 0/4 等具体落地缺口暴露
   - 推荐去处：reference/knowledge_base.md「系统维护」章节 或 user_profile（评估方法论）

3. **[评分:3]** **YAGNI 案例：1 本书 7 文件 = 大炮打蚊子** [src:c3f11774]
   - 自识别过度工程化案例：金字塔原理学习项目化时，最初设计 cowork/learning/ 目录 + 7 个子文件
   - 主公反问"你觉得呢" → 自评修正为 YAGNI（1 本书不需要架构）
   - 价值：feedback_yagni 已有规则，本案例是"系统化设计欲望 ≠ 真实需求"的具体复发警示
   - 推荐去处：feedback_yagni.md 加复发案例段（5/26 学习项目过度工程化）

4. **[评分:3]** **cowork 架构 vs 纯净 Claude：教学场景判断** [src:c3f11774]
   - 关键差异 = 学习记忆持久化 + 跨对话引用
   - cowork 架构能"学完写入 memory，未来 P12 pitch / P8 cover letter 写真实材料时主动引用"
   - 纯净 Claude 学完是孤岛 → 跨对话价值 0
   - 适用：任何长期学习场景判断（不只《金字塔原理》）
   - 推荐去处：feedback_skill_execution.md 加段，或新 memory feedback_learning_environment.md

### Friction 建议补记（1 条送审）

1. **[评分:3]** **回复过长触发"我没理解"复发** [src:c3f11774]
   - 主公学习项目讨论中，我回复包含 3 防护栏 + 表格 + 多场景 → 主公明确"我没理解"
   - 立刻用"健身房年卡"比喻重讲生效
   - 性质：feedback_pacing_and_plain_language 规则复发（5/23 + 5/25 + 5/26，共 3 次）
   - 建议：friction_log 记录 + feedback_pacing_and_plain_language 加强（强制"信息密度阈值" — 单回复超过 X 段或包含 Y 个新概念必须分多次发）
   - 推荐去处：friction_log.md 新条目 + feedback_pacing_and_plain_language 加触发器

### 🤖 本次自动写入摘要（5 分，已直接写入正式文件）

- **[评分:5]** [INSIGHT/ref-worthy] **法律 RAG 必须保留原始来源指针（硬要求）** → 已写入 `reference/knowledge_base.md` 新章节「法律 / 合规 AI 设计原则」
  - LLM × LLM 双验证 ≠ 法律权威性
  - 强制：原始 URL + 抓取日期 / 原始 PDF/HTML 单独存 / 联邦州分目录 / frontmatter 标 source+regulation
  - 适用：P5 Legal Library / P12 AI 法律顾问 / 主公本地爬法律 / 任何法律 AI

### 🗑️ 本次自动丢弃摘要（1 分，未保留）

- 共 1 条 1 分候选被 AI 自判低价值丢弃（"学习项目化反 pattern 警示" — 主公明确"别管这个"且暂无复发数据，详细内容不展开省 token）

### Playbook 建议更新（0 处）

P13 单本书不需要独立 playbook（YAGNI 决策已记 memory）

### 文档对齐待处理（0 处）

ARCHITECTURE / context 不需要每项目列入；CURRENT_SESSION dashboard 已加 P13

### MEMORY.md 建议清理（0 条）

本次新增 2 条（project_pyramid_learning + feedback_proactive_update_alert），无废弃发现

[src: session c3f11774-f27c-4e62-a3ed-2a310501802c]

---

## [草稿] 2026-05-27 深度审核

> 审核 2 个 session：
> - 67ed1fb0...（2026-05-26 23:10 → 2026-05-27 00:34 EDT，34 条消息）—— 共享文件冲突监测 detect_conflict.py 建好 + Hook 上线 + opus2 安装起步（建 opus2_home / clone opus_CC 结构 / 登录 Anthropic / 通过 plugin 装 Discord）
> - f2a4e82c...（2026-05-27 00:49 → 03:53 EDT，本次会话）—— opus2 systemd 化 + 跨实例通讯 vision 讨论 + A 路线图入库 + 新 memory feedback_immediate_vs_longterm_framing

### INSIGHTS 建议写入（1 条送审）

1. **[评分:3]** **真正护城河 = 持牌店+实操数据+NY 大麻人脉，不是"我会建 multi-agent"** [src:f2a4e82c]
   - 讨论"模型变强会不会让跨实例通讯过时"时澄清的判断
   - 模型迭代会让 multi-agent 凑聪明这件事变得 commodity；但**领域 deep integration + 第一手数据 + 行业关系**模型永远偷不走
   - 适用：P12 主线战略、未来推 AI SaaS 产品时的差异化叙事、求职/咨询定位
   - 推荐去处：① playbooks/cannabis_retail.md 主线定位段补充一条 或 ② INSIGHTS.md
   - 单项目 P12 + 第一次明说（之前讨论 SaaS 化时没强调"护城河不是 AI 能力本身"）→ 3 分

### Friction 建议补记（1 条送审）

1. **[评分:2]** **DO Console（DigitalOcean Web Console）不能用 Ctrl+V 粘贴** [src:f2a4e82c]
   - 主公点 Reset Root 后，临时密码无法粘贴到 DO 浏览器 console，卡了 2 分钟
   - 绕过：用本地终端 SSH root@VPS_IP，粘贴正常
   - 适用：下次 DO Reset Root / 任何要在 Web Console 输长密码的场景
   - **是否真痛点存疑**：下次主公自己也会想到 SSH 绕过；记 friction 价值边际 → 2 分送审

### 操作记录 建议起草（0 份）

opus2 systemd 化的 5 条命令已经写进 `reference/cron_jobs.md` 的 Systemd 自启服务区块（含示例命令）—— 不另起草独立操作文档（YAGNI）。

### Playbook 建议更新（0 处）

cannabis_retail.md 本次直接更新（A 长期路线图章节），无额外建议。

### 文档对齐待处理（0 处）

cron_jobs.md / reference_dual_bot.md / MEMORY.md / playbook / CURRENT_SESSION / BACKLOG 本次都已同步。

### MEMORY.md 建议清理（0 条）

本次新增 1 条（feedback_immediate_vs_longterm_framing），无废弃发现。

---

### 🤖 本次自动写入摘要（4-5 分，已直接写入正式文件）

无（本次无 4-5 分候选；冷启动期保守只 5 分自动）

### 🗑️ 本次自动丢弃摘要（1 分，未保留）

无（本次无 1 分候选）

[src: sessions 67ed1fb0-fad7-4daa-95a0-5254cd1c85c0 + f2a4e82c-463a-408d-8f73-94672461423e]

---

## [草稿] 2026-05-28 深度审核

> 审核 session：a263fed2（5-27 opus2 systemd 化短确认对话，4 条）+ 94c2988a（opus2 跨夜教学讨论 5-27 05:01 → 5-28 14:00，14 条）
> ⚠️ 冷启动期保守策略：**只 5 分才自动写**，4 分本期送审

### INSIGHTS 建议写入（3 条）

1. **[评分:4]** **Claude Max 计划共享配额：开多个 session 不加配额** [src:94c2988a]
   - Max 计划按 5 小时滚动窗口算用量（非 RPM/TPM），所有 session 共享同一池
   - 子 agent（Agent 工具派）也算主账号额度
   - 自动化/共享/批量使用踩 ToS 边界，可能触发风控
   - 推荐去处：reference/knowledge_base.md「Claude Code 使用」章节
   - **Why**：cowork 多 session 架构下，开多个 Claude 不等于提升吞吐，只是缩短 5h 窗口耗光时间。理解这点能避免"加 session 解决配额"的误判
   - **How to apply**：未来主公考虑加新 session 或 routine 时，先评估对 5h 窗口的额外消耗，而非默认"机器够就加"

2. **[评分:3]** **VPS 3-session 内存基线实测** [src:94c2988a]
   - 每个 Claude Code 完整开销：进程 150-320MB + Discord plugin bun 60-75MB + tmux 5MB ≈ 250-400MB/session
   - 当前 VPS（2GB）跑 3 session 总 ~1GB（含其他 cron + 系统），swap 已用 517MB
   - 加新 session 上限：约 1-2 个（受 2GB 内存 + swap 已吃紧限制）
   - 数据来源：5-28 09:50 EDT `ps -eo rss` + `free -h` 抓取
   - 推荐去处：INSIGHTS.md（不够 ref-worthy）

3. **[评分:3]** **类比论证被反问 1 次应立即审视准确性** [src:94c2988a]
   - 场景：主公反问"那为啥还有人做"时我维持立场（合规），第二次反问"AI 和淘宝一样吗"才主动修正类比（中转站像开淘宝 vs AI 不像）
   - 应该第一次反问就启动"类比对象是否准确"自检，不要等二次反问
   - 推荐去处：INSIGHTS.md 或新 memory feedback_analogy_audit
   - **Why**：维持立场是好规则，但"维持立场"≠"维持类比"。类比的准确性是另一个维度，被反问时应该单独审视——尤其当类比跨越行业（中转站 vs 淘宝 vs AI）时容易偷换概念

### 操作记录 建议起草：无

### Friction 建议补记：无（本次教学讨论无被纠正，1 次合规立场修正）

### Playbook 建议更新：无

### 文档对齐待处理：无

### MEMORY.md 建议清理：无（已扫描，无废弃条目）

---

### 🤖 本次自动写入摘要（4-5 分，已直接写入正式文件）
- 无（冷启动期 4 分送审，5 分才自动写；本次最高 4 分）

### 🗑️ 本次自动丢弃摘要（1 分，未保留）
- 2 条 1 分候选被丢弃：API 中转站原理拆解（账号池/计费/协议兼容）/ AI 行业 3 层结构（模型/应用/套利层）— 通识知识，非 cowork 系统真实痛点，主公已掌握

## [草稿] 2026-05-28 深度审核

> 审核 session：94c2988a（opus2架构讨论，17条）+ 9cffe957（本次：稳定周报+VRRM止损，29条）

### INSIGHTS 建议写入（2 条）

1. **[评分:4]** **P9 bear_thesis 必须覆盖客户集中度风险** [src:9cffe957]
   - VRRM Avis合同终止案例：Avis占收入>10%，合同终止导致-70.6%单日暴跌
   - Bear thesis 当时只写了政治/政府合同风险，遗漏了私人大客户集中度这一显性风险
   - 规则：任何单一客户占收入>10%的公司，bear_thesis 必须单独写一段"客户集中度风险"，否则视为不完整
   - 推荐去处：reference/knowledge_base.md「P9 TIDE系统」章节 + playbooks/p9_trading.md bear_thesis模板

2. **[评分:3]** **stability_check.sh 负数 NEW 值未处理 → 误报 ⚠️** [src:9cffe957]
   - NEW=CURRENT-LAST_COUNT，friction 减少时 NEW 为负数，脚本判断 NEW<=2 触发"轻微波动"
   - 修复：加 `if [ "$NEW" -le 0 ]` 分支，输出"✅ friction 减少 X 条，系统好转"
   - 推荐去处：修 stability_check.sh 第26-34行

### Playbook 建议更新（1 处）

1. **[评分:4]** **playbooks/p9_trading.md**：在 bear_thesis 模板段新增强制检查项
   - 「单一客户/合同占收入 >10%？→ 必填：客户集中度风险段，写明客户名/占比/合同到期日/历史续签率」
   - 依据：VRRM -$2,211 实际亏损案例（2026-05-27-28）

---

### 🗑️ 本次自动丢弃摘要（1 分，未保留）
- 共 2 条 1 分候选被 AI 自判低价值丢弃（澄清对话流程 × 2 次，属于正常操作无规则价值）

