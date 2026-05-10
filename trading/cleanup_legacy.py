#!/usr/bin/env python3
"""P9 TIDE legacy 数据清理脚本。"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
import traceback
import urllib.error
import urllib.request
from pathlib import Path


ENV_PATH = Path("/home/cowork/cowork/config/api_keys.env")
DB_PATH = Path("/home/cowork/cowork/trading/trading.db")
SYMBOLS_TO_CLOSE = ("NVDA", "QQQ")
KEEP_STRATEGY = "theme_v1_cognitive_arbitrage"
DROP_TABLES = (
    "feature_snapshots",
    "accuracy_log",
    "results",
    "symbol_accuracy_log",
)


def load_env_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing env file: {path}")

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ[key.strip()] = value.strip()


def get_required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def normalize_endpoint(endpoint: str) -> str:
    base = endpoint.rstrip("/")
    if not base.endswith("/v2"):
        base = f"{base}/v2"
    return base


def alpaca_request(method: str, path: str, payload: dict | None = None) -> dict:
    endpoint = normalize_endpoint(get_required_env("ALPACA_SWING_ENDPOINT"))
    url = f"{endpoint}{path}"
    headers = {
        "APCA-API-KEY-ID": get_required_env("ALPACA_SWING_KEY"),
        "APCA-API-SECRET-KEY": get_required_env("ALPACA_SWING_SECRET"),
    }
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Alpaca {method} {url} failed: HTTP {exc.code} {exc.reason} | {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Alpaca {method} {url} failed: {exc}") from exc


def submit_close_order(symbol: str) -> None:
    position = alpaca_request("GET", f"/positions/{symbol}")
    qty = str(position.get("qty", "")).strip()
    if not qty:
        raise RuntimeError(f"{symbol} position missing qty: {position}")

    order = alpaca_request(
        "POST",
        "/orders",
        {
            "symbol": symbol,
            "qty": qty,
            "side": "sell",
            "type": "market",
            "time_in_force": "day",
        },
    )
    order_id = order.get("id")
    status = order.get("status")
    if not order_id or not status:
        raise RuntimeError(f"{symbol} sell order response missing id/status: {order}")
    print(f"{symbol} order_id={order_id} status={status}")


def cleanup_database(db_path: Path) -> tuple[int, int, list[str]]:
    if not db_path.exists():
        raise FileNotFoundError(f"Missing database: {db_path}")

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM trades WHERE status = 'legacy'")
        cur.execute(
            """
            DELETE FROM decisions
            WHERE strategy_version IS NULL
               OR strategy_version != ?
            """,
            (KEEP_STRATEGY,),
        )
        for table_name in DROP_TABLES:
            cur.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.commit()

        trades_count = cur.execute("SELECT COUNT(*) FROM trades").fetchone()[0]
        decisions_count = cur.execute("SELECT COUNT(*) FROM decisions").fetchone()[0]
        table_names = [
            row[0]
            for row in cur.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
            ).fetchall()
        ]
    return trades_count, decisions_count, table_names


def main() -> None:
    print("Step 1/3: loading env and submitting Alpaca sell orders...")
    load_env_file(ENV_PATH)
    order_errors: list[tuple[str, str]] = []
    for symbol in SYMBOLS_TO_CLOSE:
        try:
            submit_close_order(symbol)
        except Exception:
            error_text = traceback.format_exc()
            order_errors.append((symbol, error_text))
            print(f"{symbol} order submission failed:")
            print(error_text.rstrip())

    print("Step 2/3: cleaning trading.db legacy rows and tables...")
    trades_count, decisions_count, table_names = cleanup_database(DB_PATH)

    print("Step 3/3: final database state")
    print(f"trades_count={trades_count}")
    print(f"decisions_count={decisions_count}")
    print(f"tables={','.join(table_names)}")

    if order_errors:
        raise RuntimeError(
            "Alpaca order submission failed for: "
            + ", ".join(symbol for symbol, _ in order_errors)
        )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
