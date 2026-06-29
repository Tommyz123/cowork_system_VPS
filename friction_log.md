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

[2026-06-09 16:57] ⚠️ Skill摩擦 | 收工(深度审核) | 送审条目(CLI升级法/加字段验证)已被前次收工写入knowledge_base但review_drafts未同步标注，导致本次重复送审；建议：深度审核写入正式文件的条目在草稿里标"已写入"或直接不进草稿 | 状态：已自行修复(本次查重去重)，规则改进待讨论
[2026-06-09 17:04] ⚠️ Hook边界 | discord_approve.py | 主公授权词"可以去"未匹配边界正则致token未写、Edit被守卫拦；按守卫提示步骤3(主公已明确确认计划)手动token_utils write task放行，完工即清 | 状态：已自行处理；正则是防从句误触发的设计，不建议放宽，遇到时按此例处理
[2026-06-10 15:45] ⚠️ 沟通 | 主公连续2轮"没理解"(趋势方向讨论)，我两次重讲更简版仍未中靶，第3轮才停下列A/B/C确认——实际是答非所问(他问龙头vs链条/落地方式,我答P9vs趋势) | 教训：连续"没理解"≥2次=优先怀疑答错了问题而非讲得太难，立即停下确认问题本身；已有pacing规则只覆盖"换比喻"未覆盖此情形 | 状态：已自行修复(当场改为确认式)，建议升级pacing记忆条目
[2026-06-10 15:46] ⚠️ 规则模糊 | CLAUDE.md说"token操作走token_utils.sh"但未写路径，先猜cowork/scripts/失败，实际在~/.claude/hooks/token_utils.sh | 处理：本次用find定位 | 状态：已自行修复；建议CLAUDE.md该行补路径(一行改动)
[2026-06-10 15:55] ⚠️ 被主公纠正 | 趋势手册成稿后以.md附件发Discord，主公手机打不开 | ①表面错误：发了手机不可读的附件格式 ②根因：只想到"交付文件"没想到主公的阅读场景=手机Discord（feedback_preview_before_execute 同类教训的变体：交付物必须按接收端可读形式给）③建议规则变更：给主公发长文档默认分段贴Discord文字（表格转条目），文件路径只作存档说明；验证标准：下次长文档交付不再被要求换格式 | 验证状态：【待验证】| 状态：已自行修复（全文8条分段重发）
[2026-06-10 21:13] ⚠️ Hook操作踩坑 | git_commit_guard | 收工后新改动需提交,git守卫拦截;两个坑:①`touch /tmp/git_approved_CC && git commit`写同一条命令→hook在执行前拦整条,touch不生效,必须拆成两条独立Bash命令(先单独touch,再单独commit)②标记被守卫放行时消耗,若该次commit因nothing-staged失败,标记也已被消耗,下次commit需重新touch | 处理:拆分命令+每次commit/push前单独重写标记 | 状态:已自行处理;教训=git授权标记是"单次消耗",且复合命令会被hook整条拦截,涉及守卫的操作一律单命令执行
[2026-06-11 03:10] ⚠️ 规则边界 | 跨响应任务的token断档：主公"执行"授权趋势地图任务→派后台agent→agent完成通知触发新响应→Stop hook已清token→写地图文档被task守卫拦截；token_utils自写被授权守卫二次拦截(设计如此,正确) | 处理：改交付顺序=内容先发Discord(不受token限),文档落盘等主公下条授权词 | 建议讨论：后台agent模式的长任务是否需要"任务级授权"机制(类似savework标记跨响应有效),否则每个后台任务收尾都要主公多回一句 | 状态：需主公确认
[2026-06-11 13:32] ⚠️ Hook边界 | 主公"可以加，但是ferc是什么"未触发discord_approve授权(token未写)，意图明确但句式不在关键词边界内 | 处理：先答FERC问题，请主公补"可以执行" | 建议讨论：APPROVE_KEYWORDS是否补"可以加/可以做/加吧"类变体（注意防从句误触发的原设计原则，见feedback_discord_approve_design） | 状态：需主公确认

