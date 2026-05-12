# 双Bot系统配置参考日志

> 完成日期：2026-05-10
> 作者：Tom + Claude (Sonnet 4.6 + Opus 4.7)
> 用途：下次重建/扩展双bot系统时的完整参考，包含架构决策、踩过的坑、最终配置

---

## 一、架构概览

VPS（DigitalOcean 142.93.207.54）上运行**两个完全独立的 Claude Code bot**：

| 维度 | cowork bot（日常助理） | opus_CC bot（重型分析） |
|---|---|---|
| 用户（Linux） | `cowork` | `cowork`（共享） |
| HOME | `/home/cowork` | `/home/cowork/opus_home` |
| Claude 设置 | `/home/cowork/.claude/` | `/home/cowork/opus_home/.claude/` |
| 模型 | claude-sonnet-4-6 | claude-opus-4-7 |
| tmux socket | 默认（无 -L） | `-L opus_socket` |
| tmux session | `cowork` | `cowork_opus` |
| 守护方式 | systemd `cowork-claude.service` | systemd `cowork-opus.service` |
| Runner脚本 | `scripts/claude_runner.sh` | `scripts/claude_opus_runner.sh` |
| Discord bot | 主公原有 bot token | 独立 opus_CC bot token |
| Discord DM channel | `1485128242808619079` | `1503165641379545228` |
| 工作目录 | `/home/cowork/cowork/` | `/home/cowork/cowork/`（共享） |

**设计原则**：两个 bot 共享同一个 Linux 用户 + 同一个代码库，但通过独立的 HOME 目录实现完全隔离（Claude 配置/插件/历史/凭证互不干扰）。

---

## 二、踩过的坑（按时间顺序）

### 坑1：systemd ExecStart 漏了 `--channels` 参数
**症状**：VPS 上 Discord bot 显示"正在输入"但 Claude 不回复；server.ts 能收到消息，但 Claude 端静默忽略。

**诊断过程（走了很多弯路）**：
1. ❌ 怀疑 WSL2 + VPS 双开抢 token → kill WSL2 后仍不工作
2. ❌ 怀疑 Discord Privileged Intents 未开 → Developer Portal 截图确认全开
3. ✅ 写独立测试脚本验证 Discord 端 + token + intents 正常
4. ✅ 注入 `[DBG-MSG]` log 到 server.ts → 确认能收到消息
5. ❌ 但 claude transcript 里完全无 Discord 消息 → 误判"协议不匹配 v2.1.137"
6. ✅ 最终：diff WSL2 vs VPS 启动命令 → **VPS 的 systemd ExecStart 缺 `--channels plugin:discord@claude-plugins-official`**

**根因**：Claude Code host 没有订阅 plugin channel，notification 收下来直接丢。

**解决**：在 ExecStart 命令末尾加 `--channels plugin:discord@claude-plugins-official`，daemon-reload + restart，立即生效。

**教训**：遇到"A 环境工作 B 不工作"，**第一动作是 diff 启动命令**，不要猜底层协议。

---

### 坑2：Discord access.json 频道填错
**症状**：opus_CC 收到 cowork DM 频道的消息，而非自己的 DM 频道。

**根因**：最初 opus_home 的 `access.json` 的 `groups` 字段填的是 cowork bot 的 DM channel ID `1485128242808619079`，应该填 opus_CC 自己的 `1503165641379545228`。

**解决**：调 Discord API（用 opus_CC token）主动创建 DM channel，获取正确 channel ID，更新 access.json。

**注意**：DM 频道 type:1 的 channel_id 形似 guild channel，容易混淆。

---

### 坑3：两个 bot 共用同一 tmux socket 导致 HOME 环境变量串
**症状**：opus_CC 启动时 HOME 变量被 cowork 的 session 覆盖，claude 读到错误的配置目录。

**根因**：两个 bot 都用默认 tmux socket，tmux 服务端环境变量会共享。

**解决**：opus_CC 改用独立 socket：`tmux -L opus_socket`，彻底隔离两个 tmux 服务。

