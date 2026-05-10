#!/usr/bin/env python3
import importlib.util
import json
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple
from urllib.parse import urlencode
from urllib.request import Request, urlopen

DB_PATH = Path("/home/cowork/cowork/trading/trading.db")
ENV_PATH = Path("/home/cowork/cowork/config/api_keys.env")
LOG_PATH = Path("/home/cowork/cowork/trading/tracker.log")


def log(message: str) -> None:
    timestamped = f"[{datetime.now().isoformat(timespec='seconds')}] {message}"
    print(timestamped)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(timestamped + "\n")


def load_env() -> Dict[str, str]:
    env: Dict[str, str] = {}
    with ENV_PATH.open(encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env[key.strip()] = value.strip()
    return env


def yfinance_available() -> bool:
    return importlib.util.find_spec("yfinance") is not None


def ensure_table_exists() -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='outcome_tracking'"
        ).fetchall()
        if not rows:
            raise RuntimeError("outcome_tracking table missing; run add_outcome_tracking.py first")
    finally:
        conn.close()


def parse_iso_date(value: str) -> datetime:
    text = (value or "").strip()
    if not text:
        raise ValueError("empty date")
    if "T" in text:
        return datetime.fromisoformat(text)
    if " " in text:
        try:
            return datetime.fromisoformat(text)
        except ValueError:
            pass
    return datetime.strptime(text[:10], "%Y-%m-%d")


def select_price_from_series(series: Dict[str, float], target_date: str) -> Optional[float]:
    target = parse_iso_date(target_date).date()
    eligible = []
    for key, price in series.items():
        try:
            day = parse_iso_date(key).date()
        except ValueError:
            continue
        if day >= target:
            eligible.append((day, price))
    if not eligible:
        return None
    eligible.sort(key=lambda item: item[0])
    return float(eligible[0][1])


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
    if hasattr(closes, "items"):
        return {
            idx.strftime("%Y-%m-%d"): float(value)
            for idx, value in closes.items()
            if value is not None
        }
    return {}


def fetch_fmp_series(symbol: str, start_date: str, end_date: str, api_key: str) -> Dict[str, float]:
    params = urlencode({"from": start_date, "to": end_date, "apikey": api_key})
    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}?{params}"
    request = Request(url, headers={"User-Agent": "cowork-price-tracker/1.0"})
    with urlopen(request, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))
    historical = payload.get("historical")
    if not isinstance(historical, list):
        message = payload.get("Error Message") or payload.get("message") or str(payload)
        raise RuntimeError(f"FMP response missing data: {message}")
    return {
        str(item.get("date")): float(item["close"])
        for item in historical
        if item.get("date") and item.get("close") is not None
    }


def fetch_price_for_date(
    symbol: str,
    target_date: str,
    env: Dict[str, str],
    prefer_yfinance: bool = True,
) -> Tuple[Optional[float], str]:
    start = (parse_iso_date(target_date) - timedelta(days=5)).date().isoformat()
    end = (parse_iso_date(target_date) + timedelta(days=8)).date().isoformat()
    fmp_key = env.get("FMP_API_KEY")

    if prefer_yfinance and yfinance_available():
        try:
            series = fetch_yfinance_series(symbol, start, end)
            price = select_price_from_series(series, target_date)
            if price is not None:
                return price, "yfinance"
            log(f"{symbol} yfinance returned no matching data for {target_date}")
        except Exception as exc:
            log(f"{symbol} yfinance failed for {target_date}: {exc}")

    if fmp_key:
        try:
            series = fetch_fmp_series(symbol, start, end, fmp_key)
            price = select_price_from_series(series, target_date)
            if price is not None:
                return price, "fmp"
            log(f"{symbol} FMP returned no matching data for {target_date}")
        except Exception as exc:
            log(f"{symbol} FMP failed for {target_date}: {exc}")

    if not prefer_yfinance and yfinance_available():
        try:
            series = fetch_yfinance_series(symbol, start, end)
            price = select_price_from_series(series, target_date)
            if price is not None:
                return price, "yfinance"
            log(f"{symbol} yfinance fallback returned no matching data for {target_date}")
        except Exception as exc:
            log(f"{symbol} yfinance fallback failed for {target_date}: {exc}")

    return None, "none"


