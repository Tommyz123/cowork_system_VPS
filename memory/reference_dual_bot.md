---
name: reference_dual_bot
description: VPS双bot架构：cowork bot + opus_CC bot，完全隔离，频道ID/IP/systemd/plugin安装方法
type: reference
originSessionId: 8a06505e-fc15-40da-9a68-546769d6bf1f
---
## 双Bot身份

| | cowork bot | opus_CC bot |
|---|---|---|
| Discord DM channel | 1485128242808619079 | 1503165641379545228 |
| Discord user_id | — | 1503158821345034360 |
| Discord username | — | opus_CC#0475 |
| HOME | /home/cowork/ | /home/cowork/opus_home/ |
| Discord token | /home/cowork/.claude/channels/discord/.env | /home/cowork/opus_home/.claude/channels/discord/.env |
| tmux | 默认 socket，session: cowork | socket: opus_socket，session: cowork_opus |

两个 bot 都在 server TT基地（id=1466957346310717636）

---

## 完全隔离架构

**必须隔离的4个层级**（任一层串联都会出问题）：
1. **tmux server**：`tmux`（cowork）vs `tmux -L opus_socket`（opus_CC）；同一server不同session会串 HOME
2. **HOME目录**：/home/cowork/ vs /home/cowork/opus_home/；plugin cache、settings、memory 全部独立
3. **plugin cache**：各自单独跑 `/plugin install`，不能共用
4. **Discord token**：各自独立 .env 文件

---

## DO VPS 信息

- hostname: ubuntu-s-1vcpu-2gb-nyc1
- IP: 142.93.207.54
- 端口: 22
- SSH: `ssh root@142.93.207.54`（已配 SSH key，无需密码）
- 管理优先级：①DO网页 Droplet Console（最简单）②本地 WSL SSH

---

## systemd 服务架构

- **cowork bot**：`cowork-claude.service`，Environment=HOME=/home/cowork/，ExecStart 在 /home/cowork/ 下
- **opus_CC**：`cowork-opus.service`，Environment=HOME=/home/cowork/opus_home/，ExecStart=claude_opus_runner.sh，ExecStop=`tmux -L opus_socket kill-server`
- 两个服务都 `enabled`，VPS reboot 自动起

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
