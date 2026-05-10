# Discord Plugin reply 工具失败 Bug — 修复记录

> 2026-05-09 闭环 / 在 VPS（DigitalOcean 142.93.207.54）/ Discord plugin `claude-plugins-official/discord/0.0.4`
> 问题悬而未决 37 天（主公 2026-04-02 在 `feedback_discord_allowlist.md` 记录"原因未查明"）
> 这份文档保存**完整时间线**（WSL→VPS 镜像→bug 诊断→修复→permission 优化）+ 修复方法 + 教训

---

## 完整时间线（从头到尾，按本次对话顺序）

### 阶段 0 — 背景（本次对话之前）

主公 2026-05-08 起做 P11 VPS 迁移：DigitalOcean Droplet（1vCPU/2GB/$12/月）/ Ubuntu 24.04 / 装好 claude code v2.1.137 + Node + bun + rclone / cowork 主目录 rsync 到 `/root/cowork/`。

迁移过程已经踩过 3 次诊断错误（plugin 协议不匹配 / host 不处理 method / systemd 漏 `--channels` 参数）→ 第 3 个修了能收 inbound，但触发新子问题：reply 失败 → cowork Stop Hook 检测漏发 → 死循环烧 token → `systemctl stop cowork-claude` 防再爆。

进度详见 `archive/vps_migration_progress_2026-05-09.md`。本次对话开始时停在这里。

### 阶段 1 — WSL→VPS 配置镜像（22:00–22:10）

主公请求"把本地电脑的配置转入到 VPS 去"。讨论后选**方案 B（选择性镜像）**：
- 备份 VPS：`cp -a /root/.claude /root/.claude.bak.20260509`（103M）
- rsync `~/.claude/` 到 VPS，**排除运行时和易冲突项**：`projects/` `plugins/` `sessions/` `shell-snapshots/` `todos/` `statsig/` `session-env/` `file-history/` `history.jsonl` `.credentials.json` `settings.json` `settings.local.json` `backups/` `paste-cache/` `downloads/` `cache/` `telemetry/` `usage-data/` `channels/` `plans/` `prompt_count` `mcp-needs-auth-cache.json`
- **memory 单独同步**（路径不一样）：`~/.claude/projects/-mnt-c-Users-zhi89-Desktop-cowork/memory/` → `/root/.claude/projects/-root-cowork/memory/`（56 文件 228K）
- `chown -R root:root /root/.claude/`（rsync 默认保留 owner 1000:1000，必须修）
- **sed 修硬编码路径**：`/mnt/c/Users/zhi89/Desktop/cowork → /root/cowork`（hooks 3 处 + skills 1 处 + 收工 SKILL.md 1 处 `/home/zhi8939/.claude → /root/.claude`）
- 验证：grep 零残留 + `bash /root/.claude/hooks/health_check.sh` 冒烟通过

**为什么 settings.json 不同步**：VPS 那份已经把 11 处 hook 路径修过 + `discord_ts_convert.py` 路径改过（WSL 是 `/mnt/c/...`，VPS 是 `/root/cowork/...`）；同步会覆盖崩。

### 阶段 2 — 启动测试，死循环复现（22:10–22:15）

启动 `systemctl start cowork-claude` → service active。主公在 Discord 发 "hi"。

第一反应抓 `/tmp/discord-server.log`：
```
[DBG-MSG] from 811758070534766613 content=hi          ← 主公消息进来
[DBG-MSG] from 1485125345014452234 content=🔐 Permission: mcp__plugin_discord_discord__reply
[DBG-MSG] from 1485125345014452234 content=🔐 Permission: mcp__plugin_discord_discord__reply
[DBG-MSG] from 1485125345014452234 content=🔐 Permission: Bash
[DBG-MSG] from 1485125345014452234 content=⚠️ 上下文提醒：当前对话已用约 50%
discord channel: shutting down
```

permission 弹 4 次 + Bash 弹 2 次 → 明显死循环，立即 stop。

### 阶段 3 — 关键转折：主公说"不要猜测，读文档"（22:15）

