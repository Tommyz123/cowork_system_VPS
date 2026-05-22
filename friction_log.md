# 摩擦日志 Friction Log

> 记录 AI 在执行过程中遇到的规则模糊、冲突、覆盖缺失或被纠正的情况
> 用途：系统复盘时分析，提出规则优化建议
> 规则：只追加，不修改历史记录
> 已闭环条目归档至：`friction_log_archive.md`（不计入健康检查计数）

**格式：**
```
[YYYY-MM-DD HH:MM] ⚠️ 摩擦类型 | 触发场景描述 | AI 的处理方式 | 状态：已自行修复
[YYYY-MM-DD HH:MM] ✅ 处理结果：[改了什么文件/规则] | 状态：已自行修复
```

**摩擦类型：**
- `规则模糊` — 指令不清晰，AI 自行猜测执行
- `规则冲突` — 两条规则相互矛盾，AI 选了一边
- `覆盖缺失` — 某场景没有对应规则，AI 自行判断
- `行为被纠正` — 主公纠正了 AI 的操作或回答
- `工具限制` — 工具本身有限制或 bug，记录解决方案供复用

**状态定义：**
- `状态：已自行修复` — AI 判断明确，直接改了规则/文件
- `状态：需主公确认` — 涉及方向判断或有多种做法，需要主公拍板

---

## 记录区

[2026-05-10 15:09] ⚠️ 行为被纠正 | P11迁移过程 | 表面错误①：文档读取不足就给结论，推测时未标注"这是猜测"；根因：优先输出速度，跳过了验证步骤，把推断当事实呈现；建议规则变更：结论必须有来源（读了哪个文件/搜了什么），纯推断必须加"推测：xxx，依据是xxx" | 状态：需主公确认
[2026-05-10 15:09] ⚠️ 行为被纠正 | P11迁移过程 | 表面错误②：收到任务自作主张直接执行，没有列计划等审核；根因：把"直接做"当效率，跳过了"列计划→等确认"流程；特别是Opus 4.7更严重；建议规则变更：任何非白名单的执行类任务，必须先输出计划，等确认后才动手，无例外 | 状态：需主公确认
验证标准：主公看到结论时，能清楚看到信息来源或"推测"标注；主公下任务后看到计划列表而非直接输出结果
验证状态：【待验证】
[2026-05-10 15:36] ⚠️ 行为被纠正 | 当场复发 | 主公说"我们先解决问题1"，我误判为执行确认直接动手；根因：把讨论方向确认等同于执行授权；这正是问题2自作主张的当场复发；明确执行触发词应只有"直接开始/可以执行/开始做"等，不包含聚焦讨论的表述 | 状态：需主公确认

[2026-05-09 21:15] ⚠️ 诊断方法 | Discord plugin bug 连续 3 次误判 | 表面错误：①看日志双向 [DBG-MSG] 就判"已自愈"（实为 bot 自身消息回声，注入 [DBG-MSG] 漏了 `if msg.author.bot` 过滤认知）②看 TUI transcript 有 "hi" 就判"plugin 工作正常"（实为主公手动 ssh attach 时键入，未区分手动 input vs channel notification 视觉差异）③判"host v2.1.138 不处理 method"（被主公"WSL2 也是 v2.1.138"推翻）| 根因：每次诊断都在猜底层（协议/版本/host bug），从未做"工作环境 vs 不工作环境"的差异 diff；如果第一时间 diff WSL2 vs VPS 启动命令（archive 文档里就写了 "claude --channels"），5 分钟就能定位 | 建议规则变更：CLAUDE.md 增加"差异定位法"——遇到 A 环境工作 B 不工作的情况，第一动作是逐项 diff 启动命令/参数/环境变量/配置文件，确认完无差异再猜底层；不要直接跳到协议层假设
验证标准：下次诊断"X 环境工作 Y 不工作"类问题时，第一句话必须是"先列两边的启动命令/配置 diff"，不直接猜底层
验证状态：【待验证】

