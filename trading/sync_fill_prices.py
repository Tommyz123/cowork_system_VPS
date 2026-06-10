#!/usr/bin/env python3
"""
开盘后 reconciliation 工具（2026-05-19 升级：从 price-sync → reconciler）。

职责：把 DB 状态同步到 Alpaca broker 真实状态——
  - Alpaca status=filled  → trades.status='filled' + scanner_picks.status='filled' / cohort='auto_filled' + 回填 fill_entry_price/fill_date/spy_fill_entry + outcome_tracking.tagged_price
  - Alpaca status=expired/canceled/rejected → trades.status=同名 + scanner_picks.status=同名（DB-broker 一致，下游持仓查询自动过滤）
  - Alpaca status=accepted/pending_new/new → 仍 pending，不动

跑完输出 reconciliation 简报（filled/expired/canceled/rejected/pending 计数）。

背景：2026-05-19 修复 ghost positions 反模式复发——cognitive_scanner 写入时改 status='submitted'/cohort='auto_pending'，
不再 hardcode 'filled'，由本脚本按 broker 实际状态 reconcile。
RCA: rca/2026_05_19_opg_expired_anti_pattern_recurrence.md

用法：python3 sync_fill_prices.py
"""
import json
import os
import sqlite3
import urllib.request
from pathlib import Path

DB_PATH = "/home/cowork/cowork/trading/trading.db"
ENV_PATH = "/home/cowork/cowork/config/api_keys.env"


def load_env():
    env = {}
    for line in Path(ENV_PATH).read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


