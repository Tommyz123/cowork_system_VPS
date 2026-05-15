"""
TIDE 系统全局配置常量

历史：
- 2026 年早期使用 SPY 作为大盘基准
- 2026-05-08 全链路切换为 IWM（小盘股基准，更符合 P9 中盘股策略）
- 2026-05-15 引入 BENCHMARK_SYMBOL 常量，消除"基准字符串散落各处"反模式

未来换基准（如换 SCHA / IJR）：只改本文件 BENCHMARK_SYMBOL 一处即可。
"""

# 大盘基准 ETF
BENCHMARK_SYMBOL = "IWM"  # iShares Russell 2000（小盘股指数）

# 行业 ETF（统一基准，简化版；未来按个股 sector 动态分配是 BACKLOG）
DEFAULT_SECTOR_ETF = "GRID"  # First Trust Smart Grid Infrastructure
