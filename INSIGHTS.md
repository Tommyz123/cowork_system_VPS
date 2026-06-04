# Insights — 临时缓冲区

> **工作流：** 新经验写这里 → 健康检查触发审核 → 有价值的迁入 `reference/knowledge_base.md` → 清空
> 格式：`[YYYY-MM-DD] [项目/领域] 标题 → 内容（一两行，说清楚怎么用）`
> 已审核的稳定参考知识在：`reference/knowledge_base.md`

---

[2026-06-04] [P8/Alpine IQ] ✅ AIQ API 正确认证方式（最终确认）→ header 必须是 `x-apikey: {KEY}`（全小写无连字符）。Bearer/X-API-Key/x-api-key/Authorization 全部 403。端点格式：`https://lab.alpineiq.com/api/v1.1/{endpoint}/{UID}`。Sage Seeds UID=4757，env 在 /home/cowork/sage_seeds/aiq/aiq.env，测试脚本在 readonly_test.py（同目录）。[ref-worthy]
[2026-06-04] [P8/Alpine IQ] 【5/29旧记录订正】之前两条记录均错误 → ①"Authorization: Bearer"是错的；②"账号侧没开通权限/客户端无解"也是错的。真正原因：header 名称非标，AIQ 用 `x-apikey` 不是 `Authorization`，用对了立即通。教训：遇到"Please provide a valid API key"且 11 种写法全 403，下次要试非标 header 名（x-apikey/apikey/token 等），不要轻易断定是账号权限问题。
[2026-06-03] [P9/yfinance] 单 ticker 取历史价 history['Close'] 返 DataFrame 不是 Series → yf.download(单只票) 时 history['Close'] 是 DataFrame（列名=ticker），对它 .items() 遍历的是列名(str)不是(日期,价格)，下游 .strftime() 报 'str' object has no attribute 'strftime'。修法：取出后判 `if hasattr(closes, "columns"): closes = closes.iloc[:, 0]` 还原成 Series 再 .items()。适用所有 P9 单票取价脚本(post_exit_tracker/price_tracker)，新写取价逻辑直接套这个守卫。[src:332a722a] [ref-worthy]









