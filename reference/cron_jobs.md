# Cowork Cron 任务总览

> 最后更新：2026-05-26（新增 AI 动态日报 09:00 EDT；Anthropic/OpenAI/Google AI 博客 + arXiv + Claude Code）
> 来源：`crontab -l` on VPS (DigitalOcean 142.93.207.54, user=cowork)
> 时区：America/New_York (EDT/EST)
> 用途：所有定时任务的**唯一索引**——加新 cron 必须在此注册

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

---

## 📈 P9 Trading System Cron

| 时间 (EDT) | 脚本 | 作用 | Log 路径 |
|---|---|---|---|
| `0 16 * * 1-5` (工作日 16:00) | `trading/signal_collector.py` | 信号采集 | `trading/signal_collector.log` |
| `0 16 * * 1-5` (工作日 16:00) | `trading/catalyst_monitor.py` | 催化剂监控 | `trading/catalyst.log` |
| `0 16 * * 1-5` (工作日 16:00) | `trading/signal_alert.py` | 信号告警 | `trading/signal_alert.log` |
| `30 16 * * 1` (周一 16:30) | `trading/scanner_tracker.py` | 周扫描器结果追踪 | `trading/scanner_tracker.log` |
| `45 16 * * 1` (周一 16:45) | `trading/price_tracker.py` | 价格追踪 | `trading/tracker.log` |
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
| `0 9 29 5 *` (5/29 09:00) | `scripts/cannabis_docket_reminder.py critical` | 关键日：OCM 答辩 deadline | 同上 |
| `0 9 30 5 *` (5/30 09:00) | `scripts/cannabis_docket_reminder.py critical` | 关键日：后续 reply / 和解可能公告 | 同上 |
| `0 9 31 5 *` (5/31 09:00) | `scripts/cannabis_docket_reminder.py critical` | 关键日 | 同上 |

⚠️ **注意:** 5/29-31 critical 提醒**明年仍会触发**——届时根据案件状态决定是否保留。

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
