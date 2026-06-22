---
name: feedback-instance-mapping
description: ⭐三实例完整映射表（AA/BB/CC↔HOME↔bot↔群频道）+操作铁律：涉及实例操作前必查此表，禁止凭目录名直觉（2026-06-22 token对调教训）
metadata:
  type: feedback
---

## 三实例完整映射表（2026-06-22 实测确认）

| 实例 | HOME | Bot名 | 群频道ID | tmux socket | systemd服务 |
|------|------|-------|---------|------------|------------|
| AA | /home/cowork | AA-Sonnet4.6 | `1485128242808619079` | 默认socket，session: cowork | cowork-claude.service |
| BB | /home/cowork/opus_home | BB-Opus4.8 | `1503165641379545228` | opus_socket，session: cowork_opus | cowork-opus.service |
| CC | /home/cowork/opus2_home | CC-Opus4.8 | `1509045714808737842` | opus2_socket，session: cowork_opus2 | cowork-opus2.service |

**口诀：opus=BB，opus2=CC**（容易搞反的就是这两个）

Bot token路径：`$HOME/.claude/channels/discord/.env`（DISCORD_BOT_TOKEN字段）

## 操作铁律

涉及BB/CC任何操作（排查/重启/改配置/查频道）前，**第一步先确认映射**：

```bash
bash /home/cowork/cowork/scripts/which_instance.sh
```

或直接查本文件表格，禁止凭目录名序号（"opus2是第二个所以是BB"）推断。

**Why:** 2026-06-22 AA凭直觉把opus2当BB，错误对调了BB/CC的Discord bot token，导致BB的DM收不到任何回复，折腾了2小时。根因是没查文档直接动手。

**How to apply:** 每次主公问"BB为什么没反应/CC在干什么"时，先跑which_instance.sh确认当前运行状态，再查问题，再动手。

[[reference_dual_bot]]
