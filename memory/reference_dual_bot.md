---
name: reference_dual_bot
description: VPS 3 实例 Claude Code 架构：cowork + opus_CC + opus2，完全隔离，频道ID/IP/systemd/plugin安装方法（文件名仍叫 dual_bot 是历史，实际已 3 实例 since 2026-05-27）
type: reference
originSessionId: 8a06505e-fc15-40da-9a68-546769d6bf1f
---
## 3 实例身份（2026-05-27 加入 opus2）

| | cowork bot | opus_CC bot | opus2 bot |
|---|---|---|---|
| Discord DM channel | 1485128242808619079 | 1503165641379545228 | （在 TT基地 guild 内，具体 ID 见 opus2_home access.json） |
| Discord user_id | — | 1503158821345034360 | （token 解码可得，未单列） |
| Discord username | — | opus_CC#0475 | — |
| 模型 | Sonnet 4.6 | Opus 4.7 | Opus 4.7 |
| HOME | /home/cowork/ | /home/cowork/opus_home/ | /home/cowork/opus2_home/ |
| Discord token | /home/cowork/.claude/channels/discord/.env | /home/cowork/opus_home/.claude/channels/discord/.env | /home/cowork/opus2_home/.claude/channels/discord/.env |
| tmux | 默认 socket，session: cowork | socket: opus_socket，session: cowork_opus | socket: opus2_socket，session: cowork_opus2 |
| systemd | cowork-claude.service | cowork-opus.service | cowork-opus2.service（**2026-05-27 上线**） |

3 个 bot 都在 server TT基地（id=1466957346310717636），3 个 systemd service 都 `enabled` 开机自启。

---

## 完全隔离架构

**必须隔离的3个层级**（任一层串联都会出问题，memory 已主动改为共享见下）：
1. **tmux server**：`tmux`（cowork）vs `tmux -L opus_socket`（opus_CC）；同一server不同session会串 HOME
2. **HOME目录**：/home/cowork/ vs /home/cowork/opus_home/；plugin cache、settings 独立（memory 例外）
3. **plugin cache**：各自单独跑 `/plugin install`，不能共用
4. **Discord token**：各自独立 .env 文件

**Memory 例外（2026-05-12 决策）：**
打破原 4 层隔离中的 memory 独立，改为 symlink 共享：
- `/home/cowork/opus_home/.claude/projects/-home-cowork-cowork/memory/` 是 symlink
- → 指向 `/home/cowork/.claude/projects/-home-cowork-cowork/memory/`（cowork bot 活 memory）
- 两个 bot 共享同一份 memory，任一 bot 修改另一个立即生效
- 理由：主公双模型入口共享上下文需求，远程使用切换繁杂
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
