---
name: reference_dual_bot
description: VPS 3 实例 Claude Code 架构：cowork + opus_CC + opus2，完全隔离，频道ID/IP/systemd/plugin安装方法（文件名仍叫 dual_bot 是历史，实际已 3 实例 since 2026-05-27）
type: reference
originSessionId: 8a06505e-fc15-40da-9a68-546769d6bf1f
---
## 3 实例身份 — 唯一权威映射表（2026-06-25 全字段运行时实测+交叉验证，单一来源）

> ⚠️ **认实例只认「tmux socket + HOME」，绝不能靠 session 名**：三实例各用独立 socket（AA 默认 / BB opus_socket / CC opus2_socket），不在同一命名空间，session 名不会撞；但仍**禁止靠 session 名判断实例**（名字会改、会误记，2026-06-25 BB 升级险些用 session 名误杀自己实锤）。任何实例操作前先跑 `bash /home/cowork/cowork/scripts/which_instance.sh`（读运行时 HOME+settings，不靠记忆/目录名）。

| 字段 | **AA** | **BB**（本文件所在实例常态） | **CC** |
|---|---|---|---|
| 模型(settings.json权威) | **claude-sonnet-4-6** | **claude-opus-4-8** | **claude-opus-4-8** |
| HOME | /home/cowork | /home/cowork/opus_home | /home/cowork/opus2_home |
| 进程别名 | cowork | opus_CC | opus2 |
| tmux socket | **默认**(无 -L) | **-L opus_socket** | **-L opus2_socket** |
| tmux session 名 | sonnet | cowork_opus | cowork_opus2 |
| Discord DM 频道 | 1485128242808619079 | 1503165641379545228 | 1509045714808737842 |
| bot app id(token解码) | 1485125345014452234 | 1503158821345034360 | 1509035650823753798 |
| Discord token | /home/cowork/.claude/channels/discord/.env | /home/cowork/opus_home/.claude/channels/discord/.env | /home/cowork/opus2_home/.claude/channels/discord/.env |
| systemd service | cowork-claude.service | cowork-opus.service | cowork-opus2.service |
| claude-code 版本 | 三实例**共享同一二进制** `/home/cowork/.local/bin/claude`（BB/CC 无独立安装；runner 脚本用**绝对路径** `CLAUDE_BIN=/home/cowork/.local/bin/claude` 调用，不靠 PATH）→ 磁盘版本必然相同，**别写死、实时查** `claude --version`。升一次=三个全升；差异只在"进程是否已重启加载新版"，不在版本号。⚠️ 系统里另潜伏一份 `/usr/bin/claude`=`/bin/claude`(root装,旧版2.1.138)——实例靠绝对路径用不到它，但**在 PATH 不含 .local/bin 的环境(如 systemd 精简 PATH)手敲 `claude` 会误中旧版**，排查版本诡异先 `readlink -f $(which claude)` 钉死用的哪份 | ← 同左 | ← 同左 |

口诀：**opus=BB，opus2=CC，裸/home/cowork=AA**。Discord 昵称 AA-Sonnet4.6 / BB-Opus4.8 / CC-Opus4.8（昵称模型名可能滞后，自报身份以 settings.json 为准，instance_identity.sh hook 自动注入）。重启某实例只 kill 其 socket（`tmux -L <socket> kill-server`，AA 是默认 socket 用确切 pid `kill <tmux_pid>` 最稳），watchdog 自动拉回。
3 个 bot 同在 server TT基地（guild id=1466957346310717636，**是 guild 不是频道**），3 个 systemd service 均 `enabled` 开机自启。

⚠️ **BB/CC 账号对 claude-fable-5 无权限**（2026-06-13）：最多 opus-4-8；误设 fable-5 会**静默失败**（收得到消息但不回复，无报错）。改模型只能在 opus-4-8 范围内。

**改 Discord 显示名方法**（2026-05-29 实测，token 在各 HOME `.claude/channels/discord/.env`）——两处分开改：群昵称 `PATCH /api/v10/guilds/1466957346310717636/members/@me {"nick":"X"}`；私聊名=bot username `PATCH /api/v10/users/@me {"username":"X"}`（允许大写连字符；坑：`global_name` 字段 bot 不认，HTTP 200 但不生效，必须改 username）。改名只动显示层，不碰 tmux/systemd/路径/plugin 连接（认 token 不认名）。

---

## 完全隔离架构

