#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_draft.py — 计算机模型类发明专利成稿闭环自检

用法:
    python check_draft.py <成稿.md> [--matrix mapping_matrix.csv] [--count-only]
    python check_draft.py <成稿.md> --json        # 机器可读输出

检查项:
    1  章节完整性            四大部分是否齐全
    2  技术问题字数          300-500（计入中文字符与英文字母数字，不计空白与标点）
    3  痛点->特征覆盖        每个 P* 是否在技术方案中出现
    4  痛点->效果覆盖        每个 P* 是否在技术效果中出现
    5  孤儿特征/孤儿效果     必要技术特征/效果是否有对应痛点
    6  禁用词                营销夸张 / 模糊 / 论文式抒情 / AI 腔
    7  术语一致性            英文缩写多种中文译名、近义模块名混用
    8  附图标记一致性        附图说明中的标记与图中标记表是否匹配
    9  数值出处提示          列出成稿中的百分比/倍数表述，提示人工核对出处

退出码: 0 = 全部 PASS；1 = 存在 FAIL；2 = 用法/读取错误
"""

import argparse
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

MIN_WORDS, MAX_WORDS = 300, 500

SECTION_PATTERNS = {
    "技术问题": r"^#{1,4}\s*一[、.．]\s*技术问题",
    "技术方案": r"^#{1,4}\s*二[、.．]\s*技术方案",
    "技术效果": r"^#{1,4}\s*三[、.．]\s*技术效果",
    "附图方案": r"^#{1,4}\s*四[、.．]\s*专利说明书附图方案",
}

FORBIDDEN = {
    "营销夸张": ["极大地", "极大提升", "革命性", "颠覆性", "完美", "彻底解决", "根本性突破",
                 "显著优于一切", "远超现有", "全面超越", "史无前例"],
    "模糊不定": ["大约", "大概", "可能是", "最好是", "适当的", "一定的", "等等", "若干种"],
    "论文式抒情": ["值得注意的是", "令人遗憾的是", "不难发现", "众所周知", "我们希望",
                   "毋庸置疑", "需要说明的", "可以看出"],
    "主观评价": ["效果很好", "性能优越", "智能化程度高", "用户体验佳", "非常优秀"],
    "绝对化": ["总是能够", "必然能够", "所有情况下均", "在任何场景下均"],
    "无依据比较": ["数倍于", "远远优于", "大幅度领先"],
    "宣传性命名": ["新一代", "超级智能", "颠覆式"],
    "AI腔": ["综上所述", "总而言之", "值得一提的是", "希望本文", "总的来说"],
}

# 术语一致性：常见近义混用词根（成对检测）
SYNONYM_PAIRS = [
    ("特征提取", "特征抽取"),
    ("特征融合", "特征聚合"),
    ("注意力加权", "注意力赋权"),
    ("归一化", "标准化"),
    ("损失函数", "代价函数"),
    ("置信度", "可信度"),
    ("阈值", "门限"),
    ("采样率", "抽样率"),
]

PUNCT_RANGES = [(0x2000, 0x206F), (0x3000, 0x303F), (0xFF00, 0xFFEF)]


def is_punct(ch: str) -> bool:
    if ch.isspace():
        return True
    cat = unicodedata.category(ch)
    if cat.startswith("P"):
        return True
    if ch in ".,;:!?\"'`~@#$%^&*()[]{}<>\\/|+-_=":
        return True
    cp = ord(ch)
    return any(a <= cp <= b for a, b in PUNCT_RANGES)


def content_chars(text: str) -> int:
    """统计正文字符数：中文字符 + 英文字母 + 数字，不计空白与标点。"""
    return sum(1 for ch in text if not is_punct(ch))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def split_sections(text: str) -> dict:
    """按四大标题切分，返回 {名称: (起, 止)} 字符索引。"""
    lines = text.splitlines()
    hits = {}
    for idx, line in enumerate(lines):
        for name, pat in SECTION_PATTERNS.items():
            if re.match(pat, line.strip()):
                hits.setdefault(name, []).append(idx)
    out = {}
    order = ["技术问题", "技术方案", "技术效果", "附图方案"]
    for i, name in enumerate(order):
        if name not in hits:
            continue
        start = hits[name][0] + 1
        end = len(lines)
        for nxt in order[i + 1:]:
            if nxt in hits:
                end = hits[nxt][0]
                break
        out[name] = "\n".join(lines[start:end])
    return out


def clean_problem_text(section: str) -> str:
    """剥离标题、表格、层级标签与字数标注，仅保留问题正文。"""
    keep = []
    for line in section.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            continue
        if s.startswith("|"):
            continue
        if re.match(r"^\**（第[一二三]层", s):
            # 形如 "**第一层 · 行业通用缺陷**" 的独占行标签
            if re.match(r"^\*\*第[一二三]层[^，。；]{0,20}\*\*$", s):
                continue
        if re.match(r"^（?本部分共计", s):
            continue
        if re.match(r"^\**痛点编号登记", s):
            break
        if re.match(r"^#{0,4}\s*\*{0,2}痛点编号登记", s):
            break
        keep.append(s)
    body = "\n".join(keep)
    body = re.sub(r"\*\*第[一二三]层[^，。；]{0,20}\*\*", "", body)
    body = re.sub(r"（本部分共计[^）]*）", "", body)
    return body


def find_pain_points(problem_section: str, matrix_path: Path | None) -> list:
    ids = re.findall(r"\bP(\d+)-(\d+)\b", problem_section)
    found = sorted({f"P{a}-{b}" for a, b in ids})
    if not found and matrix_path and matrix_path.exists():
        with matrix_path.open(encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                key = (row.get("痛点编号") or "").strip()
                if re.match(r"^P\d+-\d+$", key):
                    found.append(key)
        found = sorted(set(found))
    return found


def find_feature_ids(solution_section: str) -> list:
    return sorted({int(n) for n in re.findall(r"必要技术特征\s*(\d+)", solution_section)})


def find_effect_refs(effect_section: str) -> list:
    """返回效果段落引用的痛点编号集合。"""
    return sorted({f"P{a}-{b}" for a, b in re.findall(r"\bP(\d+)-(\d+)\b", effect_section)})


def check_marker_consistency(drawing_section: str) -> tuple:
    """附图说明中的标记 vs 模块表标记。"""
    inline = re.search(r"图中[：:]([^\n]+)", drawing_section)
    inline_ids = set()
    if inline:
        inline_ids = {m for m in re.findall(r"(\d+)\s*-", inline.group(1))}
    table_ids = set()
    for line in drawing_section.splitlines():
        s = line.strip()
        if s.startswith("|") and not re.match(r"^\|[\s\-:|]+\|$", s):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if cells and re.fullmatch(r"\d+", cells[0]):
                table_ids.add(cells[0])
    return inline_ids, table_ids


def main() -> int:
    ap = argparse.ArgumentParser(description="计算机模型类发明专利成稿闭环自检")
    ap.add_argument("draft", help="成稿 Markdown 文件路径")
    ap.add_argument("--matrix", help="三维映射表 CSV 路径", default=None)
    ap.add_argument("--count-only", action="store_true", help="仅输出技术问题字数")
    ap.add_argument("--json", action="store_true", help="以 JSON 输出")
    args = ap.parse_args()

    draft_path = Path(args.draft)
    if not draft_path.exists():
        print(f"[ERROR] 文件不存在: {draft_path}", file=sys.stderr)
        return 2
    text = read_text(draft_path)
    secs = split_sections(text)
    matrix_path = Path(args.matrix) if args.matrix else draft_path.parent / "mapping_matrix.csv"

    results = []

    def add(name, ok, detail, level="FAIL"):
        results.append({"检查项": name, "结果": "PASS" if ok else level, "说明": detail})

    # 0 字数（先算，count-only 时直接返回）
    prob_raw = secs.get("技术问题", "")
    prob_body = clean_problem_text(prob_raw)
    wc = content_chars(prob_body)
    if args.count_only:
        print(f"技术问题正文字数：{wc} 字（要求 {MIN_WORDS}-{MAX_WORDS}）")
        return 0 if MIN_WORDS <= wc <= MAX_WORDS else 1

    # 1 章节完整性
    missing = [n for n in SECTION_PATTERNS if n not in secs]
    add("1 章节完整性", not missing,
        "四大部分齐全" if not missing else f"缺少章节: {', '.join(missing)}")

    # 2 技术问题字数
    add("2 技术问题字数", MIN_WORDS <= wc <= MAX_WORDS,
        f"实际 {wc} 字（要求 {MIN_WORDS}-{MAX_WORDS}）")

    pain_ids = find_pain_points(prob_raw, matrix_path)
    sol = secs.get("技术方案", "")
    eff = secs.get("技术效果", "")

    # 3 痛点 -> 特征
    if not pain_ids:
        add("3 痛点->特征覆盖", False, "未识别到痛点编号 P*-*，请在技术问题部分登记痛点编号表")
    else:
        miss = [p for p in pain_ids if p not in sol]
        add("3 痛点->特征覆盖", not miss,
            f"共 {len(pain_ids)} 个痛点，覆盖 {len(pain_ids) - len(miss)} 个"
            + (f"；未被技术方案覆盖: {', '.join(miss)}" if miss else ""))

    # 4 痛点 -> 效果
    eff_refs = find_effect_refs(eff)
    if pain_ids:
        miss_e = [p for p in pain_ids if p not in eff_refs]
        orphans = [p for p in eff_refs if p not in pain_ids]
        ok = not miss_e and not orphans
        detail = f"共 {len(pain_ids)} 个痛点，效果引用 {len(eff_refs)} 个"
        if miss_e:
            detail += f"；未回应: {', '.join(miss_e)}"
        if orphans:
            detail += f"；孤儿效果(无对应痛点): {', '.join(orphans)}"
        add("4 痛点->效果覆盖", ok, detail)

    # 5 孤儿特征
    feat_ids = find_feature_ids(sol)
    orphan_feats = []
    for n in feat_ids:
        seg = re.search(r"必要技术特征\s*%d[：:][^\n]*" % n, sol)
        ctx = seg.group(0) if seg else ""
        nxt = re.search(r"必要技术特征\s*%d[：:].{0,400}" % n, sol, re.S)
        ctx = nxt.group(0) if nxt else ctx
        if not re.search(r"\bP\d+-\d+\b", ctx):
            orphan_feats.append(n)
    add("5 孤儿特征检查", not orphan_feats,
        f"必要技术特征 {len(feat_ids)} 条，均标注了对应痛点" if not orphan_feats
        else f"未标注对应痛点的必要技术特征: {orphan_feats}")

    # 6 禁用词
    hits = []
    for cat, words in FORBIDDEN.items():
        for w in words:
            if w in text:
                hits.append(f"{cat}:{w}")
    add("6 禁用词", not hits, "无命中" if not hits else f"命中 {len(hits)} 处 -> {', '.join(hits[:12])}",
        level="WARN")

    # 7 术语一致性
    term_issues = []
    for a, b in SYNONYM_PAIRS:
        if a in text and b in text:
            term_issues.append(f"{a}/{b} 混用")
    abbr = re.findall(r"([一-龥]{2,10})[（(]([A-Za-z][A-Za-z0-9\-]{1,9})[）)]", text)
    gloss = {}
    for cn, en in abbr:
        gloss.setdefault(en, set()).add(cn)
    for en, cns in gloss.items():
        if len(cns) > 1:
            term_issues.append(f"{en} 有多种译名: {'/'.join(sorted(cns))}")
    add("7 术语一致性", not term_issues,
        "术语统一" if not term_issues else "; ".join(term_issues), level="WARN")

    # 8 附图标记一致性
    draw = secs.get("附图方案", "")
    inline_ids, table_ids = check_marker_consistency(draw)
    if not inline_ids and not table_ids:
        add("8 附图标记一致性", False, "未识别到附图说明标记行（图中：1-…）或模块标记表")
    else:
        only_inline = sorted(inline_ids - table_ids)
        only_table = sorted(table_ids - inline_ids)
        ok = not only_inline and not only_table
        detail = f"附图说明 {len(inline_ids)} 个标记，模块表 {len(table_ids)} 个标记"
        if only_inline:
            detail += f"；仅见于附图说明: {only_inline}"
        if only_table:
            detail += f"；仅见于模块表: {only_table}"
        add("8 附图标记一致性", ok, detail, level="WARN")

    # 9 数值出处提示（永远是提示项）：列出全部带单位的量化表述
    nums = re.findall(
        r"\d+(?:\.\d+)?\s*(?:%|个百分点|倍|ms|s\b|MB|GB|GFLOPs|FLOPs|M(?![a-zA-Z])|W\b)",
        text,
    )
    flagged = [n for n in nums if n.strip()]
    add("9 数值出处核对", True,
        (f"共 {len(flagged)} 处量化表述（例：{'、'.join(flagged[:8])}），"
         f"需逐条确认有实测出处或已标注（推定）") if flagged
        else "未检出带单位的量化表述；若技术效果已给出具体数值，应核对是否均已标注出处",
        level="INFO")

    fails = [r for r in results if r["结果"] == "FAIL"]
    warns = [r for r in results if r["结果"] == "WARN"]

    if args.json:
        print(json.dumps({"字数": wc, "痛点": pain_ids, "结果": results,
                          "FAIL数": len(fails), "WARN数": len(warns)},
                         ensure_ascii=False, indent=2))
    else:
        print("=" * 62)
        print(f"自检报告：{draft_path.name}")
        print("=" * 62)
        w = max(len(r["检查项"]) for r in results)
        for r in results:
            print(f"{r['检查项']:<{w}}  {r['结果']:<5}  {r['说明']}")
        print("-" * 62)
        print(f"FAIL {len(fails)} 项 | WARN {len(warns)} 项 | 痛点 {len(pain_ids)} 个 | 技术问题 {wc} 字")
        print("结论：" + ("可交付（WARN 项建议人工复核）" if not fails else "存在 FAIL，须修稿后重跑"))

    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
