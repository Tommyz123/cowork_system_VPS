---
name: Legal Library 入库工作流
description: legal_library 的 VPS 本地工作方式：不重复 clone，累积完成后主公说 push 才推
type: feedback
originSessionId: 28862f78-beb1-48f8-8b56-32aef327ca17
---
VPS 上保留 `/home/cowork/legal_library/` 作为持久工作目录。

**Why:** 主公说直接在 VPS 拉材料、入库、做完直接 push，VPS 也留一份。不用每次 clone，不用等主公说 push。

**How to apply:**
- 每次开始入库任务：先 `git pull` 拉最新，然后直接在 `/home/cowork/legal_library/` 工作
- 不要重新 clone（目录已常驻）
- 每批入库完成后本地 commit，**不要 push**
- 只有主公明确说"做完了"/"push吧"等指令时，才执行 `git push`
- VPS 本地保留一份（不清理）
