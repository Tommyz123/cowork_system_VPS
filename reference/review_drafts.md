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

---

## [草稿] 2026-05-23 深度审核

> 审核 session：c61bb128（跨日 5/22 16:16 → 5/23 23:06，约 100 轮对话；P2 cowork 系统大瘦身 + Codex 接入 + Cannabis demo + cowork SSH key）

### INSIGHTS 建议写入（4 条）

1. **Skill 注入实测 token 成本** → 9 个未使用 Skill description 共 1238 字符 ≈ 1500 token/对话注入；归档到 cowork/skill_archives/ 后 system-reminder 列表立刻不出现；累计省 ~1500 token/对话 [src:c61bb128] [ref-worthy]

2. **Codex CLI 订阅认证方法** → `codex login --device-auth` 走 device code flow（VPS 无浏览器时唯一办法），但默认 ChatGPT 安全设置**禁用** device authorization 需主动开启；ChatGPT Plus $20/月 订阅可用，不耗 OpenAI API；安装走用户级 npm（~/.npm-global，无 sudo） [src:c61bb128] [ref-worthy]

3. **Ubuntu 24.04 bubblewrap 二段限制** → 装 bubblewrap (apt install) 还不够，AppArmor 默认 `kernel.apparmor_restrict_unprivileged_userns=1` 拦截 user namespace 创建；需要 sysctl 关闭 + 写 /etc/sysctl.d/99-userns.conf 永久生效；Docker/Codex/snap 都依赖此能力 [src:c61bb128] [ref-worthy]

4. **MEMORY.md 索引行 D 模板**（推导）→ 格式 `[主题]：[独有部分]（其他 CLAUDE.md 已有）`；权衡 token 经济（短）vs 主题可识别性（一眼分类）；A 类完全重叠直接删行，C 类纯压缩长字符串，B 类要保留独有补丁；总省 ~400 token/对话 [src:c61bb128]

### 操作记录 建议起草（1 份）

- **主题**：Codex CLI 在 cowork VPS 完整安装日志
- **背景**：今天首次在 VPS 装 Codex，踩了 device auth + bubblewrap + AppArmor 三个坑
- **建议文件名**：`reference/codex_setup_log.md`
- **内容应包含**：① npm 用户级安装命令 ② device auth + ChatGPT 安全设置开关 ③ bubblewrap + sysctl 设置 ④ codex exec / codex login status 验证 ⑤ "我+Codex 分工" 调用模式（echo "..." | codex exec）

### Friction 建议补记（3 条）

1. **"!cmd" 误导主公**：我让主公 "在 Discord 输入 `! sudo apt install -y docker.io`" —— 但 `!` 前缀只在 Claude Code 终端有效，Discord 是普通文字。已纠正。教训：**用户身处什么环境，决定指令该走什么通道**。

2. **"B 类精简"对话冗余**：B 类 4 条 memory 索引精简时，我提了"一次性处理"但主公选"逐条"，结果每条来回 3-4 轮才推进。教训：**主公追求"理解每一步"时，逐条慢比批量快更合主公节奏**。

3. **"_backup 文件"留 12 天反模式**：discord_approve_backup.py 5/11 重构时留下做备份，**12 天没人删 / 主动检查**。教训：**重构遗留的 _backup 文件应设置"7 天兜底删除"规则**——git history 已经留底，文件系统的副本只是认知噪音。

### Playbook 建议更新（2 处）

- **ARCHITECTURE.md**：加 `cowork/scripts/INDEX.md`（新脚本登记体系）+ `~/.claude/hooks/_log_hit.sh/_log_hit.py`（hook 命中日志机制）
- **playbooks/cowork_system.md**（如果有）：加 "归档 Skill 复用" 流程（怎么查 cowork/skill_archives/INDEX.md 触发关键词 → 读 SKILL.md 执行）

### 文档对齐待处理（2 处）

- **ARCHITECTURE.md hook 表格**：加 _log_hit.sh + _log_hit.py 两条共享 logger 行；每个 hook 行补"已加命中日志"标记
- **context.md cowork/scripts/ 段**：加 mention `INDEX.md` 是脚本登记册

### MEMORY.md 建议清理（1 条候选）

- **feedback_codex_collaboration.md** 之前候选删（VPS 没装 Codex），现在 VPS 装了 Codex —— 这条 feedback 又变活跃，**不删反而要更新**（增加"VPS 上 Codex CLI 安装位置 ~/.npm-global/bin/codex" 等实操信息）

### 维护提醒

