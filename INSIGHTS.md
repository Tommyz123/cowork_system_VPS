# Insights — 临时缓冲区

> **工作流：** 新经验写这里 → 健康检查触发审核 → 有价值的迁入 `reference/knowledge_base.md` → 清空
> 格式：`[YYYY-MM-DD] [项目/领域] 标题 → 内容（一两行，说清楚怎么用）`
> 已审核的稳定参考知识在：`reference/knowledge_base.md`

---

[2026-05-29] [P8/Alpine IQ] AIQ API 正确调用方式（实测验证）→ ① 真实端点是 `https://lab.alpineiq.com/api/v1.1/piis/{UID}`（v1.1、是 piis 不是 piiList，我旧文档记错了，旧路径全 404）② 认证 `Authorization: Bearer {KEY}` ③ key 绑定账号 UID：不带正确 UID 一律回 403 "Please provide a valid API key"（错误信息误导，实为缺 UID）；光有 key 无 UID 连不动 ④ UID 在 AIQ 后台 Settings→API 页面、生成 key 处同屏显示。只读测试脚本 /tmp/aiq_readonly_test.py。[ref-worthy]