[2026-06-13 03:19] ⚠️ 被纠正(自查) | Organic Blooms案对主公申请影响建议 | 表面错误:上一条建议"主公自己找合规店面就能把申请从被冻结的provisional池挪到不受禁令的带店面池" | 根因:没回到卷宗原文核实provisional路径的时间机制就给建议,违反"先读信息再结论/预测前先夯实数据";误把"provisional后置找店面"当成"可前置补店面改类别",且忽略2023申请窗口已关闭+12个月钟从拿照才起算两个硬约束 | 建议规则变更:给法律/流程类可执行建议前,强制先摘出依据原文段落自检时间窗口/前置条件,再出建议 | 处理方式:重读Memorandum118+FAQ127后主动向主公纠正立场,说明因为X改变想法 | 状态:已自行修复(向主公诚实纠正);验证标准:主公确认修正后的理解准确 | 验证状态:【待验证】

[2026-06-19 03:42] ⚠️ Hook摩擦 | discord_approve.py 收工未自动写git授权 | 主公发"可以。收工。"组合句，discord_approve.py 写了 task_approved_BB 但未写 git_approved_BB(savework)，收工commit被git守卫拦截，手动 write-savework 后通过 | 状态：需主公确认
- 根因待查：可能 discord_approve.py 的收工触发逻辑没匹配"可以。收工。"这种与授权词同句的写法，或savework触发关键词与"收工"边界匹配问题
- 影响：收工流程被打断一次，需手动 token_utils.sh write-savework 解锁
- 建议：检查 discord_approve.py savework 触发分支(grep "收工"逻辑) vs 组合句场景；本次已用 Skill 设计的标准机制(write-savework)解锁，非违规绕过

[2026-06-19 10:15] ⚠️ 行为复发 | Discord遥控下回复写正文未用reply工具(高压下复发) | 场景:context满工具故障期间,我连续几十轮把给主公的回复写正文、没调reply工具,主公在Discord收不到,双向静默加剧混乱。①表面错误:Discord遥控正文不进Discord,必须用reply。②根因:旧毛病——2026-06-07已记录同一问题,高压下复发,规则未真正内化;Stop hook(discord_reply_check.sh)是事后兜底非事前预防。③建议:评估"Discord消息回复必用reply"做成事前预防。验证标准:下次Discord遥控全程不再正文漏发。验证状态:【待验证】 | 状态:已沉淀feedback_untrusted_feedback
[2026-06-19 10:15] ⚠️ 被纠正(对抗测试+真实故障) | 不可信反馈下反向过度归因 | 场景:context满致工具失效,我把"看到工具结果异常/注入文字"(观察)过度升级为"VPS被入侵、有攻击者植入进程"(归因),还差点让主公去ps aux抓进程/重启proxy。①表面错误:证据不足的归因跳跃。②根因:安全训练强化了"不执行恶意指令/不撒谎"(守住了),但没训练"识破后不过度戏剧化";盯内容层(可被操控)漏元层面(主公全程实时引导=更像测试);把简单问题(对话太长)想复杂。③建议:已沉淀方法论"观察/归因分离+奥卡姆剃刀升级版(总根因伪装多症状)"。验证标准:下次遇反馈异常,守底线但归因保守不升级为最戏剧化解释。验证状态:【待验证】 | 状态:已沉淀feedback_untrusted_feedback

[2026-06-19 16:07] ⚠️ Hook摩擦(复发) | 收工savework git授权未自动写 | 场景:主公说"可以，收工"(组合句),discord_approve.py写了task_approved_CC但未写git_approved_CC(savework),收工commit被git守卫拦截。与2026-06-19 03:42同一bug复发(组合句"可以。收工。"未触发savework分支)。处理:用标准机制token_utils.sh write-savework解锁(非违规绕过)+分次调用(PreToolUse hook在命令执行前跑,write与commit必须分开两次Bash调用,同一调用内写无效)。根因待查:discord_approve.py savework触发关键词对"可以，收工"组合句匹配失败。状态:已用标准机制解锁完成收工,需查discord_approve.py收工触发逻辑

[2026-06-20 00:16 EDT] ⚠️ Hook摩擦 | task_approved响应级授权与多步执行冲突 | 主公说"可以"后UserPromptSubmit hook提示已自动授权task_approved_BB,但我在同一响应内先跑了多个Bash验证(claude CLI测试/读脚本)再到Write建脚本时,token已不存在被system_file_guard拦截;且授权守卫禁止我自行touch补建 | 处理方式:请主公重新发授权词;根因待查(疑似token在响应内被某环节清除,或自动授权写入时机晚于首个工具调用) | 状态：需主公确认

