# Cowork Hook 系统文档

> 最后更新：2026-06-07（新增 token_utils.sh，统一 token 操作，消除四处分散的实例推导逻辑）
> **配置分层**：通用 hook 放项目共享层 `/home/cowork/cowork/.claude/settings.json`（AA/BB/CC 自动合并继承）；实例专属 hook 才放用户层 `$HOME/.claude/settings.json`
> Hook 脚本位置：`/home/cowork/.claude/hooks/`（三实例共用此路径）和 `cowork/scripts/`

---

## token_utils.sh — 统一 token 操作工具（2026-06-07）

`/home/cowork/.claude/hooks/token_utils.sh` 是所有 token 操作的单一入口：
- `token_utils.sh instance` → 输出实例名（AA/BB/CC）
- `token_utils.sh path <task|git>` → 输出 token 完整路径
- `token_utils.sh write <task|git>` → touch token
- `token_utils.sh write-savework` → 写 savework 到 git token
- `token_utils.sh check <task|git>` → 检查 token 存在（exit 0=存在）
- `token_utils.sh clear <task|git>` → 删除 token

调用方：discord_approve.py / system_file_guard.sh / git_commit_guard.sh / settings.json（内联命令）

---

## 三实例统一架构（2026-06-02）

- **通用 hook（12个）→ 共享层** `/home/cowork/cowork/.claude/settings.json`：改一处三实例同步。包含 git/文件守卫、context_watch、discord系列、health/memory、honesty_check、时间注入(discord_ts_convert.py)、日志提醒、log_write_event
- **实例专属 → 用户层**：position_check.py（P9 专用）只在 AA(cowork) 用户层
- **token 实例隔离**：`/tmp/task_approved` `/tmp/git_approved` 带实例后缀 `_AA/_BB/_CC`，由 `$HOME` 推导（opus_home→BB / opus2_home→CC / cowork→AA / 其他→拒绝放行 fail-safe）。涉及脚本：discord_approve.py、system_file_guard.sh、git_commit_guard.sh、共享层 UserPromptSubmit 的 rm
- **时间注入统一**：废弃旧的 inject_time.sh（BB/CC 曾用），统一 discord_ts_convert.py
- 改共享层 settings.json 后需**重启实例**才生效

---

## 概览

| Hook 类型 | 文件 | 触发条件 | 目的 |
|-----------|------|----------|------|
| PreToolUse | git_commit_guard.sh | Bash 命令 | 拦截 git commit/push；拦截 Claude 自行授权 |
| PreToolUse | system_file_guard.sh | Edit / Write | 文件修改前检查授权 token |
| PostToolUse | context_watch.sh | 所有工具 | 上下文用量超阈值时 Discord 告警 |
| PostToolUse | discord_reply_clear.py | Discord reply | 清除"待回复"标志 |
| UserPromptSubmit | discord_approve.py | 收到消息 | 检测授权关键词，自动 touch task_approved |
| UserPromptSubmit | discord_reply_flag.py | 收到消息 | 标记 Discord 消息待回复 |
| UserPromptSubmit | discord_ts_convert.py* | 收到消息 | 转换 Discord 时间戳为纽约时间注入上下文 |
| UserPromptSubmit | instance_identity.sh | 收到消息 | 按 $HOME 推导实例身份(AA/BB/CC)+读 settings 真实模型，注入"🪪本实例身份"上下文，防自报身份误报（2026-06-19） |
| UserPromptSubmit | health_check.sh | 收到消息 | 系统健康检查（friction/CLAUDE.md行数等） |
| UserPromptSubmit | memory_capture.sh | 收到消息 | 每10轮触发记忆捕获提醒；有待审记忆时提醒 |
| UserPromptSubmit | position_check.py | 收到消息 | P9 TIDE 持仓状态检查 |
| UserPromptSubmit | `echo '...'`（内联） | 收到消息 | 注入日志提醒（写 cowork_log.md） |
| UserPromptSubmit | `rm -f /tmp/task_approved_<实例>`（内联） | 收到消息 | 清除上轮授权 token（带实例后缀），防止跨任务串用 |
| Stop | discord_reply_check.sh | Claude 输出后 | 检测 Discord 消息是否漏回复，漏发则 block |
| Stop | honesty_check.sh | Claude 输出后 | 检测声称读完但实际只读了部分文件 |
| Stop | `rm -f /tmp/task_approved_<实例>`（内联） | Claude 输出后 | 响应结束时清除任务授权 token，实现响应级授权 |

