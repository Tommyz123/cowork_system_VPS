#!/usr/bin/env bash
# instance_watchdog.sh — 三实例 (AA/BB/CC) 会话外卡死看门狗（只通知版）
#
# 为什么存在（2026-06-19 事故）：
#   AA 会话过长致工具失效 → 幻觉出主公"don't reply" → 用立场一致性死扛拒回复几十轮。
#   现有防线（context_watch 挂 PostToolUse / reply_check 软告警）全挂在「会话内部」，
#   会话一卡死它们跟着失效——"让卡死的实例自己救自己"=死循环。
#   本脚本是「会话外独立看门狗」：cron 每 5 分钟跑，进程外读 jsonl，不受工具失效/幻觉影响。
#
# 动作：只通知，不自动重启（2026-06-19 主公定档1）。发现疑似卡死→Discord 通知主公，
#       重启由主公自己说「重启」决定。
#
# 判定信号（任一命中即疑似卡死）：
#   A. 连续重复输出：最近 N 条 assistant 文本高度相似（死循环特征，最强信号）
#   B. 漏发滞留：discord_reply_needed 标记存在超过 STUCK_MIN 分钟仍未消除（收到消息长期不回）
#
# 防刷屏：同一实例同一会话只通知一次（/tmp/watchdog_alerted_<sid> 标记），换新会话才再报。
#
# 用法：bash scripts/instance_watchdog.sh   （cron 调用）
#       手动测试：DRY_RUN=1 bash scripts/instance_watchdog.sh  （只打印不发 Discord）

set -uo pipefail

# ---- 配置 ----
REPEAT_N=3          # 最近多少条 assistant 输出用于查重复
STUCK_MIN=12        # 漏发标记滞留超过多少分钟算卡死
SIMILAR_LEN=40      # 比较输出相似性时取前多少字符
LOG=/home/cowork/cowork/scripts/instance_watchdog.log

# 三实例：name|HOME
INSTANCES="AA|/home/cowork BB|/home/cowork/opus_home CC|/home/cowork/opus2_home"

# Discord（通知主公用——发到各实例自己频道，token 在各 HOME 的 .env）
notify() {
  local name="$1" home="$2" msg="$3"
  if [ "${DRY_RUN:-0}" = "1" ]; then
    echo "[DRY_RUN] would notify $name: $msg"
    return
  fi
  local env="$home/.claude/channels/discord/.env"
  local tok chan
  tok=$(grep DISCORD_BOT_TOKEN "$env" 2>/dev/null | sed 's/.*=//' | tr -d ' \r\n')
  # 频道 ID 从该实例最新 jsonl 挖（其 DM channel）
  chan=$(latest_chan "$home")
  [ -z "$tok" ] || [ -z "$chan" ] && { echo "$(date -Iseconds) [$name] 通知失败:缺token/chan" >> "$LOG"; return; }
  curl -s -X POST "https://discord.com/api/v10/channels/${chan}/messages" \
    -H "Authorization: Bot ${tok}" -H "Content-Type: application/json" \
    -d "{\"content\": \"${msg}\"}" > /dev/null 2>&1
  echo "$(date -Iseconds) [$name] 已通知: $msg" >> "$LOG"
}

# 取某 HOME 最新 jsonl 路径
latest_jsonl() {
  ls -t "$1/.claude/projects/-home-cowork-cowork/"*.jsonl 2>/dev/null | head -1
}

# 取某 HOME 最新 jsonl 里最后出现的 DM channel id
latest_chan() {
  local f; f=$(latest_jsonl "$1")
  [ -z "$f" ] && return
  grep -oE '1[0-9]{17,19}' "$f" 2>/dev/null | tail -1
}

# 信号A：最近 REPEAT_N 条 assistant 输出是否高度重复
check_repeat() {
  local f="$1"
  python3 - "$f" "$REPEAT_N" "$SIMILAR_LEN" <<'PY'
import json,sys
f,n,slen=sys.argv[1],int(sys.argv[2]),int(sys.argv[3])
texts=[]
try:
    for line in open(f):
        try: d=json.loads(line)
        except: continue
        m=d.get('message',{})
        if isinstance(m,dict) and m.get('role')=='assistant':
            c=m.get('content','');t=''
            if isinstance(c,list):
                for x in c:
                    if isinstance(x,dict) and x.get('type')=='text': t+=x.get('text','')
            elif isinstance(c,str): t=c
            t=t.strip()
            if t: texts.append(t[:slen].lower())
except: print("0"); sys.exit()
last=texts[-n:]
if len(last)<n: print("0"); sys.exit()
# 含 don't reply / 拒绝回复类死扛短语，或 N 条彼此高度相似 → 卡死
joined=" ".join(last)
stuck_phrase = "don't reply" in joined or "won't reply" in joined or "no message sent" in joined
# 相似性：去重后种类 <= 2 视为重复死循环
uniq=len(set(last))
print("1" if (stuck_phrase or uniq<=2) else "0")
PY
}

# 信号B：漏发标记滞留超时
check_stuck_reply() {
  local sid="$1"
  local flag="/tmp/discord_reply_needed_${sid}"
  [ ! -f "$flag" ] && { echo "0"; return; }
  local age_min=$(( ( $(date +%s) - $(stat -c %Y "$flag" 2>/dev/null || echo 0) ) / 60 ))
  [ "$age_min" -ge "$STUCK_MIN" ] && echo "1" || echo "0"
}

# ---- 主循环 ----
for inst in $INSTANCES; do
  name="${inst%%|*}"; home="${inst##*|}"
  f=$(latest_jsonl "$home")
  [ -z "$f" ] && continue
  sid=$(basename "$f" .jsonl)

  alerted="/tmp/watchdog_alerted_${sid}"
  [ -f "$alerted" ] && continue   # 这个会话已通知过，防刷屏

  rep=$(check_repeat "$f")
  stk=$(check_stuck_reply "$sid")

  if [ "$rep" = "1" ] || [ "$stk" = "1" ]; then
    reason=""
    [ "$rep" = "1" ] && reason="${reason}连续重复输出/死扛短语 "
    [ "$stk" = "1" ] && reason="${reason}消息${STUCK_MIN}分钟+未回复 "
    msg="⚠️ 看门狗警报：${name} 疑似卡死（${reason}）。建议在该实例频道发「重启」。（本会话只报一次）"
    notify "$name" "$home" "$msg"
    touch "$alerted"
  fi
done

# 清理：删掉超过 24h 的旧 alerted 标记（防 /tmp 堆积）
find /tmp -maxdepth 1 -name 'watchdog_alerted_*' -mmin +1440 -delete 2>/dev/null

exit 0
