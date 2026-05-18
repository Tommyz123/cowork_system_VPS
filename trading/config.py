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

# ─────────────────────────────────────────
# P9 账号路由（2026-05-18 引入）
# ─────────────────────────────────────────
# P9 TIDE 系统所有下单（buy/sell）都必须在 P9_ACCOUNT 上执行
# 历史：intraday 账号是第一系统遗留，已 2026-05-06 彻底停用
# 主公 2026-05-18 要求：P9 数据必须统一在一个账号，避免 attribution 混乱
P9_ACCOUNT = "swing"

# 允许写操作（place_order/cancel_order/close_position）的账号白名单
# 任何写入 P9 数据的代码必须验证 account in ALLOWED_WRITE_ACCOUNTS，否则 raise
ALLOWED_WRITE_ACCOUNTS = ("swing",)


def assert_p9_account(account: str) -> None:
    """所有 P9 写操作必须先调这个，确保不会下到错账号。

    Raises ValueError if account not in ALLOWED_WRITE_ACCOUNTS.
    """
    if account not in ALLOWED_WRITE_ACCOUNTS:
        raise ValueError(
            f"P9 账号路由违规：尝试在 '{account}' 账号执行写操作，"
            f"但 ALLOWED_WRITE_ACCOUNTS = {ALLOWED_WRITE_ACCOUNTS}。"
            f"原因：2026-05-18 主公要求 P9 数据统一账号。"
            f"修复：account='{P9_ACCOUNT}' 或 import config.P9_ACCOUNT"
        )
