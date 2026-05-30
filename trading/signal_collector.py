#!/usr/bin/env python3
"""
TIDE系统 - 每日信号积累器（每天12PM EDT自动跑）
抓取候选股票的 FMP 新闻全文和 SEC 8-K，写入 trading.db signals 表。
为 theme_discovery.py 提供原料（积累60-90天后触发主题发现）。
默认仅抓今天；--backfill N 抓取最近 N 天。
"""
import argparse
import json
import re
import sqlite3
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

import requests

from transcript_fetcher import fetch_news_finnhub

ENV_PATH = Path("/home/cowork/cowork/config/api_keys.env")
DB_PATH = Path("/home/cowork/cowork/trading/trading.db")
SCREEN_OUTPUT_PATH = Path("/home/cowork/cowork/trading/screener_output.json")
SYSTEM_LOG_PATH = Path("/home/cowork/cowork/trading/system_log.md")
SEC_URL = "https://efts.sec.gov/LATEST/search-index"
CIK_MAP_PATH = Path("/home/cowork/cowork/trading/cik_map.json")
CIK_MAP_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_USER_AGENT = "cowork-signal-collector/1.0 (zhitao776@gmail.com)"

# 8-K Item 类型 → 信号质量。一份 8-K 可含多个 Item，取最高档。
ITEM_HIGH = {"1.01", "8.01", "1.03", "2.01"}  # 重大合同/重大事件/破产/资产收购
ITEM_MEDIUM = {"5.02", "7.01", "2.02", "5.07"}  # 高管变动/Reg FD/财报/股东投票


