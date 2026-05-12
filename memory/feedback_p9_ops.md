---
name: feedback_p9_ops
description: P9 TIDE系统操作规则：进入对话先念下一步/手动扫描用bash/检查信号先确认交易日
type: feedback
originSessionId: fb2ad148-a891-4de5-9022-d0c801600b4e
---
P9手动触发季度扫描必须用 `bash run_scanner.sh`，不能直接 `python3 cognitive_scanner.py`。

**Why:** `run_scanner.sh` 有 `trap ERR` 失败告警——扫描失败会自动发邮件通知。直接跑 `.py` 跳过这个保护，失败了不会有通知，主公不会知道。（同理：旧第一系统 run_trading.sh 也是同样原则，2026-05-01踩坑）

**How to apply:** 凡是需要手动重跑TIDE季度扫描的场景（调试/补跑/验证），第一步确认用 `bash run_scanner.sh`（在 `/home/cowork/cowork/trading/` 目录下），不走 `python3` 直接调用。

---

进入P9对话（主公说"继续P9"/"看看P9"等）→ 必须第一时间读 `CURRENT_SESSION.md` 中 P9 区块，主动念出"下一步"列表让主公选择——不等主公问"有什么要做的"。

**Why:** 主公明确要求此行为（2026-05-09）。不主动念出会让主公每次都要多说一句。

**How to apply:** 任何进入P9工作场景的第一个动作：read CURRENT_SESSION.md → 列出下一步 → 等选择。

---

检查P9信号状态时，必须先确认当天是否为交易日（周一至周五且非美股节假日），再判断 signal_collector 是否漏跑。

**Why:** 直接看 log 日期差会在周末/节假日误判成"漏跑"（2026-05-09踩坑）。

**How to apply:** 收到"P9今天跑了吗"类问题 → 先 `date` 确认星期几 → 再查 log。
