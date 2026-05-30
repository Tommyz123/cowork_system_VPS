# Insights — 临时缓冲区

> **工作流：** 新经验写这里 → 健康检查触发审核 → 有价值的迁入 `reference/knowledge_base.md` → 清空
> 格式：`[YYYY-MM-DD] [项目/领域] 标题 → 内容（一两行，说清楚怎么用）`
> 已审核的稳定参考知识在：`reference/knowledge_base.md`

---

[2026-05-29] [P8/Alpine IQ] AIQ API 正确调用方式（实测验证）→ ① 真实端点 `https://lab.alpineiq.com/api/v1.1/piis/{UID}`（v1.1、是 piis 不是 piiList，旧文档记错，旧路径全 404）② 认证 `Authorization: Bearer {KEY}` ③ UID 在 AIQ 后台 Settings→API 页面、生成 key 处同屏显示。只读测试脚本 /tmp/aiq_readonly_test.py。[ref-worthy]
[2026-05-29] [P8/Alpine IQ] 【订正上一条】403 "Please provide a valid API key" ≠ 缺 UID → 之前（opus 实例）判断"403 是缺 UID 导致、补上 UID 就好"是错的。实测：带真实 UID 4757 + 主公二次确认完整正确的 key，跑 11 种认证写法（Bearer/原始/apiKey头/X-API-KEY/query/uid:key 拼接/uid 放各种位置）全部同一个 403，错误信息不随 UID 放法变化 → 服务器在「验 key」阶段就拒、根本没到 UID。诊断法：错误信息恒定 = 卡在 key 校验层 = 账号侧没开通 API 权限（或 key 未激活/IP 限制），客户端无解，需 AIQ 后台/老板开通。教训：403+"invalid key" 别想当然归因缺参数，先做「错误信息是否随参数变化」实验定位卡点。[ref-worthy]









