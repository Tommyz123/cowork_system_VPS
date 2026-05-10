"""
Mac mini M4 价格监控 - Google Shopping via SerpAPI
低于目标价才发Email通知
"""
import sqlite3
import os
import sys
from datetime import date

DB_PATH = os.path.join(os.path.dirname(__file__), "mac_prices.db")
TARGET_PRICE = 410  # 低于此价格才发通知

ENV_PATH = "/home/cowork/cowork/config/api_keys.env"


def load_env():
    env = {}
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS mac_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_date TEXT NOT NULL,
            store TEXT NOT NULL,
            price REAL,
            link TEXT
        )
    """)
    conn.commit()
    conn.close()


def search_prices(api_keys: list) -> list:
    from serpapi import GoogleSearch
    params = {
        "engine": "google_shopping",
        "q": "Apple Mac mini M4 16GB 256GB",
        "gl": "us",
        "hl": "en",
        "currency": "USD",
    }
    for i, key in enumerate(api_keys):
        try:
            params["api_key"] = key
            results = GoogleSearch(params).get_dict()
            if "error" in results:
                print(f"KEY{i+1} error: {results['error']}, trying next...", file=sys.stderr)
                continue
            items = results.get("shopping_results", [])
            prices = []
            for item in items[:10]:
                price_str = str(item.get("price", "")).replace("$", "").replace(",", "").strip()
                try:
                    price = float(price_str)
                    if 300 < price < 700:
                        prices.append({
                            "store": item.get("source", "Unknown"),
                            "price": price,
                            "link": item.get("product_link", ""),
                        })
                except ValueError:
                    continue
            print(f"Used KEY{i+1}", file=sys.stderr)
            return sorted(prices, key=lambda x: x["price"])
        except Exception as e:
            print(f"KEY{i+1} failed: {e}, trying next...", file=sys.stderr)
    return []


def get_all_time_low() -> float | None:
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT MIN(price) FROM mac_prices WHERE price IS NOT NULL").fetchone()
    conn.close()
    return row[0] if row else None


def save_results(results: list):
    today = date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    for r in results:
        conn.execute(
            "INSERT INTO mac_prices (record_date, store, price, link) VALUES (?,?,?,?)",
            (today, r["store"], r["price"], r["link"])
        )
    conn.commit()
    conn.close()


def main():
    init_db()
    env = load_env()
    api_keys = [k for k in [env.get("SERPAPI_KEY"), env.get("SERPAPI_KEY2")] if k]

    prices = search_prices(api_keys)
    if not prices:
        print("NO_RESULTS", file=sys.stderr)
        sys.exit(0)

    save_results(prices)

    atl = get_all_time_low()
    cheapest = prices[0]
    today = date.today().isoformat()

    # 只在低于目标价时输出报告
    if cheapest["price"] >= TARGET_PRICE:
        print(f"SILENT: cheapest=${cheapest['price']:.0f}, above target=${TARGET_PRICE}")
        sys.exit(0)

    is_new_low = atl is not None and cheapest["price"] < atl
    low_tag = " 🔥 历史新低！" if is_new_low else ""

    rows = ""
    for r in prices[:5]:
        tag = low_tag if r == cheapest else ""
        store_name = r['store'] + tag
        rows += f'<tr><td style="padding:6px 12px;font-weight:bold;">{store_name}</td><td style="padding:6px 12px;color:#d32f2f;font-size:1.1em;">${r["price"]:.0f}</td><td style="padding:6px 12px;"><a href="{r["link"]}">查看商品</a></td></tr>\n'

    new_low_banner = '<p style="color:#e65100;font-weight:bold;">🎯 这是有史以来最低价，强烈建议考虑入手！</p>' if is_new_low else ""

    html = f"""<h2>🖥️ Mac mini M4 低价提醒 | {today}</h2>
<hr>
<p>⚡ 发现低价，低于目标价 <strong>${TARGET_PRICE}</strong>！</p>
<table border="0" cellspacing="0" cellpadding="0" style="border-collapse:collapse;">
<tr style="background:#f5f5f5;"><th style="padding:6px 12px;text-align:left;">店铺</th><th style="padding:6px 12px;text-align:left;">价格</th><th style="padding:6px 12px;text-align:left;">链接</th></tr>
{rows}</table>
{new_low_banner}"""

    print(html)


if __name__ == "__main__":
    main()