*`discord_ts_convert.py` 位于 `cowork/scripts/`，非 hooks/ 目录

---

## 详细说明

### PreToolUse

#### `git_commit_guard.sh`
- **触发**：任何 Bash 命令
- **逻辑1（git 守卫）**：命令含 `git commit` 或 `git push` → 拦截，提示先列变更等主公确认；需主公执行 `touch /tmp/git_approved_<实例>` 解锁（实例由 $HOME 推导）
- **逻辑2（touch 守卫）**：命令含 `touch /tmp/task_approved`（含后缀变体）→ block，提示"Claude 无权自行授权，需主公通过 Discord 触发"
- **逻辑3（实例守卫）**：$HOME 无法推导实例身份 → 拒绝放行 git 操作
- **为什么**：git 操作不可逆；task_approved 自授权等于无守卫；token 带实例后缀防三实例串用

#### `system_file_guard.sh`
- **触发**：Edit 或 Write 工具
- **白名单**（直接放行）：cowork_log.md、CURRENT_SESSION.md、friction_log.md、INSIGHTS.md、auto_pending.md、archive/、/tmp/
- **非白名单**：检查 `/tmp/task_approved_<实例>` 是否存在（实例由 $HOME 推导），不存在则拦截，提示走授权流程；$HOME 无法推导则直接拒绝（fail-safe）
- **为什么**：防止 Claude 自作主张修改系统文件；token 带实例后缀防三实例串用

---

### PostToolUse

#### `context_watch.sh`
- **触发**：任意工具调用后
- **逻辑**：读取当前 transcript.jsonl 文件大小，超过 700KB（约50%）发 Discord 告警；超过 1050KB（约75%）升级警告；每个会话只告警一次
- **为什么**：防止 token 耗尽被迫中断，提前提醒主公保存进度

#### `discord_reply_clear.py`
- **触发**：Discord reply 工具调用后
- **逻辑**：清除 `/tmp/discord_reply_needed_{session_id}` 标志文件
- **为什么**：配合 Stop Hook 的漏发检测，reply 发出后标志清除

---

### UserPromptSubmit

#### `discord_approve.py`
- **触发**：收到 Discord 消息
- **授权关键词**：「可以执行」「开始执行」「直接开始」「可以开始」「执行吧」「执行」「做吧」「去做」「好的做」「开始」「可以」「go ahead」「proceed」「approved」
- **逻辑**：检测 prompt 里是否来自 Discord（含 `source="plugin:discord:discord"`）且包含关键词 → `touch /tmp/task_approved_<实例>`（实例由 $HOME 推导，推导失败则不授权），注入授权确认消息
- **为什么**：让主公在 Discord 手机端就能授权文件修改，不需要 SSH 进终端

#### `discord_reply_flag.py`
- **触发**：收到 Discord 消息
- **逻辑**：在 `/tmp/discord_reply_needed_{session_id}` 创建标志文件，表示需要回复
- **为什么**：配合 Stop Hook 检测漏发

#### `discord_ts_convert.py`（位于 cowork/scripts/）
- **触发**：每条消息
- **逻辑**：解析 stdin JSON，提取 Discord `ts` 字段（UTC），转换为纽约时间（EDT/EST），输出到 additionalContext 注入上下文
- **为什么**：所有时间统一纽约时间，主公看到"2026-05-10 15:54 EDT"而非 UTC

