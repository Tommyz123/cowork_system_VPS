# cowork/scripts/ + newscripts/ 脚本登记册

> 每个脚本的"做什么 + 谁在用 + 状态"。新增脚本必须在此登记。
> 最后审计：2026-05-26

## 📊 状态汇总

| 状态 | 数量 | 说明 |
|---|---|---|
| 🟢 活跃 | 18 | 有 cron / hook / Skill / 其他脚本在调用 |
| 🟡 库存 | 1 | 当前无调用但功能有用，留作备用 |
| ⚫ 一次性 | 1 | 历史建库，留备重建（backfill_sessions.py 已移 archive/） |
| **总计** | **20** | （log_write_event.py + detect_conflict.py 新增 2026-05-26 共享文件冲突监测） |

---

## 🟢 活跃脚本

### index_conversations.py
- **功能**：解析 JSONL 对话历史 → FTS5 全文索引写入 cowork.db（支持 `--rebuild`）
- **调用方**：`~/.claude/skills/收工/SKILL.md:321`（每次收工增量索引）
- **频率**：高（每次收工，约日均 1-3 次）
- **依赖**：`cowork.db`、`~/.claude/projects/-home-cowork-cowork/*.jsonl`

### search_conversations.py
- **功能**：FTS5 + 语义混合搜索 cowork.db，返回匹配片段
- **调用方**：`~/.claude/skills/搜索/SKILL.md`（主公说"搜索 XXX" 时触发）
- **频率**：低-中（每周几次）
- **依赖**：`cowork.db`、Voyage AI API key

### embed_sessions.py / embed_messages.py
- **功能**：用 Voyage AI 把会话/消息向量化，写入 `session_embeddings` / `message_embeddings` 表
- **调用方**：`log_session.py`（收工流程自动触发）
- **频率**：高（每次收工）
- **依赖**：Voyage AI API key

### log_session.py
- **功能**：收工时写 `sessions` 表（含 project_ids/summary/next-steps/corrections/files）
- **调用方**：`~/.claude/skills/收工/SKILL.md`
- **频率**：高（每次收工）

### check_doc_sync.py
- **功能**：收工时扫 ARCHITECTURE.md + context.md 提到的 .py 文件名，对比文件系统，输出不匹配
- **调用方**：`~/.claude/skills/收工/SKILL.md`
- **频率**：高（每次收工）

### discord_ts_convert.py
- **功能**：把 Discord 消息里的 UTC 时间戳转成 NYC 时间注入到 context
- **调用方**：`~/.claude/settings.json` UserPromptSubmit hook
- **频率**：每次主公输入都跑（约日均数百次）

### rclone_backup.sh
- **功能**：Google Drive 全量同步备份
- **调用方**：cron 每日 02:00 EDT
- **频率**：每日

### run_mac_monitor.sh
- **功能**：Mac mini M4 价格监控 cron 入口（调 mac_monitor.py）
- **调用方**：cron 每日 17:30 EDT
- **频率**：每日

### mac_monitor.py
- **功能**：抓取 Mac mini M4 价格，低于阈值发邮件
- **调用方**：`run_mac_monitor.sh`
- **频率**：每日（被 .sh 触发）

### cannabis_docket_reminder.py
- **功能**：NY 大麻 December Queue 诉讼追踪邮件提醒（critical / weekly 两种模式）
- **调用方**：cron 周一 09:00 + 关键日期（5/29、5/30、5/31）
- **频率**：每周 + 关键日

### trend_watch_reminder.py
- **作用**：趋势观察池周检提醒（周一 09:35 EDT 发 Discord，清单在 trading/notes/趋势观察池.md）
- **调用方**：cron（见 reference/cron_jobs.md 趋势主线区块）
- **依赖**：`newscripts/send_discord_dm.py`
- **新建**：2026-06-11（趋势地图 2026-Q2 配套）

### ferc_watch.py
- **作用**：FERC 裁决自动哨兵（每天 17:05 SerpAPI 搜裁决新闻，命中→Discord 报警，无命中静默）；一次性使命，裁决落地后删 cron+归档
- **调用方**：cron（见 reference/cron_jobs.md 趋势主线区块）；`--test` 验证管道
- **依赖**：SerpAPI KEY1→KEY2 fallback（config/api_keys.env）、`newscripts/send_discord_dm.py`
- **新建**：2026-06-12（观察池 E1 配套；KEY1 已 429 实测 fallback 正常）