**必须隔离的3个层级**（任一层串联都会出问题，memory 已主动改为共享见下）：
1. **tmux server**：`tmux`（cowork）vs `tmux -L opus_socket`（opus_CC）；同一server不同session会串 HOME
2. **HOME目录**：/home/cowork/ vs /home/cowork/opus_home/；plugin cache、settings 独立（memory 例外）
3. **plugin cache**：各自单独跑 `/plugin install`，不能共用
4. **Discord token**：各自独立 .env 文件

**⚠️ Claude 账号登录 = 共享层（非隔离，2026-06-20 事故暴露）：**
三实例用**同一个 Claude 账号**登录（同 email zhitao776@gmail.com + 同 accountUuid，各 `$HOME/.claude/.credentials.json`）。这是 OAuth refreshToken **互挤掉线**的结构性来源——同账号谁刷新一次可能让其他实例旧 refreshToken 作废 → accessToken 过期后 401。
- 症状/诊断/修复（手动 /login）详见 `reference/knowledge_base.md` "三实例 Claude 登录 401 掉线"
- 排查铁律：①重启无效（重读残缺凭证）②别凭欢迎页 "Claude Max" 判断恢复，必须实测消息能回

**Memory 例外（2026-05-12 决策，2026-06-10 升级为单一物理目录）：**
打破原 4 层隔离中的 memory 独立，三实例共享**同一份物理记忆** `/home/cowork/cowork/memory/`（git 正本）：
- AA/BB/CC 的 `$HOME/.claude/projects/-home-cowork-cowork/memory` **全部是 symlink** → `/home/cowork/cowork/memory`
- 原生记忆机制和自建规矩（CLAUDE.md/整理记忆 skill）写的是同一处，任一实例修改全员立即生效
- 历史教训（2026-06-10 漂移事故）：5/12 只链了 BB、5/27 CC 上线漏链 → CC 裸跑无记忆 + 双目录漂移；详见 friction_log 2026-06-10 + INSIGHTS [ref-worthy]
- ⚠️ **新实例上线 checklist（必做）**：创建 `$NEW_HOME/.claude/projects/-home-cowork-cowork/` 后，**禁止留真目录**，必须执行
  `ln -s /home/cowork/cowork/memory $NEW_HOME/.claude/projects/-home-cowork-cowork/memory`
  并用 `readlink -f` 逐实例实测确认（不能凭记录断言已配置）
- 理由：主公多模型入口共享上下文需求，远程使用切换繁杂
- 详细记录见 `reference/dual_bot_setup_log.md` 章节六

---

## DO VPS 信息

- hostname: ubuntu-s-1vcpu-2gb-nyc1
- IP: 142.93.207.54
- 端口: 22
- SSH: `ssh root@142.93.207.54`（已配 SSH key，无需密码）
- 管理优先级：①DO网页 Droplet Console（最简单）②本地 WSL SSH

---

## systemd 服务架构

- **cowork bot**：`cowork-claude.service`，Environment=HOME=/home/cowork/，ExecStart=claude_runner.sh
- **opus_CC**：`cowork-opus.service`，Environment=HOME=/home/cowork/opus_home/，ExecStart=claude_opus_runner.sh，ExecStop=`tmux -L opus_socket kill-server`
- **opus2**：`cowork-opus2.service`，Environment=HOME=/home/cowork/opus2_home/，ExecStart=claude_opus2_runner.sh，ExecStop=`tmux -L opus2_socket kill-server`（2026-05-27 上线）
- 3 个服务都 `enabled`，VPS reboot 自动起；完整索引见 `cowork/reference/cron_jobs.md` 的 Systemd 区块

---

## 远程给独立HOME装plugin

```bash
tmux -L opus_socket send-keys -t cowork_opus '/plugin install <plugin-name>' Enter
# 等8秒
tmux -L opus_socket send-keys -t cowork_opus '' Enter   # 确认 user scope
# 等2秒
tmux -L opus_socket send-keys -t cowork_opus '/reload-plugins' Enter
```

之后重启进程让顶部 banner 刷新（显示 "Listening for channel messages from: ..." 表示订阅生效）

---

## 实例间任务派发（2026-05-29 实测打通）

一个实例可直接给另一个实例派任务，三段链已验证：**投递 → 执行 → 共享文件回传**。实测从 opus_CC 派"查纽约天气"给 opus2，opus2 自动 WebSearch 后写回 `/tmp/team_mailbox/opus2_weather.txt`，18 秒拿到结果。

