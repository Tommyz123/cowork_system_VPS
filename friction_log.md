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

[2026-05-28 19:52 EDT] ⚠️ 资源限制 | 2GB VPS 跑 3 个 Opus 实例内存偏紧 | 场景：主公追问"为什么回复慢/卡住"。体检数据：mem 总 1.9G/已用 1.2G/可用 787M + swap 已用 353M，3 实例常驻、峰值动 swap 拖慢。诊断结论：①重启那 3 分钟是冷启动(进程重生+上下文重载+Discord 握手)非模型慢 ②日常回复慢大头是 Opus 模型本身(速度换质量)+长上下文，加内存治不好 ③内存偏紧只影响卡顿/swap 颠簸。建议 2GB→4GB。主公决定：暂时先用不升级 | 状态：暂缓，日后卡顿加剧时作升级依据


[2026-06-06 20:15] ⚠️ Hook机制摩擦 | 收工 git commit 两个独立问题 | 场景：执行收工 Skill 第3步 commit+push | ①`touch /tmp/git_approved_CC && git commit` 写在同一个 Bash 调用里被 PreToolUse 守卫拦截——守卫在 `&&` 左侧 touch 执行**之前**就检查 token，此时 token 还没生成。**正解：touch 必须单独一个 Bash 调用先跑，git commit 再单独一个调用。** ②本次收工 savework 自动授权（`git_approved_CC` 内容 savework）**没触发**，discord_approve hook 没写该 token，回退到手动 one-shot touch；按 CLAUDE.md「收工自动授权 git」规则本应自动放行整个 commit+push。另：失败重试之间 staging 被 reset，需重新 git add | 状态：需主公确认——savework 自动授权为何没触发（可能因这是 Discord 续聊会话、UserPromptSubmit 没带"收工"原词触发 discord_approve）；及是否在 CLAUDE.md 明确「token touch 与 git 命令必须分两次 Bash 调用」

[2026-06-07 00:47] ⚠️ 行为问题 | 本次对话连续3次用终端文本回复主公而非Discord reply工具，被Stop hook(discord_reply_check.sh)拦截补发 | 根因：主公在Discord遥控，但我多轮纯分析/讲解时惯性用正文输出，忘了正文不进Discord | 处理：每次收到source="plugin:discord:discord"消息，回复第一动作就是reply工具，不在正文写给主公看的内容 | 状态：已自行修复

[2026-06-07 01:25] ⚠️ 工具限制 | discord_approve.py 授权词匹配对"是的，执行c"这种连写/带后缀的组合失效，未触发 task_approved，导致主公以为已授权但守卫仍拦截 | 处理：让主公重发干净授权词 | 状态：需主公确认 — 建议优化匹配逻辑(去标点/分词后再匹配，或对"执行"做包含式而非整词匹配)

[2026-06-07 01:55] ⚠️ 工具限制 | 主公在我上个响应"执行中"异步发"收工"，该消息未走正常UserPromptSubmit授权链，discord_approve.py未写git_approved savework，导致收工commit被守卫拦截 | 处理：让主公重发"收工"作为独立消息才触发授权 | 状态：需主公确认 — 根因：异步到达消息(system-reminder"message arrived while working")不触发hook；建议探讨能否让异步消息也触发授权，或收工流程检测到此情况主动提示重发

[2026-06-07 18:38] ⚠️ 工具限制 | claude.ai Google Calendar/Gmail MCP 授权必须终端跑/mcp,authenticate工具调用只返回该指引不吐授权URL=纯Discord手机遥控无法完成授权 | 处理:如实告知主公需某刻碰终端SSH | 状态：需主公确认(是否换可远程授权的日历/邮箱接入方案,如直连CalDAV/Google API service account)

[2026-06-08 02:42] ⚠️ 工具限制 | Discord reply 工具参数名是 `text` 不是 `content` | 用 content 报错 "undefined is not an object (evaluating 'text.length')"，改用 text 即通 | 状态：已自行修复

