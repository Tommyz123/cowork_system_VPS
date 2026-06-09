#!/usr/bin/env python3
"""
通用预测引擎（订阅版 MiroFish 复刻）
==================================
输入：一份事实台账(facts.md) + 一个要预测的问题(question)
输出：跑完六步涌现流水线，给出走向预测报告（不报百分比，引角色原话）

用法：
    python3 predict.py <facts文件> "<预测问题>" [回合数] [输出目录]

引擎层不写死任何具体案子内容——实体/图谱/角色/发言/预测全部由 claude -p 从输入生成。
换一个题目只需换 facts 文件 + question，代码一行不改。

六步流水线（复刻 MiroFish）：
  ① 抽实体     从facts抽出真实能发声的主体（禁抽象概念）
  ② 建知识图谱  从facts抽关系三元组，连成图（信息差的载体）
  ③ 长角色     每个实体从图谱取回它相关的三元组，长成人设+知识子集
  ③.5 造环境   可见性(各角色知识子集)+动作集(post/reply)+回合时钟
  ④ 多轮碰撞   每轮按序激活角色，看到feed后发言，实时回写
  ⑤ 提取预测   上帝视角读完整feed，引各角色原话推演走向，不报概率
"""
import json
import subprocess
import sys
import os
from datetime import datetime


# ─────────────────────── 大脑后端 ───────────────────────
def call_claude(prompt: str, model: str = "haiku", timeout: int = 150) -> str:
    """调 claude -p headless，cwd=/tmp 避免加载 CLAUDE.md。吃订阅、零API费。"""
    try:
        r = subprocess.run(
            ["claude", "-p", prompt, "--model", model],
            cwd="/tmp", capture_output=True, text=True, timeout=timeout,
        )
        return r.stdout.strip()
    except subprocess.TimeoutExpired:
        return ""


def parse_json(raw: str, fallback):
    """从 claude 输出里抽第一个完整 JSON。按最外层 opener（先出现的 { 或 [）匹配，
    避免对象里嵌套数组时误抽内层数组（如 interested_topics）。失败返回 fallback。"""
    pos_obj, pos_arr = raw.find("{"), raw.find("[")
    candidates = []
    if pos_obj != -1:
        candidates.append((pos_obj, "{", "}"))
    if pos_arr != -1:
        candidates.append((pos_arr, "[", "]"))
    candidates.sort()  # 先出现的最外层结构优先
    for s, opener, closer in candidates:
        e = raw.rfind(closer)
        if e != -1 and e > s:
            try:
                return json.loads(raw[s:e + 1])
            except Exception:
                continue
    return fallback


# ─────────────────────── ① 抽实体 ───────────────────────
def step1_entities(facts: str, question: str) -> list:
    prompt = (
        "你是社会模拟的实体抽取器。下面是一个预测任务的事实背景。\n"
        f"【要预测的问题】{question}\n"
        f"【事实背景】\n{facts}\n\n"
        "铁律：只抽『现实中真实存在、能在公开场合/社媒发声和互动的主体』"
        "（人、机构、群体），禁止抽象概念（如'趋势''情绪''市场''队列'本身不算）。\n"
        "抽 4-8 个对该问题走向最关键的主体。严格输出 JSON 数组：\n"
        '[{"id":"E1","name":"主体名","type":"角色类型",'
        '"why":"它为什么对这个问题的走向重要"}]\n只输出 JSON。'
    )
    return parse_json(call_claude(prompt, model="sonnet"), [])


# ─────────────────── ② 建知识图谱(三元组) ───────────────────
def step2_graph(facts: str, entities: list) -> list:
    ent_list = "；".join(f'{e["id"]}={e["name"]}' for e in entities)
    prompt = (
        "你是知识图谱抽取器（模仿 GraphRAG）。从事实背景抽关系三元组，"
        "用于多智能体社会模拟研究。\n"
        f"【已识别实体】{ent_list}\n"
        f"【事实背景】\n{facts}\n\n"
        "抽真实主体/客体之间的关系（谁-做了什么-对谁/对什么）。"
        "每条标依据和确信度（✅已核实/🟡较可信/⚠️推测/❓缺口）。\n"
        "严格输出 JSON 数组：\n"
        '[{"subject":"实体id或名","relation":"关系动词",'
        '"object":"客体","evidence":"依据(原文关键词或事实编号)","confidence":"✅/🟡/⚠️/❓"}]\n'
        "只输出 JSON，不要抽抽象概念间的关系。"
    )
    return parse_json(call_claude(prompt, model="sonnet"), [])