**用法**：
```bash
# 1. 先只读看目标是否空闲，避免打断
tmux -L opus2_socket capture-pane -t cowork_opus2 -p | tail
# 2. 发任务文字（单引号防本机 $ 展开）
tmux -L opus2_socket send-keys -t cowork_opus2 '任务文字...'
# 3. 必须【单独】再发一次 Enter 才会提交（关键坑）
tmux -L opus2_socket send-keys -t cowork_opus2 Enter
# 4. 轮询共享文件取结果（约定 /tmp/team_mailbox/）
```

**实测要点**：
- **Enter 必须分开发**：文字和 Enter 同一条 send-keys（如 `'...' Enter`）→ 文字进输入框但**不提交**；补发单独 Enter 才提交。（与上面装 plugin 的写法不同，长任务文字尤其要分开）
- **opus2 当时是 bypass permissions 模式** → 执行工具不弹授权、不卡死；非 bypass 实例派需工具授权的活会卡（无人点允许）
- **输入框里的历史命令是 ghost 提示**，不是真内容，Ctrl+U/Escape/退格都删不掉，但一打字就被替换 → 直接输入即可，不用清
- 回传走共享文件最稳（send-keys 反向"门铃"叫醒发起方是可选增强；Stop hook 自动查信未测）

**让被派实例把结果发回主公 Discord（2026-05-29 实测通）**：派任务时在指令里给它自己的频道 chat_id，让它调 `mcp__plugin_discord_discord__reply`。opus2 的 chat_id = `1509045714808737842`。坑：send-keys 进去的是**终端门**，不经 Discord，所以默认主公在频道看不到；要主公手机可见必须显式让被派实例 reply 到自己频道。chat_id 不在 access.json，要从该实例 jsonl `grep 'chat_id="[0-9]+"'` 挖。

---

## BB/CC MCP 配置（2026-06-22 资源优化）

BB（opus_home）已**禁用** `context7` 和 `playwright` 两个常驻 MCP（`/home/cowork/opus_home/.claude/settings.json` 中 `disabled: true`）。禁后 swap 435M→293M，常驻内存占用降低。CC（opus2_home）配置同步跟进。

**原因**：VPS 1核/1.9G，三实例 Claude 主进程合计 ~877M，同时跑重任务仍会卡顿，禁用不常用 MCP 是缓解措施，根治需升级 2核4G（待 Mac mini 迁移解决）。

**bot token 警示（2026-06-22 教训）**：AA 曾错误对调 BB/CC 的 Discord bot token，导致 BB 两小时无响应。root cause：凭目录名序号（opus2=第2个=BB）直觉动手而非查文档。**操作铁律：涉及 BB/CC 任何操作前，先查 `memory/feedback_instance_mapping.md` 表格或跑 `which_instance.sh`**。

---

## 实例疑似卡死/串台 诊断防错（2026-06-19 AA 幻觉事故沉淀）

**🩺 实例疑似卡死的标准诊断流程**（别凭体感猜，按序走）：
1. `bash scripts/which_instance.sh` → 确认进程活没活（活着但不回 ≠ 进程死）
2. 读它最新 jsonl（`$HOME/.claude/projects/-home-cowork-cowork/*.jsonl`）→ 看是不是**幻觉死扛**：连续重复输出 / 把某条指令误读成"别回复"等
3. 确认是会话级卡死 → 杀对应 tmux server（**杀前必核对 `/proc/<pid>/environ` 的 HOME 确认是目标实例**，systemd 无 root 权限重启会被拦）→ watchdog 自动拉起干净进程
4. 看门狗 `scripts/instance_watchdog.sh` 已自动做第1-2步检测并通知（每5分钟），但**只通知不自动重启**，重启仍需主公/人工触发

**🚫 一个实例无法从自己的 Bash 工具干净拉起「别的」实例（2026-06-26 CC 实测两次踩坑）**：
某实例（如 CC）想用自己的 Bash 工具 `setsid`/`nohup`/`env` 启动另一个实例（如 AA）的 runner，**HOME 会被强制注入成发起方自己的值**（CC 起 AA → 子进程 HOME 仍是 opus2_home），结果起出来的是发起方的副本（又一个 CC），不是目标实例，并会双进程连同一 Discord 频道冲突。`HOME=/home/cowork` 命令前缀**穿不透**（源头是 claude 进程对子进程的 env 注入/shell-snapshot，非脚本文本）。
- **铁律**：拉起/重启某实例**只有两条干净路径**——① 主公用 `sudo systemctl start/restart <service>`（systemd 启动环境干净，不继承任何实例 shell）；② 从一个**不受发起方 shell 污染**的独立终端。**禁止**用 Bash 工具 setsid/nohup 跨实例拉起。
- 若误起了副本：立即 `kill <pid>`（**先核 `/proc/<pid>/environ` 的 HOME 确认是误起的副本再杀**），CC/BB 正常进程不受影响。

