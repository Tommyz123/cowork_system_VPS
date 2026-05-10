---
name: feedback_p9_ops
description: P9 TIDE系统操作规则：手动扫描必须用bash脚本，不能直接跑python
type: feedback
originSessionId: fb2ad148-a891-4de5-9022-d0c801600b4e
---
P9手动触发季度扫描必须用 `bash run_scanner.sh`，不能直接 `python3 cognitive_scanner.py`。

**Why:** `run_scanner.sh` 有 `trap ERR` 失败告警——扫描失败会自动发邮件通知。直接跑 `.py` 跳过这个保护，失败了不会有通知，主公不会知道。（同理：旧第一系统 run_trading.sh 也是同样原则，2026-05-01踩坑）

**How to apply:** 凡是需要手动重跑TIDE季度扫描的场景（调试/补跑/验证），第一步确认用 `bash run_scanner.sh`（在 `/mnt/c/Users/zhi89/Desktop/cowork/trading/` 目录下），不走 `python3` 直接调用。
