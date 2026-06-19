# -*- coding: utf-8 -*-
"""data/shelf.json(소스 오브 트루스) -> README.md + data/shelf.js 생성.

사용법:
    py build.py

- README.md: GitHub 저장소에서 보기 좋은 목록(자동 생성)
- data/shelf.js: 웹사이트(index.html)가 읽는 전역 데이터.
  `window.SHELF_DATA = {...}` 형태라 file:// 더블클릭으로도 동작(CORS 회피).

항목을 추가/수정하려면 data/shelf.json만 고치고 이 스크립트를 실행한다.
"""
import json
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "shelf.json"
README = ROOT / "README.md"
SHELF_JS = ROOT / "data" / "shelf.js"
SITE_URL = "https://joongi007.github.io/awesome-shelf/"

def gh_anchor(text: str) -> str:
    """GitHub(github-slugger)와 동일하게 헤딩 텍스트 -> 앵커 슬러그 변환.

    유지: 글자(L)·숫자(N)·결합표시(Mn, 변형선택자 포함)·연결구두점(Pc)·공백·하이픈.
    제거: 이모지(So) 등 그 외 기호. 공백은 하이픈으로.
    """
    s = text.strip().lower()
    out = []
    for ch in s:
        cat = unicodedata.category(ch)
        if ch in " -" or cat[0] in ("L", "N") or cat in ("Mn", "Pc"):
            out.append(ch)
    return "".join(out).replace(" ", "-")


def render_readme(data: dict) -> str:
    out = []
    out.append(f"# {data['title']}")
    out.append("")
    if data.get("intro"):
        out.append(f"> {data['intro']}")
        out.append("")

    total = sum(len(s["entries"]) for s in data["sections"])
    out.append(
        f"**🌐 [웹에서 보기]({SITE_URL})** &nbsp;·&nbsp; "
        f"📂 **{total}**개 항목 &nbsp;·&nbsp; 🗂️ **{len(data['sections'])}**개 섹션"
    )
    out.append("")
    out.append(
        "<sub>⚙️ 이 파일은 `data/shelf.json`에서 자동 생성됩니다 — "
        "수정은 `data/shelf.json`을 고친 뒤 `py build.py` · "
        "자세한 방법은 [편집 가이드](GUIDE.md)</sub>")
    out.append("")

    # ── 목차 (섹션 점프 + 개수) ──
    out.append("## 📑 목차")
    out.append("")
    out.append("| 섹션 | 개수 |")
    out.append("| :--- | ---: |")
    for s in data["sections"]:
        head = f"{s['emoji']} {s['title']}"
        out.append(f"| [{head}](#{gh_anchor(head)}) | {len(s['entries'])} |")
    if data.get("archived"):
        arc_head = "🗄️ 보관함"
        out.append(f"| [{arc_head}](#{gh_anchor(arc_head)}) | {len(data['archived'])} |")
    out.append("")
    out.append("---")
    out.append("")

    # ── 섹션별 항목 ──
    for s in data["sections"]:
        out.append(f"## {s['emoji']} {s['title']}")
        out.append("")
        if s.get("note"):
            out.append(f"_{s['note']}_")
            out.append("")
        for e in s["entries"]:
            line = f"- **[{e['name']}]({e['url']})**"
            if e.get("desc"):
                line += f" — {e['desc']}"
            out.append(line)
        out.append("")
        out.append("<sub>[⬆ 목차로](#-목차)</sub>")
        out.append("")

    # ── 보관함 ──
    archived = data.get("archived", [])
    if archived:
        out.append("## 🗄️ 보관함")
        out.append("")
        out.append("_원본 링크가 사라졌지만 나중을 위해 보관해 둔 항목 (이전처·미러 포함)_")
        out.append("")
        for e in archived:
            links = " · ".join(f"[{l['label']}]({l['url']})" for l in e.get("links", []))
            line = f"- ~~[{e['name']}]({e['url']})~~ — {e.get('reason','')}"
            if links:
                line += f"  \n  ↳ {links}"
            out.append(line)
        out.append("")

    return "\n".join(out).rstrip() + "\n"


def main():
    if not DATA.exists():
        print(f"오류: {DATA} 가 없습니다. 먼저 scripts/migrate_from_readme.py 를 실행하세요.")
        return 1
    data = json.loads(DATA.read_text(encoding="utf-8"))

    README.write_text(render_readme(data), encoding="utf-8")

    # 웹사이트용 전역 데이터(파일 프로토콜에서도 동작)
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    SHELF_JS.write_text(f"window.SHELF_DATA = {payload};\n", encoding="utf-8")

    total = sum(len(s["entries"]) for s in data["sections"])
    print(f"README.md + data/shelf.js 생성 완료 "
          f"(섹션 {len(data['sections'])}개, 항목 {total}개, 보관함 {len(data.get('archived', []))}개)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