[2026-06-08 18:00] ⚠️ 工具参数错误 | Discord reply 工具连续3次报错 "undefined is not an object (evaluating 'text.length')" | 读 jsonl 确认我传的是 message 字段，但工具 schema 要求的是 text 字段；改用 text 后发送成功 | 状态：已自行修复
[2026-06-08 18:00] ✅ 处理结果：记录正确参数名 = chat_id + text（非 message）；reply schema 必填 {chat_id, text}，可选 {reply_to, files} | 状态：已自行修复

[2026-06-08 19:35] ⚠️ 被主公纠正(自查) | MiroFish原版人设机制 | ①表面错误:我说"原版用自由文本人设不是MBTI",主公追问"原版用什么",读oasis_profile_generator.py发现原版profile结构明确含mbti字段(:50)+MBTI_TYPES 16型列表(:155)+age/gender/profession/interested_topics ②根因:没读oasis_profile_generator.py就凭"~2000字人设"的印象答MBTI有无,正好踩刚写进CLAUDE.md的"没读到的别靠猜补全" ③建议规则变更:无需改规则(规则已对),是执行没遵守——回答"原版有没有X"前必须grep源码确认 | 验证标准:今后答原版机制问题前先读对应源码文件 | 验证状态:已自行修复(读代码纠正)

[2026-06-08 23:47] ⚠️ 被纠正 | Discord遥控时误用AskUserQuestion交互菜单 | 主公在Discord问"美国债务危机预测哪个方向"，我用AskUserQuestion弹终端交互菜单收集选择——主公在Discord看不到终端UI，导致卡等(主公连发"为什么没有回复""hi")。表面错误=用了交互式选择界面；根因=澄清需求时下意识用了AskUserQuestion工具，忘了CLAUDE.md明令"禁止用交互式菜单/UI/键盘选择界面，所有选项必须以Discord文字消息呈现"；建议规则变更=无需改规则(规则已存在)，是执行时违规——澄清/给选项一律走Discord reply文字版(带编号选项)，AskUserQuestion仅限主公在终端前时用。验证标准:下次需要主公在多选项间澄清时，用Discord文字列编号选项而非AskUserQuestion。验证状态：【待验证】 | 状态：已自行修复(当场道歉+改回Discord文字)

[2026-06-09 14:01] ⚠️ 被纠正 | 主公问"能切成fable5.0吗"，我直接答"没听说过这个模型/不在主流清单里"，主公说"是最新的模型"后WebSearch确认=Claude Fable 5确是Anthropic今天(6/9)刚发布的最强公开模型(Mythos级)，我之前否认是错的 | ①表面错误:对超出知识截止的新模型直接断言"不存在/没听说过"；②根因:遇到我不认识的名词时，凭训练数据"查无此项"就下陈述句否认，没先WebSearch核实——和今天parse_json"凭印象"、6/8 MBTI"没读就答"同源(凭已有认知补全未知，违反"没读到的别猜")；③建议规则变更:遇到"最新/刚发布/新出的X"类(模型/产品/工具/事件)，因必然超知识截止，禁止直接否认存在，第一动作WebSearch核实再答。验证标准:下次被问及不认识的"新"名词，先WebSearch不直接说"没有"。验证状态:【待验证】 | 状态:已自行修复(WebSearch后纠正)