**最终**：
- cowork → 默认 socket，session `cowork`
- opus_CC → `-L opus_socket`，session `cowork_opus`

---

### 坑4：opus_CC 蹭 cowork 的 plugin cache（没有独立插件状态）
**症状**：opus_CC 的 Discord plugin 不稳定，因为 HOME 不同导致 plugin 路径找不到。

**解决**：通过 `tmux send-keys` 模拟在 opus_CC session 里执行：
```
/plugin install discord@claude-plugins-official
/reload-plugins
```
让 opus_home 自己完整安装一次 plugin，建立独立的插件状态。

---

### 坑5：opus_home settings.json 缺 `env.PATH`
**症状**：opus_CC 的 Discord MCP 显示 failed（✗），不 connected。

**根因**：opus_home 的 settings.json 没有设 `env.PATH`，导致 bun 找不到（MCP server 需要 bun 来跑 server.ts）。

**解决**：在 opus_home `settings.json` 加入：
```json
"env": {
  "PATH": "/home/cowork/.bun/bin:/home/cowork/.local/bin:/home/cowork/.nvm/versions/node/v22.18.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
}
```

**教训**：修改任何 settings.json 时，**必须确认 `env.PATH` 包含 bun/nvm/local**，漏掉会断 Discord。

---

### 坑6：重启命令互相误杀
**症状**：`!重启` 之前用 `tmux kill-session -t cowork`，在 opus_CC session 里执行会找不到 cowork session（因为不同 socket），但如果 socket 共享时会误杀对方。

**解决**：CLAUDE.md 重启规则按 `$HOME` 动态识别自己：
```bash
[ "$HOME" = "/home/cowork/opus_home" ] && tmux -L opus_socket kill-server || tmux kill-session -t cowork
```
两个 bot 各杀各的，互不误伤。

---

### 坑7：VPS 上 pkill 容易把 SSH 连接也杀掉
**症状**：`pkill -f claude` 或 `pkill -f bun` 执行后 SSH exit 255（SSH 本身被杀）。

**解决**：用精确 PID kill，不用模式匹配。

---

### 坑8：诊断工具误判（debug log 回声）
**症状**：注入 `[DBG-MSG]` 后看到日志有消息进来，误以为 Discord 链路通了。

**根因**：`[DBG-MSG]` 漏了 `if msg.author.bot` 过滤，bot 自己发的消息也被记录（回声），造成误判。

**教训**：诊断 claude 工具执行失败时，**第一动作读 claude session jsonl**（`~/.claude/projects/<cwd>/<sid>.jsonl`），而不是看 hook log 或 server stderr。

---

## 三、最终配置文件清单

### 3.1 Systemd 服务

**cowork bot** (`/etc/systemd/system/cowork-claude.service`)：
```ini
[Unit]
Description=Cowork Claude Code (tmux-wrapped, non-root, watchdog)
After=network.target

[Service]
Type=simple
Restart=on-failure
RestartSec=5
User=cowork
Group=cowork
Environment=HOME=/home/cowork
WorkingDirectory=/home/cowork/cowork
ExecStart=/home/cowork/cowork/scripts/claude_runner.sh
ExecStop=/bin/sh -c "/usr/bin/tmux has-session -t cowork && /usr/bin/tmux kill-session -t cowork || true"

[Install]
WantedBy=multi-user.target
```

**opus_CC bot** (`/etc/systemd/system/cowork-opus.service`)：
```ini
[Unit]
Description=Cowork Opus Claude Code (tmux-wrapped, non-root, watchdog)
After=network.target

[Service]
Type=simple
Restart=on-failure
RestartSec=5
User=cowork
Group=cowork
Environment=HOME=/home/cowork/opus_home
WorkingDirectory=/home/cowork/cowork
ExecStart=/home/cowork/cowork/scripts/claude_opus_runner.sh
ExecStop=/bin/sh -c "/usr/bin/tmux -L opus_socket has-session -t cowork_opus && /usr/bin/tmux -L opus_socket kill-server || true"

[Install]
WantedBy=multi-user.target
```

