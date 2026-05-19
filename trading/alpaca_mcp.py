#!/usr/bin/env python3
"""Alpaca MCP Server - P9 swing 账号（唯一）

历史：
- 2026-05-18 锁定写操作只能 swing（assert_p9_account）
- 2026-05-18 ghost positions 事件后，主公决定删除 intraday paper 账户，
  P9 所有数据统一到 swing 单账号。本文件不再引用 intraday。
"""
import json
import sqlite3
import time
import urllib.request
import urllib.error
import os
import sys
from pathlib import Path
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    class FastMCP:
        def __init__(self, name: str):
            self.name = name

        def tool(self):
            def decorator(func):
                return func
            return decorator

        def run(self):
            while True:
                time.sleep(60)

_env_path = Path(__file__).parent.parent / "config" / "api_keys.env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

sys.path.insert(0, str(Path(__file__).parent))
from config import P9_ACCOUNT, ALLOWED_WRITE_ACCOUNTS, assert_p9_account

mcp = FastMCP("alpaca-trading")

SWING = {
    "endpoint": os.getenv("ALPACA_SWING_ENDPOINT", "https://paper-api.alpaca.markets/v2"),
    "key": os.getenv("ALPACA_SWING_KEY", ""),
    "secret": os.getenv("ALPACA_SWING_SECRET", ""),
}


def _headers():
    return {
        "APCA-API-KEY-ID": SWING["key"],
        "APCA-API-SECRET-KEY": SWING["secret"],
    }


def _request(path: str) -> dict:
    url = f"{SWING['endpoint']}{path}"
    req = urllib.request.Request(url, headers=_headers())
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"error": str(e)}


def _post(path: str, body: dict) -> dict:
    url = f"{SWING['endpoint']}{path}"
    headers = {**_headers(), "Content-Type": "application/json"}
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"error": str(e)}


def _delete(path: str) -> dict:
    url = f"{SWING['endpoint']}{path}"
    req = urllib.request.Request(url, headers=_headers(), method="DELETE")
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"error": str(e)}


def _check_account(account: str) -> dict | None:
    if account != P9_ACCOUNT:
        return {"error": f"P9 路由违规：account='{account}'，仅支持 '{P9_ACCOUNT}'"}
    return None


@mcp.tool()
def get_account(account: str = "swing") -> str:
    """查账户资金状态。account 必须 = 'swing'（P9 单账号）"""
    err = _check_account(account)
    if err:
        return json.dumps(err, ensure_ascii=False)
    data = _request("/account")
    if "error" in data:
        return data["error"]
    return json.dumps({
        "account": account,
        "equity": f"${float(data['equity']):.2f}",
        "cash": f"${float(data['cash']):.2f}",
        "buying_power": f"${float(data['buying_power']):.2f}",
        "portfolio_value": f"${float(data['portfolio_value']):.2f}",
        "daytrade_count": data.get("daytrade_count", 0),
    }, ensure_ascii=False)


@mcp.tool()
def get_positions(account: str = "swing") -> str:
    """查当前持仓。account 必须 = 'swing'（P9 单账号）"""
    err = _check_account(account)
    if err:
        return json.dumps(err, ensure_ascii=False)
    data = _request("/positions")
    if isinstance(data, dict) and "error" in data:
        return data["error"]
    if not data:
        return f"{account}账号当前无持仓"
    positions = []
    for p in data:
        positions.append({
            "symbol": p["symbol"],
            "qty": p["qty"],
            "side": p["side"],
            "market_value": f"${float(p['market_value']):.2f}",
            "unrealized_pl": f"${float(p['unrealized_pl']):.2f}",
            "unrealized_plpc": f"{float(p['unrealized_plpc'])*100:.2f}%",
            "avg_entry": f"${float(p['avg_entry_price']):.2f}",
            "current_price": f"${float(p['current_price']):.2f}",
        })
    return json.dumps({"account": account, "positions": positions}, ensure_ascii=False)


@mcp.tool()
def get_orders(account: str = "swing", status: str = "open") -> str:
    """查订单。account 必须 = 'swing'；status: 'open'/'closed'/'all'"""
    err = _check_account(account)
    if err:
        return json.dumps(err, ensure_ascii=False)
    data = _request(f"/orders?status={status}&limit=20")
    if isinstance(data, dict) and "error" in data:
        return data["error"]
    if not data:
        return f"{account}账号无{status}订单"
    orders = []
    for o in data:
        orders.append({
            "symbol": o["symbol"],
            "side": o["side"],
            "type": o["type"],
            "qty": o["qty"],
            "status": o["status"],
            "submitted_at": o.get("submitted_at", "")[:10],
            "filled_avg_price": f"${float(o['filled_avg_price']):.2f}" if o.get("filled_avg_price") else "pending",
        })
    return json.dumps({"account": account, "status": status, "orders": orders}, ensure_ascii=False)


@mcp.tool()
def place_order(symbol: str, side: str, qty: int, account: str = "swing", reason: str = "",
                time_in_force: str = "day") -> str:
    """下单买入或卖出。side: 'buy'/'sell'；account 必须 = 'swing'；reason: 归因（写DB）；
    time_in_force: 'day'（盘中市价）/'opg'（盘后扫描用，next-open 成交）/'gtc'"""
    try:
        assert_p9_account(account)
    except ValueError as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
    if time_in_force not in ("day", "opg", "gtc"):
        return json.dumps({"error": f"invalid time_in_force: {time_in_force}"}, ensure_ascii=False)
    result = _post("/orders", {
        "symbol": symbol,
        "qty": str(qty),
        "side": side,
        "type": "market",
        "time_in_force": time_in_force,
    })
    if "error" in result:
        return json.dumps(result, ensure_ascii=False)

    order_id = result.get("id")
    filled_avg_price = result.get("filled_avg_price")
    db_path = "/home/cowork/cowork/trading/trading.db"
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT OR IGNORE INTO trades (symbol, side, order_id, entry_date, qty, fill_price, status)
            VALUES (?, ?, ?, date('now'), ?, ?, 'open')
            """,
            (symbol, side, order_id, qty, filled_avg_price),
        )
        cur.execute(
            """
            INSERT INTO decisions (date, symbol, signal, order_id, reasoning, strategy_version)
            VALUES (date('now'), ?, ?, ?, ?, 'theme_v1_cognitive_arbitrage')
            """,
            (symbol, side.upper(), order_id, reason),
        )
        conn.commit()
    finally:
        conn.close()

    return json.dumps({
        "symbol": symbol,
        "side": side,
        "qty": qty,
        "order_id": order_id,
        "fill_price": filled_avg_price,
        "status": "submitted",
    })


@mcp.tool()
def cancel_order(order_id: str, account: str = "swing") -> str:
    """取消未成交订单。account 必须 = 'swing'"""
    try:
        assert_p9_account(account)
    except ValueError as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
    result = _delete(f"/orders/{order_id}")
    if "message" in result or "code" in result or "error" in result:
        return f"Cancel failed: {result}"
    return f"Order {order_id} cancelled successfully."


if __name__ == "__main__":
    mcp.run()