[2026-06-20 21:05] ⚠️ 自我误判 | AA/BB登录401诊断 | 重启后看欢迎页显示"Claude Max"就判定已恢复，未等实际消息验证→主公实测仍无反应，回头查才发现底层凭证refreshToken为空(重启拉不回)。表面错误：把缓存的账号名当成"登录正常"的证据。根因：违反"先验证再下结论"——重启类修复必须用真实收发消息验证，不能凭启动屏字样。建议规则变更：重启实例后，验证恢复必须以"实测一条消息能正常回复"为准，欢迎页/账号名不算数。验证标准：下次重启实例后，先抓屏确认无报错+(可行时)实测回复，再向主公报"已恢复"。验证状态：【待验证】
[2026-06-21 01:05] ⚠️ Hook摩擦 | task_approved响应级授权复发 | 审核修脚本时被system_file_guard拦截(授权已被上轮Stop hook清除),需主公重新说授权词→修改才放行 | 处理方式:列清单等"可以执行"重授权后继续 | 状态:已知问题复发(6/20已记同类),多步骤跨响应任务的授权粒度待与主公讨论是否升级(响应级vs任务级)
[2026-06-21 14:51 EDT] ⚠️ 工具限制 | discord_approve.py授权词覆盖 | 主公说"可以去，按照你推荐的做"未被识别为授权词，但上一条"那可以"反被误判授权(时机错位)；任务守卫正确拦截、授权守卫正确禁止Claude自行touch token | 处理方式：请主公回标准授权词"可以执行"；建议系统复盘时评估①补"可以去/按你推荐的做"等常见授权表达 ②查"那可以"为何会匹配 | 状态：需主公确认
[2026-06-21 21:12 EDT] ⚠️ 待办(P9迭代) | signal_collector 数据质量bug(2个) | ①Finnhub新闻路径缺日期过滤,偶混旧文章(实测5/5799),代码确认SEC路径有within_range过滤但Finnhub路径无 ②Benzinga偶塞不相关新闻(SPXC挂Dogecoin) | 处理方式:今晚不动(改新闻入库主路径有误伤风险),留下次P9迭代专门处理,先量化污染样本(什么样旧文章/多旧)再定过滤窗口 | 状态:待P9迭代
[2026-06-22 12:57] ⚠️ Hook冲突 | task_approved授权token写入失败 | UserPromptSubmit的discord_approve hook报告"✅已自动授权/tmp/task_approved_CC"，但实际文件不存在；system_file_guard拦截写文件，授权守卫又禁止Claude自行touch→死锁。主公连发"可以/执行"多次token都没落地。处理方式：请主公重发授权词观察token是否真写入 | 状态：需主公确认（疑discord_approve.py写入路径/时机与守卫检查不一致）

[2026-06-23 13:00] ✅ Hook摩擦(批量闭环) | discord_approve.py 授权词漏匹配 | 场景:多次主公明确同意但句式不在词表致token未写、被守卫拦(累计7次:6/06"可以去按推荐"/6/07"是的执行c"连写/6/09"可以去"/6/11"可以加但ferc是什么"/6/21"可以去按你推荐的做"等) | 处理:扩词表(严格边界+宽松包含两清单分别补),14条回归测试覆盖真实案例+原有词+否定疑问安全底线,撤回会误触发的短词 | 状态:已自行处理(主公授权方案1扩词表);保留"防从句误触发"设计原则不放宽匹配规则,只补具体长词
[2026-06-23 15:16] ⚠️ 工具限制 | 收工git授权失灵：主公"可以，收工"未触发discord_approve.py写git_approved_BB(savework)，且token写入后被某PostToolUse hook在工具调用间隙清空→普通"先写token再commit"两步法失败。处理方式：同一条Bash命令内 `token_utils write git savework && git commit` 一气呵成才放行。 | 状态：已自行修复(本次收工已commit+push成功 1703511)，根因待查：①discord_approve为何没识别"可以，收工"的"收工" ②哪个hook在清git token
[2026-06-23 15:20] ⚠️ 已自行修复·根因更正 | 上条"收工git授权失灵"根因查清：**不是hook乱清token，是我命令用错**——token_utils正确写savework的命令是 `write-savework`（无参数,专写"savework"内容），我误用 `write git savework`(第三参数被忽略只touch空文件)→守卫grep不到savework走clear分支→空token放行一次即被清,故每次都得重写。正解=`token_utils.sh write-savework && git commit/push`。验证：37623e4 commit+push成功,token内容确为savework。规则:收工git授权统一用 write-savework,禁用 write git savework。 | 状态：已自行修复