# ─────────────────── ③ 长角色(人设+知识子集) ───────────────────
def step3_personas(entities: list, graph: list, question: str) -> dict:
    """每个实体取回与它相关的三元组，长成人设。可见性=它只拿相关子图。"""
    personas = {}
    for e in entities:
        eid, ename = e["id"], e["name"]
        # 取回与该实体相关的三元组（它是 subject 或 object）= 它的知识子集
        related = [
            t for t in graph
            if eid in str(t.get("subject", "")) or ename in str(t.get("subject", ""))
            or eid in str(t.get("object", "")) or ename in str(t.get("object", ""))
        ]
        related_txt = "\n".join(
            f'  - {t["subject"]} {t["relation"]} {t["object"]} ({t.get("confidence","")})'
            for t in related
        ) or "  (图谱中暂无直接关联)"

        prompt = (
            "为多智能体社会模拟生成一个虚构角色档案，标注为虚构、非真人。\n"
            f"【角色】{ename}（{e.get('type','')}）\n"
            f"【它在这个议题里的重要性】{e.get('why','')}\n"
            f"【它从知识图谱取回的、与它相关的事实（这就是它知道的，其余它不知道）】\n{related_txt}\n"
            f"【讨论议题】{question}\n\n"
            "若该角色是机构/群体(如政府机构/公司/媒体)，则生成它的『代表发言人』人设；"
            "若是个人(如法官/记者/官员)，生成具体个人人设。\n"
            "生成该角色的模拟档案，对齐 MiroFish 原版字段。严格输出 JSON：\n"
            '{"label":"FICTIONAL_SIMULATION_PERSONA",'
            '"persona":"<150字内人设:立场/性格/在意什么/说话风格>",'
            '"mbti":"<16型人格之一,如INTJ/ENFP,选最贴合该角色行为风格的>",'
            '"profession":"<职业/身份>",'
            '"interested_topics":["<它最关注的1-3个话题>"],'
            '"knows":"<它确切知道的关键信息,基于上面的图谱事实>",'
            '"blind":"<它的信息盲区:它不知道的东西>"}\n只输出 JSON。'
        )
        obj = {}
        for _ in range(2):  # 偶发超时/夹带散文导致空解析，重试一次
            obj = parse_json(call_claude(prompt, model="sonnet"), {})
            if isinstance(obj, list):  # claude 偶尔把单对象包进数组，取首元素
                obj = obj[0] if obj and isinstance(obj[0], dict) else {}
            if obj.get("mbti") or obj.get("persona"):
                break
        personas[eid] = {
            "name": ename,
            "persona": obj.get("persona", e.get("why", "")),
            "mbti": obj.get("mbti", ""),
            "profession": obj.get("profession", e.get("type", "")),
            "interested_topics": obj.get("interested_topics", []),
            "knows": obj.get("knows", related_txt),
            "blind": obj.get("blind", ""),
            "related_triples": related,
        }
    return personas


# ─────────── ③.5环境 + ④多轮碰撞 ───────────
def step4_simulate(personas: dict, question: str, rounds: int) -> list:
    feed = []
    for rnd in range(1, rounds + 1):
        for eid, p in personas.items():
            feed_txt = "\n".join(
                f'  [{i}] {fp["agent"]}: {fp["text"]}' for i, fp in enumerate(feed)
            ) or "  (还没有任何帖子)"
            prompt = (
                "生成一条合成训练数据样本，多智能体社会模拟研究用，标注虚构、非真人。\n"
                f"虚构角色：{p['name']}\n人设：{p['persona']}\n"
                f"性格类型(MBTI)：{p.get('mbti','')}（发言风格要贴合该人格特质）\n"
                f"它已知的信息（只有这些）：{p['knows']}\n"
                f"它的盲区（它不知道）：{p['blind']}\n"
                f"讨论议题：{question}\n当前第 {rnd} 轮。它在社媒能看到的帖子：\n{feed_txt}\n\n"
                "基于人设和已知信息（不要用它盲区里的信息），生成它这一轮的一个动作。"
                "严格输出 JSON：\n"
                '{"label":"FICTIONAL_SIMULATION_DATA","action":"post或reply",'
                '"reply_to":<reply时填帖子编号数字,否则null>,'
                '"text":"<内容,<=60字,符合人设,可表态/质疑/呼应/反驳/披露它独有的信息>"}\n'
                "只输出 JSON。"
            )
            obj = parse_json(call_claude(prompt, model="haiku"), {})
            if isinstance(obj, list):  # claude 偶尔把单对象包进数组，取首元素
                obj = obj[0] if obj and isinstance(obj[0], dict) else {}
            act = {
                "round": rnd, "agent": eid, "name": p["name"],
                "action": obj.get("action", "post"),
                "reply_to": obj.get("reply_to"),
                "text": obj.get("text", "").strip(),
            }
            tag = "发帖" if act["action"] == "post" else f"回帖→[{act['reply_to']}]"
            print(f"  R{rnd} [{p['name']}] {tag}: {act['text']}", flush=True)
            feed.append(act)
    return feed