我准备给"打 [DBG-FETCH] 调试日志"方案。主公一句话："你需要把文档都读取了，然后再分析问题，不要猜测。"

立即转向，系统性读取所有相关文档：
1. `archive/vps_migration_progress_2026-05-09.md`（迁移全程进度）
2. `memory/feedback_discord_allowlist.md`（37 天前 memory：dmPolicy=allowlist 时 reply 报错"原因未查明"）
3. `server.ts` 完整代码（`gate` + `fetchAllowedChannel` + `handleInbound` + 启动逻辑）
4. `access.json`（VPS vs WSL 完全一致）
5. `/tmp/discord-server.log` 全文（无 "static mode downgraded" 字样 → STATIC=false → dmPolicy=pairing）
6. claude session jsonl —— **关键**：第一次看 session 数据，发现 claude 实际调了 reply，被 plugin 拒绝（前 4 次诊断都没看这个）

读完结论：**代码逻辑应该让 reply 成功，但实际不行；连主公自己 memory 都写"原因未查明"**。文档读尽，必须加运行时调试。

### 阶段 4 — 加 [DBG-FETCH] 调试，主公同意（22:18）

向主公汇报：文档读完无法定位，必须加 stderr 打印 `ch.type / recipientId / dmMap` 才能看真相。主公同意。

写 `/tmp/patch_server.py`，scp 到 VPS，python 精确替换在 `fetchAllowedChannel` 第一行 `const access = loadAccess()` 后插入：
```ts
process.stderr.write(`[DBG-FETCH] id=${id} type=${ch.type} isDM=${ch.type === ChannelType.DM} isThread=${ch.isThread?.()} recipientId=${(ch as any).recipientId} dmMap=${dmChannelUserMap.get(id)} groupKeys=${Object.keys(access.groups).join(",")} dmPolicy=${access.dmPolicy} allowFrom=${access.allowFrom.join(",")}\n`)
```

清空 `/tmp/discord-server.log`，systemctl restart cowork-claude。主公发 hi。立即 stop，抓 log。

### 阶段 5 — 真根因定位（22:20）

[DBG-FETCH] 输出抓到铁证：
```
[DBG-FETCH] id=1485128242808619079 
            type=1 isDM=true                      ← channel 实际是 DM 类型
            recipientId=1485125345014452234       ← BOT 自己 ID（应为对方=主公 ID）
            dmMap=811758070534766613              ← 主公 user_id（inbound 已正确缓存）
            groupKeys=1485128242808619079         
            dmPolicy=pairing 
            allowFrom=811758070534766613
```

**真根因 = `??` 短路 + partial channel 错值**：
- ch.recipientId 在 partial DM 状态下错返 bot 自己 ID（应为对方 ID）
- `??` 只在 null/undefined 时 fallback，bot ID 非空 → 不走 dmMap fallback
- `allowFrom.includes(bot_id)` → false → 抛 not allowlisted

**为什么 WSL 通 VPS 不通**：partial channel 数据状态依赖运行时 cache/timing。WSL 上 ch.recipientId 真的是 undefined → 走 fallback；VPS 上是 bot ID → 不走。**两边都有 bug，WSL 运气好没暴露**。

### 阶段 6 — 一行代码修复（22:25）

写 `/tmp/fix_server.py`：反转 `??` 顺序为 `dmChannelUserMap.get(id) ?? ch.recipientId`（dmMap 是 inbound 验证过的可靠值优先），同时清掉 [DBG-FETCH] 和遗留的 [DBG-MSG]（`+` 字符串拼接的那行 regex 漏抓，sed -d 补刀）。

verify：grep 零 DBG 残留，line 415 修复就位。

### 阶段 7 — 验证修复（22:27）

systemctl restart → 主公发 hi → 抓 session jsonl + log：
```
22:00:38 ASST-TOOL: mcp__plugin_discord_discord__reply input={'chat_id': '...', 'text': '主公好！今天想做点什么？'}
22:00:42 TOOL-RESULT: 'sent (id: 1502852852001800212)'   ← ✅ 不再 reply failed
22:00:50 主公又发"你好"
22:00:53 ASST-TOOL: reply
22:00:56 TOOL-RESULT: 'sent (id: ...)'                    ← ✅ 又成功
```

