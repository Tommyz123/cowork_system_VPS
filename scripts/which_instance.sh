#!/usr/bin/env bash
# which_instance.sh — 三实例 (AA/BB/CC) 真相速查
#
# 为什么存在：实例命名天然错位（目录 opus_home 其实是 BB，opus2_home 才是 CC），
# 靠记忆/目录名直觉判断会搞错（2026-06-19 教训：把 BB 误当 AA 查）。
# 本脚本只读运行时真相（进程 HOME + settings.json），不靠记忆，不改任何配置。
#
# 口诀：裸 /home/cowork = AA ｜ opus_home = BB ｜ opus2_home = CC
# 用法：bash scripts/which_instance.sh

set -uo pipefail

# HOME → 实例名映射（唯一权威，运行时按进程 HOME 反查）
home_to_name() {
  case "$1" in
    /home/cowork|/home/cowork/)                       echo "AA" ;;
    /home/cowork/opus_home|/home/cowork/opus_home/)   echo "BB" ;;
    /home/cowork/opus2_home|/home/cowork/opus2_home/) echo "CC" ;;
    *) echo "??" ;;
  esac
}

# 取某进程的 HOME 环境变量
pid_home() {
  tr '\0' '\n' < "/proc/$1/environ" 2>/dev/null | sed -n 's/^HOME=//p' | head -1
}

# 取某 HOME 的 settings.json model 字段
home_model() {
  local f="$1/.claude/settings.json"
  [ -f "$f" ] || { echo "无文件"; return; }
  local m
  m=$(grep -oE '"model"[[:space:]]*:[[:space:]]*"[^"]*"' "$f" | head -1 | sed -E 's/.*:[[:space:]]*"([^"]*)".*/\1/')
  [ -n "$m" ] && echo "$m" || echo "无model字段(用默认)"
}

printf '\n=== 三实例真相速查 (运行时 HOME，非记忆) ===\n'
printf '口诀: 裸/home/cowork=AA | opus_home=BB | opus2_home=CC\n\n'
printf '%-4s %-8s %-26s %-22s %s\n' "实例" "PID" "HOME" "model(settings.json)" "tmux"
printf '%s\n' "--------------------------------------------------------------------------------------------"

found=0
while read -r pid; do
  [ -z "$pid" ] && continue
  h=$(pid_home "$pid")
  [ -z "$h" ] && continue
  name=$(home_to_name "$h")
  model=$(home_model "$h")
  tinfo=$(pstree -ps "$pid" 2>/dev/null | grep -oE 'tmux[^(]*\([0-9]+\)' | head -1)
  [ -z "$tinfo" ] && tinfo="(无tmux父)"
  printf '%-4s %-8s %-26s %-22s %s\n' "$name" "$pid" "$h" "$model" "$tinfo"
  found=$((found+1))
done < <(pgrep -f '/claude .*--channels' 2>/dev/null | while read -r p; do
           # 只要真正的 claude 主进程，排除 tmux/runner 包装层
           comm=$(ps -o comm= -p "$p" 2>/dev/null)
           [ "$comm" = "claude" ] && echo "$p"
         done)

[ "$found" -eq 0 ] && printf '⚠️ 没找到运行中的 claude --channels 进程\n'

printf '\n注: model 直接读 settings.json，可能比 Discord 昵称里的型号新。改任何实例前先看这张表。\n\n'