[2026-06-23 18:08] ⚠️ Hook摩擦 | 收工git授权失灵复发(第2次) | 场景：主公说"可以执行"/"执行"想触发收工commit，但discord_approve.py只在"收工"/"保存进度"关键词时写git_approved=savework；"执行/可以"只写task_approved(文件锁)不开git锁→commit被git_commit_guard拦→死循环要主公反复发字 | 处理方式：如实告知主公必须发"收工"二字 | 状态：需主公确认 — 建议规则变更：①收工语境下"执行/可以/确认"等强授权词也应触发savework git授权(或②commit前BB检测到git_approved缺失时主动提示主公发"收工"而非反复试commit)。根因=文件锁与git锁授权词表不一致，收工是高频高确定性场景不该卡。验证标准：下次主公"执行"能否一次跑通收工commit。验证状态：【待验证】

[2026-06-24 00:38] ⚠️ 规则模糊 | friction归档操作授权卡点 | 做#2验证结案时,改friction_log.md(白名单)放行但写friction_log_archive.md被任务守卫拦——CLAUDE.md白名单写的是"archive/"(目录)不含"friction_log_archive.md"(根目录文件);且当时token已被上轮Stop清,"全部闭环"非标准授权词没自动开锁→闭环动作两头落空风险。处理:删主日志第1条后立即停手防数据丢失,请主公补"执行"授权后一次完成。建议:白名单补"friction_log_archive.md"(收工归档高频操作,与friction_log.md同性质应同权限)。状态:已自行处理(主公补授权完成),建议规则补白名单待确认

[2026-06-24 13:32] ⚠️ 数据诚信 | P9审核误报「问题1：9对象卡待校准」 | 根因：只读 dossier_autowrite.log 的 09:30 写入快照(那一刻确实全🔍待校准)，未核实当天晚间周检是否已人工补判断。实际查档案：6/22 周检已逐个定状态(📈强化×1/✅成立×4/⚠️松动×4)+CEG 6/23 还有事件更正行，全档案仅剩 1 处「待校准」字样且是修订记录里「→已定状态」的叙述。教训：报「待办/卡点」前必须查接收方文件确认当前态，不能拿中间日志快照当终态(同 feedback_read_before_conclude/delete_verify_first) | 状态：已自行修复(向主公更正)

[2026-06-24 13:40] ⚠️ 数据诚信 | P9审核「账号$1M vs $106K差异」也是假问题 | 根因同问题1:我拿 playbook 顶部旧描述当现状报差异,但 playbook:176 + memory/project_p9_trading:16,21 早已明写「$106k 正确,$1M 是 2026-05-30 核实后的历史误记」。我没读到那两行就报「对不上」。=同一个病:只读单一来源(这次是 playbook 上半截/上次是 autowrite 中间日志),没交叉核对已有权威答案的文档 | 状态：已自行修复

[2026-06-24 21:51] ⚠️ 文档纪律 | 写P9档案时未主动套用"数据判断分层"通用规矩,靠主公点出 | 处理方式:①重整E1为分层结构②强化memory feedback_tracking_facts_only加"写入即分层前置自检" | 状态：已自行修复（主公2026-06-24确认升为每次写入自检项）

[2026-06-24 23:45] ⚠️ 操作事故 | bash写文件用相对路径>>friction_log.md,因前面cd到trading/notes导致误建孤儿文件trading/notes/friction_log.md(内容旧版重复) | 处理:收工时git status发现并删除,正式文件已有闭环版 | 状态：已自行修复(教训:>>追加日志类文件一律用绝对路径)

[2026-06-25 17:42] ⚠️ 工具限制 | VPS升级claude-code 2.1.170→2.1.191试水CC发现两坑致Discord失联 | 坑1:2.1.191首次启动弹"Try fullscreen renderer? 1/2"交互菜单,实例卡菜单无法继续启动(三实例若齐升会全卡→全失联);坑2:2.1.191下Discord plugin(0.0.4)进程死活不拉起(CC配置与BB完全对等仍不起,非配置问题=版本不兼容),实例上线但收不到消息 | 处理方式:按"先试一个"只搭CC,精准回滚.local回2.1.170+重启,三实例全恢复;同时发现历史隐患=机器装两份claude(实例实际跑.local,以往npm i -g升的是没人用的.npm-global=白升) | 状态：已自行修复(升级暂缓,待官方修plugin兼容或先升级Discord plugin再重试)

