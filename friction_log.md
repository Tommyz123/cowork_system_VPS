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
