#!/usr/bin/env python3
"""
趋势档案周报 · Markdown → HTML 渲染器

把 dossier_weekly.py 生成的 markdown 报告渲染成结构化 HTML 邮件：
  - ## 标题 → 分区标题条
  - **加粗** → <b>
  - 状态关键词（强化/成立稳定/松动/瓦解/黄灯/待...）→ 彩色标签（=判断）
  - 每个对象的依据再拆成「📊 数据」「🧭 判断」两块（数据/判断分层，主公铁律）
  - 趋势层/个股层列表 → 卡片
  - 本周关注 → 编号要点块

设计取舍（2026-06-22 与主公定）：
  - 邮件走结构化 HTML（卡片），不再 \\n→<br> 硬拼
  - 内联 style（邮件客户端不支持 <style> 标签/外链）
  - 移动端友好：单列卡片
  - 数据与判断分层：状态标签+判断区 vs 数据区视觉隔离
"""
import re
import html as html_lib

# 状态 → 颜色（背景, 文字）
STATUS_COLORS = {
    "强化":     ("#1b5e20", "#fff"),   # 深绿
    "成立稳定": ("#2e7d32", "#fff"),   # 绿
    "黄灯":     ("#f9a825", "#000"),   # 黄
    "松动":     ("#ef6c00", "#fff"),   # 橙
    "瓦解":     ("#c62828", "#fff"),   # 红
    "待":       ("#757575", "#fff"),   # 灰
}

EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF✨⚠️📈📉]+"
)

# 识别"数据型"片段：含 价格/百分比/PE/距高/日期范围 等客观数字
DATA_HINT_RE = re.compile(
    r"(\$\d|[\d.]+%|PE|pe|距高|[-+]?\d+\.\d+|\d+/\d+|\d+x|\d+天|52周)"
)


def status_badge(text: str) -> str:
    """从状态文字识别关键词，返回彩色标签（=判断）。"""
    clean = EMOJI_RE.sub("", text).strip()
    for key, (bg, fg) in STATUS_COLORS.items():
        if key in clean:
            return (
                f'<span style="display:inline-block;background:{bg};color:{fg};'
                f'padding:2px 10px;border-radius:12px;font-size:12px;'
                f'font-weight:600;white-space:nowrap;">{html_lib.escape(clean)}</span>'
            )
    return (
        f'<span style="display:inline-block;background:#757575;color:#fff;'
        f'padding:2px 10px;border-radius:12px;font-size:12px;">'
        f'{html_lib.escape(clean)}</span>'
    )


def inline_md(text: str) -> str:
    esc = html_lib.escape(text)
    esc = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", esc)
    return esc


def split_data_judgment(detail: str):
    """
    尽力把一句话依据拆成 (数据片段, 判断片段)。
    策略：按 标点(；;，,) 切句，含客观数字的归数据，其余归判断。
    这是渲染层的"尽力拆"；根治方案是让 AI 直接输出两字段（见 dossier_weekly prompt）。
    """
    pieces = re.split(r"[；;，,]", detail)
    data_parts, judge_parts = [], []
    for p in pieces:
        p = p.strip()
        if not p:
            continue
        if DATA_HINT_RE.search(p):
            data_parts.append(p)
        else:
            judge_parts.append(p)
    data = "，".join(data_parts)
    judge = "，".join(judge_parts)
    return data, judge


def parse_object_line(line: str):
    body = line.lstrip("- ").strip()
    m = re.match(r"^(.*?)[：:](.*)$", body)
    if not m:
        return None
    name_part = m.group(1).strip()
    rest = m.group(2).strip()
    sm = re.match(r"^(.*?)\s*[—–-]\s*(.*)$", rest)
    if sm:
        status_text = sm.group(1).strip()
        detail = sm.group(2).strip()
    else:
        status_text = rest
        detail = ""
    return (name_part, status_text, detail)


