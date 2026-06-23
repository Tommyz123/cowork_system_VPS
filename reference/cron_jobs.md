# Cowork Cron 任务总览

> 最后更新：2026-05-27（新增 systemd 自启服务区块——cowork-opus2 装好后顺手把 3 个 service 集中登记）
> 来源：`crontab -l` + `systemctl list-units` on VPS (DigitalOcean 142.93.207.54, user=cowork)
> 时区：America/New_York (EDT/EST)
> 用途：所有**自动触发任务**（cron 定时 + systemd 自启）的唯一索引——加新 cron / service 必须在此注册

---

## 全局配置

```
PATH=/home/cowork/.bun/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```

时间格式：`分 时 日 月 周`

---

## 📅 每日 / 每周固定任务

| 时间 (EDT) | 脚本 | 作用 | Log 路径 |
|---|---|---|---|
| `0 2 * * *` (02:00 daily) | `scripts/rclone_backup.sh` | Google Drive 全量同步备份 | `scripts/rclone_backup.log` |
| `0 9 * * *` (09:00 daily) | `newscripts/run_ai_news.sh` | AI 动态日报（Anthropic/OpenAI/Google AI 博客 + arXiv + Claude Code 更新）→ 邮件 | `newscripts/ai_news.log` |
| `0 13 * * *` (13:00 daily) | `newscripts/run_daily_news.sh` | 每日新闻日报（政治/股市/加密/AI/大麻NY 5类） | `newscripts/run.log` |
| `30 17 * * *` (17:30 daily) | `scripts/run_mac_monitor.sh` | Mac mini M4 价格监控 | `scripts/mac_monitor.log` |
| `0 21 * * *` (21:00 daily) | `trading/run_py.sh trading/price_snapshot.py` | P9 每日价格快照 | `trading/price_snapshot.log` |
| `30 17 * * 2,4` (周二/四 17:30) | `flightscripts/run_flight.sh` | 机票监控（SerpAPI 双 key 自动轮换） | `flightscripts/run.log` |
| `0 17 * * 3` (周三 17:00) | `stability_check.sh` | 系统稳定性检查 | `stability_check.log` |
| `* * * * *` (每分钟) | `scripts/detect_conflict.py` | 共享文件冲突监测（扫 `logs/write_events.log`，10 秒窗口内同文件被两个不同 HOME 写过 → 写 `reference/conflict_log.md` + DM 频道告警；幂等） | `logs/detect_conflict.log` |
| `*/5 * * * *` (每5分钟) | `scripts/instance_watchdog.sh` | 三实例(AA/BB/CC)会话外卡死看门狗——读各实例最新 jsonl 检测卡死信号（重复输出/don't reply死扛短语/漏发标记滞留≥12min），命中→Discord 通知主公建议「重启」。**只通知不自动重启**（2026-06-19 主公定档1）。防刷屏：同会话只报一次。由来=2026-06-19 AA 幻觉卡死事故 | `scripts/instance_watchdog.log` |

---

## 📈 P9 Trading System Cron

| 时间 (EDT) | 脚本 | 作用 | Log 路径 |
|---|---|---|---|
| `0 16 * * 1-5` (工作日 16:00) | `trading/signal_collector.py` | 信号采集 | `trading/signal_collector.log` |
| `0 16 * * 1-5` (工作日 16:00) | `trading/catalyst_monitor.py` | 催化剂监控 | `trading/catalyst.log` |
| `0 16 * * 1-5` (工作日 16:00) | `trading/signal_alert.py` | 信号告警 | `trading/signal_alert.log` |
| `30 16 * * 1` (周一 16:30) | `trading/scanner_tracker.py` | 周扫描器结果追踪 | `trading/scanner_tracker.log` |
| `45 16 * * 1` (周一 16:45) | `trading/price_tracker.py` | 价格追踪 | `trading/tracker.log` |
| `0 17 * * 1` (周一 17:00) | `trading/post_exit_tracker.py` | 平仓后追踪：记录已平仓票平仓日之后走势(post_exit_peak/3m_return)，验证 P9 卖出时机；平仓日期取自 trades.exit_date，无 exit_date 的历史平仓票跳过等补齐；纯观察不碰选股/下单 | `trading/post_exit_tracker.log` |
| `30 16 * * 3` (周三 16:30) | `trading/thesis_monitor.py` | 持仓 thesis 监控 | `trading/thesis_monitor.log` |
| `0 16 * * 0` (周日 16:00) | `trading/weekly_review.py` | 周报 | `trading/weekly.log` |
| `30 20 * * 1-5` (工作日 20:30) | `trading/price_guard.py` | 价格守卫 | `trading/price_guard.log` |
| `30 19 1-7 2,5,8,11 1` (季度首周一 19:30) | `trading/run_scanner.sh` | 季度大扫描（OPG orders 需 7pm+ 才可提交） | `trading/run_scanner.log` |
| `0 15 1-7 * 1` (月首周一 15:00) | `trading/screener.py` | 月度筛选器 | `trading/screener.log` |
| `30 18 1-7 2,5,8,11 1` (季度首周一 18:30) | `trading/quarterly_review.py` | 季度复盘 | `trading/quarterly_review.log` |
| `45 13 * * 1-5` (工作日 9:45 EDT) | `trading/sync_fill_prices.py` | 开盘后同步 fill_price（Swing 账号实际成交价回填 trades/scanner_picks/outcome_tracking） | `trading/fill_price_sync.log` |
| `45 15 * * 0` (周日 15:45 EDT) | `trading/gtrends_collector.py` | P9 alt-data sidecar：SerpAPI 拉 5 个 P9 theme 关键词 Google Trends search volume，写入 alt_signals 表；完全独立于 P9 主线，不进评分不进 weekly_review；主公 on-demand query 用（研究纪律：1 年后 sample 累积再考虑入评分） | `trading/gtrends_collector.log` |

