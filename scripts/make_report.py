# -*- coding: utf-8 -*-
"""verify_results.json + shelf.json -> data/verify_report.md (사람이 검토할 리포트)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
shelf = json.loads((ROOT / "data" / "shelf.json").read_text(encoding="utf-8"))
results = json.loads((ROOT / "data" / "verify_results.json").read_text(encoding="utf-8"))

SECTION_TITLE = {s["key"]: f"{s['emoji']} {s['title']}" for s in shelf["sections"]}

# flat 인덱스 -> 원본 항목
flat = []
for s in shelf["sections"]:
    for e in s["entries"]:
        flat.append({**e, "section": s["key"]})

res_by_idx = {r["idx"]: r for r in results}

dead, blocked = [], []
section_moves, desc_issues = [], []
ok = 0
for i, e in enumerate(flat):
    r = res_by_idx.get(i, {})
    st = r.get("status", "?")
    if st == "ok":
        ok += 1
    elif st == "dead":
        dead.append((i, e, r))
    elif st == "blocked":
        blocked.append((i, e, r))
    if r.get("suggested_section"):
        section_moves.append((i, e, r))
    if r.get("current_desc_issue"):
        desc_issues.append((i, e, r))

out = []
out.append("# 🔍 링크 검증 리포트")
out.append("")
out.append(f"- 전체 {len(flat)}개 · 정상 {ok} · 죽은 링크 {len(dead)} · 확인 불가(차단/로그인) {len(blocked)}")
out.append(f"- 분류 이동 제안 {len(section_moves)}건 · 설명/태그 이슈 {len(desc_issues)}건")
out.append("")

out.append("## ☠️ 죽은 링크 (조치 필요)")
out.append("")
if dead:
    for i, e, r in dead:
        out.append(f"- [{i}] [{e['name']}]({e['url']}) — {r.get('current_desc_issue','')}")
else:
    out.append("- 없음")
out.append("")

out.append("## 🚧 확인 불가 (페이지는 있으나 봇 차단/로그인 필요 — 대부분 정상 서비스)")
out.append("")
for i, e, r in blocked:
    out.append(f"- [{i}] [{e['name']}]({e['url']})")
out.append("")

out.append("## 🔀 분류 이동 제안")
out.append("")
out.append("| idx | 항목 | 현재 | 제안 |")
out.append("|----:|------|------|------|")
for i, e, r in section_moves:
    out.append(f"| {i} | [{e['name']}]({e['url']}) | {e['section']} | **{r['suggested_section']}** |")
out.append("")

out.append("## ⚠️ 설명·태그 이슈 (사실 오류/오타/오해 소지)")
out.append("")
out.append("| idx | 항목 | 지적 사항 | 제안 요약 |")
out.append("|----:|------|-----------|-----------|")
for i, e, r in desc_issues:
    out.append(f"| {i} | [{e['name']}]({e['url']}) | {r['current_desc_issue']} | {r.get('summary','')} |")
out.append("")

out.append("## 📝 전체 재요약 (섹션별: 기존 → 제안)")
out.append("")
cur_section = None
for i, e in enumerate(flat):
    if e["section"] != cur_section:
        cur_section = e["section"]
        out.append("")
        out.append(f"### {SECTION_TITLE.get(cur_section, cur_section)}")
        out.append("")
    r = res_by_idx.get(i, {})
    new = r.get("summary", "")
    flag = {"dead": " ☠️", "blocked": " 🚧"}.get(r.get("status"), "")
    if not new:
        out.append(f"- **{e['name']}**{flag}  \n  기존: {e['desc']}")
    else:
        out.append(f"- **{e['name']}**{flag}  \n  기존: {e['desc']}  \n  제안: {new}")
out.append("")

(ROOT / "data" / "verify_report.md").write_text("\n".join(out), encoding="utf-8")
print(f"리포트 생성: data/verify_report.md")
print(f"정상 {ok} / 죽은 {len(dead)} / 확인불가 {len(blocked)} / 이동제안 {len(section_moves)} / 설명이슈 {len(desc_issues)}")
