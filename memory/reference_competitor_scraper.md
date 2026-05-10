---
name: reference_competitor_scraper
description: 竞品爬虫架构：GF用Playwright捕dutchie graphql，ZenZest用HTTP直连WP proxy，DB在cowork/scraper/
type: reference
---

竞品爬虫架构（2026-05-01建立），路径：`cowork/scraper/competitor.db`

**Green Flower（GF）& Sage Seeds（SS）：**
- 技术：Playwright 捕获 `dutchie.com/api-2/graphql`
- 原因：dutchie前端动态加载，需浏览器渲染后截获GraphQL请求

**ZenZest（ZZ）：**
- 技术：HTTP直连 WP proxy（无需Playwright）
- 接口：`zenzest.com/wp-json/cannaplanners/v1/graphql/`
- retailerId：`e1950697-7b52-4a58-9f3f-f83ce99390da`（固定不变）

**How to apply:** 修改或新建竞品爬虫时，GF/SS走Playwright方案，ZZ直接HTTP请求+上述retailerId。