**Trading 时间调整记录（2026-05-11）:** scanner_tracker→16:30, price_tracker→16:45, thesis_monitor→16:30, run_scanner→17:00, quarterly_review→18:30（错开 DB 冲突）
**2026-05-18 时间调整:** run_scanner→19:30（Alpaca OPG orders 需在 7pm EDT 后提交，原 17:00 触发导致全批 403 拒单）
**2026-05-14 新增:** sync_fill_prices.py 工作日 9:45 EDT 自动回填 fill_price（已验证 Swing 账号 10 条历史记录同步成功）

---

## ⚖️ NY 大麻 December Queue 诉讼追踪（2026-05-12 新建）

**案件:** Organic Blooms LLC v. NYS CCB, Index No. 904497-24
**追踪文档:** `/home/cowork/legal_library/18_Organic_Blooms_v_CCB_Tracking.md`

| 时间 (EDT) | 脚本 | 作用 | Log 路径 |
|---|---|---|---|
| `0 9 * * 1` (周一 09:00) | `scripts/cannabis_docket_reminder.py weekly` | 周提醒：查 NYSCEF docket | `scripts/cannabis_docket_reminder.log` |
| `0 9 2 7 *` (7/2 09:00) | `scripts/cannabis_docket_reminder.py critical` | 关键日：SJ 动议开庭前一天 | 同上 |
| `0 9 3 7 *` (7/3 09:00) | `scripts/cannabis_docket_reminder.py critical` | 关键日：summary judgment 动议开庭日 09:30 | 同上 |
| `0 9 4 7 *` (7/4 09:00) | `scripts/cannabis_docket_reminder.py critical` | 关键日：开庭后（关注裁决/原告 affidavit） | 同上 |

⚠️ **注意:** critical 提醒按年循环（`* `月份字段）**明年仍会触发**——案件结束后需手动清理 7/2-7/4 三条。原 6/12-14 节点（OCM 答辩，已于 2026-06-12 提交）已更新为 7/3 SJ 开庭节点。

---

## 🤖 Systemd 自启服务（3 个 Claude Code 实例）

VPS 启动时由 systemd 自动拉起，**reboot 不需要主公手动管**。