def alpaca_get(env, path):
    endpoint = env.get("ALPACA_SWING_ENDPOINT", "https://paper-api.alpaca.markets/v2").rstrip("/v2").rstrip("/")
    url = f"{endpoint}/v2{path}"
    headers = {
        "APCA-API-KEY-ID": env.get("ALPACA_SWING_KEY", ""),
        "APCA-API-SECRET-KEY": env.get("ALPACA_SWING_SECRET", ""),
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def fetch_iwm_close(date_str: str):
    """拉指定日期 IWM 收盘价（yfinance）。失败返回 None。"""
    try:
        import yfinance as yf
        from datetime import datetime, timedelta
        d = datetime.strptime(date_str, "%Y-%m-%d")
        h = yf.Ticker("IWM").history(start=date_str, end=(d + timedelta(days=2)).strftime("%Y-%m-%d"))
        if not h.empty:
            return float(h["Close"].iloc[0])
    except Exception as e:
        print(f"  ⚠️ fetch IWM {date_str} 失败: {e}")
    return None


def main():
    env = load_env()
    conn = sqlite3.connect(DB_PATH)

    rows = conn.execute(
        "SELECT id, symbol, order_id FROM trades WHERE fill_price IS NULL AND status = 'open'"
    ).fetchall()

    if not rows:
        print("没有需要 reconcile 的记录。")
        conn.close()
        return

    counts = {"filled": 0, "expired": 0, "canceled": 0, "rejected": 0, "pending": 0, "error": 0}

    for trade_id, symbol, order_id in rows:
        if not order_id:
            print(f"[{symbol}] 无 order_id，跳过")
            continue
        try:
            order = alpaca_get(env, f"/orders/{order_id}")
            fill_price = order.get("filled_avg_price")
            status = order.get("status")
            filled_qty = float(order.get("filled_qty") or 0)
            filled_at = order.get("filled_at", "")[:10] if order.get("filled_at") else None
            print(f"[{symbol}] order_id={order_id[:8]} status={status} fill_price={fill_price} filled_qty={filled_qty:g}")

            # 2026-06-10 部分成交修复：OPG 单部分成交后终态是 expired/canceled 但 filled_qty>0，
            # 持仓真实存在。只看 status 会把真实持仓标成 expired（GNTX 97/132、WTS 9/10 漏记 3 周教训）。
            is_partial_fill = status in ("expired", "canceled") and filled_qty > 0 and fill_price

            if (status == "filled" or is_partial_fill) and fill_price:
                if is_partial_fill:
                    print(f"  ⚠️ 部分成交：订单终态 {status} 但实际成交 {filled_qty:g} 股 → 按 filled 处理")
                fill_price = float(fill_price)
                # 1. trades: status='filled' + fill_price + 实际成交股数（部分成交时 != 下单 qty）
                conn.execute(
                    "UPDATE trades SET fill_price = ?, filled_qty = ?, status = 'filled' WHERE id = ?",
                    (fill_price, filled_qty, trade_id),
                )
                # 2. scanner_picks: 'submitted'→'filled' / 'auto_pending'→'auto_filled' + 回填 fill 字段
                # （不覆盖 entry_price=signal price 保留语义，只更新 fill_entry_price/fill_date 执行端字段）
                conn.execute(
                    """UPDATE scanner_picks SET
                       status = 'filled',
                       cohort = CASE WHEN cohort = 'auto_pending' THEN 'auto_filled' ELSE cohort END,
                       fill_entry_price = ?, fill_date = COALESCE(fill_date, ?)
                       WHERE symbol = ?
                         AND (cohort IN ('auto_pending', 'auto_filled') OR status IN ('submitted', 'filled', 'filled_late'))
                         AND (fill_entry_price IS NULL OR fill_entry_price = 0)""",
                    (fill_price, filled_at, symbol),
                )
                # 3. spy_fill_entry（fill day IWM 价）— 让 execution_alpha 无 IWM bias
                if filled_at:
                    iwm_fill = fetch_iwm_close(filled_at)
                    if iwm_fill:
                        conn.execute(
                            """UPDATE scanner_picks SET spy_fill_entry = ?
                               WHERE symbol = ?
                                 AND (cohort IN ('auto_pending', 'auto_filled') OR status IN ('filled', 'filled_late'))
                                 AND spy_fill_entry IS NULL""",
                            (iwm_fill, symbol),
                        )
                        print(f"  → scanner_picks {symbol} spy_fill_entry={iwm_fill} (IWM {filled_at})")
                # 4. outcome_tracking（UPSERT：先 INSERT OR IGNORE 再 UPDATE
                # 2026-05-19 修复：之前只 UPDATE，导致 auto_filled / late_fill 新 cohort
                # 没在 outcome_tracking 留下行 → 6/14 30 天 outcome 查空。
                # 现在 reconcile 时自动建 row，next outcome cron 能算上）
                pick_row = conn.execute(
                    "SELECT id FROM scanner_picks WHERE symbol=? AND fill_date=? LIMIT 1",
                    (symbol, filled_at),
                ).fetchone()
                pick_id = pick_row[0] if pick_row else None
                conn.execute(
                    """INSERT OR IGNORE INTO outcome_tracking
                       (symbol, tagged_date, scanner_pick_id, tagged_price, last_updated)
                       VALUES (?, ?, ?, ?, datetime('now'))""",
                    (symbol, filled_at, pick_id, fill_price),
                )
                conn.execute(
                    "UPDATE outcome_tracking SET tagged_price = ?, last_updated = datetime('now') WHERE symbol = ? AND tagged_date = ?",
                    (fill_price, symbol, filled_at),
                )
                print(f"  ✅ filled: trades id={trade_id} fill={fill_price} / scanner_picks 'auto_pending'→'auto_filled' / outcome_tracking 更新")
                counts["filled"] += 1

            elif status in ("expired", "canceled", "rejected"):
                # reconcile: DB 同步成 broker 真实状态（核心：避免 ghost positions 反模式复发）
                conn.execute(
                    "UPDATE trades SET status = ? WHERE id = ?",
                    (status, trade_id),
                )
                conn.execute(
                    """UPDATE scanner_picks SET status = ?
                       WHERE symbol = ? AND cohort = 'auto_pending'""",
                    (status, symbol),
                )
                print(f"  ⚠️ {status}: trades + scanner_picks 标记 {status}（下游持仓查询自动过滤）")
                counts[status] += 1

            else:
                # accepted / pending_new / new / submitted → 仍 pending，不动 DB
                print(f"  ⏳ 仍 pending (status={status})，不动 DB")
                counts["pending"] += 1

        except Exception as e:
            print(f"[{symbol}] 查询失败: {e}")
            counts["error"] += 1

    conn.commit()
    conn.close()

    # reconciliation 简报
    total = sum(counts.values())
    print(f"\n=== Reconciliation 简报 ===")
    print(f"扫描 {total} 单：")
    print(f"  ✅ filled    : {counts['filled']}")
    print(f"  ⚠️  expired   : {counts['expired']}")
    print(f"  ⚠️  canceled  : {counts['canceled']}")
    print(f"  ⚠️  rejected  : {counts['rejected']}")
    print(f"  ⏳ pending   : {counts['pending']}")
    if counts.get("error"):
        print(f"  ❌ error     : {counts['error']}")
    print("Reconciliation 完成。")


if __name__ == "__main__":
    main()
