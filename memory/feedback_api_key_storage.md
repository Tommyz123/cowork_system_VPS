---
name: feedback_api_key_storage
description: API key必须独立存放，禁止硬编码在脚本中
type: feedback
originSessionId: fb7379c1-70fd-4004-8ae4-b866fc324cb8
---
**API key 不得硬编码在脚本里，必须存入独立 `.env` 文件，通过环境变量读取。**

**Why:** 硬编码的 key 会进入 git 历史，即使删除也可被找到；且违反模型无关性设计原则（配置与代码应分离）。（2026-04-16 flight_monitor.py 被发现 SerpAPI key 硬编码）

**How to apply:** 写任何需要 API key 的脚本时：
- Python：`os.environ.get("KEY_NAME")`
- Shell：从 `.env` 文件读取并 `export`
- `.env` 文件加入 `.gitignore`，不追踪到 git