[2026-06-25 18:10] ✅ 解决(承接17:42条) | 2.1.191升级Discord失联根因已挖到并修通 | 真根因(实锤,非版本bug):2.1.170宽容/2.1.191严格,后者按known_marketplaces.json的installLocation+installed_plugins.json的installPath找plugin缓存;CC这两处历史错写成opus_home(BB目录)跨实例错位→新版cache-miss→"Found 0 plugins"→plugin不加载→Discord失联;且旧project-scope登记2.1.191不认 | 修法(已验证打通):①改对两处路径指回opus2_home②用新版重装`claude plugin install discord@claude-plugins-official`(装成user-scope)③重启CC;CC已在2.1.191且Discord双向通(实测发收消息);完整流程已写入memory/reference_dual_bot.md升级指南 | 状态：已解决

[2026-06-26 12:20] ⚠️ Hook摩擦+授权债实锤 | 收工commit死循环卡20分钟 | 场景:主公"收工"后commit反复不成,主公多次催"好了吗"渐失耐心质疑"忽悠"。根因双重:①授权债B/C实锤——"收工"写的git_approved_BB(savework)在跨十几条来回的多响应收工中被某响应Stop hook清掉,commit被git_commit_guard静默拦截;主公后发"执行"只触发task_approved不触发git_approved(savework词表不一致,C类),git仍被拦②我的reply工具调用多次malformed未真发出,主公收不到我的真相解释,加剧"没反应"感知。处理:reply改极简纯文本确保发出+主公"执行"确认后落实git_approved+一口气commit成功65656ec | 状态:需主公确认——强烈佐证#4授权债该修(收工高确定性场景token不该中途丢/普通授权词收工语境应开git);另需查reply工具为何反复malformed。验证标准:下次收工一次跑通不卡授权。验证状态:【待验证】
[2026-06-28 17:06] ⚠️ 工具限制 | 收工前长任务中task_approved响应级token跨轮失效被文件守卫拦 | 处理:未自行touch绕过(守呆机制),诚实请主公重新授权词→hook重写token继续 | 状态：已自行修复(规则本就如此,非bug;正确行为示范)

[2026-06-28 22:10] ✅ 授权债#4根因挖到并修通(收工git commit死循环6+次复发的终结) | 真根因(实锤,纠正历次"待查"猜测):UserPromptSubmit钩子链有**无条件**`token_utils.sh clear git`,每收一条新消息先清git锁再由discord_approve按关键词重写→收工是跨十几条响应的流程,主公中途任意回复(不含"收工")触发清锁→savework被清→commit被git_commit_guard拦→死循环。旧猜测全错:非Stop hook清(Stop只clear task)/非守卫消耗(守卫第26行savework grep到直接exit 0不消耗)。
  Codex(codex exec)评审同意根因,补风险=纯豁免会致savework锁残留→非收工任务git被无条件放行(收尾clear可能没跑成)。
  修法(主公2026-06-28授权"执行",已全部验证):①git_commit_guard.sh `grep -q savework`→`grep -qx`精确整行匹配(防xsaveworky子串伪装)②savework放行加mtime TTL 30分钟,过期清掉+exit 2拦截③新建clear_git_unless_savework.sh替代链里无条件clear git(savework新鲜则保留/过期或普通锁照清)④settings.json共享层UserPromptSubmit第94行命令替换,保持在discord_approve之前。9个场景测试全PASS(新鲜保留/普通清/过期清/子串不豁免/守卫放行不消耗/守卫过期拦截/无锁拦截/普通锁消耗/非git放行)。备份.bak_20260628_220723(git_commit_guard+settings.json,7天兜底删)。共享层settings.json改动需重启三实例生效。 | 状态：已自行修复(待重启生效+下次收工实测验证)

[2026-06-29 17:58] ⚠️ 数据错误(被主公纠正) | 场景：P8 Sage Seeds市场分析报"花中位单价$9/64%卖$20以下",主公一句"哪里有$9的花"点破 | 表面错误：把Alpine IQ parentCategory=Flower全算成"花",得出荒谬的$9中位价 | 根因：未对原始数据做常识校验(NY大麻花不可能$9),也没看商品name字段——Flower分类下混了大量预卷(Pre-Roll/0.5g/joint),是预卷把中位拉到$7-9;真实散花(3.5g/7g/28g)中位$33均$38 | 建议规则变更：①输出任何"价格/单价"统计前必须先看几条原始记录的name+单位,做常识校验(违反feedback_understand_before_act+prediction_data_first)②品类聚合前先确认子品类构成,别把混合品类当单一品类 | 验证标准：下次做品类/价格分析,先抽样5条看name确认口径再聚合 | 验证状态：【待验证】 | 状态：已自行修复(重算拆分预卷/散花)
