# 迁移日记 (Migration Log)

> **用途**：记录每次"机器迁移"的实操过程，下次搬到新机器时查这份就知道当时怎么做的。
>
> **维护规则**：
> - 每次迁移完成时，在**顶部**追加新章节（时间倒序，最新在上）
> - 每节标准格式：① 时间+起讫机器 ② 关键凭证 ③ 已完成（按操作顺序）④ 踩坑提醒 ⑤ 下次迁移 checklist ⑥ 详细诊断引用（指向 `archive/`）
>
> **职责边界**（避免和其他文档冲突）：
> - 本文档只记 **"做了哪些操作"**（cp/sed/systemctl 等动作）
> - **"当前配置长什么样"**（settings.json deny 列表/hook 表/工作流细节）→ 看 `ARCHITECTURE.md` "权限与守卫体系"节
> - **"某天的实时诊断时间线"** → 看 `archive/<date>_*.md`

---

## 2026-05-10：最终完成 — cowork 用户化 + 全面交接

### 路径变更（root → cowork 用户）

迁移初期系统以 root 用户运行（路径 `/root/cowork/`）。后续创建了 cowork 专用用户，所有文件和 Claude Code 进程迁至 cowork 用户，提高安全性。

| 旧路径（root 用户） | 新路径（cowork 用户） |
|---|---|
| `/root/cowork/` | `/home/cowork/cowork/` |
| `/root/.claude/` | `/home/cowork/.claude/` |
| systemd `User=root` | systemd `User=cowork` |

### 今日最终完成项（2026-05-10）

1. **WSL2 cron 关闭**：主公在 WSL2 跑 `crontab -r`，VPS 成为唯一运行端 ✅
2. **完整冒烟测试通过**：Discord reply / Brevo发件 / cowork.db(71 sessions) / P9持仓DB(6只open) / catalyst_monitor实跑 / signal_alert / 搜索Skill 全部验证 ✅
3. **smtplib → Brevo 修复**：`run_daily_news.sh` ERR trap + Step3 发件从 smtplib 改 Brevo HTTP API（DO封了出站SMTP 465/587端口）✅
4. **临时文件路径修复**：`/tmp/news_ai.txt` 被 root 占用导致 VPS 首跑失败；改用 `$SCRIPTS/news_ai.tmp`（cowork 有权限）✅
5. **Discord Bot token fallback**：`tide_utils.py load_env()` 加 fallback，自动从 `.claude/channels/discord/.env` 补读 DISCORD_BOT_TOKEN；`config/api_keys.env` 删除过期旧 token ✅
6. **sshfs WSL 挂载配置**：`sshfs root@142.93.207.54:/home/cowork/cowork ~/vps-cowork`；`~/.bashrc` 加自动挂载 ✅

### 最新关键路径（cowork 用户）

| 用途 | 路径 |
|---|---|
| cowork 主目录 | `/home/cowork/cowork/` |
| Claude Code 配置 | `/home/cowork/.claude/` |
| Discord 配置 | `/home/cowork/.claude/channels/discord/` |
| Discord plugin 源码 | `/home/cowork/.claude/plugins/cache/claude-plugins-official/discord/0.0.4/` |
| API keys | `/home/cowork/cowork/config/api_keys.env` |
| Discord bot token | `/home/cowork/.claude/channels/discord/.env` |
| WSL 挂载点 | `~/vps-cowork/`（= VPS `/home/cowork/cowork/`）|
| systemd service | `cowork-claude.service`（User=cowork）|

### 关键命令（最新版）

```bash
# 进 VPS
ssh root@142.93.207.54

# 切 cowork 用户
sudo su cowork

# 进入 cowork claude tmux
tmux attach -t cowork

# 查看服务状态
systemctl status cowork-claude

# WSL 挂载 VPS（已写入 ~/.bashrc 自动挂载）
sshfs root@142.93.207.54:/home/cowork/cowork ~/vps-cowork
```

---

## 2026-05-08 → 2026-05-10：WSL2 → DigitalOcean VPS（NYC1）

### 关键凭证（VPS 信息）

| 项 | 值 |
|---|---|
| 提供商 | DigitalOcean Basic Droplet |
| 规格 | 1 vCPU / 2GB RAM / 50GB SSD / NYC1 |
| 价格 | $12/月 |
| **IPv4** | **142.93.207.54** |
| SSH | `ssh -i ~/.ssh/id_ed25519 root@142.93.207.54` |
| Ubuntu | 24.04 LTS |
| 时区 | America/New_York (EDT) |
| swap | 2GB（已激活）|

## ✅ 已完成

1. **阶段 A：VPS 基础环境**
   - apt update + upgrade
   - 装 git / tmux / python3-pip / build-essential / rclone / sqlite3 / unzip
   - Node.js v22.22.2 + npm 10.9.7
   - bun 1.3.13（在 /root/.bun/bin/bun，软链 /usr/local/bin/bun）
   - 时区设为 America/New_York
   - 加 2GB swap

