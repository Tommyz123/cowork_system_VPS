---
name: Legal Library 工作流（入库 + 审核）
description: legal_library 的 VPS 本地工作方式（不重复 clone，主公说 push 才推）+ CCB 材料审核 3 步流程
type: feedback
originSessionId: 28862f78-beb1-48f8-8b56-32aef327ca17
---
## 一、入库工作流（VPS 本地）
VPS 上保留 `/home/cowork/legal_library/` 作为持久工作目录。

**Why:** 主公说直接在 VPS 拉材料、入库、做完直接 push，VPS 也留一份。不用每次 clone，不用等主公说 push。

**How to apply:**
- 每次开始入库任务：先 `git pull` 拉最新，然后直接在 `/home/cowork/legal_library/` 工作
- 不要重新 clone（目录已常驻）
- 每批入库完成后本地 commit，**不要 push**
- 只有主公明确说"做完了"/"push吧"等指令时，才执行 `git push`
- VPS 本地保留一份（不清理）

## 二、CCB 材料审核 3 步
每次主公发 CCB 材料（PDF/文件），必须按以下 3 步执行，不能只给大概：

1. **详细讲内容** — 具体说材料讲了什么，关键条款/数字/案件名/裁决结果，不是泛泛带过
2. **法律/案例入库判断** — 有增量价值的提取入库；说清楚为什么值得存，或为什么跳过
3. **12月批次线索扫描** — 每份材料都主动扫，有没有提到：
   - December Queue / 无地址申请批次
   - 2023年10月申请窗口
   - 队列推进进展 / 审核时间线
   - 主公的申请相关信息（12月批次零售执照）
   - 有的话专门标出来告诉主公

**Why:** 主公在 NY 零售执照 12月批次等待审核，想追踪自己申请进展；同时建立法律知识库供未来运营参考。

**How to apply:** 每次法律材料审核会话都适用，无需主公提醒。
