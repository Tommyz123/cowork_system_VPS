"""Build Discord report from flight_monitor.py JSON output."""
import sys
import json

data = json.load(sys.stdin)
results = data["results"]
yesterday = data["yesterday_prices"]
today = data["today"]


def fmt_price(price, yp):
    if price is None:
        return "N/A"
    if yp:
        diff = price - yp
        arrow = "↑" if diff > 0 else ("↓" if diff < 0 else "→")
        sign = "+" if diff > 0 else ""
        return f"${price} {arrow}{sign}${diff}"
    return f"${price}"


lines = [f"✈️ **机票日报 {today}**\n"]

lines.append("🛋️ **超级经济舱（转机）：**")
for r in [x for x in results if x["cabin"] == "2"]:
    if r["price"] is None:
        continue
    yp = yesterday.get(r["label"])
    p = fmt_price(r["price"], yp)
    airlines = r.get("airlines", "?")
    dep = r.get("dep_time", "")
    arr = r.get("arr_time", "")
    dur = r.get("duration", "")
    best_date = r.get("best_date", "")
    time_str = f"{dep}→{arr} ({dur})" if dep and arr else ""
    link = r.get("search_url", "")
    lines.append(f"• **{r['label']}**: {p} ({airlines})")
    if time_str:
        lines.append(f"  ⏰ {time_str} | 出发:{best_date}")
    if link:
        lines.append(f"  🔗 [查看购买]({link})")

lines.append("")
lines.append("💺 **经济舱（直飞）：**")
for r in [x for x in results if x["cabin"] == "1"]:
    if r["price"] is None:
        continue
    yp = yesterday.get(r["label"])
    p = fmt_price(r["price"], yp)
    airlines = r.get("airlines", "?")
    dep = r.get("dep_time", "")
    arr = r.get("arr_time", "")
    dur = r.get("duration", "")
    best_date = r.get("best_date", "")
    time_str = f"{dep}→{arr} ({dur})" if dep and arr else ""
    link = r.get("search_url", "")
    lines.append(f"• **{r['label']}**: {p} ({airlines})")
    if time_str:
        lines.append(f"  ⏰ {time_str} | 出发:{best_date}")
    if link:
        lines.append(f"  🔗 [查看购买]({link})")

print("\n".join(lines))
