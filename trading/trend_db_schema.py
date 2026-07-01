"""
第2层趋势主线·提速攒样本实验 DB Schema（5 表 + 冻结 trigger）

【是什么】trading.db 里第2层前向纸仓实验的建表模块。与第1层表（scanner_picks/trades/
signals/narrative_* 等）零交集——第1层 schema 在 db_schema.py，本文件只管 trend_* 5 表。

【为什么做】主公 2026-07-01 拍板：intraday 纸账户放开出手门槛快速攒"判断→结果"样本，
验证第2层六维趋势方法方向对不对；死约束=数据零污染。
方案：trading/notes/第2层提速攒样本方案_20260701.md（v0.2，含 Fable5 对抗审核修法）。

【为什么这样设计】
- 三层物理分表 = 数据/判断分层铁律（feedback_tracking_facts_only）落到 DB 结构：
  trend_judgments（判断冻结层）/ trend_signal_prices + trend_paper_trades（客观数据层）/
  trend_verdicts（判断层，滚动多条）/ trend_scan_longlist（供给留痕层）
- 冻结层和 verdict 层用 SQLite TRIGGER 硬闸禁 UPDATE/DELETE（审核重要-6：
  "永不UPDATE"不能只是文档承诺）——复盘/纠错只许 INSERT 新记录。
- 对答案口径预注册在方案文档四节，本文件不做判定逻辑（判定在 trend_verdict_check.py）。

【演进】2026-07-01 v0.2 首版建表。
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trading.db")

TREND_TABLES_SQL = """
-- ① 判断冻结层：登记后永不改（trigger 硬闸）
CREATE TABLE IF NOT EXISTS trend_judgments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    judgment_date TEXT NOT NULL,          -- 登记日 YYYY-MM-DD（backfill 时=原打分日，如实记）
    trend_name TEXT NOT NULL,             -- 趋势名（如 "AI 电力/数据中心能源"）
    proxy_symbol TEXT NOT NULL,           -- 代理标的（美股 only）
    proxy_type TEXT NOT NULL,             -- etf | stock
    proxy_reason TEXT,                    -- 选择理由
    proxy_chosen_date TEXT,               -- 代理选择日（backfill 补选的如实标 7/1，与 judgment_date 区分）
    sector_benchmark TEXT,                -- 板块基准代码，规则见方案规则3；代理=一级sector ETF 时 'N/A'
    score_json TEXT,                      -- 六维分+出处 JSON
    score_display TEXT,                   -- 可读总分（如 "5/6"）
    score_pct REAL,                       -- 得分率 0-100
    veto_hit INTEGER DEFAULT 0,           -- 一票否决命中 0/1
    manual_version TEXT NOT NULL,         -- 手册版本（如 v1.1），跨版本样本不混算
    cohort TEXT NOT NULL,                 -- passed | borderline | rejected
    risk_cluster TEXT NOT NULL,           -- 风险簇（B账同簇同窗口合并计1；结论门槛=独立簇数≥8）
    trigger_source TEXT NOT NULL,         -- showdown|w7|heatmap|quota_scan|user|backfill
    direction TEXT,                       -- long|short|neutral|NULL（NULL=未冻结方向，不进B账）
    no_direction_frozen INTEGER DEFAULT 0,-- 1=方向字段留空是刻意的（第0批防事后诸葛亮）
    direction_basis TEXT,
    verification_points TEXT,             -- 验证点（什么兑现算对）
    exit_signals TEXT,                    -- 下车信号（rejected 组不设，留空）
    entry_price_rule TEXT DEFAULT '登记日下一交易日开盘价',
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- ② 客观数据层：信号层基线价（每 judgment 一行，INSERT once）
CREATE TABLE IF NOT EXISTS trend_signal_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    judgment_id INTEGER NOT NULL UNIQUE REFERENCES trend_judgments(id),
    entry_date TEXT,                      -- 实际取到的"下一交易日"
    proxy_entry_price REAL,               -- 代理标的该日开盘价
    spy_entry_price REAL,
    sector_entry_price REAL,              -- 板块基准该日开盘价（N/A 时空）
    source TEXT,                          -- yfinance 等
    fetched_at TEXT DEFAULT (datetime('now'))
);