def initialize_rows(env: Dict[str, str]) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        pending_init = conn.execute(
            """
            SELECT sp.id, sp.symbol, sp.scan_date, sp.entry_price
            FROM scanner_picks sp
            LEFT JOIN outcome_tracking ot
              ON ot.scanner_pick_id = sp.id
             OR (ot.symbol = sp.symbol AND ot.tagged_date = sp.scan_date)
            WHERE sp.status IN ('open', 'closed_watching')
              AND COALESCE(TRIM(sp.symbol), '') != ''
              AND COALESCE(TRIM(sp.scan_date), '') != ''
              AND ot.id IS NULL
            ORDER BY sp.scan_date, sp.id
            """
        ).fetchall()

        log(f"initializing {len(pending_init)} scanner_picks rows")
        for row in pending_init:
            symbol = row["symbol"].strip().upper()
            tagged_date = row["scan_date"][:10]
            tagged_price = row["entry_price"]
            notes = []
            if tagged_price is None:
                fetched_price, source = fetch_price_for_date(symbol, tagged_date, env, prefer_yfinance=True)
                if fetched_price is None:
                    log(f"skip init {symbol} {tagged_date}: no tagged_price available")
                    continue
                tagged_price = fetched_price
                notes.append(f"tagged_price sourced from {source}")

            conn.execute(
                """
                INSERT OR IGNORE INTO outcome_tracking (
                    symbol, tagged_date, scanner_pick_id, tagged_price, notes, last_updated
                ) VALUES (?, ?, ?, ?, ?, datetime('now'))
                """,
                (
                    symbol,
                    tagged_date,
                    row["id"],
                    float(tagged_price),
                    "; ".join(notes) if notes else None,
                ),
            )
            log(f"initialized {symbol} {tagged_date} tagged_price={tagged_price}")
        conn.commit()
    finally:
        conn.close()


def compute_return(tagged_price: Optional[float], later_price: Optional[float]) -> Optional[float]:
    if tagged_price in (None, 0) or later_price is None:
        return None
    return ((float(later_price) - float(tagged_price)) / float(tagged_price)) * 100.0


def update_pending_rows(env: Dict[str, str]) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT *
            FROM outcome_tracking
            WHERE signal_verdict = 'pending'
            ORDER BY tagged_date, id
            """
        ).fetchall()
        log(f"updating {len(rows)} pending outcome rows")

        for row in rows:
            symbol = row["symbol"].strip().upper()
            tagged_date = row["tagged_date"][:10]
            tagged_price = row["tagged_price"]
            if tagged_price in (None, 0):
                log(f"skip update {symbol} {tagged_date}: missing tagged_price")
                continue

            today = datetime.now(UTC).date()
            update_fields = {}
            notes = row["notes"] or ""

            for days, price_col, return_col in (
                (30, "price_30d", "return_30d"),
                (60, "price_60d", "return_60d"),
                (90, "price_90d", "return_90d"),
            ):
                if row[price_col] is not None:
                    continue
                target = (parse_iso_date(tagged_date).date() + timedelta(days=days)).isoformat()
                if parse_iso_date(target).date() > today:
                    continue
                price, source = fetch_price_for_date(symbol, target, env, prefer_yfinance=True)
                if price is None:
                    log(f"skip {symbol} {tagged_date} {days}d: no price data")
                    continue
                update_fields[price_col] = float(price)
                update_fields[return_col] = compute_return(tagged_price, price)
                note_fragment = f"{days}d={source}"
                if note_fragment not in notes:
                    notes = f"{notes}; {note_fragment}".strip("; ").strip()
                log(
                    f"updated {symbol} {tagged_date} {days}d price={price} return={update_fields[return_col]:.2f}%"
                )

            if not update_fields:
                continue

            verdict = "closed" if update_fields.get("price_90d") is not None or row["price_90d"] is not None else "pending"
            update_fields["signal_verdict"] = verdict
            update_fields["notes"] = notes or None

            conn.execute(
                """
                UPDATE outcome_tracking
                SET price_30d = COALESCE(?, price_30d),
                    price_60d = COALESCE(?, price_60d),
                    price_90d = COALESCE(?, price_90d),
                    return_30d = COALESCE(?, return_30d),
                    return_60d = COALESCE(?, return_60d),
                    return_90d = COALESCE(?, return_90d),
                    signal_verdict = ?,
                    notes = ?,
                    last_updated = datetime('now')
                WHERE id = ?
                """,
                (
                    update_fields.get("price_30d"),
                    update_fields.get("price_60d"),
                    update_fields.get("price_90d"),
                    update_fields.get("return_30d"),
                    update_fields.get("return_60d"),
                    update_fields.get("return_90d"),
                    update_fields["signal_verdict"],
                    update_fields["notes"],
                    row["id"],
                ),
            )
        conn.commit()
    finally:
        conn.close()


def main() -> None:
    env = load_env()
    log(
        "startup: "
        f"yfinance_available={yfinance_available()} "
        f"fmp_key_present={bool(env.get('FMP_API_KEY'))}"
    )
    ensure_table_exists()
    initialize_rows(env)
    update_pending_rows(env)
    log("price tracker complete")


if __name__ == "__main__":
    main()