### 3.2 Runner 脚本

**cowork bot** (`scripts/claude_runner.sh`)：
```bash
#!/bin/bash
TMUX_BIN=/usr/bin/tmux
SESSION=cowork
WORKDIR=/home/cowork/cowork
CLAUDE_BIN=/usr/bin/claude

if $TMUX_BIN has-session -t $SESSION 2>/dev/null; then
    $TMUX_BIN kill-session -t $SESSION
fi
$TMUX_BIN new-session -d -s $SESSION -c $WORKDIR $CLAUDE_BIN --channels plugin:discord@claude-plugins-official

while $TMUX_BIN has-session -t $SESSION 2>/dev/null; do
    sleep 5
done
exit 1   # 触发 systemd Restart=on-failure
```

**opus_CC bot** (`scripts/claude_opus_runner.sh`)：
```bash
#!/bin/bash
TMUX_BIN="/usr/bin/tmux -L opus_socket"
SESSION=cowork_opus
WORKDIR=/home/cowork/cowork
CLAUDE_BIN=/usr/bin/claude
export HOME=/home/cowork/opus_home

while true; do
    if ! $TMUX_BIN has-session -t $SESSION 2>/dev/null; then
        $TMUX_BIN new-session -d -s $SESSION -c $WORKDIR $CLAUDE_BIN --channels plugin:discord@claude-plugins-official
    fi
    sleep 5
done
```

> 注意两个脚本守护方式不同：cowork 用 systemd Restart=on-failure 机制（脚本退出1触发），opus_CC 用自身 while true 循环（不依赖 systemd restart，因为 cowork 用户 sudoers 权限问题）。

### 3.3 Discord access.json

**cowork bot** (`/home/cowork/.claude/channels/discord/access.json`)：
```json
{
  "dmPolicy": "pairing",
  "allowFrom": ["811758070534766613"],
  "groups": {
    "1485128242808619079": {
      "requireMention": false,
      "allowFrom": ["811758070534766613"]
    }
  },
  "pending": {}
}
```

**opus_CC bot** (`/home/cowork/opus_home/.claude/channels/discord/access.json`)：
```json
{
  "dmPolicy": "pairing",
  "allowFrom": ["811758070534766613"],
  "groups": {
    "1503165641379545228": {
      "requireMention": false,
      "allowFrom": ["811758070534766613"]
    }
  },
  "pending": {}
}
```

> `811758070534766613` = 主公的 Discord user ID (tommzzz.)
> `1485128242808619079` = cowork bot DM channel
> `1503165641379545228` = opus_CC DM channel

### 3.4 opus_home settings.json 关键字段

```json
{
  "model": "claude-opus-4-7",
  "permissions": {
    "defaultMode": "bypassPermissions",
    ...
  },
  "skipDangerousModePermissionPrompt": true,
  "enabledPlugins": { "discord@claude-plugins-official": true },
  "env": {
    "PATH": "/home/cowork/.bun/bin:/home/cowork/.local/bin:/home/cowork/.nvm/versions/node/v22.18.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
  }
}
```

---

## 四、日常操作速查

### 查看状态
```bash
systemctl status cowork-claude    # cowork bot
systemctl status cowork-opus      # opus_CC bot
tmux ls                           # 看 cowork session（默认 socket）
tmux -L opus_socket ls            # 看 opus_CC session
```

### 手动重启
```bash
systemctl restart cowork-claude   # 重启 cowork bot
systemctl restart cowork-opus     # 重启 opus_CC bot
```

### Attach 进 TUI
```bash
ssh root@142.93.207.54            # 先 SSH 进 VPS
tmux attach -t cowork             # cowork bot TUI
tmux -L opus_socket attach -t cowork_opus  # opus_CC bot TUI
```

### Discord 内重启（在 Discord DM 里说）
- `!重启` 或 `请退出进程`
- 各 bot 只杀自己的 tmux server，3 秒内自动重启

