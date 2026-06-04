#!/usr/bin/env python3
"""平仓后追踪：记录已平仓票在平仓日之后的走势，验证 P9 的卖出时机。

只读价格 + 写 scanner_picks 的 post_exit_* 字段，不碰任何选股/下单逻辑。
平仓日期来源：trades.exit_date（权威）；scanner_picks 有平仓状态但 trades 无 exit_date 的，
跳过并记日志，等历史平仓日期补齐后再追踪。
"""
import importlib.util
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from tide_utils import load_env, run_with_alert

DB_PATH = Path("/home/cowork/cowork/trading/trading.db")
LOG_PATH = Path("/home/cowork/cowork/trading/post_exit_tracker.log")
TRACK_DAYS = 90  # 平仓后追踪窗口（天）


def log(message: str) -> None:
    timestamped = f"[{datetime.now().isoformat(timespec='seconds')}] {message}"
    print(timestamped)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(timestamped + "\n")


def yfinance_available() -> bool:
    return importlib.util.find_spec("yfinance") is not None


def parse_iso_date(value: str) -> datetime:
    text = (value or "").strip()
    if not text:
        raise ValueError("empty date")
    if "T" in text:
        return datetime.fromisoformat(text)
    return datetime.strptime(text, "%Y-%m-%d")


def fetch_yfinance_series(symbol: str, start_date: str, end_date: str) -> Dict[str, float]:
    import yfinance as yf

    history = yf.download(
        symbol,
        start=start_date,
        end=end_date,
        auto_adjust=False,
        progress=False,
        interval="1d",
        threads=False,
    )
    if history is None or history.empty:
        return {}
    closes = history["Close"]
    # 单 ticker 时 yfinance 返回 DataFrame（列名=ticker），取第一列还原成 Series
    if hasattr(closes, "columns"):
        closes = closes.iloc[:, 0]
    return {
        idx.strftime("%Y-%m-%d"): float(value)
        for idx, value in closes.items()
        if value is not None
    }


def fetch_fmp_series(symbol: str, start_date: str, end_date: str, api_key: str) -> Dict[str, float]:
    params = urlencode({"from": start_date, "to": end_date, "apikey": api_key})
    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}?{params}"
    request = Request(url, headers={"User-Agent": "cowork-post-exit-tracker/1.0"})
    with urlopen(request, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))
    historical = payload.get("historical")
    if not isinstance(historical, list):
        return {}
    return {
        str(item.get("date")): float(item["close"])
        for item in historical
        if item.get("date") and item.get("close") is not None
    }


def fetch_series(symbol: str, start: str, end: str, env: Dict[str, str]) -> Dict[str, float]:
    """拉 [start, end] 区间日收盘价；yfinance 优先，FMP 兜底。"""
    if yfinance_available():
        try:
            series = fetch_yfinance_series(symbol, start, end)
            if series:
                return series
            log(f"{symbol} yfinance returned no data for {start}~{end}")
        except Exception as exc:
            log(f"{symbol} yfinance failed for {start}~{end}: {exc}")
    fmp_key = env.get("FMP_API_KEY")
    if fmp_key:
        try:
            series = fetch_fmp_series(symbol, start, end, fmp_key)
            if series:
                return series
            log(f"{symbol} FMP returned no data for {start}~{end}")
        except Exception as exc:
            log(f"{symbol} FMP failed for {start}~{end}: {exc}")
    return {}


def get_exit_dates() -> Dict[str, str]:
    """从 trades 表取每只票最近一次的平仓日期（symbol -> exit_date）。"""
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(
            """
            SELECT symbol, exit_date
            FROM trades
            WHERE status IN ('closed', 'exited')
              AND COALESCE(TRIM(exit_date), '') != ''
            ORDER BY exit_date
            """
        ).fetchall()
    finally:
        conn.close()
    exit_dates: Dict[str, str] = {}
    for symbol, exit_date in rows:
        exit_dates[symbol.strip().upper()] = exit_date[:10]
    return exit_dates


def get_closed_picks() -> List[Tuple[int, str, Optional[float]]]:
    """scanner_picks 里平仓状态的票 (id, symbol, exit_price)。"""
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(
            """
            SELECT id, symbol, exit_price
            FROM scanner_picks
            WHERE status IN ('closed', 'exited')
              AND COALESCE(TRIM(symbol), '') != ''
            ORDER BY id
            """
        ).fetchall()
    finally:
        conn.close()
    return [(r[0], r[1].strip().upper(), r[2]) for r in rows]


def track(env: Dict[str, str]) -> None:
    exit_dates = get_exit_dates()
    picks = get_closed_picks()
    log(f"{len(picks)} closed picks; {len(exit_dates)} have exit_date in trades")

    conn = sqlite3.connect(DB_PATH)
    try:
        for pick_id, symbol, exit_price in picks:
            exit_date = exit_dates.get(symbol)
            if not exit_date:
                log(f"skip {symbol} (pick {pick_id}): no exit_date in trades, awaiting backfill")
                continue

            start = parse_iso_date(exit_date).date().isoformat()
            end = (parse_iso_date(exit_date) + timedelta(days=TRACK_DAYS + 5)).date().isoformat()
            series = fetch_series(symbol, start, end, env)
            # 只保留平仓日之后的价格点
            post = {d: p for d, p in series.items() if d > exit_date}
            if not post:
                log(f"{symbol}: no post-exit prices yet (exit {exit_date})")
                continue

            peak = max(post.values())
            ordered = sorted(post.items())
            last_date, last_price = ordered[-1]
            ref = exit_price if exit_price not in (None, 0) else None
            ret_3m = None
            if ref is not None:
                ret_3m = round((last_price - ref) / ref * 100.0, 2)

            conn.execute(
                """
                UPDATE scanner_picks
                SET post_exit_prices = ?,
                    post_exit_peak = ?,
                    post_exit_3m_return = ?
                WHERE id = ?
                """,
                (json.dumps(post, sort_keys=True), round(peak, 4), ret_3m, pick_id),
            )
            log(
                f"{symbol}: exit={exit_date} peak={peak:.2f} "
                f"last({last_date})={last_price:.2f} 3m_return={ret_3m}% pts={len(post)}"
            )
        conn.commit()
    finally:
        conn.close()


def main() -> None:
    env = load_env()
    log(f"startup: yfinance_available={yfinance_available()} fmp_key={bool(env.get('FMP_API_KEY'))}")
    track(env)
    log("post-exit tracker complete")


if __name__ == "__main__":
    run_with_alert("post_exit_tracker", main)