2. **阶段 B：Claude Code + 依赖**
   - 装 Claude Code v2.1.137 (`/usr/bin/claude`)
   - **OAuth 已登录**（主公 Anthropic Max 账号，credentials 在 `/root/.claude/.credentials.json`）
   - Python 包：yfinance / alpaca-py / anthropic / openai / voyageai / pandas / curl-cffi / discord.py / feedparser 等都装好（system Python，--break-system-packages）
   - Playwright + Chromium 装好

3. **阶段 C：数据迁移**
   - cowork 主目录搬到 `/root/cowork/`（58MB，字节级一致验证通过）
   - `~/.claude/` 配置搬到 VPS：settings.json + 9 Hooks + 12 Skills + channels/discord/.env + plugins/（含 Discord plugin v0.0.4）
   - 路径硬编码全部 sed 替换：`/mnt/c/Users/zhi89/Desktop/cowork → /root/cowork` + `/home/zhi8939 → /root`
     - settings.json 0 残留
     - hooks/ 9 个文件 0 残留
     - cowork *.py/*.sh 全替换
     - plugins/installed_plugins.json 0 残留
     - **cowork 内 .md 文档还有 37 处残留路径**（不影响运行，是文档同步债）
   - chown -R root:root /root/.claude /root/cowork
   - 关键文件验证：cowork.db (45MB) / personal.db (5.3MB) / trading.db (820KB) 字节一致

4. **阶段 C-5：cron 任务**
   - 15 个定时任务全部翻译路径并写到 root crontab
   - PATH 已加 `/root/.bun/bin` 让 cron 能找 bun
   - 所有 .sh 文件加了执行权限

## ⚠️ 当前状态（VPS 上还在跑）

```
tmux session "cowork" 仍然在跑（PID 22045/22046）
bun server.ts 仍然在跑（PID 22071）—— Discord MCP server
```

## ❌ 未完成 / 明天要做

### ✅ P0：Discord plugin bug 完整闭环（2026-05-09 22:30）

**两阶段闭环**：

**阶段 A（21:11）—— inbound 链路修复**：
- 真根因：systemd unit ExecStart 漏 `--channels plugin:discord@claude-plugins-official` → host 没订阅 plugin channel → notification 收下来直接丢
- 修复：sed 改 ExecStart + daemon-reload + restart + ack trust → claude TUI 显示 "Listening for channel messages from: plugin:discord@claude-plugins-official"
- 验证：[DBG-MSG]/[DBG-GATE]/[DBG-NOTIFY] 三步全过 → claude 收 channel notification 进入 agent loop

**阶段 B（22:30）—— reply outbound bug 修复（37 天悬案）**：
- 真根因：server.ts line 415 `ch.recipientId ?? dmChannelUserMap.get(id)` 中 ch.recipientId 在 partial DM channel 状态下错返 bot 自己 ID → ?? 短路不走 fallback → bot ID 不在 allowFrom → 抛 "channel is not allowlisted"
- 解释为何 WSL 通 VPS 不通：partial 数据状态依赖运行时 cache/timing；WSL 上 ch.recipientId 是 undefined → 走 fallback；VPS 上是 bot ID → 不走；**两边都有 bug，WSL 运气好没暴露**
- 修复：反转 `??` 顺序为 `dmChannelUserMap.get(id) ?? ch.recipientId`（dmMap 是 inbound 验证过的可靠值）
- 备份：`/root/.claude/plugins/cache/.../discord/0.0.4/server.ts.bak_fix`
- ⚠️ **plugin 升级会丢失修复，需重 patch**

**配套：Claude Code 权限体系建立（2026-05-09 22:55 → 2026-05-10 00:25）**：

按时间顺序的操作步骤（**配置内容看 `ARCHITECTURE.md` "权限与守卫体系"节**）：

1. **22:55** — 往 `~/.claude/settings.json` `permissions.allow` 加 5 个 Discord mcp 工具（reply/react/edit_message/fetch_messages/download_attachment），免每次发回复弹窗
2. **23:35** — 加 `WebFetch` + `WebSearch` 到 allow（避免每次抓官方文档/查资料弹窗）
3. **23:54** — 升级到 **task-scoped 一次性授权模型**：
   - 加 `permissions.defaultMode: "bypassPermissions"`（permission 弹窗整体关掉）
   - 加 `permissions.deny` 15 条兜底毁灭性操作（rm -rf /root/home/~/$HOME / mkfs / dd of=/dev/* / git push -f / curl|bash / chmod 777 / chown -R）
   - 配套 hook 不变（`system_file_guard.sh` / `git_commit_guard.sh` / UserPromptSubmit 自动 `rm /tmp/task_approved`）
4. **00:25** — 升格本文档：`mv archive/vps_migration_progress_2026-05-09.md → cowork/MIGRATION_LOG.md`，作为可持续追加的迁移日记主入口

**新工作流（task-scoped）**：主公给任务 → 我列方案 → 主公同意 → `touch /tmp/task_approved` → 我一气呵成执行 → 完成时 `rm /tmp/task_approved` → 下次主公消息 UserPromptSubmit hook 自动清。

**前判错误（已 friction）**：①双向 [DBG-MSG] 误判"已自愈"②TUI hi 误判"plugin 工作"③判"host v2.1.138 不处理 method"④判"cowork 规则在 channel mode 不调 reply 工具"（实际 claude 调了被 plugin 拒绝，没看 session jsonl 就下结论）。

**完整诊断+修复记录**：见 `archive/discord_plugin_reply_bug_fix_2026-05-09.md`（9 阶段时间线 + 可复用 patch.py 脚本 + 5 条教训）。

**当前 server.ts 状态**：所有调试日志（[DBG-MSG]/[DBG-GATE]/[DBG-NOTIFY]/[DBG-FETCH]）已清干净。备份位置：`server.ts.bak_fix`（干净版+修复后），`server.ts.bak_dbg`（patch 前的调试版本）。

### 🟡 P1：systemd 服务（开机自启 + 进程崩溃自动重启）
未配。重启 VPS 后 tmux + claude 不会自动起来。
明天先建 `/etc/systemd/system/cowork-claude.service`：
```
[Service]
Type=forking
ExecStart=/usr/bin/tmux new-session -d -s cowork -c /root/cowork "/usr/bin/claude"
ExecStartPost=/bin/bash -c "sleep 3 && /usr/bin/tmux send-keys -t cowork 1 Enter"
ExecStop=/usr/bin/tmux kill-session -t cowork
Restart=on-failure
```

### 🟡 P2：rclone Google Drive 异地备份
未配。明天：
1. `rclone config` 在 VPS 上跑（OAuth 主公手机点 Allow）
2. 写 cron：每天 02:00 同步 `/root/cowork/trading/` 到 `gdrive:cowork-backup/trading/` 并加 `--backup-dir` 保留历史

### 🟡 P3：冒烟测试
- 跑 `bash /root/cowork/trading/run_py.sh /root/cowork/trading/cognitive_scanner.py` 看是否能正常跑
- 跑 `bash /root/cowork/newscripts/run_daily_news.sh` 看新闻能不能拉
- 检查 cron log 是否累积

## 关键路径（VPS 上）⚠️ 已过期，见顶部"最新关键路径"

| 用途 | VPS 路径（旧·root用户，已迁移至 cowork 用户）|
|---|---|
| cowork 主目录 | ~~`/root/cowork/`~~ → `/home/cowork/cowork/` |
| Claude Code 配置 | ~~`/root/.claude/`~~ → `/home/cowork/.claude/` |
| Discord 配置 | ~~`/root/.claude/channels/discord/`~~ → `/home/cowork/.claude/channels/discord/` |
| API keys | ~~`/root/cowork/config/api_keys.env`~~ → `/home/cowork/cowork/config/api_keys.env` |
| Discord bot token | `/home/cowork/.claude/channels/discord/.env`（路径不变）|
| 日志（debug）| `/tmp/discord-server.log` |
| crontab | `crontab -l` 看（cowork 用户下）|

## 关键命令（明天接续用）

```bash
# 进 VPS
ssh -i ~/.ssh/id_ed25519 root@142.93.207.54

# 看 cowork claude 是否还在跑
tmux ls
ps aux | grep -E '/usr/bin/claude|bun' | grep -v grep

# 进入 cowork claude TUI
tmux attach -t cowork

# 退出 tmux 不杀进程
# Ctrl+B 然后按 D

# 重启 cowork claude
tmux kill-session -t cowork
cd /root/cowork && tmux new-session -d -s cowork -c /root/cowork '/usr/bin/claude'
sleep 3
tmux send-keys -t cowork '1' Enter

# 看 Discord plugin debug 日志
tail -50 /tmp/discord-server.log
```

## 重要事项 / 注意事项

- ⚠️ **VPS 上 ssh 跑 `pkill -f claude` 或 `pkill -f bun` 容易把 SSH 连接也杀了** — 要用精确 PID kill
- ⚠️ **Windows 这边主公 WSL2 的 cowork 助理（pts/2 上的 PID 133112 那个 claude）今晚还在跑** — 主公明天可以决定彻底关掉（关 Windows terminal）转 VPS，或者继续在 Windows 用（备份）
- ⚠️ **WSL2 + VPS 不要同时跑 Discord plugin**（双开 token 互踢）
- ✅ Discord bot token 在 VPS 上 `/root/.claude/channels/discord/.env`，bot 名 CC#4034 / CCclaude
- ✅ 主公的 user_id: 811758070534766613 在 access.json allowFrom 里
- ✅ 主公 guild "TT基地" id: 1466957346310717636

---

**保存于 2026-05-09 00:10 EDT。主公好梦，明天接续。**
