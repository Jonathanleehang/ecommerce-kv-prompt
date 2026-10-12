#!/usr/bin/env python3
"""校验电商 KV 提示词产出物。

用法:
    python3 validate_kv.py <产出.json> [配套.md]

检查项:
  1. JSON 可解析
  2. meta / recognition / decision / global_constraints / logo / posters 六大块齐全
  3. posters 数量与 meta.poster_count 一致
  4. 每张海报六件套齐全: 中文提示词 / 英文Prompt / 负面词 / 排版说明 / LOGO位置 / CTA
  5. 中文提示词 600-1000 字
  6. 负面词 20-30 个
  7. 画面文字都是中英文成对出现(排版表里 text_zh 有值时 text_en 不得为空, CTA/标题类元素)
  8. Markdown 里 10 个小节编号齐全(可选)

退出码 0 表示全部通过, 1 表示有 FAIL, 2 表示用法错误。
"""

import json
import re
import sys
from pathlib import Path

EXPECTED_ROLES = {
    "01": "主KV视觉",
    "02": "生活场景",
    "03": "工艺/概念",
    "04": "细节特写01",
    "05": "细节特写02",
    "06": "细节特写03",
    "07": "细节特写04或评价",
    "08": "品牌故事",
    "09": "参数规格",
    "10": "使用指南",
}

SINGLE_LANG_OK = {"单语", "LOGO"}


def check(problems, ok_list, name, cond, detail=""):
    (ok_list if cond else problems).append(f"{name}{(' — ' + detail) if detail else ''}")


