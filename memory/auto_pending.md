# 待审记忆（Auto Pending）

> 由系统自动捕获，Claude 审核后写入正式 memory/
> 格式：[时间][类型] 内容
> 类型：user / feedback / project / reference

[2026-05-09][project] P9 TIDE当前阶段原则：快速验证模式（纸账号）。操作偏向执行不过度分析；全买候选池+等权分配最大化数据点；进实盘前才切换谨慎模式。所有P9建议基于此框架给出。

[2026-05-09][feedback] 进入任何项目对话（主公说"继续PX"/"继续P9"等）→ 必须第一时间读CURRENT_SESSION.md对应区块，把"下一步"列表主动念出来，让主公选做哪个；不等主公问"有什么要做的"。这是主公明确要求的行为。

[2026-05-09][feedback] 检查P9信号状态时，必须先确认当天是否为交易日（周一至周五且非美股节假日），再判断signal_collector是否漏跑；直接看log日期差就下结论会在周末误判成"漏跑"。

[2026-05-09][project] P9明确决策：纸账号阶段不做每日价格记录（无日线DB表）。验证框架是30/60/90天节点，max_drawdown_pct等日线指标延迟到真账号上线前再做。price_guard的-7%告警已覆盖紧急情况。

[2026-05-09][project] P11 VPS Discord bug降级方案：plugin修不好则改建自建discord.py bot（~100行），直接监听消息→调claude --print→回复，不依赖Claude Code plugin版本，更稳定。比webhook强（双向），比plugin稳（无版本依赖）。

[2026-05-09][project] Cowork系统架构决策："保存存档"（上下文满/换对话）和"收工"（结束工作）应是两个独立指令。保存存档=30秒(CURRENT_SESSION+log+commit)；收工=完整流程。后台agent负责文档对齐+memory预处理，减少收工负担。待建。

[2026-05-09][feedback] 主公的真实痛点：收工太重，上下文满了被迫走完整流程。应优先建轻量"保存存档"指令，和后台文档对齐/memory预处理agent，让收工只剩确认步骤。

[2026-05-09][reference] Discord plugin v0.0.4 fetchAllowedChannel bug：server.ts line 415 `ch.recipientId ?? dmChannelUserMap.get(id)` 在 partial DM channel 状态下 ch.recipientId 错返 bot 自己 ID（应为对方 user ID），?? 短路不走 fallback 导致抛 "channel is not allowlisted"。修复：反转 ?? 顺序为 `dmChannelUserMap.get(id) ?? ch.recipientId`（dmMap 是 inbound 验证过的可靠值）。每次 plugin 升级后需重新 patch。备份位置：VPS /root/.claude/plugins/cache/.../discord/0.0.4/server.ts.bak_fix。

[2026-05-09][feedback] 诊断 plugin/工具执行问题必须先看 claude session jsonl（~/.claude/projects/<cwd>/<sid>.jsonl）解析 user/assistant/tool_use/tool_result 事件流，看 claude 实际做了什么。只看 hook log/server stderr 不看 claude 行为会反复误判（P11 4 次诊断全错的根因）。

[2026-05-10][reference] DigitalOcean VPS 封了所有出站 SMTP 端口（25/465/587），Gmail/Brevo/SendGrid 的 SMTP 方式全部不通。唯一可用的方式是 HTTP API（走443）。当前用 Brevo REST API（https://api.brevo.com/v3/smtp/email）替代，BREVO_API_KEY存 config/api_keys.env。所有发件脚本已改为 urllib 调 Brevo API（不依赖 smtplib）。

[2026-05-10][project] VPS 架构澄清：cowork-claude.service 跑在 cowork 用户下（/home/cowork/cowork/），不是 root 用户（/root/cowork/）。这是从 root 迁移到非 root 用户后的当前状态。scripts/log_session.py 里的 JSONL_DIR 已修正为 -home-cowork-cowork/（原来是 -root-cowork/，已修复）。

[2026-05-10][feedback] 遇到新环境/新会话，第一步必须跑 hostname + whoami + pwd + curl ifconfig.me 确认环境；不能凭路径格式猜测（/home/cowork/不一定是云端，可能就是VPS上的非root用户）。本次对话浪费大量来回是因为没有先查环境信息。

[2026-05-10][feedback] 执行确认标准：只有主公说"可以执行/开始做/直接开始"等才是执行授权；"先解决问题1/先讨论X"只是聚焦方向，不是执行确认。问题2（自作主张）在当场复发就是因为误判了这个边界。

[2026-05-10][feedback] 规则越多模型越飘。认知类行为问题（如猜测标注）不加新规则，改精现有规则；执行流程类问题才考虑 Hook。新增规则门槛："违反了会出事"才写，其他内化。

[2026-05-10][reference] honesty_check.sh Stop Hook：~/.claude/hooks/honesty_check.sh，检测声称读完（全文/读完了/entire file等）但实际只读部分的情况，从 transcript_path 解析 Read 工具调用参数（offset/limit/文件行数）判断是否部分读取，触发时输出警告。

