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
| `*/5 * * * *` (每5分钟) | `scripts/instance_watchdog.sh` | 三实例(AA/BB/CC)会话外卡死看门狗——读各实例最新 jsonl 检测卡死信号（重复输出/don't reply死扛短语/漏发标记滞留≥25min），命中→Discord 通知主公建议「重启」。**只通知不自动重启**（2026-06-19 主公定档1）。防刷屏：同会话只报一次。由来=2026-06-19 AA 幻觉卡死事故。**2026-06-24 防误报升级**：阈值12→25min + 新增「活跃度闸门」（漏发滞留信号B 须 jsonl 近10min 静默才报，区分"埋头干长任务"vs"真卡死"；死循环信号A 不过闸门照报，因死循环时 jsonl 反而疯狂写） | `scripts/instance_watchdog.log` |

---

## 📈 P9 Trading System Cron

| 时间 (EDT) | 脚本 | 作用 | Log 路径 |
|---|---|---|---|
| `0 16 * * 1-5` (工作日 16:00) | `trading/signal_collector.py` | 信号采集 | `trading/signal_collector.log` |
| `0 16 * * 1-5` (工作日 16:00) | `trading/catalyst_monitor.py` | 催化剂监控 | `trading/catalyst.log` |
| `0 16 * * 1-5` (工作日 16:00) | `trading/signal_alert.py` | 信号告警 | `trading/signal_alert.log` |
| `30 16 * * 1` (周一 16:30) | `trading/scanner_tracker.py` | 周扫描器结果追踪 | `trading/scanner_tracker.log` |
| `45 16 * * 1` (周一 16:45) | `trading/price_tracker.py` | 价格追踪 | `trading/tracker.log` |
| `50 16 * * 1` (周一 16:50) | `trading/theme_heatmap.py` | **信号升温榜**（theme_discovery 阶段0 排雷）：列近30天信号突然变多的股票+升温倍数+🟢🔴好坏消息+板块+持仓标记，发 Discord。验证"信号聚集→能预示主题"地基假设；纯读 DB 不碰下单 | `trading/theme_heatmap.log` |
| `30 9 24 8 *` (2026-08-24 9:30, 一次性) | `trading/heatmap_review_reminder.py` | **升温榜8周验收提醒**：到排雷期满那天自动 Discord 提醒主公验收（命中率≥60%+认可→进阶段1 / 不到→停）。脚本内置日期守卫(<8/24自动跳过)；触发后此 cron 可删 | `trading/heatmap_review_reminder.log` |
| `0 17 * * 1` (周一 17:00) | `trading/post_exit_tracker.py` | 平仓后追踪：记录已平仓票平仓日之后走势(post_exit_peak/3m_return)，验证 P9 卖出时机；平仓日期取自 trades.exit_date，无 exit_date 的历史平仓票跳过等补齐；纯观察不碰选股/下单 | `trading/post_exit_tracker.log` |
| `5 17 * * 1` (周一 17:05) | `trading/unfilled_tracker.py` | **未成交票纸面跟踪**（验证选股眼光）：对 OPG 过期票(没买到)从信号日起跟踪股价，数据层写 unfilled_track_*(客观涨跌)+审计层用确定性规则(>+2%对/<-2%错)打 audit_pick_verdict；三层分离不碰判断 verdict；接 P9「过期单也对答案」/主题累积研究loop数据地基(B-轻量版,2026-06-27)；纯观察不碰选股/下单 | `trading/unfilled_tracker.log` |
| `15 17 * * 1` (周一 17:15) | `trading/trend_verdict_check.py` | **第2层提速实验·对答案机械判定**：补缺的信号层基线价(登记次日开盘)→到期窗口(3m/6m/12m)按预注册口径机械算相对SPY/板块并落 trend_verdicts(A排序力记数值/B方向三向判定/C下车后3月**相对SPY**判躲跌vs卖飞;收益=同基准复算auto_adjust总收益,冻结价只作存证;退市=最后可得收盘为终值;void作废样本跳过)→**完整性哨兵**(5表行数+缺号+哈希→notes/trend_integrity_log.txt,未登记缺号Discord告警)→Discord报；⚠️铁律=机械落库 BB 无权改判(防裁判自审,只可另INSERT discrepancy标记报主公)；幂等可重跑；方案 notes/第2层提速攒样本方案_20260701.md（2026-07-01新建） | `trading/trend_verdict.log` |
| `30 16 * * 3` (周三 16:30) | `trading/thesis_monitor.py` | 持仓 thesis 监控 | `trading/thesis_monitor.log` |
| `0 16 * * 0` (周日 16:00) | `trading/weekly_review.py` | 周报 | `trading/weekly.log` |
| `30 20 * * 1-5` (工作日 20:30) | `trading/price_guard.py` | 价格守卫 | `trading/price_guard.log` |
| `30 19 1-7 2,5,8,11 1` (季度首周一 19:30) | `trading/run_scanner.sh` | 季度大扫描（OPG orders 需 7pm+ 才可提交） | `trading/run_scanner.log` |
| `0 15 1-7 * 1` (月首周一 15:00) | `trading/screener.py` | 月度筛选器 | `trading/screener.log` |
| `30 18 1-7 2,5,8,11 1` (季度首周一 18:30) | `trading/quarterly_review.py` | 季度复盘 | `trading/quarterly_review.log` |
| `45 13 * * 1-5` (工作日 9:45 EDT) | `trading/sync_fill_prices.py` | 开盘后同步 fill_price（Swing 账号实际成交价回填 trades/scanner_picks/outcome_tracking） | `trading/fill_price_sync.log` |
| `45 15 * * 0` (周日 15:45 EDT) | `trading/gtrends_collector.py` | P9 alt-data sidecar：SerpAPI 拉 5 个 P9 theme 关键词 Google Trends search volume，写入 alt_signals 表；完全独立于 P9 主线，不进评分不进 weekly_review；主公 on-demand query 用（研究纪律：1 年后 sample 累积再考虑入评分） | `trading/gtrends_collector.log` |
| `0 8 * * *` (每天 08:00 EDT) | `trading/narrative_earnings_watch.py` | 公司叙事追踪 MVP 财报日哨兵：从 `narrative_hypotheses` 表解析在追踪的公司(数据驱动不硬编码)→yfinance 查下次财报日→临近≤5天 Discord 提醒"该对照假设触发/失效条件对答案"；财报日只当提醒不当死排期(每次重查+记抓取时间)；空表不报错。配套核心=`narrative_dossier.py`(手动录入假设/证据/周记 CLI)；方案见 `trading/notes/新闻追踪方案_2026-06-27.md`；2026-06-27 新建，先 VST 1 只跑 6-8 周验证 | `trading/narrative_earnings_watch.log` |
| `30 8 * * 1` (每周一 08:30 EDT) | `trading/narrative_weekly_sentinel.py` | 公司叙事追踪 MVP 周记哨兵：抓追踪票本周新闻(Finnhub)→claude CLI 让 AI 筛新闻/绑假设/提信心建议→生成"周记草稿"→Discord 发主公(分段)。⚠️红线=**只出草稿、只读不写判断**(不改信心/不插 evidence)，落库改信心需主公与 CC 讨论后人手动；草稿建议采纳/驳回记 `narrative_evidence.adoption`(成绩单第③层原料)。MVP 头几周定位=考核 AI 草稿靠不靠谱，非享受自动化。2026-06-28 新建 | `trading/narrative_weekly_sentinel.log` |

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
- ~~2026-05-18 09:00 EDT - P9 ORA pre-market 提醒~~ → 5/18 触发时 Discord 发送报 403 崩在自删逻辑之前，cron 沦为僵尸（每年 5/18 复活崩一次）；2026-06-25 系统审核发现后手动删 cron + 删脚本 `scripts/p9_ora_premarket_reminder.py`；背景：`trading/case_studies/ORA_2026_05_18.md`
- ~~2026-06-18 09:15 EDT - P9 首批完整 hit rate 提醒~~ → 6/18 触发后已自删 cron（脚本 `scripts/p9_first_hitrate_reminder.py` 自删逻辑生效）；2026-06-25 审核确认 crontab 已无此条，移入已清理