def render_card(name_raw, status_text, data, judge, fallback="") -> str:
    """统一卡片渲染：名称 + 状态标签 + 📊数据 + 🧭判断。"""
    badge = status_badge(status_text)
    name_html = inline_md(name_raw)

    rows = ""
    if data:
        rows += (
            '<div style="font-size:12px;color:#37474f;line-height:1.5;margin-top:6px;">'
            '<span style="color:#90a4ae;font-weight:600;">📊 数据</span>&nbsp;'
            f'{inline_md(data)}</div>'
        )
    if judge:
        rows += (
            '<div style="font-size:12px;color:#5d4037;line-height:1.5;margin-top:4px;'
            'background:#fff8e1;border-radius:4px;padding:4px 8px;">'
            '<span style="color:#bf9000;font-weight:600;">🧭 判断</span>&nbsp;'
            f'{inline_md(judge)}</div>'
        )
    if not rows:  # 兜底：两字段都空就放 fallback 整句
        rows = (
            f'<div style="font-size:12px;color:#555;line-height:1.5;margin-top:6px;">'
            f'{inline_md(fallback)}</div>'
        )

    return (
        '<div style="border:1px solid #e0e0e0;border-radius:8px;padding:12px 14px;'
        'margin:8px 0;background:#fff;">'
        '<div style="display:flex;justify-content:space-between;align-items:center;'
        'gap:8px;">'
        f'<span style="font-weight:700;font-size:15px;color:#1a1a1a;">{name_html}</span>'
        f'{badge}</div>'
        f'{rows}'
        '</div>'
    )


def parse_name_status(line: str):
    """解析对象名称行：`- VST：成立稳定` → (name, status)。"""
    body = line.lstrip("- ").strip()
    m = re.match(r"^(.*?)[：:](.*)$", body)
    if not m:
        return (body, "")
    return (m.group(1).strip(), m.group(2).strip())


def render_object_card(name_raw, status_text, detail_raw) -> str:
    """旧式单行卡片（A方案/兜底）：依据靠 split_data_judgment 猜拆。"""
    badge = status_badge(status_text)
    name_html = inline_md(name_raw)
    data, judge = split_data_judgment(detail_raw)

    rows = ""
    if data:
        rows += (
            '<div style="font-size:12px;color:#37474f;line-height:1.5;margin-top:6px;">'
            '<span style="color:#90a4ae;font-weight:600;">📊 数据</span>&nbsp;'
            f'{inline_md(data)}</div>'
        )
    if judge:
        rows += (
            '<div style="font-size:12px;color:#5d4037;line-height:1.5;margin-top:4px;'
            'background:#fff8e1;border-radius:4px;padding:4px 8px;">'
            '<span style="color:#bf9000;font-weight:600;">🧭 判断</span>&nbsp;'
            f'{inline_md(judge)}</div>'
        )
    if not rows:  # 兜底：拆不出就整句放数据区
        rows = (
            f'<div style="font-size:12px;color:#555;line-height:1.5;margin-top:6px;">'
            f'{inline_md(detail_raw)}</div>'
        )

    return (
        '<div style="border:1px solid #e0e0e0;border-radius:8px;padding:12px 14px;'
        'margin:8px 0;background:#fff;">'
        '<div style="display:flex;justify-content:space-between;align-items:center;'
        'gap:8px;">'
        f'<span style="font-weight:700;font-size:15px;color:#1a1a1a;">{name_html}</span>'
        f'{badge}</div>'
        f'{rows}'
        '</div>'
    )