| Service | HOME | tmux socket / session | Runner | Discord 频道 |
|---|---|---|---|---|
| `cowork-claude.service` | `/home/cowork` | 默认 socket / `cowork` | `scripts/claude_runner.sh` | DM `1485128242808619079` |
| `cowork-opus.service` | `/home/cowork/opus_home` | `opus_socket` / `cowork_opus` | `scripts/claude_opus_runner.sh` | DM `1503165641379545228` (opus_CC#0475) |
| `cowork-opus2.service` | `/home/cowork/opus2_home` | `opus2_socket` / `cowork_opus2` | `scripts/claude_opus2_runner.sh` | TT基地 guild `1466957346310717636`（具体 DM 频道见 `opus2_home/.claude/channels/discord/access.json`） |

**3 个 service 都 `enabled`**（验证：`systemctl is-enabled cowork-claude cowork-opus cowork-opus2`）。

**常用管理命令：**
```bash
sudo systemctl status cowork-opus2    # 查状态
sudo systemctl restart cowork-opus2   # 重启
sudo systemctl stop cowork-opus2      # 停（要 root）
sudo journalctl -u cowork-opus2 -n 50 # 看最近日志
```

**Service 文件源：** `/home/cowork/cowork/scripts/cowork-*.service`（git 跟踪），装到 `/etc/systemd/system/` 用：
```bash
sudo cp /home/cowork/cowork/scripts/cowork-opus2.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now cowork-opus2
```

**历史：**
- 2026-05-10：cowork + opus_CC 双 bot 上线（systemd 自启）
- 2026-05-27：opus2（第 3 实例）从手动启升级为 systemd 自启

---

## 🛠️ 管理命令

```bash
# 查看当前 crontab
crontab -l

# 编辑 crontab
crontab -e

# 备份当前 crontab
crontab -l > /tmp/crontab.backup.$(date +%s)

# 恢复（如出错）
crontab /tmp/crontab.backup.<timestamp>

# 查看某个 log 最近输出
tail -50 /home/cowork/cowork/scripts/cannabis_docket_reminder.log
```

---

## 📋 添加新 cron 的标准流程

按 `feedback_artifact_indexing` 规则，加新 cron 必须 4 步：

1. **写脚本**到 `/home/cowork/cowork/scripts/` 或对应子目录
2. **测试运行**确认 syntax + 行为
3. **添加 crontab 条目**（含 log 重定向）
4. **在此文件注册**（必须有时间 / 脚本 / 作用 / log 路径四项）

**不在此文件注册的 cron 视为未完成。**

---

## 🔍 监控 cron 健康

- **统一 ops_log:** `/home/cowork/cowork/ops_log.md`（所有 cron 应该写入此文件）
- **每周三 stability_check.sh** 会扫描各 log，发现错误发邮件告警
- **SMTP 通道:** 已改为 Brevo HTTP API（2026-05-11 修复，DO 封 SMTP 25 端口）

## 一次性 cron（已清理）
- ~~2026-05-17 18:00 EDT - P9 outcome 模板评估提醒~~ → 触发后 token 路径读错发送失败；2026-05-17 手动清理 cron + 删脚本；背景文档 `reference/p9_outcome_template_review_pending.md` 保留待主公 A/B/C/D 决策

## 一次性 cron（active）
- 2026-05-18 09:00 EDT - P9 ORA pre-market 提醒（trim 30-60% 决策）
  - 脚本：`scripts/p9_ora_premarket_reminder.py`
  - 触发后自删 cron 条目 + 守卫 `if TODAY != "2026-05-18"`
  - 背景：`trading/case_studies/ORA_2026_05_18.md`
- 2026-06-18 09:15 EDT - P9 首批完整 hit rate 提醒（16 只 5 月持仓全满 30 天）
  - cron：`15 9 18 6 *`
  - 脚本：`scripts/p9_first_hitrate_reminder.py`（log: `scripts/p9_first_hitrate_reminder.log`）
  - 触发后自删 cron 条目 + 守卫 `if TODAY != "2026-06-18"`；发至 cowork bot DM 频道
  - 背景：5/6 那 7 只 6/5 满期 / 5/18 那 8 只 6/17 / 5/19 那 1 只 6/18 → 6/18 全到期；2026-05-30 主公确认 B 方案（完整 hit rate，非 6/5 局部预览）

## 📡 趋势主线（第2层）观察池周检（2026-06-11 新建）

**清单实体:** `/home/cowork/cowork/trading/notes/趋势观察池.md`（W1-W6 信号 + E 事件日历）
**背景:** 趋势地图 2026-Q2 配套盯防层；触发条件命中→Discord 报警主公

| 时间 (EDT) | 脚本 | 作用 | Log 路径 |
|---|---|---|---|
| `30 9 * * 1` (周一 09:30) | `trading/dossier_autowrite.py` | 趋势追踪档案轨迹自动写入：**从档案自身解析对象**(读`**追踪代码**`字段,不硬编码)→yfinance查价→给每对象轨迹表追加一行(价格/估值/距高)；逻辑状态列留`🔍待校准`等人工补；加新对象只改档案脚本零改动；阶段2-B（2026-06-21新建，先于09:35周检让其读到最新轨迹） | `trading/dossier_autowrite.log` |
| `35 9 * * 1` (周一 09:35) | `scripts/trend_watch_reminder.py` | 周提醒：按观察池清单执行周检（对 BB 说"趋势周检"） | `scripts/trend_watch_reminder.log` |
| `5 17 * * *` (每天 17:05) | `scripts/ferc_watch.py` | FERC裁决自动哨兵(观察池E1)：SerpAPI搜新闻命中报警，静默无打扰；**一次性**——裁决落地后删cron行+归档脚本 | `scripts/ferc_watch.log` |
| `0 10 * * 1` (周一 10:00) | `trading/dossier_weekly.py` | 趋势追踪档案AI周报：读`趋势追踪档案.md`→claude CLI分析每对象(直出📊数据/🧭判断两字段)→归档`trading/reports/weekly/`(markdown)+`render_dossier_html.py`渲染HTML卡片email推送主公；护栏=只事实分析不写买卖；阶段2-A（2026-06-20新建，2026-06-22排版重排+数据判断分层） | `trading/dossier_weekly.log` |
