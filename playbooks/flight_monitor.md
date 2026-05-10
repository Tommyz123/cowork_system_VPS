---
name: flight_monitor
triggers: [机票, 航班, 监控, flight, flightscripts]
---

# Flight Monitor — 机票监控操作手册

## 快速启动

```bash
# 手动运行日报
bash /mnt/c/Users/zhi89/Desktop/cowork/flightscripts/run_flight.sh

# 查看运行日志
tail -f /mnt/c/Users/zhi89/Desktop/cowork/flightscripts/run.log

# 查看价格历史
sqlite3 /mnt/c/Users/zhi89/Desktop/cowork/flightscripts/flight_prices.db \
  "SELECT record_date, label, price, airlines FROM prices ORDER BY record_date DESC LIMIT 20;"
```

## 路径

- 主目录：`C:\Users\zhi89\Desktop\cowork\flightscripts\`
- WSL路径：`/mnt/c/Users/zhi89/Desktop/cowork/flightscripts/`
- 详细文档：`flightscripts/README.md`

## cron 设置

```
30 17 * * * bash /mnt/c/Users/zhi89/Desktop/cowork/flightscripts/run_flight.sh >> /mnt/c/Users/zhi89/Desktop/cowork/flightscripts/run.log 2>&1
```
每天 17:30 UTC = 13:30 EDT

## 监控范围

- **超级经济舱（转机）：** JFK/EWR → HKG/CAN/SZX（6条）
- **经济舱（直飞）：** JFK → HKG/CAN（2条）
- 行程：2026年9月出发，10月回程，约一个月

## 修改配置

| 需要改什么 | 改哪里 |
|-----------|--------|
| 监控路线 | `flight_monitor.py` → `ROUTES` 列表 |
| 采样日期 | `flight_monitor.py` → `SAMPLE_DATES` 列表 |
| 最长飞行时间过滤 | `flight_monitor.py` → `MAX_DURATION_MINUTES` |
| 日报格式 | `build_report.py` |
| Discord / cron | `run_flight.sh` |

## 进度

见 `CURRENT_SESSION.md [P6]`

## 协作习惯

- 修改舱位时注意：SerpAPI 代码 1=经济 / 2=超级经济 / 3=商务 / 4=头等
- SerpAPI 免费额度 250次/月，当前用量约 48次/天，勿随意增加采样日期
- 测试前先确认消耗额度是否合理


## 历史对话搜索
搜索此项目相关历史对话：
```bash
python3 /mnt/c/Users/zhi89/Desktop/cowork/scripts/search_conversations.py "关键词"
```
