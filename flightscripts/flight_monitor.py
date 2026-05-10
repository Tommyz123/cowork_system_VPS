"""
Flight price monitor - queries SerpAPI for NYC→HK/GZ/SZ routes,
stores history in SQLite, and prints formatted data for claude analysis.
"""
import os
import sys
import json
import sqlite3
from datetime import date, datetime, timedelta
from serpapi import GoogleSearch

_SERPAPI_KEYS = [k for k in [
    os.environ.get("SERPAPI_KEY", ""),
    os.environ.get("SERPAPI_KEY_FALLBACK", ""),
] if k]
DB_PATH = "/home/cowork/cowork/flightscripts/flight_prices.db"

ROUTES = [
    # (origin, dest, cabin_code, cabin_label, stops_filter)
    # SerpAPI: 1=Economy, 2=PremiumEconomy, 3=Business, 4=First
    ("JFK", "HKG", "2", "超级经济转机", "0"),
    ("JFK", "CAN", "2", "超级经济转机", "0"),
    ("JFK", "SZX", "2", "超级经济转机", "0"),
    ("EWR", "HKG", "2", "超级经济转机", "0"),
    ("EWR", "CAN", "2", "超级经济转机", "0"),
    ("EWR", "SZX", "2", "超级经济转机", "0"),
    ("JFK", "HKG", "1", "经济直飞", "1"),
    ("JFK", "CAN", "1", "经济直飞", "1"),
]

# 9月采样日期（每5天取一个）
SAMPLE_DATES = [
    "2026-09-01", "2026-09-06", "2026-09-11",
    "2026-09-16", "2026-09-21", "2026-09-26",
]


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_date TEXT NOT NULL,
            label TEXT NOT NULL,
            price INTEGER,
            airlines TEXT,
            best_outbound TEXT
        )
    """)
    conn.commit()
    conn.close()


def get_yesterday_price(label: str) -> int | None:
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT price FROM prices WHERE label=? AND price IS NOT NULL ORDER BY record_date DESC LIMIT 1 OFFSET 1",
        (label,)
    ).fetchone()
    conn.close()
    return row[0] if row else None


def get_week_history(label: str) -> list:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT record_date, price FROM prices WHERE label=? AND price IS NOT NULL ORDER BY record_date DESC LIMIT 7",
        (label,)
    ).fetchall()
    conn.close()
    return [{"date": r[0], "price": r[1]} for r in rows]


def save_results(results: list):
    today = date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    for r in results:
        conn.execute(
            "INSERT INTO prices (record_date, label, price, airlines, best_outbound) VALUES (?,?,?,?,?)",
            (today, r["label"], r["price"], r.get("airlines"), r.get("best_date"))
        )
    conn.commit()
    conn.close()


MAX_DURATION_MINUTES = 1440  # 过滤超过24小时的绕路航班


def query_route(origin, dest, cabin_code, stops_filter, outbound_date):
    return_date = (datetime.strptime(outbound_date, "%Y-%m-%d") + timedelta(days=30)).strftime("%Y-%m-%d")
    params = {
        "engine": "google_flights",
        "departure_id": origin,
        "arrival_id": dest,
        "outbound_date": outbound_date,
        "return_date": return_date,
        "travel_class": cabin_code,
        "currency": "USD",
        "hl": "en",
    }
    if stops_filter == "1":
        params["stops"] = "1"

    data = None
    for api_key in _SERPAPI_KEYS:
        try:
            params["api_key"] = api_key
            result = GoogleSearch(params).get_dict()
            if "error" in result:
                continue  # 配额耗尽或其他错误，尝试下一个key
            data = result
            break
        except Exception:
            continue

    if data is None:
        return None

    # 获取 Google Flights 真实搜索链接
    search_url = data.get("search_metadata", {}).get("google_flights_url", "")

    flights = data.get("best_flights", []) + data.get("other_flights", [])
    if stops_filter == "1":
        flights = [f for f in flights if len(f.get("flights", [])) == 1]

    # 过滤超长绕路（>24小时）
    flights = [f for f in flights if f.get("total_duration", 0) <= MAX_DURATION_MINUTES]

    if not flights:
        return None

    cheapest = min(flights, key=lambda x: x.get("price", 999999))
    legs = cheapest.get("flights", [])
    airlines = "/".join(set(fl.get("airline", "?") for fl in legs))

    # 提取出发和到达时间
    dep_time = legs[0].get("departure_airport", {}).get("time", "") if legs else ""
    arr_time = legs[-1].get("arrival_airport", {}).get("time", "") if legs else ""
    duration_h = cheapest.get("total_duration", 0) // 60
    duration_m = cheapest.get("total_duration", 0) % 60

    return {
        "price": cheapest.get("price"),
        "airlines": airlines,
        "search_url": search_url,
        "dep_time": dep_time,
        "arr_time": arr_time,
        "duration": f"{duration_h}h{duration_m}m",
    }


def main():
    init_db()
    today = date.today().isoformat()
    days_to_sep = (date(2026, 9, 1) - date.today()).days

    results = []
    for origin, dest, cabin_code, cabin_label, stops_filter in ROUTES:
        label = f"{origin}→{dest} {cabin_label}"
        best = None
        best_date = None

        for d in SAMPLE_DATES:
            r = query_route(origin, dest, cabin_code, stops_filter, d)
            if r and r.get("price") is not None and (best is None or r["price"] < best["price"]):
                best = r
                best_date = d

        results.append({
            "label": label,
            "origin": origin,
            "dest": dest,
            "cabin": cabin_code,
            "price": best["price"] if best else None,
            "airlines": best["airlines"] if best else None,
            "best_date": best_date,
            "search_url": best["search_url"] if best else "",
            "dep_time": best.get("dep_time", "") if best else "",
            "arr_time": best.get("arr_time", "") if best else "",
            "duration": best.get("duration", "") if best else "",
        })

    save_results(results)

    # 构建给 claude 分析的数据摘要
    history_lines = []
    for r in results:
        if r["price"] is None:
            continue
        hist = get_week_history(r["label"])
        hist_str = "、".join(f"{h['date']}=${h['price']}" for h in reversed(hist[:5]))
        yp = get_yesterday_price(r["label"])
        diff_str = f"(比昨天{'+'if r['price']>(yp or r['price']) else ''}{r['price']-(yp or r['price'])})" if yp else ""
        history_lines.append(f"- {r['label']}: 今日${r['price']}{diff_str} 历史:{hist_str or '首次记录'}")

    prompt_data = f"""今天是{today}，距离计划出发（2026年9月）还有约{days_to_sep}天。

各航线今日价格及历史记录：
{chr(10).join(history_lines)}

请简洁分析走势，给出"现在买还是等"的建议（2-3句，中文）。"""

    # 输出 JSON 供 shell 使用
    output = {
        "today": today,
        "days_to_sep": days_to_sep,
        "results": results,
        "yesterday_prices": {r["label"]: get_yesterday_price(r["label"]) for r in results},
        "prompt_for_claude": prompt_data,
    }
    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
