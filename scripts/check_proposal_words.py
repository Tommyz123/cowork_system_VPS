#!/usr/bin/env python3
"""Stop Hook: 检测 AI 回复是否包含推方案词，留痕到 friction_log"""
import json
import sys
import os
import re
from datetime import datetime


PROPOSAL_PATTERN = re.compile(
    r'(值得(抄|借鉴|加入|纳入)'
    r'|加到.{0,5}BACKLOG|BACKLOG.{0,5}加'
    r'|纳入.*BACKLOG'
    r'|不妨(试试|考虑|引入|加)'
    r'|可以(引入|抄入|借鉴)这)',
    re.UNICODE
)

FRICTION_LOG = '/home/cowork/cowork/friction_log.md'


def get_last_assistant_text(transcript_path):
    try:
        lines = open(transcript_path).readlines()
    except Exception:
        return ''

    last_user = -1
    for i, l in enumerate(lines):
        try:
            if json.loads(l).get('role') == 'user':
                last_user = i
        except Exception:
            pass

    texts = []
    for l in lines[last_user + 1:]:
        try:
            d = json.loads(l)
            if d.get('role') != 'assistant':
                continue
            content = d.get('message', {}).get('content', [])
            if isinstance(content, list):
                for c in content:
                    if isinstance(c, dict) and c.get('type') == 'text':
                        texts.append(c.get('text', ''))
            elif isinstance(content, str):
                texts.append(content)
        except Exception:
            pass

    return ' '.join(texts)


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    transcript_path = data.get('transcript_path', '')
    if not transcript_path or not os.path.isfile(transcript_path):
        sys.exit(0)

    text = get_last_assistant_text(transcript_path)
    if not text:
        sys.exit(0)

    match = PROPOSAL_PATTERN.search(text)
    if not match:
        sys.exit(0)

    now = datetime.now().strftime('%Y-%m-%d %H:%M EDT')
    snippet = text[:120].replace('\n', ' ')
    entry = (
        f"\n[{now}] ⚠️ Stop Hook 告警 | 推方案词检测"
        f" | 命中词：「{match.group(0)}」"
        f" | 摘要：{snippet}..."
        f" | 状态：自动留痕，请检查本轮是否已 grep friction_log 验证痛点"
    )

    try:
        with open(FRICTION_LOG, 'a') as f:
            f.write(entry + '\n')
        print(f"⚠️ [推方案检查] 命中「{match.group(0)}」，已记录 friction_log")
    except Exception:
        pass

    sys.exit(0)


if __name__ == '__main__':
    main()
