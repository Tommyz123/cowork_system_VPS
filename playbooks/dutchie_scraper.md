---
name: dutchie_scraper
description: Dutchie POS 平台产品数据爬取：门店菜单抓取方法和技术文档
triggers: [dutchie, scraper, 爬虫, 菜单爬取, sageseedsny, POS, 产品数据抓取]
working_dir: C:\Users\zhi89\Desktop\marketing\
status: paused
---

# Dutchie 菜单爬取方法文档

> 记录日期：2026-03-28
> 目标网站：sageseedsny.com（大麻门店，POS 平台为 Dutchie）
> 目的：抓取门店完整产品数据（名称/品牌/价格/THC/CBD/分类等）

---

## ✅ 最终可行方案：Playwright 响应拦截

### 原理
Dutchie 嵌入菜单以 iframe 形式加载 `dutchie.com/embedded-menu/down-to-earth-canna`，iframe 内部通过 **GET 请求**（无 Authorization）访问 `dutchie.com/api-1/graphql`，操作名 `FilteredProducts`，直接返回完整产品 JSON。用 Playwright 加载父页面并拦截所有响应即可。

### 关键信息
| 字段 | 值 |
|------|-----|
| 门店 slug | `down-to-earth-canna` |
| Dispensary ID（MongoDB ObjectId） | `65e0b54d6114e50009ed7836` |
| 真实 API endpoint | `https://dutchie.com/api-1/graphql` |
| GraphQL 操作名 | `FilteredProducts` |
| 请求方式 | GET（参数 URL encode） |
| 认证要求 | **无需认证** |
| 父页面入口 | `https://sageseed.com/cannabis-menu/` |

### 可用数据字段（共 63 个）
核心字段：`_id` / `Name` / `brand` / `type`（分类）/ `strainType` / `THCContent` / `CBDContent` / `Prices` / `recPrices` / `effects` / `subcategory` / `images` / `specialData` / `strainType` / `Status` / `Options`

### 实测产品数量
- 总抓取：462 条（含重复分类）
- 去重后：**388 个唯一产品**
- 分类：Pre-Rolls(107) / Vaporizers(117) / Flower(79) / Edible(59) / Concentrate(25) / Accessories(1)

### 最小可用代码

```python
import asyncio
from playwright.async_api import async_playwright
import json

async def scrape_sage_seeds():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
        )
        page = await context.new_page()
        products = []

        async def on_response(response):
            if 'api-1/graphql' in response.url and 'FilteredProducts' in response.url:
                try:
                    body = await response.json()
                    batch = (body.get('data') or {}).get('filteredProducts', {}).get('products', [])
                    products.extend(batch)
                except:
                    pass

        context.on("response", on_response)
        await page.goto("https://sageseed.com/cannabis-menu/", timeout=45000)
        await asyncio.sleep(20)  # 等待所有分类懒加载完成
        await browser.close()

        # 去重
        unique = list({p['_id']: p for p in products}.values())
        return unique

products = asyncio.run(scrape_sage_seeds())
print(f"抓取 {len(products)} 个产品")
```

### 注意事项
- 等待时间建议 20s，页面有懒加载，滚动触发更多请求
- 如需触发全部分类，可在等待期间加入自动滚动
- Dutchie 无 rate limit（公开菜单），但建议跑完后随机间隔避免被标记

---

## ❌ 失败方案记录

### 失败 1：直接 HTTP 请求 dutchie.com/graphql
- **尝试**：Python `urllib` 直接 POST 到 `https://dutchie.com/graphql`
- **结果**：`HTTP 400 Bad Request`
- **原因**：该端点字段名与我们猜的不匹配，且隐藏错误提示（`[Suggestion hidden]`）

### 失败 2：尝试 Dutchie Plus API（plus.dutchie.com）
- **尝试**：`https://plus.dutchie.com/plus/2021-07/graphql`，字段 `retailer(id)` + `menu(retailerId)`
- **结果**：`UNAUTHENTICATED` — 需要 Bearer API Key
- **原因**：Plus API 是给门店开发者用的，需要门店申请专属 API Key
- **注**：字段结构正确（从官方 GitHub 示例 repo 获得），但无法绕过认证

### 失败 3：Dutchie REST API 猜测
- **尝试**：`/api/v1/menu`、`/api/v2/dispensary/{id}/menu` 等多个路径
- **结果**：全部 `HTTP 404`
- **原因**：Dutchie 已全面迁移到 GraphQL，不再维护 REST 端点

### 失败 4：直接访问 embedded-menu iframe URL
- **尝试**：Python/Playwright 直接 GET `https://dutchie.com/embedded-menu/down-to-earth-canna/`
- **结果**：`Cloudflare` 拦截（需要浏览器 cookie + JS 指纹）
- **原因**：Cloudflare Bot 管理，直接访问被识别为爬虫

### 失败 5：Dutchie 旧版 consumer API（filteredMenu）
- **尝试**：在 `dutchie.com/graphql` 使用 `filteredMenu(dispensaryId)` 查询（2020-2021 年社区文档记载的公开 API）
- **结果**：`Cannot query field "filteredMenu" on type "Query"`
- **原因**：Dutchie 在 2022 年后迁移了 consumer API，旧字段已废弃

### 失败 6：GraphQL Introspection
- **尝试**：发送 `__schema` introspection query 到两个端点
- **结果**：`GraphQL introspection is not allowed by Apollo Server`
- **原因**：生产环境标准安全设置，无法枚举 schema

### 失败 7：api.dutchie.com/graphql
- **尝试**：在 `api.dutchie.com/graphql` 穷举多个字段名
- **结果**：全部 `Cannot query field ... [Suggestion hidden]`
- **原因**：该端点功能未知，且主动隐藏字段建议

---

## 🔍 关键侦察路径（如何找到答案的）

1. 抓取 `sageseedsny.com` 主页 HTML → 找到 Dutchie carousel embed URL
2. URL 中直接暴露 `dispensaryId = 65e0b54d6114e50009ed7836`
3. 从 `sageseed.com/cannabis-menu/`（routeRoot 域）找到 `dutchie.com/api/v2/embedded-menu/{id}.js` 加载方式
4. Clone 官方 GitHub 示例 repo `GetDutchie/dutchie-plus-nextjs-example` → 获得 Plus API 结构（但需认证）
5. Playwright 加载 `sageseed.com/cannabis-menu/` 拦截网络请求 → 发现真实 iframe URL
6. 再次用 Playwright 加载完整页面 + 拦截响应 → 发现 `api-1/graphql` + `FilteredProducts` 无需认证