def load_env():
    env = {}
    with ENV_PATH.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def load_cik_map():
    """symbol→CIK 映射。本地缓存当天有效；过期或缺失则从 SEC 拉取。
    SEC company_tickers.json 结构: {"0": {"cik_str": 320193, "ticker": "AAPL", ...}, ...}
    """
    if CIK_MAP_PATH.exists():
        age_days = (datetime.now() - datetime.fromtimestamp(CIK_MAP_PATH.stat().st_mtime)).days
        if age_days < 1:
            try:
                return {k: int(v) for k, v in json.loads(CIK_MAP_PATH.read_text()).items()}
            except Exception:
                pass
    try:
        r = requests.get(CIK_MAP_URL, headers={"User-Agent": SEC_USER_AGENT}, timeout=20)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"[cik_map] 拉取失败: {e}，尝试用旧缓存")
        if CIK_MAP_PATH.exists():
            try:
                return {k: int(v) for k, v in json.loads(CIK_MAP_PATH.read_text()).items()}
            except Exception:
                return {}
        return {}
    mapping = {}
    for row in data.values():
        ticker = str(row.get("ticker", "")).strip().upper()
        cik = row.get("cik_str")
        if ticker and cik is not None:
            mapping[ticker] = int(cik)
    try:
        CIK_MAP_PATH.write_text(json.dumps(mapping))
    except Exception:
        pass
    return mapping


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            date TEXT,
            signal_type TEXT,
            headline TEXT,
            full_text TEXT,
            source TEXT,
            created_at TEXT,
            UNIQUE(symbol, date, headline)
        )
        """
    )
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_signals_unique ON signals(symbol, date, headline)"
    )
    ensure_signal_quality_column(conn)
    conn.commit()
    return conn


def ensure_signal_quality_column(conn):
    columns = [row[1] for row in conn.execute("PRAGMA table_info(signals)").fetchall()]
    if "signal_quality" not in columns:
        conn.execute("ALTER TABLE signals ADD COLUMN signal_quality TEXT")


def load_open_symbols_from_db(conn):
    try:
        rows = conn.execute(
            "SELECT DISTINCT symbol FROM scanner_picks WHERE status IN ('filled', 'filled_late') AND symbol IS NOT NULL AND symbol != ''"
        ).fetchall()
        return {row[0].strip().upper() for row in rows if row and row[0]}
    except Exception:
        return set()


def load_symbols_from_screener():
    if not SCREEN_OUTPUT_PATH.exists():
        return set()
    try:
        rows = json.loads(SCREEN_OUTPUT_PATH.read_text(encoding="utf-8"))
    except Exception:
        return set()
    symbols = set()
    if isinstance(rows, list):
        for row in rows:
            if isinstance(row, dict) and row.get("symbol"):
                symbols.add(str(row["symbol"]).strip().upper())
    return symbols


def get_target_symbols(conn):
    return sorted(load_open_symbols_from_db(conn) | load_symbols_from_screener())


def parse_iso_day(raw_value):
    if not raw_value:
        return None
    text = str(raw_value).strip()
    if not text:
        return None
    candidate = text[:10]
    try:
        return datetime.strptime(candidate, "%Y-%m-%d").date()
    except ValueError:
        return None


def within_range(raw_value, start_day, end_day):
    day = parse_iso_day(raw_value)
    if day is None:
        return False
    return start_day <= day <= end_day


def fetch_finnhub_signals(symbol, api_key, start_day, end_day):
    try:
        news_list = fetch_news_finnhub(symbol, api_key, start_day, end_day)
    except Exception:
        return []
    items = []
    for item in news_list:
        pub_date = item.get("date", "")
        if not pub_date:
            continue
        items.append(
            {
                "symbol": symbol,
                "date": pub_date,
                "signal_type": "news",
                "headline": (item.get("title") or "").strip(),
                "full_text": (item.get("text") or "")[:800],
                "source": (item.get("publisher") or "").strip(),
            }
        )
    return [item for item in items if item["headline"]]


def _coerce_text(value):
    if isinstance(value, list):
        return ", ".join(str(v).strip() for v in value if str(v).strip())
    return str(value or "").strip()



def quality_from_items(item_codes):
    """8-K Item 代码列表 → 信号质量，取最高档。"""
    codes = {str(c).strip() for c in (item_codes or [])}
    if codes & ITEM_HIGH:
        return "high"
    if codes & ITEM_MEDIUM:
        return "medium"
    return "low"


def fetch_filing_text(cik, adsh):
    """用 adsh 拉 8-K 完整提交文本，提取正文摘要。失败返回空串。"""
    adsh_nodash = adsh.replace("-", "")
    url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{adsh_nodash}/{adsh}.txt"
    try:
        r = requests.get(url, headers={"User-Agent": SEC_USER_AGENT}, timeout=30)
        r.raise_for_status()
    except Exception:
        return ""
    raw = r.text
    # 跳过 SGML 头/XBRL，从第一个 "Item X.XX" 正文锚点开始；找不到则退回去标签全文
    match = re.search(r"Item\s+\d+\.\d+", raw)
    body = raw[match.start():] if match else raw
    text = re.sub(r"<[^>]+>", " ", body)
    text = re.sub(r"&[a-zA-Z#0-9]+;", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:1200]


def fetch_sec_8k_signals(symbol, cik, start_day, end_day):
    """按 CIK 精确查 8-K（替代旧的 q=symbol 全文搜，避免命中无关公司）。
    items 字段直接来自 efts 搜索结果用于评级；正文用 adsh 单独拉。
    """
    if cik is None:
        return []
    params = {
        "forms": "8-K",
        "dateRange": "custom",
        "startdt": start_day.isoformat(),
        "enddt": end_day.isoformat(),
        "ciks": f"{int(cik):010d}",
    }
    headers = {"User-Agent": SEC_USER_AGENT, "Accept": "application/json"}
    try:
        response = requests.get(SEC_URL, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return []

    raw_hits = payload.get("hits", {})
    if isinstance(raw_hits, dict):
        raw_hits = raw_hits.get("hits", [])
    if not isinstance(raw_hits, list):
        return []

    results = []
    for hit in raw_hits:
        source = hit.get("_source", hit) if isinstance(hit, dict) else {}
        file_date = source.get("file_date") or source.get("filedAt") or source.get("date")
        if not within_range(file_date, start_day, end_day):
            continue
        display_names = _coerce_text(
            source.get("display_names") or source.get("display_name") or source.get("displayNames")
        )
        item_codes = source.get("items") or []
        if isinstance(item_codes, str):
            item_codes = [c.strip() for c in item_codes.split(",") if c.strip()]
        quality = quality_from_items(item_codes)
        items_label = ", ".join(str(c) for c in item_codes) if item_codes else "?"
        headline = f"{display_names} 8-K Item {items_label}".strip() or f"{symbol} 8-K"

        # adsh 来自 _id（格式 "adsh:primary_doc"）或 source.adsh
        _id = hit.get("_id", "") if isinstance(hit, dict) else ""
        adsh = _id.split(":")[0] if ":" in _id else _coerce_text(source.get("adsh"))
        full_text = fetch_filing_text(cik, adsh) if adsh else ""
        if not full_text:
            full_text = f"{display_names} 8-K Items: {items_label}".strip()

        results.append(
            {
                "symbol": symbol,
                "date": str(parse_iso_day(file_date)),
                "signal_type": "8k",
                "headline": headline,
                "full_text": full_text,
                "source": "SEC EDGAR",
                "signal_quality": quality,
            }
        )
    return results


def insert_signals(conn, signals):
    created_at = datetime.utcnow().isoformat(timespec="seconds")
    before = conn.total_changes
    conn.executemany(
        """
        INSERT OR IGNORE INTO signals (
            symbol, date, signal_type, headline, full_text, source, created_at, signal_quality
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                item["symbol"],
                item["date"],
                item["signal_type"],
                item["headline"],
                item["full_text"],
                item["source"],
                created_at,
                compute_signal_quality(item),
            )
            for item in signals
        ],
    )
    conn.commit()
    return conn.total_changes - before


def compute_signal_quality(item):
    # 8-K 在 fetch_sec_8k_signals 里已按 efts items 字段评级
    if item.get("signal_quality"):
        return item["signal_quality"]
    signal_type = str(item.get("signal_type") or "").strip().lower()
    if signal_type == "news":
        return "medium"
    return "low"


