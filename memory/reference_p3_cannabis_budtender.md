---
name: reference_p3_cannabis_budtender
description: P3 Cannabis AI Budtender 资源位置：目录路径、图片获取方案、后端启动
type: reference
originSessionId: 1ea4abd3-d11a-4c15-8b70-d1877a9347d7
---
**工作目录（VPS，2026-06-01 确认）：** `/home/cowork/Cannabis-AI-Budtender/`（旧 Windows 路径 `C:\Users\zhi89\Desktop\...` 已废弃）
**后端：** FastAPI，backend/main.py，:8000；**前端：** frontend/（静态 http.server :3000）
**启动：** `scripts/run_local.sh`（前台，后端 8000 + 前端 3000）；远程后台展示用 nohup 起两个进程
**依赖就绪：** venv/ 已建、data/products.db（217 产品）已就绪
**API key：** /chat 需 OPENAI_API_KEY；config.py 用 load_dotenv() 读项目根 `.env`；key 在全局 config/api_keys.env，需复制到项目 `.env`（已在 .gitignore）
**前端连后端：** frontend/placeholders.js 的 `API_BASE`；本地展示设 ""，公网展示设 `http://<VPS_IP>:8000`（CORS 已 allow_origins=["*"]）
**公网展示：** VPS IP 142.93.207.54；需主公 sudo 开 ufw 端口（3000/8000）；展示完停服务 + 关端口
**进度：** 见 `CURRENT_SESSION.md [P3]`

**图片方案（踩坑记录）：**
- Unsplash/Pexels 随机猜 ID 不稳定，不要用
- ✅ Flickr API（key 存 `config/api_keys.env` → `FLICKR_API_KEY`）可关键词搜索 CC 授权 cannabis 图片
- ✅ loremflickr.com 关键词搜索也有效

**How to apply:** 需要找 cannabis 产品图时直接用 Flickr API，不要重新踩 Unsplash 的坑。