**完整链路通**，无死循环。37 天悬案闭环。

### 阶段 8 — Permission 免弹优化（22:30–22:55）

bug 修了但每次 reply 都弹 `🔐 Permission` 让主公点 ✅Allow，体验差。主公问"那个可以删除吗"。

误判：先答"两边 settings.json 一样为何 WSL 不弹"。主公提示"WSL 一般不弹是因为有守卫 hook"。

读完所有 5 个 hook + CLAUDE.md 守卫规则：
- `system_file_guard.sh`：白名单文件直接 exit 0；非白名单要 `/tmp/task_approved`
- `git_commit_guard.sh`：拦 `git commit/push` 要 `/tmp/git_approved`
- 其他 4 个是日志 / context 警告 / 记忆捕获 / 立场检查（PostToolUse / Stop / UserPromptSubmit）
- settings.json `permissions.allow` 中 `Write/Edit(/mnt/c/Users/zhi89/Desktop/*)` 已让 Desktop 内文件操作不弹

**结论**：reply 是发回主公自己 channel 无风险，等同于 `Write(Desktop/*)` 白名单，永远 allow。

修改 VPS `/root/.claude/settings.json` 的 `permissions.allow` 追加 5 个 mcp 工具 + restart service → 主公测试 ✅ 不再弹。

### 阶段 9 — 归档保存记录（23:00–23:30）

写本份完整记录文档 + INSIGHTS.md 加 4 条速查（session jsonl 诊断法 / plugin 修复指引 / `??` 盲区 / discord 工具 allow） + auto_pending.md 加 2 条记忆（plugin bug reference + 诊断方法论 feedback）。

---

## 症状

- VPS 启动 `cowork-claude.service`（systemd → tmux → claude --channels plugin:discord@claude-plugins-official）
- 主公在 Discord 发任意消息（"hi"）
- claude 进入 agent loop，调用 `mcp__plugin_discord_discord__reply` 工具
- **工具返回错误**：`reply failed: channel <channel_id> is not allowlisted — add via /discord:access`
- claude 输出文字解释错误 → cowork Stop Hook 检测"漏发 reply" → block 让 claude 补发 → claude 又试 → 又失败 → **死循环烧 token**（实测 2 分 25 秒烧 2.9k token）

**矛盾点**：`access.json` 配置正确（dmPolicy: pairing + 主公 user_id 在 allowFrom + 主公 channel id 在 groups），按代码逻辑应该通过；同样的代码在 WSL 上能正常 reply。

---

## 错误的诊断（4 次，前后烧 ~10k token）

| # | 假设的根因 | 实际是 |
|---|---|---|
| 1 | plugin 协议与 host v2.1.137 不匹配 | ❌ 瞎猜，没证据 |
| 2 | host 不处理 channel notification method | ❌ 瞎猜（被"WSL2 也是 v2.1.138"反例推翻）|
| 3 | systemd ExecStart 漏 `--channels plugin:discord@claude-plugins-official` | ✅ 部分对 — host 没订阅 plugin channel；修了能收到 inbound，但 outbound 还卡（即本 bug）|
| 4 | cowork 规则在 channel mode 适配（claude 不调 reply 工具）| ❌ **根本没看 claude session jsonl 就下结论** |

### 第 4 次诊断的关键失误（教训）
- 当时观察 TUI 输出 + Stop Hook 报"reply 漏发" → 主观推测"claude 没真调 reply 工具"
- **实际上 session jsonl 里第 4 秒就有 `tool_use: mcp__plugin_discord_discord__reply` 记录**，第 6 秒就有 `tool_result: reply failed: ... not allowlisted`
- 数据 5 月 9 日早上就有了，没去看就给了主公错的报告
- 教训：**诊断 plugin/工具问题必须先看 `~/.claude/projects/<cwd>/<sid>.jsonl`**

---

## 真根因（代码定位）

