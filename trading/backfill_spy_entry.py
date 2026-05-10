#!/usr/bin/env python3
import sqlite3
from datetime import datetime, timedelta

import yfinance as yf


DB_PATH = "/home/cowork/cowork/trading/trading.db"
SECTOR_ETF = "GRID"


def fetch_close(symbol: str, scan_date: str) -> float:
    start_date = datetime.strptime(scan_date, "%Y-%m-%d").date()
    end_date = start_date + timedelta(days=1)
    history = yf.download(
        symbol,
        start=start_date.isoformat(),
        end=end_date.isoformat(),
        period="1d",
        progress=False,
        auto_adjust=False,
        threads=False,
    )
    if history.empty or "Close" not in history:
        raise ValueError(f"{symbol} returned no Close data for {scan_date}")

    close_series = history["Close"].dropna()
    if close_series.empty:
        raise ValueError(f"{symbol} Close is empty for {scan_date}")

    return float(close_series.iloc[-1])


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        """
        SELECT id, symbol, scan_date
        FROM scanner_picks
        WHERE status = 'open' AND spy_entry IS NULL
        ORDER BY id
        """
    ).fetchall()

    if not rows:
        print("No open rows need backfill.")
        conn.close()
        return

    for row_id, symbol, scan_date in rows:
        try:
            spy_entry = fetch_close("SPY", scan_date)
            sector_etf_entry = fetch_close(SECTOR_ETF, scan_date)
        except Exception as exc:  # noqa: BLE001
            print(
                f"SKIP id={row_id} symbol={symbol} scan_date={scan_date}: {exc}"
            )
            continue

        conn.execute(
            """
            UPDATE scanner_picks
            SET spy_entry = ?, sector_etf = ?, sector_etf_entry = ?
            WHERE id = ?
            """,
            (spy_entry, SECTOR_ETF, sector_etf_entry, row_id),
        )
        conn.commit()
        print(
            "UPDATED "
            f"id={row_id} symbol={symbol} scan_date={scan_date} "
            f"spy_entry={spy_entry} sector_etf={SECTOR_ETF} "
            f"sector_etf_entry={sector_etf_entry}"
        )

    conn.close()


if __name__ == "__main__":
    main()