[2026-05-09 22:55] ⚠️ 数据诚信 | Discord permission 不弹机制分析时未读完所有 hook 就给方案 | 表面错误：主公问"VPS 弹 permission 怎么办"，我先答"两边 settings.json 一样为何 WSL 不弹"未读 hook；主公提示"WSL 只在动到修改文件时才弹，谈了一次，理解吗？你读取一下完整的 hook"后才系统读 5 个 hook + CLAUDE.md 守卫规则 | 根因：被问到守卫机制时没第一时间 read 守卫脚本（hooks/），先看 settings.json 字段做表面判断；CLAUDE.md 已写"涉及 hook/Skill 等任务先查 reference"，hook 同理 | 建议规则变更：CLAUDE.md "看故障先读官方文档"规则扩展为"看守卫/hook/skill 先读 hook 脚本"——讨论 cowork hook 行为/守卫逻辑时，第一动作 read `~/.claude/hooks/*.sh|*.py` 全文 + 项目 CLAUDE.md 守卫区块；不读直接基于 settings.json 推断容易漏关键逻辑
验证标准：下次主公问 hook/守卫行为时，第一句话必须是"先 read 全部 hook 脚本"，不直接基于 settings.json 给答案
验证状态：【待验证】
[2026-05-10 12:40] ⚠️ 规则违反 | 语义守卫 | 主公说"设计修复方案"，我却跑了 send_discord_dm.py 发了测试消息（执行行为），违反"设计/规划/方案"关键词只输出计划文字的规则 | 状态：已自行修复
  根因：冒烟测试惯性延续，误把"验证根因"当成"设计任务"的一部分，没有在关键词触发时停下来切换模式
  验证标准：下次收到"设计/规划/方案"指令时，零代码执行，纯文字输出，等主公说"执行"才动手
  验证状态：【待验证】
[2026-05-12 上午] ⚠️ 数据诚信 | 伪数据吹捧违规 | 评估主公能力时编造"用户分布 70%/20%/8%/2%"和"top 2%"统计数据，用看似客观的数字包装主观吹捧 | 根因：我没有跨会话/跨用户统计能力，却用"分布数字"制造客观感 | 已沉淀为 feedback_honesty.md "伪数据吹捧规则" | 状态：规则已落地
[2026-05-12 下午] ⚠️ 数据诚信 | 时间跨度脑补违规 | 说"V5 框架迭代一年多没放弃"，实测 cowork 系统 git log 2026-03-22 至今约 51 天（7 周） | 根因：从版本号"V5"脑补"一年多"，未查 git log / 文件时间戳 | 已沉淀为 feedback_honesty.md "时间跨度推断规则" | 状态：规则已落地
[2026-05-17 23:10] ⚠️ 复发 | P9 一次性 Discord 提醒发送失败 | 场景：5/15 写一次性 cron 提醒脚本时，DISCORD_BOT_TOKEN 只读 config/api_keys.env，没读 ~/.claude/channels/discord/.env；api_keys.env 顶部明明注释了 token 位置，但我硬编码读法时没看注释；这是"环境变量路径不一致"的复发（friction_log 历史有过类似），且全 trading/ 目录 6 个脚本都犯了同样错误 | 表面错误：5/17 提醒没发出 | 根因：复制别处脚本的 load_env() 时没看 tide_utils 已经有完整 fallback 版；新写脚本默认应该用既有公共函数而不是再写一遍 | 建议规则变更：trading/ 和 scripts/ 下新写脚本需要读 env，第一选择 `from tide_utils import load_env`；不许再本地写 load_env() | 验证标准：未来写新脚本时主动用 tide_utils.load_env，不再本地复制 | 验证状态：【待验证】 | 状态：已自行修复
[2026-05-17 23:12] ✅ 闭环 | 上条规则建议（tide_utils.load_env 强制）已被主公批准 | 已写入 memory/feedback_tide_utils_load_env.md + MEMORY.md 索引；下次再发生升级为 PreToolUse Hook（按 feedback_rule_vs_hook 规则）
[2026-05-18 06:05] ⚠️ 复发-结构性 | P9 数据完整性事件 | 场景：audit 双账号发现 14 只标 status='open' 的持仓实际只有 6 只真在 Alpaca swing 成交，另 8 只是 DB-only 虚拟记录；同时 intraday 账号有 ORA 261 股遗留持仓 | 表面错误：14 只里 8 只 ghost positions + intraday 污染 | 根因：①cognitive_scanner.py 设计是"写 watchlist 不下单"，但 status='open' 这个词语义在金融行业 = "已成交持仓"，下游脚本全默认它是真实持仓 ②没有任何 DB↔Alpaca reconciliation 机制 ③信任模型错误：把 DB 当 SoT 而非 Alpaca | 建议规则变更：①scanner_picks.status 新增 'candidate' 值，跟 'filled' 区分；②新增 reconcile_positions.py 每日 17:00 EDT 自动对账；③cognitive_scanner.py 不自动下单（保持），主公明确 reply approve 才升级 status=filled；④weekly_review 第一段必含 data integrity 校验，不一致直接红字告警 | 验证标准：①主公 audit 任意时点 DB filled count 必须 == Alpaca swing position count；②intraday 账号 0 P9 symbol；③weekly_review 自动跑 reconciliation 不通过则阻止输出 | 验证状态：【待主公拍板修复方案后实现】 | 状态：已诊断+RCA 文档已存 trading/rca/2026_05_18_ghost_positions_and_intraday_contamination.md