## 一次性 cron（active）
- 2026-06-28 09:00 EDT - 删 P9 告警重构 .bak（`run_py.sh.bak` / `ops_alert.py.bak`）→ 触发后自删 cron 行（run_py/ops_alert 重构兜底；目标文件现已手动删，触发时为空操作但 cron 仍按时自删）
- 2026-07-01 04:00 EDT - 删 `instance_watchdog.sh.bak`（标记 `WD_BAK_CLEANUP_20260701`）→ 触发后自删 cron 行（watchdog 活跃度闸门重构兜底）

## 📡 趋势主线（第2层）观察池周检（2026-06-11 新建）

**清单实体:** `/home/cowork/cowork/trading/notes/趋势观察池.md`（W1-W6 信号 + E 事件日历）
**信号→动作速查（给AI看）:** `/home/cowork/cowork/trading/notes/信号作战表.md`（一信号一行:谁盯/什么算触发/机器做啥/然后AI做啥/为什么；周检时 AI 必须对着它逐条过）
**背景:** 趋势地图 2026-Q2 配套盯防层；触发条件命中→Discord 报警主公

| 时间 (EDT) | 脚本 | 作用 | Log 路径 |
|---|---|---|---|
| `30 9 * * 1` (周一 09:30) | `trading/dossier_autowrite.py` | 趋势追踪档案轨迹自动写入：**从档案自身解析对象**(读`**追踪代码**`字段,不硬编码)→yfinance查价→给每对象轨迹表追加一行(价格/估值/距高)；逻辑状态列留`🔍待校准`等人工补；加新对象只改档案脚本零改动；阶段2-B（2026-06-21新建，先于09:35周检让其读到最新轨迹） | `trading/dossier_autowrite.log` |
| `35 9 * * 1` (周一 09:35) | `scripts/trend_watch_reminder.py` | 周提醒：按观察池清单执行周检（对 BB 说"趋势周检"） | `scripts/trend_watch_reminder.log` |
| `5 17 * * *` (每天 17:05) | `scripts/ferc_watch.py` | FERC大负荷接入规则哨兵(观察池E1)：SerpAPI搜新闻命中报警，静默无打扰；**两阶段**(2026-06-23改:一阶段6/18 show cause已落非终局→继续盯二阶段最终规则约8-9月,落地且利好才退役)；命中后必须BB人工确认真假 | `scripts/ferc_watch.log` |
| `0 10 * * 1` (周一 10:00) | `trading/dossier_weekly.py` | 趋势追踪档案AI周报：读`趋势追踪档案.md`→claude CLI分析每对象(直出📊数据/🧭判断两字段)→归档`trading/reports/weekly/`(markdown)+`render_dossier_html.py`渲染HTML卡片email推送主公；护栏=只事实分析不写买卖；阶段2-A（2026-06-20新建，2026-06-22排版重排+数据判断分层） | `trading/dossier_weekly.log` |
