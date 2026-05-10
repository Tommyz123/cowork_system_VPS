---
name: feedback_deprecation_cleanup
description: 停用系统/模块时的清理流程：弃用标记+引用扫描+数据层清理三层checklist
type: feedback
originSessionId: fb2ad148-a891-4de5-9022-d0c801600b4e
---
任何系统/模块/功能正式停用时，必须完成以下三层清理，缺任何一层都会导致新系统数据混乱：

**① 弃用标记原则**
memory文件里的相关引用不要静默删除——改为加 `⚠️ 已废弃：[停用原因/日期]` 标记。
理由：保留历史背景，同时明确标注不再使用，防止未来对话误认为当前状态。

**② 引用层清理Checklist**
1. `grep` 全部 memory/ 和 playbooks/ 找遗留引用（停用模块名/脚本名/指标名等）
2. 每处引用：加弃用标记，或更新为当前状态
3. 更新 MEMORY.md 对应描述行
4. 确认无遗漏后在 friction_log 或 cowork_log 记录一行"已完成停用清理"

**③ 数据层清理Checklist**（新增，2026-05-07）
1. DB：DELETE 旧系统专属记录；DROP 旧系统专属表（feature_snapshots/accuracy_log等）
2. 外部账号：平掉旧系统建立的持仓（Alpaca/exchange等）
3. 验证：确认新系统的数据/账号与本地记录完全一致，才算停用完成

**Why:** P9第一系统停用时只删了代码和引用，没清DB旧数据和Alpaca旧持仓，导致TIDE系统启动后新旧数据混杂，无法信任本地记录（2026-05-07发现）。

**How to apply:** 触发场景：停用某个功能/模块/系统后，同时触发①②③三层。不需要等主公提醒，自主完成。
