# Flight Monitor — 机票监控 Agent

每天自动查询纽约→香港/广州/深圳的机票价格，AI 分析走势，Discord 推送日报。

---

## 功能

- 每日查询 8 条航线最低价（超级经济舱转机 + 经济舱直飞）
- 对比昨日价格，显示涨跌幅（↑↓→）
- 记录历史价格到 SQLite，积累走势数据
- Claude AI 分析价格走势，给出"买还是等"建议
- Discord 推送日报，含航班时间 + 真实 Google Flights 购买链接

---

## 监控航线

| 航线 | 舱位 | 说明 |
|------|------|------|
| JFK → HKG | 超级经济舱 | 转机，自动最优路由 |
| JFK → CAN | 超级经济舱 | 转机，自动最优路由 |
| JFK → SZX | 超级经济舱 | 转机，自动最优路由 |
| EWR → HKG | 超级经济舱 | 转机，自动最优路由 |
| EWR → CAN | 超级经济舱 | 转机，自动最优路由 |
| EWR → SZX | 超级经济舱 | 转机，自动最优路由 |
| JFK → HKG | 经济舱 | 仅直飞 |
| JFK → CAN | 经济舱 | 仅直飞 |

**行程：** 出发 2026年9月任意日期，回程10月（约一个月）

---

## 文件结构

```
flightscripts/
├── run_flight.sh        # 主入口：查价→分析→推送（cron 调用此文件）
├── flight_monitor.py    # 查 SerpAPI + 存 SQLite + 输出 JSON
├── build_report.py      # 将 JSON 格式化为 Discord 日报文本
├── flight_prices.db     # SQLite 历史价格库（自动创建）
├── run.log              # 运行日志（自动创建）
└── README.md            # 本文件
```

---

## 技术栈

| 组件 | 工具 |
|------|------|
| 机票数据 | SerpAPI Google Flights API |
| 历史存储 | SQLite |
| AI 分析 | Claude CLI (`claude --print`) |
| 通知 | Discord Bot（现有 bot token） |
| 定时运行 | 本地 cron |

---

## 设置与运行

### 依赖安装

```bash
pip install google-search-results --break-system-packages
```

### 手动测试运行

```bash
bash /mnt/c/Users/zhi89/Desktop/cowork/flightscripts/run_flight.sh
```

### 设置 cron（每天 13:30 EDT）

```bash
crontab -e
```

添加：
```
30 17 * * * bash /mnt/c/Users/zhi89/Desktop/cowork/flightscripts/run_flight.sh >> /mnt/c/Users/zhi89/Desktop/cowork/flightscripts/run.log 2>&1
```

> 注：17:30 UTC = 13:30 EDT（夏令时）

### 查看运行日志

```bash
tail -f /mnt/c/Users/zhi89/Desktop/cowork/flightscripts/run.log
```

---

## API Key

- **SerpAPI Key**：已写入 `flight_monitor.py`（SERPAPI_KEY 变量）
- **Claude**：使用本地 claude CLI，无需额外 API Key
- **Discord Bot Token**：读取自 `/home/zhi8939/.claude/channels/discord/.env`

---

## 日报示例

```
✈️ 机票日报 2026-04-13

🛋️ 超级经济舱（转机）：
• JFK→HKG 超级经济转机: $1,957 (Delta)
  ⏰ 2026-09-16 18:00→2026-09-18 05:05 (23h5m) | 出发:2026-09-16
  🔗 查看购买

💺 经济舱（直飞）：
• JFK→HKG 经济直飞: $1,389 (Cathay Pacific)
  ⏰ 2026-09-21 14:55→2026-09-22 19:05 (16h10m) | 出发:2026-09-21
  🔗 查看购买

🤖 AI建议：距出发还有 141 天，价格处于合理区间...
```

---

## 注意事项

- SerpAPI 免费额度：250 次/月，8 条路线 × 6 日期 = 48 次/天，约每月消耗在额度内
- 每次运行消耗约 48 次 SerpAPI 查询（8 路线 × 6 个9月采样日期）
- 过滤规则：总飞行时长 > 24 小时的绕路航班自动排除
- 深圳（SZX）路线价格通常偏高（$4,000+），属正常现象