def render(markdown: str, date_str: str) -> str:
    lines = markdown.splitlines()
    sections = []
    cur_title = None
    cur_items = []

    def flush():
        nonlocal cur_title, cur_items
        if cur_title is not None:
            sections.append((cur_title, cur_items))
        cur_items = []

    for raw in lines:
        line = raw.rstrip()
        if line.startswith("# "):
            continue
        if line.startswith("> "):
            continue
        if line.startswith("## "):
            flush()
            cur_title = line[3:].strip()
            continue
        if line.strip() in ("", "---"):
            continue
        if line.startswith("_") and line.endswith("_"):
            continue
        cur_items.append(line)
    flush()

    parts = []
    parts.append(
        '<div style="max-width:640px;margin:0 auto;font-family:-apple-system,'
        'BlinkMacSystemFont,\'Segoe UI\',Roboto,sans-serif;background:#f5f6f8;'
        'padding:20px;">'
    )
    parts.append(
        '<div style="background:linear-gradient(135deg,#1a237e,#283593);color:#fff;'
        'padding:18px 22px;border-radius:10px 10px 0 0;">'
        '<div style="font-size:20px;font-weight:700;">📊 趋势档案周报</div>'
        f'<div style="font-size:13px;opacity:.85;margin-top:4px;">{date_str} · '
        'AI 读档案自动分析</div>'
        '<div style="font-size:11px;opacity:.7;margin-top:6px;">'
        '📊数据=客观事实 · 🧭判断=AI推断 · 只做事实+逻辑分析+反思，不构成买卖建议</div>'
        '</div>'
    )
    parts.append('<div style="background:#fff;padding:18px 22px;border-radius:0 0 10px 10px;">')

    for title, items in sections:
        parts.append(
            f'<div style="font-size:16px;font-weight:700;color:#283593;'
            f'border-left:4px solid #283593;padding-left:10px;margin:18px 0 10px;">'
            f'{html_lib.escape(EMOJI_RE.sub("", title).strip())}</div>'
        )
        if "总览" in title:
            text = " ".join(items)
            parts.append(
                '<div style="background:#fff8e1;border-left:3px solid #bf9000;'
                'border-radius:6px;padding:14px;font-size:14px;line-height:1.6;'
                f'color:#1a1a1a;"><span style="color:#bf9000;font-weight:600;'
                f'font-size:12px;">🧭 整体判断</span><br>{inline_md(text)}</div>'
            )
        elif "关注" in title:
            parts.append('<ol style="margin:0;padding-left:20px;">')
            for it in items:
                it = re.sub(r"^\d+\.\s*", "", it)
                parts.append(
                    f'<li style="font-size:13px;color:#444;line-height:1.6;'
                    f'margin-bottom:8px;">{inline_md(it)}</li>'
                )
            parts.append('</ol>')
        else:
            # B 格式：对象按三行成组（- 名称：状态 / 数据: ... / 判断: ...）
            i = 0
            n = len(items)
            while i < n:
                it = items[i]
                if not it.startswith("-"):
                    if "注" in it:
                        parts.append(
                            f'<div style="font-size:12px;color:#999;font-style:italic;'
                            f'margin:4px 0;">{inline_md(it)}</div>'
                        )
                    i += 1
                    continue

                # 看接下来的行是不是 数据:/判断: 字段
                data_val, judge_val = "", ""
                j = i + 1
                while j < n and not items[j].startswith("-"):
                    nxt = items[j].strip()
                    dm = re.match(r"^[📊\s]*数据[：:]\s*(.*)$", nxt)
                    jm = re.match(r"^[🧭\s]*判断[：:]\s*(.*)$", nxt)
                    if dm:
                        data_val = dm.group(1).strip()
                    elif jm:
                        judge_val = jm.group(1).strip()
                    j += 1

                if data_val or judge_val:
                    # B 格式：显式字段，直接渲染不靠猜
                    name_raw, status = parse_name_status(it)
                    parts.append(render_card(name_raw, status, data_val, judge_val))
                    i = j
                else:
                    # 兜底：旧单行格式，靠 split_data_judgment 猜拆
                    parsed = parse_object_line(it)
                    if parsed:
                        parts.append(render_object_card(*parsed))
                    else:
                        parts.append(
                            f'<div style="font-size:13px;color:#444;">{inline_md(it)}</div>'
                        )
                    i += 1

    parts.append('</div>')
    parts.append(
        '<div style="text-align:center;font-size:11px;color:#999;margin-top:14px;">'
        '数据来源：趋势追踪档案.md · 决策权在主公 · 自动生成 by dossier_weekly.py'
        '</div>'
    )
    parts.append('</div>')
    return "\n".join(parts)


if __name__ == "__main__":
    import sys
    from pathlib import Path
    md_path = Path(sys.argv[1])
    text = md_path.read_text(encoding="utf-8")
    date_m = re.search(r"(\d{4}-\d{2}-\d{2})", md_path.name)
    date_str = date_m.group(1) if date_m else ""
    out = render(text, date_str)
    out_path = md_path.with_suffix(".sample.html")
    out_path.write_text(out, encoding="utf-8")
    print(f"written: {out_path}")
