---
name: feedback_env_check
description: 进入新环境/新会话必须先查环境信息，不能凭路径猜测
type: feedback
originSessionId: 8a06505e-fc15-40da-9a68-546769d6bf1f
---
进入任何新环境或不确定当前在哪台机器时，第一步必须跑：

```bash
hostname && whoami && pwd && curl -s ifconfig.me
```

**Why:** 路径格式不可靠——`/home/cowork/` 可能是 VPS 非 root 用户，也可能是本地。P11 迁移对话中因为没有先查环境，把 VPS cowork 用户误判为其他环境，浪费了大量来回确认（2026-05-09）。

**How to apply:** 凡是对话开始时不确定运行环境（云端/本地/哪个用户），或者看到不熟悉的路径时，先跑这4个命令确认再动手，不要猜。
