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

[2026-05-10][reference] 双 bot Discord 身份：cowork bot DM channel=1485128242808619079，opus_CC DM channel=1503165641379545228（user_id=1503158821345034360, username=opus_CC#0475），两 bot 都在 server TT基地(id=1466957346310717636)；token 各自独立存 /home/cowork/.claude/channels/discord/.env 和 /home/cowork/opus_home/.claude/channels/discord/.env

[2026-05-10][reference] 双 bot 完全隔离架构（防 HOME 被串）：独立 tmux server（`tmux -L opus_socket`）+ 独立 HOME（/home/cowork vs /home/cowork/opus_home）+ 独立 plugin cache（必须各自跑 /plugin install）+ 独立 Discord token；用同一 tmux server 不同 session 会串 HOME

[2026-05-10][reference] 远程给独立 HOME 的 Claude Code 装 plugin 方法：`tmux -L <socket> send-keys -t <session> '/plugin install xxx' Enter` → 8s 后再 `send-keys Enter` 确认 user scope → 再 send-keys '/reload-plugins' Enter；之后重启进程让顶部 banner 刷新

[2026-05-10][reference] VPS DigitalOcean droplet 信息：hostname=ubuntu-s-1vcpu-2gb-nyc1, IP=142.93.207.54, 端口22；root 直接 SSH 登入（PermitRootLogin yes），主公本地 WSL 已配 SSH key 无需密码；管理方式优先 DO 网页 Droplet Console（最简单），其次本地 WSL `ssh root@142.93.207.54`

[2026-05-10][reference] opus_CC systemd 服务最终架构：cowork-opus.service 装在 /etc/systemd/system/，Environment=HOME=/home/cowork/opus_home，ExecStart=claude_opus_runner.sh，ExecStop=tmux -L opus_socket kill-server；与 cowork-claude.service 完全独立；两个 bot 都 enabled，VPS reboot 自动起

[2026-05-09][reference] Discord plugin v0.0.4 fetchAllowedChannel bug：server.ts line 415 `ch.recipientId ?? dmChannelUserMap.get(id)` 在 partial DM channel 状态下 ch.recipientId 错返 bot 自己 ID（应为对方 user ID），?? 短路不走 fallback 导致抛 "channel is not allowlisted"。修复：反转 ?? 顺序为 `dmChannelUserMap.get(id) ?? ch.recipientId`（dmMap 是 inbound 验证过的可靠值）。每次 plugin 升级后需重新 patch。备份位置：VPS /root/.claude/plugins/cache/.../discord/0.0.4/server.ts.bak_fix。

[2026-05-09][feedback] 诊断 plugin/工具执行问题必须先看 claude session jsonl（~/.claude/projects/<cwd>/<sid>.jsonl）解析 user/assistant/tool_use/tool_result 事件流，看 claude 实际做了什么。只看 hook log/server stderr 不看 claude 行为会反复误判（P11 4 次诊断全错的根因）。

[2026-05-10][reference] DigitalOcean VPS 封了所有出站 SMTP 端口（25/465/587），Gmail/Brevo/SendGrid 的 SMTP 方式全部不通。唯一可用的方式是 HTTP API（走443）。当前用 Brevo REST API（https://api.brevo.com/v3/smtp/email）替代，BREVO_API_KEY存 config/api_keys.env。所有发件脚本已改为 urllib 调 Brevo API（不依赖 smtplib）。

[2026-05-10][project] VPS 架构澄清：cowork-claude.service 跑在 cowork 用户下（/home/cowork/cowork/），不是 root 用户（/root/cowork/）。这是从 root 迁移到非 root 用户后的当前状态。scripts/log_session.py 里的 JSONL_DIR 已修正为 -home-cowork-cowork/（原来是 -root-cowork/，已修复）。

[2026-05-10][feedback] 遇到新环境/新会话，第一步必须跑 hostname + whoami + pwd + curl ifconfig.me 确认环境；不能凭路径格式猜测（/home/cowork/不一定是云端，可能就是VPS上的非root用户）。本次对话浪费大量来回是因为没有先查环境信息。


[2026-05-11][reference] Playwright MCP 已禁用（mcp.json disabled:true），需要时告知我临时开启+重启对话；实际未被主动使用过，scraper走Python库不走MCP

[2026-05-11][reference] cowork bot 无法访问 opus_CC 的 DM channel（1503165641379545228）—— Missing Access，因为那个 channel 是用 opus_CC token 建的。要问 Opus 意见，改用 Agent tool with model="opus" 派子agent。

[2026-05-11][feedback] token 优化优先级（Opus 验证）：① MEMORY.md 分层（高频/低频 feedback 分两文件，省 2-3KB/对话，ROI 最高）② /compact 习惯 ③ Playwright MCP 禁用（已完成）④ CLAUDE.md 精简（收益太小，执行确认区压缩净负向，不做）

[2026-05-11][reference] Sonnet 4.6 context window = 200K tokens；Prompt Cache 工作正常（每轮几乎全从缓存读，incremental 极低）；Opus sub-agent 返回结果占 ~26K tokens（派 Opus 很贵，非必要少用）；87K/200K = 43% 是约 15 轮正常对话的水平（含大文件读取+agent spawn）