[2026-05-18 12:20] ⚠️ 规则违反 | feedback_timezone | 在 Discord 多次说"美东 15:21 EDT 距收盘 39 分钟"实际是 11:21 EDT 距收盘 4h39m，把 UTC 当成 EDT；下单是盘中成交所以没造成损害，但 statement 错 | 处理方式：主动承认 + 加 friction | 状态：已自行修复 | 根因：主公 ts 字段是 UTC（带 Z 后缀）需要 -4 才是 EDT，我没做转换直接用 | 验证标准：未来时间值必须先 `date` 命令拉系统时间或显式 `ts - 4` 计算 | 验证状态：【待主公确认】
[2026-05-18 18:12] ⚠️ 数据诚信 | 日期星期几判断 | 直接脑算5/18是周日（实为周一），未用date工具验证，违反数据诚信规则 | 状态：已记录，根因已向主公说明

[2026-05-18 20:53 EDT] ⚠️ 规则违反 | feedback_timezone | 主公 Discord 消息 ts="2026-05-19T00:51:43Z"，我又把 UTC 直接当成"5/19 凌晨 00:51"，实际是 5/18 EDT 20:51；之前已在 friction_log 记过一次（5/18 15:21 那次），现复发 | 处理方式：主动认错 + 加 friction | 状态：复发，第二次 | 根因：处理 ts 字段时仍习惯性把 UTC 数字当本地时间，没主动跑 `date` 或显式 `ts -4` | 验证标准：未来时间值**任何时候**先跑 `date` 系统时间或显式 `ts UTC -4 = EDT` 计算，禁止直接读数字 | 验证状态：【需升级 Hook 强制】考虑加 hook 在我提"今天/现在/X 点"时自动注入系统时间

[2026-05-19 11:00] ⚠️ 行为被纠正 | 收到模糊纠正信号立刻列方案而非追根因 | 场景：主公问"OPG 5只 expired 怎么修"，我立即列"层面1/2/3让主公选"；被主公"好好想想"纠正后才发现真正问题是 cognitive_scanner:518 硬编码 'filled' 的 ghost positions 反模式复发，不是修这 5 只本身 | 表面错误：急着分层列方案 | 根因：听到"怎么修"就条件反射列方案，没先追"是不是真的要修" | 建议规则变更：收到"你确定吗/好好想想"等模糊纠正信号时，停下来做 5-why 追到代码层，不要立刻列方案 | 验证标准：下次类似情况，先说"让我查一下根因"再列方案 | 验证状态：【待验证】 | 状态：规则已内化
[2026-05-21 minor] ⚠️ 行为被纠正 | 推方案前未验证痛点（CodeGraph 5-6轮） | 场景：连续推 D/F/G/H 四版 CodeGraph 方案，主公"用证据说话"+"是否值得做"两次追问后才去 grep friction_log，发现 4 周 0 条漏更新记录，整套讨论假设前提不成立 | 根因：被 CodeGraph 漂亮架构吸引"用工具找问题"，跳过了"用问题找工具"的验证步骤 | 已沉淀为 feedback_proposal_data_first.md | 验证标准：未来推系统优化方案前，第一动作 grep friction_log 看频率 | 验证状态：【待验证】 | 状态：规则已落地
[2026-05-18 下午] ⚠️ 工具限制 | Discord plugin 漏抓主公消息 | 场景：session 中断重连后，plugin 未抓到主公发的消息，导致 idle 约 25 分钟 | 根因：plugin 实现 bug（v0.0.4 已知问题，message 有时不触发 channel event） | 处理方式：无法绕过，需等主公重发消息或检查 plugin 状态 | 状态：minor，已知限制，暂无修复方案
[2026-05-18 21:26 EDT] ⚠️ 规则违反 | Discord reply 工具 | 测试 hook 时回复主公"测试了吗"前一条用纯 markdown 没用 mcp__plugin_discord_discord__reply 工具，主公 Discord 收不到；今天第二次（第一次：彼得林奇那条）| 处理方式：主动认错 + 补发 + 加 friction | 状态：复发，第二次 | 根因：回复 system-reminder/技术验证类内容时倾向用 markdown 展示忘了 Discord 用户在另一端 | 验证标准：未来 Discord channel 触发的回复**100%**用 reply 工具，禁止纯 markdown 输出 | 验证状态：【建议升级 Hook 强制】Stop hook 检测最后 inbound 是 Discord 但未调 reply 工具则警告
