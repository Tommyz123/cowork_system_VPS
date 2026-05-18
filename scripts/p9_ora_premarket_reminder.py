#!/usr/bin/env python3
"""
P9 ORA pre-market 提醒（一次性 cron）
触发：2026-05-18 09:00 EDT（盘前 30 分钟）
功能：抓 ORA pre-market 报价，Discord 推送提醒主公看 case study + 决定 trim 百分比
触发后自删 cron 条目，防重复触发。

⚠️ Token 读取必须用 tide_utils.load_env（按 feedback_tide_utils_load_env 规则）
"""
import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime

sys.path.insert(0, "/home/cowork/cowork/trading")
from tide_utils import load_env

NOW = datetime.now().strftime("%Y-%m-%d %H:%M EDT")
TODAY = datetime.now().strftime("%Y-%m-%d")

# 只在 2026-05-18 当天触发
if TODAY != "2026-05-18":
    print(f"今天 {TODAY} 不是触发日，跳过")
    sys.exit(0)


def fetch_premarket_price(symbol: str):
    """yfinance 抓 pre-market 报价（如果时间不在 pre-market 窗口则返回最近收盘价）"""
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        info = ticker.info
        pre = info.get("preMarketPrice") or info.get("regularMarketPrice")
        prev_close = info.get("regularMarketPreviousClose") or info.get("previousClose")
        return pre, prev_close
    except Exception as e:
        return None, str(e)


def send_discord(token: str, channel_id: str, content: str) -> bool:
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json",
    }
    data = json.dumps({"content": content}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"Discord OK: {resp.status}")
            return True
    except Exception as e:
        print(f"Discord error: {e}")
        return False


def remove_self_from_crontab():
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        if result.returncode != 0:
            return
        lines = result.stdout.split("\n")
        filtered = [l for l in lines if "p9_ora_premarket_reminder.py" not in l]
        new_crontab = "\n".join(filtered)
        subprocess.run(["crontab", "-"], input=new_crontab, text=True)
        print("已从 crontab 删除自己")
    except Exception as e:
        print(f"crontab 清理失败（不影响功能）: {e}")


def main():
    env = load_env()
    token = env.get("DISCORD_BOT_TOKEN")
    channel_id = env.get("DISCORD_CHANNEL_ID")
    if not token or not channel_id:
        print("ERROR: 缺少 Discord token 或 channel_id")
        sys.exit(1)

    pre, prev = fetch_premarket_price("ORA")
    if isinstance(pre, (int, float)) and isinstance(prev, (int, float)):
        change_pct = (pre - prev) / prev * 100
        price_line = f"💰 **ORA 当前**: ${pre:.2f}（前收 ${prev:.2f}，{'+' if change_pct >= 0 else ''}{change_pct:.2f}%）"
    else:
        price_line = f"💰 **ORA 报价获取异常**（pre={pre}, prev={prev}），请手工查 Yahoo Finance"

    msg = f"""☕ **主公早安 — P9 ORA pre-market 提醒** ({NOW})

{price_line}

📌 **昨晚分析结论**（详见 `trading/case_studies/ORA_2026_05_18.md`）:
- ORA 是 14 只里 alpha 第一（+9.51% vs IWM, +6.3% absolute）
- Red team 揭示 5 个结构性 bear 角度（地热衰减资本化掩盖 / Puna 单一资产风险 / Kenya FX / 储能 merchant 估值 mismatch / IRA 政策回滚）
- **推荐方向：trim 30-60% 仓位**（具体百分比看主公风险偏好）

📊 **决策三选项**：
- **A. trim 1/3**（保守，留 67% 接 bull case 上行）
- **B. trim 1/2**（平衡，对冲 bear/bull 不对称）
- **C. trim 2/3**（激进，重锁 alpha，仅留 33% 子弹）

⚠️ **如有意外利空**（pre-market 跌幅 >2% / 隔夜公告）→ 考虑直接全清

📍 **Hidden Risk 监测信号**（继续 hold 期间要盯）：
1. 地热 resource degradation - 监测下季 10-K capex 拆分
2. 肯尼亚 Olkaria 应收 + KES 汇率
3. IRA 地热 PTC 政策动向

主公看完 pre-market 决定 A/B/C 或自行调整，告诉我具体百分比我执行。
"""

    success = send_discord(token, channel_id, msg)
    if success:
        remove_self_from_crontab()
        log_line = f"[{NOW}] CRON[P9] | ora_premarket_reminder | ✅ | 提醒已发送+自删\n"
        with open("/home/cowork/cowork/ops_log.md", "a", encoding="utf-8") as f:
            f.write(log_line)


if __name__ == "__main__":
    main()
