---
name: reference_p3_cannabis_budtender
description: P3 Cannabis AI Budtender 资源位置：目录路径、图片获取方案、后端启动
type: reference
originSessionId: 1ea4abd3-d11a-4c15-8b70-d1877a9347d7
---
**工作目录：** `C:\Users\zhi89\Desktop\cannabis_AI_BUDTENDER\`
**前端：** `frontend-next/preview.html`（130KB 独立文件）
**后端：** FastAPI，`localhost:8000`，`start_backend.bat` 双击启动
**进度：** 见 `CURRENT_SESSION.md [P3]`

**图片方案（踩坑记录）：**
- Unsplash/Pexels 随机猜 ID 不稳定，不要用
- ✅ Flickr API（key 存 `config/api_keys.env` → `FLICKR_API_KEY`）可关键词搜索 CC 授权 cannabis 图片
- ✅ loremflickr.com 关键词搜索也有效

**How to apply:** 需要找 cannabis 产品图时直接用 Flickr API，不要重新踩 Unsplash 的坑。