#### `instance_identity.sh`（2026-06-19）
- **触发**：每条消息
- **逻辑**：按 `$HOME` case 推导实例代号（opus_home→BB / opus2_home→CC / cowork→AA / 其他→明确报推导失败不瞎猜），从该实例 settings.json grep 真实 `model` 字段，注入"🪪 本实例身份：你是 X（进程名…）当前模型 Y"到上下文
- **为什么**：系统无任何地方硬声明实例身份，原须由 HOME→reference_dual_bot.md 映射表手动推导；BB 实例曾连续多次把自己误报成 AA（违反数据诚信，friction 2026-06-19）→ 软规则升级为硬注入
- **坑**：grep model 无匹配时需 `|| true`，否则 `set -e` 会让整个脚本静默退出（AA 无 model 字段时复现过）

#### `health_check.sh`
- **触发**：每条消息
- **逻辑**：检查 CLAUDE.md 行数（超180行预警）、friction_log 活跃条目数、auto_pending 待审记忆数等
- **为什么**：保持系统健康，防止 CLAUDE.md 臃肿

#### `memory_capture.sh`
- **触发**：每条消息（每10轮触发一次提醒）
- **逻辑**：计数器达到阈值时注入"🧠 记忆捕获"提醒；auto_pending.md 有内容时注入"⏳ 待审记忆"提醒
- **为什么**：确保有价值的偏好/决策被捕获到记忆系统

#### `position_check.py`
- **触发**：每条消息（非每次执行，有去重逻辑）
- **逻辑**：检查 P9 TIDE 系统当天是否有新信号/持仓变动需要关注
- **为什么**：P9 持仓监控的辅助提醒

#### 内联：日志提醒
```json
echo '{"hookSpecificOutput":{"additionalContext":"⚠️ 提醒：完成任务后记得写 cowork_log.md 日志..."}}'
```
- 每条消息注入，防止 Claude 忘记写日志

#### 内联：`rm -f /tmp/git_approved_<实例>`
- 每条消息清除 git 授权 token（UserPromptSubmit），由 discord_approve.py 按需重授
- **注意**：task_approved 不在此处清除，改由 Stop hook 在响应结束时清除（2026-06-06 改动，实现响应级授权）

---

### Stop

#### `discord_reply_check.sh`
- **触发**：Claude 完成输出后
- **逻辑**：检查 `/tmp/discord_reply_needed_{session_id}` 是否存在 → 存在说明收到了 Discord 消息但没有调用 reply 工具 → 返回 `decision: block`，强制 Claude 补发回复
- **为什么**：Discord 是主要沟通渠道，漏发等于主公收不到回复

#### `honesty_check.sh`
- **触发**：Claude 完成输出后
- **逻辑**：扫描最后一轮 assistant 输出是否含"全文/读完了/完整内容/entire file"等关键词；如果有，核对同轮 Read 工具调用参数（offset/limit/文件行数）是否真的读完；声称读完但实际部分读取 → 输出警告
- **为什么**：防止 Claude 谎称读完文档给出不准确的结论（数据诚信规则配套执行层）

---

## 授权流程

```
（INSTANCE 由 $HOME 推导：opus_home→BB / opus2_home→CC / cowork→AA / 其他→拒绝）

主公发消息 → UserPromptSubmit
  ├─ rm git_approved_<INSTANCE>（清除 git 授权，按需重授）
  ├─ discord_approve.py（检测授权关键词）
  │    └─ 含关键词 → touch /tmp/task_approved_<INSTANCE>
  └─ 其他提醒 Hook

Claude 准备修改文件 → PreToolUse
  └─ system_file_guard.sh
       ├─ 白名单 → 放行
       ├─ $HOME 无法推导实例 → 拒绝（fail-safe）
       └─ 非白名单 → 检查 task_approved_<INSTANCE>
            ├─ 存在 → 放行
            └─ 不存在 → 拦截，提示走授权流程

Claude 响应结束 → Stop
  └─ rm -f /tmp/task_approved_<INSTANCE>（自动清除，无需手动 rm）
```