**文件**：`/root/.claude/plugins/cache/claude-plugins-official/discord/0.0.4/server.ts`
**函数**：`fetchAllowedChannel` (line 410-422)

```typescript
async function fetchAllowedChannel(id: string) {
  const ch = await fetchTextChannel(id)
  const access = loadAccess()
  if (ch.type === ChannelType.DM) {
    // recipientId can be undefined for partial DM channels — fall back to runtime cache
    const recipientId = ch.recipientId ?? dmChannelUserMap.get(id)  // ← BUG 在这里
    if (recipientId && access.allowFrom.includes(recipientId)) return ch
  } else {
    const key = ch.isThread() ? ch.parentId ?? ch.id : ch.id
    if (key in access.groups) return ch
  }
  throw new Error(`channel ${id} is not allowlisted — add via /discord:access`)
}
```

### 调试日志注入抓到的实际值

```
[DBG-FETCH] id=1485128242808619079 
            type=1 isDM=true               ← channel 实际是 DM 类型
            isThread=false 
            recipientId=1485125345014452234   ← BOT 自己的 ID（应为对方 ID = 主公）
            dmMap=811758070534766613         ← 主公 user_id（inbound gate 已正确缓存）
            groupKeys=1485128242808619079    ← access.groups 配置
            dmPolicy=pairing 
            allowFrom=811758070534766613     ← 主公 user_id
```

### 为什么会错

1. Discord.js 在 partial DM channel 数据下，`ch.recipientId` 应该返回**对方** user ID（即主公 ID），但**实际错返回了 bot 自己的 ID**（这是 partial 数据的不一致行为）
2. 注释说"recipientId can be undefined" → fallback 设计假设 undefined 时才走 dmChannelUserMap
3. 但**错值（bot ID）不是 undefined**，`??` 短路 → 不走 fallback → 用错的 bot ID 检查 allowFrom
4. `access.allowFrom.includes(bot_id)` → false → 抛错

### 为什么 WSL 跑得通 VPS 跑不通

同样的代码、同样的 plugin 版本（v0.0.4）、同样的 access.json，但：
- WSL 上 `ch.recipientId` 真的是 undefined（partial 数据另一种状态）→ 走 fallback → 拿到主公 ID → ✅ 通过
- VPS 上 `ch.recipientId` 是 bot ID → 不走 fallback → ❌ 报错

partial channel 的字段值依赖运行时 cache 状态，WSL 和 VPS 进程启动顺序/timing 不同导致行为差异。**两边都有 bug，只是 WSL 运气好没暴露**。

---

## 修复

### 一行代码修复
反转 `??` 顺序，让 dmMap（inbound gate 验证过的可靠值）优先：

```diff
-    const recipientId = ch.recipientId ?? dmChannelUserMap.get(id)
+    const recipientId = dmChannelUserMap.get(id) ?? ch.recipientId
```

### 自动化 patch 脚本（plugin 升级后重跑这个）

```python
#!/usr/bin/env python3
# /tmp/fix_server.py
import sys

path = "/root/.claude/plugins/cache/claude-plugins-official/discord/0.0.4/server.ts"
with open(path) as f:
    content = f.read()
with open(path + ".bak_fix", "w") as f:
    f.write(content)

old = "const recipientId = ch.recipientId ?? dmChannelUserMap.get(id)"
new = "const recipientId = dmChannelUserMap.get(id) ?? ch.recipientId"

if old not in content:
    print("ERROR: pattern not found (plugin updated? line 415 changed?)")
    sys.exit(1)

content = content.replace(old, new, 1)
with open(path, "w") as f:
    f.write(content)
print("PATCHED")
```

执行：
```bash
scp /tmp/fix_server.py root@142.93.207.54:/tmp/
ssh root@142.93.207.54 "python3 /tmp/fix_server.py && systemctl restart cowork-claude"
```

### 备份位置
- 原版本：`/root/.claude/plugins/cache/claude-plugins-official/discord/0.0.4/server.ts.bak_fix`
- patch 前的 stderr 调试版本：`server.ts.bak_dbg`