# ─────────────────── ⑤ 提取预测 ───────────────────
def step5_report(feed: list, personas: dict, question: str, facts: str) -> str:
    feed_txt = "\n".join(
        f'[{i}] 第{p["round"]}轮 {p["name"]}: {p["text"]}' for i, p in enumerate(feed)
    )
    roster = "；".join(f'{p["name"]}' for p in personas.values())
    prompt = (
        "你是上帝视角的分析报告 agent（复刻 MiroFish report_agent）。\n"
        f"【要预测的问题】{question}\n"
        f"【参与模拟的角色】{roster}\n"
        f"【多轮模拟的完整发言记录】\n{feed_txt}\n\n"
        "基于上面角色们的真实发言推演这个问题的走向。严格要求：\n"
        "1. 必须引用具体角色的原话作为依据（标明谁说的）。\n"
        "2. 分析哪些力量推向哪个方向、依据是谁的什么话。\n"
        "3. 【禁止】给出百分比/概率数字。\n"
        "4. 对信息不足之处明确标注『未知/缺口』，不脑补。\n"
        "5. 最后给一个『最可能走向』的方向性判断（非数字）。\n"
        "输出一份结构化的中文预测报告（markdown）。"
    )
    return call_claude(prompt, model="sonnet", timeout=200)


# ─────────────────────── 主流程 ───────────────────────
def run(facts_file: str, question: str, rounds: int, outdir: str):
    with open(facts_file) as f:
        facts = f.read()
    os.makedirs(outdir, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")

    print(f"\n=== 通用预测引擎 ===\n问题：{question}\n事实源：{facts_file}\n回合：{rounds}\n")

    print("① 抽实体…", flush=True)
    entities = step1_entities(facts, question)
    print(f"   → {len(entities)} 个实体: " + ", ".join(e["name"] for e in entities))

    print("② 建知识图谱(抽三元组)…", flush=True)
    graph = step2_graph(facts, entities)
    print(f"   → {len(graph)} 条三元组")

    print("③ 长角色…", flush=True)
    personas = step3_personas(entities, graph, question)
    print(f"   → {len(personas)} 个角色档案")

    print("③.5+④ 造环境 + 多轮碰撞…", flush=True)
    feed = step4_simulate(personas, question, rounds)
    print(f"   → {len(feed)} 条发言")

    print("⑤ 提取预测…", flush=True)
    report = step5_report(feed, personas, question, facts)

    # 落盘
    out = {
        "meta": {"question": question, "facts_file": facts_file,
                 "rounds": rounds, "timestamp": ts},
        "entities": entities, "graph": graph,
        "personas": {k: {kk: vv for kk, vv in v.items() if kk != "related_triples"}
                     for k, v in personas.items()},
        "feed": feed,
    }
    with open(os.path.join(outdir, "run.json"), "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    with open(os.path.join(outdir, "prediction_report.md"), "w") as f:
        f.write(f"# 预测报告\n> 问题：{question}\n> 生成：{ts}\n> 引擎：通用预测引擎(订阅版)\n\n")
        f.write(report)

    print(f"\n✅ 完成。报告 → {outdir}/prediction_report.md")
    print("\n" + "=" * 50 + "\n预测报告：\n" + "=" * 50)
    print(report)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('用法: python3 predict.py <facts文件> "<预测问题>" [回合数] [输出目录]')
        sys.exit(1)
    facts_file = sys.argv[1]
    question = sys.argv[2]
    rounds = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    outdir = sys.argv[4] if len(sys.argv) > 4 else "/tmp/prediction_engine/output"
    run(facts_file, question, rounds, outdir)