def backup_db():
    import shutil
    from datetime import timezone, timedelta
    edt = timezone(timedelta(hours=-4))
    today = datetime.now(edt).strftime("%Y%m%d")
    backup_dir = DB_PATH.parent / "backups"
    backup_dir.mkdir(exist_ok=True)
    dest = backup_dir / f"trading_{today}.db"
    shutil.copy2(DB_PATH, dest)
    # 删除30天前的备份
    cutoff = datetime.now(edt).date() - timedelta(days=30)
    for f in backup_dir.glob("trading_*.db"):
        try:
            file_date_str = f.stem.replace("trading_", "")
            from datetime import date as _date
            file_date = _date(int(file_date_str[:4]), int(file_date_str[4:6]), int(file_date_str[6:8]))
            if file_date < cutoff:
                f.unlink()
        except Exception:
            pass
    print(f"[backup] {dest.name} ({dest.stat().st_size // 1024}KB)")


def _send_alert_email(env, subject, body):
    api_key = env.get("BREVO_API_KEY")
    gmail_user = env.get("GMAIL_USER")
    gmail_to = env.get("GMAIL_TO")
    if not api_key or not gmail_user or not gmail_to:
        print("[email] 缺少邮件配置，跳过")
        return
    payload = json.dumps({
        "sender": {"name": "Cowork VPS", "email": gmail_user},
        "to": [{"email": gmail_to}],
        "subject": subject,
        "textContent": body,
    }).encode()
    req = urllib.request.Request(
        "https://api.brevo.com/v3/smtp/email",
        data=payload,
        headers={"api-key": api_key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=15)
        print(f"[email] 已发送：{subject}")
    except Exception as e:
        print(f"[email] 发送失败：{e}")


def write_system_log(processed, news_count, sec_count, inserted, has_finnhub_key, env=None):
    from datetime import timezone, timedelta
    edt = timezone(timedelta(hours=-4))
    now = datetime.now(edt).strftime("%Y-%m-%d %H:%M EDT")
    if has_finnhub_key:
        finnhub_status = "OK" if news_count > 0 else "WARN(0条)"
    else:
        finnhub_status = "无key"
    overall = "✅" if (news_count > 0 or sec_count > 0) else "❌"
    line = (
        f"[{now}] {overall} symbols={processed} news={news_count} "
        f"8k={sec_count} inserted={inserted} | Finnhub:{finnhub_status} SEC:OK\n"
    )
    with SYSTEM_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line)
    print(f"[system_log] {line.strip()}")
    # Finnhub失效告警
    if has_finnhub_key and news_count == 0 and env:
        _send_alert_email(
            env,
            subject=f"⚠️ TIDE系统：Finnhub新闻today={now}全部为0",
            body=(
                f"signal_collector 今日运行结果：\n\n"
                f"  symbols={processed}  news=0  8k={sec_count}  inserted={inserted}\n\n"
                f"Finnhub新闻为0条（共{processed}只股票），可能原因：\n"
                f"  1. Finnhub API key失效或超限\n"
                f"  2. 今日确实无新闻（较罕见）\n\n"
                f"请登录 finnhub.io 检查账号状态。\n\nSystem Log: {SYSTEM_LOG_PATH}"
            ),
        )


def collect_signals(backfill_days):
    env = load_env()
    finnhub_key = env.get("FINNHUB_API_KEY", "")

    end_day = date.today()
    start_day = end_day - timedelta(days=max(backfill_days - 1, 0))
    conn = init_db()
    symbols = get_target_symbols(conn)
    cik_map = load_cik_map()

    inserted = 0
    processed = 0
    news_count = 0
    sec_count = 0

    print(f"[signal_collector] symbols={len(symbols)} cik_map={len(cik_map)} window={start_day.isoformat()}..{end_day.isoformat()}")
    for symbol in symbols:
        processed += 1
        news_items = fetch_finnhub_signals(symbol, finnhub_key, start_day, end_day) if finnhub_key else []
        sec_items = fetch_sec_8k_signals(symbol, cik_map.get(symbol.upper()), start_day, end_day)
        n = insert_signals(conn, news_items + sec_items)
        inserted += n
        news_count += len(news_items)
        sec_count += len(sec_items)
        print(f"[signal_collector] {symbol}: news={len(news_items)} 8k={len(sec_items)} new_rows={n}")

    total = conn.execute("SELECT COUNT(*) FROM signals").fetchone()[0]
    conn.close()
    print(
        f"[signal_collector] done processed={processed} news={news_count} "
        f"8k={sec_count} inserted={inserted} total_in_db={total}"
    )
    write_system_log(processed, news_count, sec_count, inserted, bool(finnhub_key), env=env)
    backup_db()


def main():
    parser = argparse.ArgumentParser(description="Collect FMP news and SEC 8-K signals.")
    parser.add_argument(
        "--backfill",
        type=int,
        default=1,
        metavar="N",
        help="抓取最近 N 天（含今天），默认 1。",
    )
    args = parser.parse_args()
    collect_signals(max(args.backfill, 1))


if __name__ == "__main__":
    from tide_utils import run_with_alert
    run_with_alert("signal_collector", main)