---

## 验证步骤

### 1. 确认 patch 已应用
```bash
ssh root@142.93.207.54 "grep -n 'recipientId =' /root/.claude/plugins/cache/claude-plugins-official/discord/0.0.4/server.ts"
# 期望输出：
# 415:    const recipientId = dmChannelUserMap.get(id) ?? ch.recipientId
```

### 2. 重启服务
```bash
ssh root@142.93.207.54 "systemctl restart cowork-claude && sleep 5 && systemctl is-active cowork-claude"
# 期望：active
```

### 3. 主公在 Discord 发 hi 测试

期望 session jsonl（`/root/.claude/projects/-root-cowork/<latest>.jsonl`）出现：
```
ASST-TOOL: mcp__plugin_discord_discord__reply input={'chat_id': '...', 'text': '...'}
TOOL-RESULT: 'sent (id: ...)'    ← 关键：sent 而不是 "reply failed"
```

### 4. 实测验证（已通过）
- 22:00 主公发 "hi" → bot 回 "主公好！今天想做点什么？" ✅ sent
- 22:01 主公发 "你好" → bot 回 "主公好！有什么吩咐？" ✅ sent
- 没死循环、没 Stop Hook 误报、没 token 烧到飞起

---

## 配套：reply 免 permission 弹窗

修了 reply 失败的 bug 后，发现每次 reply 都弹 `🔐 Permission: mcp__plugin_discord_discord__reply` 让主公在 Discord 点 ✅Allow，体验差。

**修复**：`/root/.claude/settings.json` 的 `permissions.allow` 追加 5 个 discord 工具：

```json
"mcp__plugin_discord_discord__reply",
"mcp__plugin_discord_discord__react",
"mcp__plugin_discord_discord__edit_message",
"mcp__plugin_discord_discord__fetch_messages",
"mcp__plugin_discord_discord__download_attachment"
```

加完 `systemctl restart cowork-claude` 即生效。

设计哲学：reply 是发回主公自己 channel，等同于 `Write(/mnt/c/Users/zhi89/Desktop/*)` 白名单逻辑，永远 allow 没风险。

---

## 教训（写给未来的我）

1. **诊断 claude 工具行为问题，第一步永远是看 session jsonl**（位置 `~/.claude/projects/<cwd>/<sid>.jsonl`），解析 user / assistant / tool_use / tool_result 流。看 hook log 或 stderr 只是辅助，看 claude 实际做了什么才是真相。

2. **不要在没看代码前假设是 plugin/host 协议问题**，那是最难证伪的方向，容易陷入猜测循环。先看 claude 内部行为日志。

3. **同样配置 + 同样代码 + 不同环境表现不同 → 强烈暗示运行时 state 问题**（partial 数据、cache、内存 Map 等），不是配置问题。这种 bug 必须加运行时调试日志才能定位。

4. **`??` 操作符的盲区**：只在 `null/undefined` 时 fallback，"错的非空值"会跳过 fallback。当主数据源不可靠时，应该把 fallback 设为优先（`fallback ?? primary`），或加显式校验。

5. **plugin 升级会丢失修复**。每次 `~/.claude/plugins/cache/claude-plugins-official/discord/<version>/` 路径变化（版本升级），都要重新 patch。考虑：
   - 在 INSIGHTS / knowledge_base 提示
   - 或写一个 cron 周期检查 server.ts 是否包含 `dmChannelUserMap.get(id) ?? ch.recipientId`，缺失则告警

---

## 相关文件 / 引用

- 主公 37 天前的 memory：`memory/feedback_discord_allowlist.md`（"原因未查明"，本次已查明）
- VPS 迁移进度：`archive/vps_migration_progress_2026-05-09.md`
- session 数据位置：`/root/.claude/projects/-root-cowork/*.jsonl`
- discord-server 调试日志：`/tmp/discord-server.log`
- plugin 源码：`/root/.claude/plugins/cache/claude-plugins-official/discord/0.0.4/server.ts`
- access.json 位置：`/root/.claude/channels/discord/access.json`