---

## 五、主要配置路径汇总

| 文件 | 路径 |
|---|---|
| cowork bot 设置 | `/home/cowork/.claude/settings.json` |
| opus_CC bot 设置 | `/home/cowork/opus_home/.claude/settings.json` |
| cowork Discord access | `/home/cowork/.claude/channels/discord/access.json` |
| opus_CC Discord access | `/home/cowork/opus_home/.claude/channels/discord/access.json` |
| cowork runner | `/home/cowork/cowork/scripts/claude_runner.sh` |
| opus_CC runner | `/home/cowork/cowork/scripts/claude_opus_runner.sh` |
| cowork systemd | `/etc/systemd/system/cowork-claude.service` |
| opus_CC systemd | `/etc/systemd/system/cowork-opus.service` |
| cowork 工作目录 | `/home/cowork/cowork/` |
| VPS IP | `142.93.207.54` |

---

## 六、Memory 共享改造（2026-05-12）

### 背景
原设计中两个 bot 的 memory 路径完全独立（4 层隔离原则之一）。但实测发现：
- `/home/cowork/opus_home/.claude/projects/-home-cowork-cowork/memory/` 一直为空（opus_CC bot 从未在那写入过任何文件）
- opus_CC bot 实际上一直在通过 git repo 备份（`/home/cowork/cowork/memory/`）**只读** cowork bot 的 memory
- opus_CC bot 修改 memory 时改的是 git repo 备份，**不会回写到 cowork bot 的活 memory**——导致 cowork bot 下次启动看不到新规则

### 决策
打破"4 层隔离"中的 memory 层独立——改为 **symlink 共享**。

### 理由
- 主公使用模式：双模型入口共享上下文（不做模型对比实验）
- 远程使用切换模型繁杂，希望两个 bot 共享同一套规则/记忆
- 想用纯净无记忆模型时单独开新 Claude Code 实例

### 实施命令（2026-05-12 完成）
```bash
# 1. 先把 opus_CC 改过但未同步的规则 cp 到 cowork bot 活 memory（一次性补齐）
cp /home/cowork/cowork/memory/feedback_honesty.md \
   /home/cowork/.claude/projects/-home-cowork-cowork/memory/
cp /home/cowork/cowork/memory/feedback_backlog_format.md \
   /home/cowork/.claude/projects/-home-cowork-cowork/memory/

# 2. 删除 opus_home 下的空 memory 目录
rmdir /home/cowork/opus_home/.claude/projects/-home-cowork-cowork/memory/

# 3. 建立 symlink：opus_home memory → cowork bot 活 memory
ln -s /home/cowork/.claude/projects/-home-cowork-cowork/memory \
      /home/cowork/opus_home/.claude/projects/-home-cowork-cowork/memory
```

### 验证
两个 bot 看到同一份 memory（61 个文件），任一 bot 修改另一个立即生效。

### 回滚方法
```bash
rm /home/cowork/opus_home/.claude/projects/-home-cowork-cowork/memory  # 删 symlink
mkdir /home/cowork/opus_home/.claude/projects/-home-cowork-cowork/memory  # 重建空目录
```

### 后续影响
- 收工 SKILL.md 步骤 3 的"同步 memory 备份"逻辑仍保留——`cp /home/cowork/.claude/projects/.../memory/*.md → git repo`，git 备份继续生效
- 任一 bot 改 memory 都会立即被另一个看到，**不需要手动同步**
- 唯一并发风险：两个 bot 同时往 `auto_pending.md` append 时可能交错（极低频）

### 收工分工（2026-05-12 约定）
两个 bot 都用过的日子，**分别说"收工"一次**：
- 每个 bot 跑各自的步骤 1（更新自己懂的项目进度）+ 步骤 4（写自己 session 摘要到 cowork.db）
- 其他步骤（git/索引/深度审核）会重复跑但有去重表保护，不冲突
- 如果只用了一个 bot，只让那个 bot 收工即可