def validate_json(path: Path):
    problems, oks = [], []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"JSON 解析失败: {e}"], []

    # 2. 六大块
    for block in ("meta", "recognition", "decision", "global_constraints", "logo", "posters"):
        check(problems, oks, f"顶层含 {block}", block in data)

    if "meta" not in data or "posters" not in data:
        return problems, oks

    meta, posters = data["meta"], data["posters"]

    # 3. 张数
    want = meta.get("poster_count", 10)
    check(problems, oks, "海报张数", len(posters) == want, f"期望 {want}, 实际 {len(posters)}")

    # meta 必填
    for k in ("visual_style", "typography_style", "aspect_ratio", "title_bilingual_format"):
        check(problems, oks, f"meta.{k}", bool(meta.get(k)), "字段缺失或为空")

    # recognition 必填
    rec = data.get("recognition", {})
    sp = rec.get("selling_points", [])
    check(problems, oks, "核心卖点 >= 3 条", len(sp) >= 3, f"实际 {len(sp)} 条")
    colors = rec.get("colors", {}).get("primary", [])
    check(problems, oks, "主色调 >= 1 个", len(colors) >= 1)
    for c in colors + rec.get("colors", {}).get("secondary", []) + rec.get("colors", {}).get("accent", []):
        check(problems, oks, f"色值格式 {c.get('name', '?')}", bool(re.fullmatch(r"#[0-9A-Fa-f]{6}", c.get("hex", ""))), c.get("hex", ""))

    # global_constraints
    gc = data.get("global_constraints", {})
    check(problems, oks, "全局产品还原约束", "严格还原" in gc.get("product_fidelity", ""))
    check(problems, oks, "全局 LOGO 位置", bool(gc.get("logo_placement")))

    # logo 块
    logo = data.get("logo", {})
    for k in ("prompt_zh", "prompt_en"):
        check(problems, oks, f"logo.{k}", bool(logo.get(k)))
    n = len(logo.get("negative", []))
    check(problems, oks, "logo.negative 数量 20-30", 20 <= n <= 30, f"实际 {n}")

    # 4-7. 逐张海报
    seen_ids = set()
    for i, p in enumerate(posters):
        pid = p.get("id", str(i + 1).zfill(2))
        seen_ids.add(str(pid))
        tag = f"海报 {pid}"

        check(problems, oks, f"{tag} 有 role", bool(p.get("role")))
        check(problems, oks, f"{tag} 有 function", bool(p.get("function")))

        zh = p.get("prompt_zh", "")
        check(problems, oks, f"{tag} 中文提示词非空", bool(zh))
        if zh:
            check(problems, oks, f"{tag} 中文提示词 600-1000 字", 600 <= len(zh) <= 1000, f"实际 {len(zh)} 字")

        en = p.get("prompt_en", "")
        check(problems, oks, f"{tag} 英文 Prompt 非空", bool(en))
        if en:
            ascii_ratio = sum(1 for ch in en if ord(ch) < 128) / len(en)
            check(problems, oks, f"{tag} 英文 Prompt 主体为英文", ascii_ratio > 0.7, f"ASCII 占比 {ascii_ratio:.0%}")
            check(problems, oks, f"{tag} 英文不是中文摘要",
                  not re.match(r"^\s*(Chinese|ZH|中文)[:：]", en) and len(en) > 200, f"实际 {len(en)} 字符")

        negatives = p.get("negative", [])
        check(problems, oks, f"{tag} 负面词 20-30 个", 20 <= len(negatives) <= 30, f"实际 {len(negatives)}")
        check(problems, oks, f"{tag} 负面词无重复", len(negatives) == len(set(negatives)))

        layout = p.get("layout", [])
        check(problems, oks, f"{tag} 排版说明 >= 4 行", len(layout) >= 4, f"实际 {len(layout)}")

        has_logo = any(it.get("element", "").upper().find("LOGO") >= 0 or "LOGO" in it.get("element", "").upper() for it in layout)
        check(problems, oks, f"{tag} 排版含 LOGO 位置", has_logo)

        has_cta = any("CTA" in it.get("element", "").upper() or "按钮" in it.get("element", "") for it in layout)
        check(problems, oks, f"{tag} 排版含 CTA 按钮", has_cta)

        # 7. 双语成对
        missing_en = [
            it.get("element", "?")
            for it in layout
            if it.get("text_zh")
            and not it.get("text_en")
            and it.get("bilingual_format") not in SINGLE_LANG_OK
            and "LOGO" not in it.get("element", "").upper()
        ]
        check(problems, oks, f"{tag} 画面文字中英成对", not missing_en, "缺英文: " + "、".join(missing_en))

        # 每张LAYOUT必填字段
        bad_size = [it.get("element", "?") for it in layout if it.get("size_level") not in ("超大", "大", "中", "小")]
        check(problems, oks, f"{tag} 字号层级合法", not bad_size, "异常: " + "、".join(bad_size))

        # 出现产品的海报必须有还原约束
        if p.get("has_product"):
            check(problems, oks, f"{tag} 写了产品还原约束", "还原" in (p.get("product_fidelity_note", "") + " ".join(
                [zh, en])), "has_product=true 但未见还原描述")

        # 负面词在 10 张之间不应完全相同
    texts = [tuple(p.get("negative", [])) for p in posters]
    if len(texts) > 1 and len(set(texts)) == 1:
        problems.append("10 张海报负面词完全相同 — 不同场景应配不同的针对性负面词")

    missing_roles = set(EXPECTED_ROLES) - seen_ids
    check(problems, oks, "10 张编号齐全 (01-10)", not missing_roles, "缺: " + "、".join(sorted(missing_roles)))

    return problems, oks


def validate_md(md: Path):
    problems, oks = [], []
    if not md.exists():
        return [f"Markdown 不存在: {md}"], []
    text = md.read_text(encoding="utf-8")
    check(problems, oks, "含识别报告小节", "【识别报告】" in text or "识别报告" in text)
    for num in range(1, 11):
        found = re.search(rf"海报\s*{num:02d}|海报\s*{num}\b|海报{num:02d}", text)
        check(problems, oks, f"含海报 {num:02d} 小节", bool(found))
    check(problems, oks, "含 LOGO 生成提示词小节", "LOGO" in text and ("LOGO 生成提示词" in text or "LOGO生成提示词" in text))
    return problems, oks


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    jp = Path(sys.argv[1])

    all_problems, all_oks = [], []
    p1, o1 = validate_json(jp)
    all_problems += p1
    all_oks += o1

    if len(sys.argv) > 2:
        p2, o2 = validate_md(Path(sys.argv[2]))
        all_problems += p2
        all_oks += o2

    print(f"检查通过 {len(all_oks)} 项")
    if all_problems:
        print(f"\n发现问题 {len(all_problems)} 项:")
        for x in all_problems:
            print("  [FAIL]", x)
        return 1
    print("\n全部通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