### claude_opus_runner.sh
- **功能**：Opus bot 的 tmux watchdog（HOME=opus_home，独立 socket，无限自重启）
- **调用方**：手动启动 / systemd（双 bot 架构核心）
- **频率**：常驻
- **⚠️ 警告**：双 bot 架构核心，**绝不可删**

### claude_runner.sh
- **功能**：主 cowork bot 的 tmux watchdog（systemd 拉起）
- **调用方**：systemd 服务
- **频率**：常驻
- **⚠️ 警告**：双 bot 架构核心，**绝不可删**

### which_instance.sh
- **功能**：三实例(AA/BB/CC)真相速查——读运行时进程 HOME + settings.json model，输出 实例↔PID↔HOME↔model↔tmux 对照表。不靠记忆/目录名直觉（破解命名错位陷阱：opus_home=BB 非AA，opus2_home=CC）
- **调用方**：手动（涉及实例操作前先跑一遍核对，防搞错）
- **频率**：按需
- **依赖**：pgrep/pstree/ps（procps，标准）
- **由来**：2026-06-19 教训，CC 两次把 BB 误当 AA 查，固化映射为只读工具

### instance_watchdog.sh
- **功能**：三实例(AA/BB/CC)会话外卡死看门狗（只通知版）。cron 每 5 分钟跑，进程外读各实例最新 jsonl，检测卡死信号（A.最近3条assistant输出高度重复/含 don't reply 类死扛短语 B.discord_reply_needed 标记滞留≥12分钟未消除），命中→Discord 通知主公"XX疑似卡死,建议发『重启』"。**只通知不自动重启**（2026-06-19 主公定档1）。防刷屏：同会话只报一次（/tmp/watchdog_alerted_<sid>）
- **调用方**：cron `*/5 * * * *`（见 reference/cron_jobs.md）
- **频率**：每 5 分钟
- **依赖**：python3/curl/标准 coreutils
- **由来**：2026-06-19 AA 幻觉卡死事故根因——现有防线(context_watch/reply_check)全挂会话内,会话烂了一起失效;本脚本是会话外独立监测,不受工具失效/幻觉影响。测试：DRY_RUN=1 跑（不发 Discord）
- **Log**：scripts/instance_watchdog.log

### log_write_event.py
- **功能**：PostToolUse hook，记录每次 Edit/Write/MultiEdit 共享文件的事件到 `logs/write_events.log`（共享文件清单：cowork_log.md / CURRENT_SESSION.md / friction_log.md / INSIGHTS.md）
- **调用方**：`/home/cowork/cowork/.claude/settings.json` PostToolUse hook（项目级，所有 claude 实例共享）
- **频率**：每次写共享文件触发（约日均几十次）
- **依赖**：无（标准库 Python）

### check_rating_question.py
- **功能**：UserPromptSubmit Hook，检测主公输入是否含评级/排名类问题词（什么水平/算高手/和别人比等），命中则注入 system-reminder 警告"禁止编造百分比/等级分布"
- **调用方**：`/home/cowork/cowork/.claude/settings.json` UserPromptSubmit hook（项目级，三实例共享）
- **频率**：每次主公输入时触发
- **依赖**：无（标准库 Python）

### check_proposal_words.py
- **功能**：Stop Hook，检测 AI 回复是否含推方案词（值得抄/不妨试试/加到BACKLOG等），命中则追加记录到 `friction_log.md`（留痕不阻断）
- **调用方**：`/home/cowork/cowork/.claude/settings.json` Stop hook（项目级，三实例共享）
- **频率**：每次 Claude 回复结束时触发
- **依赖**：无（标准库 Python）

