---
name: feedback_tmux_cross_instance
description: tmux send-keys 跨实例通讯必须用英文/ASCII，中文字符不会写入目标 pane
type: feedback
originSessionId: ae8aed06-a3ca-4bd3-b157-e20e9455f29e
---
tmux send-keys 跨实例通讯必须用英文/ASCII 字符。中文字符 send-keys 不会写入目标 pane 输入行（❯显示空白，对方根本没收到），改用英文指令后立即成功。

**Why:** 中文多字节字符在 tmux send-keys 跨 socket 发送时被截断/丢弃，是 tmux 编码限制，非配置问题。

**How to apply:** 所有 `tmux -L <socket> send-keys` 跨实例场景，指令内容必须用 ASCII/英文，不能含中文。
