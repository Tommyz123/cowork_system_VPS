---
name: marketing
description: 纽约大麻 AI 顾问数据库建设：产品数据抓取、市场分析、消费者选品
triggers: [marketing, 大麻顾问, weedmaps, market.db, 产品数据库, 纽约大麻, 顾问项目]
working_dir: C:\Users\zhi89\Desktop\marketing\
status: paused
---

# Playbook: 纽约大麻 AI 顾问项目

> 工作目录：`C:\Users\zhi89\Desktop\marketing\`
> 规则文件（不重复）：`marketing/CLAUDE.md`

---

## 启动序列（每次进入项目必做）

1. 读 `session_progress.txt` — 了解当前进度、数据库状态、待做事项
2. 读 `PROJECT_INDEX.md` — 了解项目结构和数据概况
3. 确认本次任务目标（和主公确认或从 session_progress 提取）

---

## 典型工作流：strain_type 填充

```
1. 确认目标品牌/条目（从 session_progress.txt 或主公指定）
2. 查询数据库空缺：
   SELECT product_name, strain FROM products WHERE strain_type IS NULL AND brand = 'X'
3. 逐条搜索（按 CLAUDE.md 顺序：官网 → 门店 → Leafly）
4. 用三列表格汇报结果（见 CLAUDE.md 格式）
5. 主公确认后批量写入数据库
6. 更新 session_progress.txt + PROJECT_INDEX.md
```

---

## 典型工作流：爬虫运行

```
1. 确认目标（新门店 / 更新产品 / 特定 URL）
2. 进入 weedmaps-listings-scraper/ 目录
3. 运行前检查 headers 和 rate limit 设置
4. 运行脚本，监控输出
5. 验证数据写入是否正常（查库确认）
6. 更新 session_progress.txt
```

---

## 格式标准

> 详细格式见 `marketing/CLAUDE.md`，以下为快速参考：

| 项目 | 标准 |
|------|------|
| strain_type 值 | `Indica` / `Sativa` / `Hybrid`（首字母大写） |
| 数据库更新来源 | 必须标注渠道（官网/门店/Leafly） |
| 日志 | 写入 `.claude/activity.log`，格式见 CLAUDE.md |

**CLAUDE.md 为权威来源，有冲突时以 CLAUDE.md 为准。**

---

## 主数据库路径

`marketing/weedmaps-listings-scraper/dumps/market.db`

---

## 收工前必做

- 更新 `session_progress.txt`（当前进度、下一步、数据库状态）
- 如数据规模或结构变化，更新 `PROJECT_INDEX.md`