[2026-06-09 15:26 EDT] ⚠️ 实例身份混淆(复发·自查) | 多个session自报实例/模型身份不一致 | 今天反复触发:①session 2ac51975自报"Claude Fable 5,BB实例(opus2_home)" ②session 4d7bed1c自报"claude-fable-5" ③cowork_log 15:20条写"BB实例" ④本次收工首答也口误"BB"——但token_utils.sh:11-14权威映射明确opus2_home→CC(不是BB),本次实例实测模型=claude-opus-4-8。①表面错误:凭印象自报实例编号和模型ID不查权威源;②根因:实例身份(AA/BB/CC)由$HOME经token_utils.sh case推导是唯一权威,不能凭记忆答(同"没读到别猜");③建议规则:被问"哪个实例/什么模型"时,实例必查token_utils.sh或echo $HOME比对case,模型ID以env/系统报告为准。验证标准:下次自报身份前先查$HOME映射。验证状态:【待验证】 | 状态:已自行修复(查token_utils.sh纠正)
[2026-06-09 16:57] ⚠️ Skill摩擦 | 收工(深度审核) | 送审条目(CLI升级法/加字段验证)已被前次收工写入knowledge_base但review_drafts未同步标注，导致本次重复送审；建议：深度审核写入正式文件的条目在草稿里标"已写入"或直接不进草稿 | 状态：已自行修复(本次查重去重)，规则改进待讨论
[2026-06-09 17:04] ⚠️ Hook边界 | discord_approve.py | 主公授权词"可以去"未匹配边界正则致token未写、Edit被守卫拦；按守卫提示步骤3(主公已明确确认计划)手动token_utils write task放行，完工即清 | 状态：已自行处理；正则是防从句误触发的设计，不建议放宽，遇到时按此例处理
[2026-06-10 00:42] ⚠️ 被主公纠正 | memory共享结构断言 | ①表面错误：称"三实例symlink已指向同一份"，实测CC(opus2_home)是独立空真目录未链接，CC一直拿不到原生记忆注入 ②根因：凭MEMORY.md旧记录("三实例symlink共享")断言现状，违反数据诚信——陈述句没有当下工具验证来源 ③建议：涉及"N个实例/N处配置都X"的断言必须逐实例实测后才能说"都" | 验证标准：下次跨实例状态断言前cowork_log可见逐实例验证命令 | 验证状态：【待验证】
[2026-06-10 15:45] ⚠️ 沟通 | 主公连续2轮"没理解"(趋势方向讨论)，我两次重讲更简版仍未中靶，第3轮才停下列A/B/C确认——实际是答非所问(他问龙头vs链条/落地方式,我答P9vs趋势) | 教训：连续"没理解"≥2次=优先怀疑答错了问题而非讲得太难，立即停下确认问题本身；已有pacing规则只覆盖"换比喻"未覆盖此情形 | 状态：已自行修复(当场改为确认式)，建议升级pacing记忆条目
[2026-06-10 15:46] ⚠️ 规则模糊 | CLAUDE.md说"token操作走token_utils.sh"但未写路径，先猜cowork/scripts/失败，实际在~/.claude/hooks/token_utils.sh | 处理：本次用find定位 | 状态：已自行修复；建议CLAUDE.md该行补路径(一行改动)
[2026-06-10 15:55] ⚠️ 被主公纠正 | 趋势手册成稿后以.md附件发Discord，主公手机打不开 | ①表面错误：发了手机不可读的附件格式 ②根因：只想到"交付文件"没想到主公的阅读场景=手机Discord（feedback_preview_before_execute 同类教训的变体：交付物必须按接收端可读形式给）③建议规则变更：给主公发长文档默认分段贴Discord文字（表格转条目），文件路径只作存档说明；验证标准：下次长文档交付不再被要求换格式 | 验证状态：【待验证】| 状态：已自行修复（全文8条分段重发）
[2026-06-10 21:13] ⚠️ Hook操作踩坑 | git_commit_guard | 收工后新改动需提交,git守卫拦截;两个坑:①`touch /tmp/git_approved_CC && git commit`写同一条命令→hook在执行前拦整条,touch不生效,必须拆成两条独立Bash命令(先单独touch,再单独commit)②标记被守卫放行时消耗,若该次commit因nothing-staged失败,标记也已被消耗,下次commit需重新touch | 处理:拆分命令+每次commit/push前单独重写标记 | 状态:已自行处理;教训=git授权标记是"单次消耗",且复合命令会被hook整条拦截,涉及守卫的操作一律单命令执行