### detect_conflict.py
- **功能**：扫 `write_events.log`，找 10 秒内同文件被两个不同 HOME 实例写过 → 追加到 `reference/conflict_log.md` + 发 Discord 告警（DM 频道，与 cron 系列一致）；用 `.conflict_alerted` 保证幂等
- **调用方**：cron `* * * * *`（每分钟）
- **频率**：每分钟
- **依赖**：`requests`、`/home/cowork/.claude/channels/discord/.env`（DISCORD_BOT_TOKEN）

---

## 📰 Newscripts 目录（/home/cowork/cowork/newscripts/）

### ai_news_monitor.py
- **功能**：AI 动态日报：抓取 Anthropic/OpenAI/Google AI 博客新文章 + arXiv cs.AI（Claude haiku 过滤）+ Claude Code 版本更新雷达；HTML 邮件发 zhitao776@gmail.com
- **调用方**：`newscripts/run_ai_news.sh`（cron 09:00 EDT daily）
- **频率**：每日
- **依赖**：`config/api_keys.env`（BREVO_API_KEY/CLAUDE_API_KEY）、`newscripts/ai_news.db`（seen_items 去重）、`scripts/send_email.py`、`claude --print`（haiku 过滤）

### run_ai_news.sh
- **功能**：ai_news_monitor.py 的 cron 包装（set -e + ERR trap → Brevo 失败告警邮件）
- **调用方**：cron `0 9 * * *`（cron_jobs.md 已登记）
- **频率**：每日 09:00 EDT
- **log**：`newscripts/ai_news.log`

---

## 🟡 库存脚本（功能有用，当前无调用）

### send_email.py
- **功能**：通用 Brevo HTTP API 邮件发送工具（读 config/api_keys.env，支持 text / html 邮件）
- **签名**：`send_email(subject, body, to=None, html=False)`
- **调用方**：**当前无脚本 import**——trading 脚本各自定义了简化版 send_email(env, subject, body)
- **状态**：库存。功能完整且**支持 HTML**（trading 版本不支持）
- **🎯 未来邮件需求请优先复用此模块**——避免每个脚本独立写一遍；要 HTML 邮件这是唯一选择

---

## ⚫ 一次性脚本（已完成历史任务）

### setup_db.py
- **功能**：初始化 cowork.db（建 FTS5 conversations 表 + sessions / embeddings 等）
- **调用方**：建库时手动跑过一次（2026-04-16）
- **状态**：留备——万一 cowork.db 损坏需要重建

### archive/backfill_sessions.py（2026-05-23 已移入 archive/）
- **功能**：从历史 JSONL 提取会话总结，回填 sessions 表
- **调用方**：一次性回填脚本（2026-04 跑过）
- **⚠️ 路径硬编码到旧 `~/.claude/projects/-root-cowork/`**，再用需先改为 `-home-cowork-cowork/`
- **位置**：`cowork/scripts/archive/backfill_sessions.py`

---

## 🗑️ 已删除记录

- **discord_approve_backup.py**（2026-05-23 删）—— Discord 授权检测早期版本（40 行），被 `~/.claude/hooks/discord_approve.py`（66 行）完全替代；旧版有 "收工" 误触发 bug

---

## 📝 维护规则

- 新增 `scripts/` 下脚本 → 必须在此 INDEX.md 加一段
- 删除脚本 → 同步删此处对应段
- 调用方变更（cron 启停 / Skill 改链路）→ 更新对应"调用方"行
- 季度审计：grep 调用关系验证"调用方"是否还真实存在

## 🔧 怎么扫调用方（参考给后人）

```bash
# cron 调用：
crontab -l | grep -E "\.(py|sh)"

# settings.json hook 调用：
python3 -c "import json; d=json.load(open('/home/cowork/.claude/settings.json')); ..."

# Skill 调用：
grep -rEn "scripts/" /home/cowork/.claude/skills/ /home/cowork/cowork/skill_archives/

# 文档引用：
grep -rEn "scripts/" /home/cowork/cowork/playbooks/ /home/cowork/cowork/reference/ /home/cowork/cowork/CLAUDE.md /home/cowork/cowork/ARCHITECTURE.md /home/cowork/cowork/context.md

# 脚本互调（import / subprocess）：
grep -rEn "scripts/" /home/cowork/cowork/scripts/ /home/cowork/cowork/trading/ /home/cowork/cowork/newscripts/
```
