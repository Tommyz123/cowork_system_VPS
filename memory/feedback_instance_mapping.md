---
name: feedback-instance-mapping
description: ⭐三实例操作铁律：动手前必先查映射（which_instance.sh 或权威全表 reference_dual_bot），禁止凭目录名直觉（2026-06-22 token对调教训）。完整映射表见 [[reference_dual_bot]]，本文件只留"为什么+怎么做"
metadata:
  type: feedback
---

## 操作铁律：涉及实例的任何操作，先确认映射再动手

涉及 AA/BB/CC 任何操作（排查/重启/改配置/查频道/换 token）前，**第一步先确认映射**，二选一：

```bash
bash /home/cowork/cowork/scripts/which_instance.sh   # 读运行时 HOME+settings，最权威
```

或查**唯一权威全表** [[reference_dual_bot]]（HOME / socket / session / 频道 / token / service / 模型全字段）。

**禁止凭目录名序号推断**（"opus2 是第二个所以是 BB"——错，opus2=CC）。

**记忆锚点（只记最易搞反的）：opus=BB，opus2=CC，裸 /home/cowork=AA**。

## Why（为什么这条是铁律）

2026-06-22 AA 凭直觉把 opus2 当 BB，错误对调了 BB/CC 的 Discord bot token，导致 BB 的 DM 收不到任何回复，折腾了 2 小时。根因是没查文档直接动手。

## How to apply

每次主公问"BB 为什么没反应 / CC 在干什么"，先跑 `which_instance.sh` 确认当前运行状态，再查问题，再动手。

> 📌 映射表为何不再写在本文件：避免"两张全表各记各的、改一处忘改另一处"打架（2026-06-25 session 名两张表不一致即此病）。全字段映射**单一权威源 = [[reference_dual_bot]]**，本文件只承载"操作纪律"。