- 内核重启 6.8.0-71 → 6.8.0-117（apt 已升级未重启，找 bot 闲置时段做，systemd 会自动拉起 cowork bot）
- 5/30 hook 命中日志审计（今天埋的 _log_hit 跑一周后看哪些 hook 0 触发）
- Cannabis-AI-Budtender/（248MB，主公未决定保留/删除——长期不演示可删）

[src: session c61bb128-11c2-47a5-9fa1-9d9250847fd5]

---

## [草稿] 2026-05-24 深度审核

> 审核 session：acfb36f9（P8 求职策略大重定向，1.5h 深度讨论）

### INSIGHTS 建议写入（3 条）

1. **岗位 title 看似相同但内涵差很大** [src:acfb36f9] [ref-worthy]
   - "Customer Success Manager" vs "Customer Engineer" / "Solutions Engineer" vs "Sales Engineer"——title 看起来近义但工作性质完全不同
   - 判断方法：看 JD 里有没有 `write code / build / deploy / integrate / Python / API / LLM`——有就是技术岗，没有就是客服/销售岗
   - 推广：以后讨论求职/选岗位时不能只看 title，必须读 JD 关键词

2. **跳板策略需要兼顾"履历可跳性"** [src:acfb36f9] [ref-worthy]
   - "第一份工作"的价值不只是薪资 + 学习，还要看"6-12 月后能跳到哪里"
   - YC 早期 AI 履历 → 跳任何 AI 公司都易（同圈互认）
   - Cannabis Tech 履历 → 跳到 AI 公司难（AI 公司未必认）
   - 推广：评估"敲门砖"工作时，要把"履历的下游兼容性"作为第三维度

3. **Hard requirement vs nice-to-have 必须主动追问** [src:acfb36f9]
   - 主公开头说"什么都行 / 只要进 AI 公司"——我以为是宽松偏好
   - 多轮后才补充"必须能学到 + 能用上"——这是 hard requirement 不是偏好
   - 教训：当用户说"什么都行"时，要主动追问 "是不是真的什么都行？有没有不接受的"
   - 推广到所有需求收集场景

### Friction 建议补记（1 条）

1. **数据诚信违规（虚构精确百分比）** [src:acfb36f9]
   - 我开头说"主公在全球用户顶级 0.5%"+ L1-L5 占比表（60/25/12/2.5/0.5）+ "到 L5 要 2-5 年"
   - 主公追问"有根据吗" → 我承认全部是估算 + 撤回
   - 根因：偷懒用看似精确数字（0.5%）伪装主观判断
   - 违反规则：CLAUDE.md "数据诚信" 第 ① 条（陈述句默认有工具来源）
   - 建议升级：以后任何分布/百分比/年限预估，必须先说"推测：" 或者干脆用定性词（"很少见" 而不是 "0.5%"）
   - 已有相关 feedback：feedback_proposal_data_first.md（推方案前先查数据）；此次属于"评估时虚构数据"，是相邻但不同场景

### Playbook 建议更新（1 处）

- `playbooks/career_ops.md`（如果存在）：原"作品敲门"策略已过时，建议按 2026-05-24 新策略更新：
  - 跳板策略（6-12 月）
  - 甜区岗位定义（Solutions/Customer/Implementation/Founding/Applied AI Engineer）
  - 30+ 家公司清单 4 优先级
  - 不投清单（FDE / Tier 1 Lab / CSM / Sales / Marketing / Operations）
  - 与 P12 双线协同方案
  - 主公真实约束（英文 B1 / Sage Seeds 现役 / 牌照等待）

### MEMORY 建议新增（2 条，待主公确认后写入）

1. `memory/feedback_job_title_keyword_check.md`
   - 评估 AI 公司岗位时，必须看 JD 里有没有 write code/Python/API/LLM 关键词
   - 看 title 不看 JD = 错投 = 学不到 + 用不上
   - 来源：2026-05-24 P8 策略讨论

2. `memory/user_career_constraints_2026.md`（user 类型）
   - 主公 P8 求职 hard requirement：必须能学到 + 用得上 cowork 经验
   - 英文 B1（淘汰 FDE/Tier 1）
   - Sage Seeds 现役 budtender + NY 牌照申请人
   - 跳板策略 6-12 月
   - 形式偏好：打工 > Consultant
   - 用途：以后任何 P8 / Cannabis 相关讨论的基础上下文

### 文档对齐待处理（无）

本次未影响 ARCHITECTURE.md / context.md / MEMORY.md（如新增 memory 需要在 MEMORY.md 加索引）

### MEMORY.md 建议清理（无）

本次未发现废弃条目