-- ③ 客观数据层：纸仓执行（仅 passed/borderline；出场字段允许事实回填）
CREATE TABLE IF NOT EXISTS trend_paper_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    judgment_id INTEGER NOT NULL REFERENCES trend_judgments(id),
    symbol TEXT NOT NULL,
    account TEXT NOT NULL DEFAULT 'intraday',
    entry_order_id TEXT,
    entry_date TEXT,
    entry_fill_price REAL,
    qty REAL,
    notional REAL,                        -- 统一 $25,000
    exit_order_id TEXT,
    exit_date TEXT,
    exit_fill_price REAL,
    exit_reason TEXT,                     -- 下车信号|保命线|12m终判到期
    status TEXT DEFAULT 'open',           -- open | closed
    created_at TEXT DEFAULT (datetime('now'))
);

-- ④ 判断层：对答案（滚动多条，永不改，trigger 硬闸）
CREATE TABLE IF NOT EXISTS trend_verdicts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    judgment_id INTEGER NOT NULL REFERENCES trend_judgments(id),
    account_type TEXT NOT NULL,           -- A_ranking | B_direction | C_exit | discrepancy
    window TEXT NOT NULL,                 -- 3m | 6m | 12m | post_exit_3m
    raw_return REAL,                      -- 代理标的买入持有收益 %
    rel_spy REAL,                         -- 相对 SPY %
    rel_sector REAL,                      -- 相对板块基准 %（N/A 时空）
    verdict TEXT,                         -- B账: 对|错|待定；A账: 记数值不判定；C账: 躲跌|卖飞|中性
    verdict_date TEXT NOT NULL,
    basis TEXT,                           -- 判定依据：基线价/窗口末价/数据源，可复算
    mechanical INTEGER DEFAULT 1,         -- 1=脚本机械判定；0=discrepancy 人工标记（须附证据）
    created_at TEXT DEFAULT (datetime('now'))
);

-- ⑤ 供给留痕层：扫描长名单（防选择性供给）
CREATE TABLE IF NOT EXISTS trend_scan_longlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_date TEXT NOT NULL,
    candidate TEXT NOT NULL,
    drop_reason TEXT,                     -- 一句话淘汰理由；进入打分则写 '进入打分'
    advanced INTEGER DEFAULT 0,           -- 1=进入六维打分
    created_at TEXT DEFAULT (datetime('now'))
);
"""

FREEZE_TRIGGERS_SQL = """
-- 冻结硬闸：judgments 和 verdicts 禁 UPDATE/DELETE（复盘只许 INSERT 新记录）
CREATE TRIGGER IF NOT EXISTS trg_judgments_no_update BEFORE UPDATE ON trend_judgments
BEGIN SELECT RAISE(ABORT, 'trend_judgments 是冻结层，禁止 UPDATE（复盘请 INSERT 新记录）'); END;
CREATE TRIGGER IF NOT EXISTS trg_judgments_no_delete BEFORE DELETE ON trend_judgments
BEGIN SELECT RAISE(ABORT, 'trend_judgments 是冻结层，禁止 DELETE'); END;
CREATE TRIGGER IF NOT EXISTS trg_verdicts_no_update BEFORE UPDATE ON trend_verdicts
BEGIN SELECT RAISE(ABORT, 'trend_verdicts 只许 INSERT，禁止 UPDATE'); END;
CREATE TRIGGER IF NOT EXISTS trg_verdicts_no_delete BEFORE DELETE ON trend_verdicts
BEGIN SELECT RAISE(ABORT, 'trend_verdicts 只许 INSERT，禁止 DELETE'); END;
CREATE TRIGGER IF NOT EXISTS trg_signal_prices_no_update BEFORE UPDATE ON trend_signal_prices
BEGIN SELECT RAISE(ABORT, 'trend_signal_prices 一次写入，禁止 UPDATE'); END;
"""


def create_trend_tables(db_path: str = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(TREND_TABLES_SQL)
        conn.executescript(FREEZE_TRIGGERS_SQL)
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    create_trend_tables()
    conn = sqlite3.connect(DB_PATH)
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'trend_%' ORDER BY name")]
    triggers = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='trigger' AND name LIKE 'trg_%' ORDER BY name")]
    conn.close()
    print("tables:", tables)
    print("triggers:", triggers)