**🆔 guild ID ≠ channel ID（曾误判）**：
`1466957346310717636` 是 Discord 服务器「TT基地」的 **guild ID**，**不是频道号**。三 bot 都在这个 guild，但日常对话走各自 DM 频道（type=1）。看到它别当成"残留频道号"。三实例 DM 频道见上表（AA=...18619079 / BB=...79545228 / CC=...09737842）。

**⬆️ 升级 claude-code 的完整指南（2026-06-25 CC 实测打通 2.1.170→2.1.191）**：
- ⚠️ **两份安装陷阱**：实例实际跑的是 `/home/cowork/.local/bin/claude`（PATH 里它在前），而 `npm config get prefix` 指向 `opus_home/.npm-global`。**`npm i -g` 升的是 .npm-global 那份=没人用、白升**。要升必须 `npm install -g --prefix /home/cowork/.local @anthropic-ai/claude-code@<ver>`。
- **升级标准流程（务必先试一个非当前对话实例，CC 最佳）**：
  1. 备份 `$HOME/.claude/plugins/{installed_plugins,known_marketplaces}.json`
  2. 升级 .local（见上）
  3. **关键：用新版重装 Discord plugin** `HOME=$TARGET /home/cowork/.local/bin/claude plugin install discord@claude-plugins-official`（旧的 project-scope 登记 2.1.191 不认，重装成 user-scope 才识别）
  4. 重启实例 `tmux -L <socket> kill-server`（systemd 无 root 重启会被拦），watchdog 自动拉回；CC socket=opus2_socket
  5. 验证：debug 日志 `Found N plugins (N enabled)` + `MCP server "plugin:discord:discord": Successfully connected` + bun discord 进程归属对（`ps` 看 HOME）；最后实测发条 Discord 消息确认双向通
- **2.1.191 不兼容的真根因（不是版本 bug）**：旧版 2.1.170 宽容，2.1.191 严格按 `known_marketplaces.json` 的 `installLocation` + `installed_plugins.json` 的 `installPath` 找 plugin 缓存；CC 这两处历史上**错写成 opus_home（BB目录）跨实例错位**，旧版能绕过、新版 cache-miss→`Found 0 plugins`→plugin 不加载→Discord 失联。修法=改对路径指回自己 opus2_home + 用新版重装（见上步骤3）。
- 首启会弹 "Try fullscreen renderer? 1/2" 交互菜单卡启动，选 2 跳过一次后记住。
- **隔离调试法**（不碰运行实例）：独立 socket 跑 `tmux -L test_sock ... HOME=$TARGET /home/cowork/.local/bin/claude --debug --channels plugin:discord@...`，读 `$HOME/.claude/debug/*.txt` 看 plugin 加载报错。
- 回滚：`npm install -g --prefix /home/cowork/.local @anthropic-ai/claude-code@2.1.170` + 重启。磁盘换版不影响运行中进程（旧版在内存），故可单实例试错。
- ⚠️ **关于"各实例版本"的澄清（2026-06-25 CC 实测）**：三实例共享同一二进制（见上表版本栏），不存在"某实例还停在旧版"这回事——磁盘上只有一份，当前 2.1.193。升级 = 换那一份 = 三个一起换。本指南里的 `2.1.170` 是**历史踩坑记录**（当时从 2.1.170 升 2.1.191 的过程），不是任何实例的当前状态。要查当前版本永远跑 `claude --version`。

**🔍 "真串台 vs 主公转述" 判别法**（曾两度误判）：
看到**别的实例的署名/回复出现在我频道**时，先查 Discord API 该消息的 `author` 字段：
`GET /api/v10/channels/<chan>/messages/<msgid>` → author.id 若是主公(811758070534766613)=**主公手动转述**（给我看的），不是实时串台；若是某 bot id=才是真串台。
辅证：跨频道 `fetch_messages` 报 **403 Missing Access** = 频道物理隔离正常，bot 进不去别人频道。
**别凭"看到别的实例名字"就推理串台**，先用 author 字段证伪。
