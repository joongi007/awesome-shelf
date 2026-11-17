"""shelf.json으로 README.md와 목록이 포함된 정적 index.html을 생성한다."""

import json
import re
import sys
import unicodedata
from collections import Counter
from html import escape
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).absolute().parent
DATA = ROOT / "data" / "shelf.json"
README = ROOT / "README.md"
INDEX = ROOT / "index.html"
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
        "자세한 방법은 [편집 가이드](GUIDE.md)</sub>"
    )
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
        out.append(
            f"| [{arc_head}](#{gh_anchor(arc_head)}) | {len(data['archived'])} |"
        )
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
        out.append(
            "_원본 링크가 사라졌지만 나중을 위해 보관해 둔 항목 (이전처·미러 포함)_"
        )
        out.append("")
        for e in archived:
            links = " · ".join(
                f"[{l['label']}]({l['url']})" for l in e.get("links", [])
            )
            line = f"- ~~[{e['name']}]({e['url']})~~ — {e.get('reason', '')}"
            if links:
                line += f"  \n  ↳ {links}"
            out.append(line)
        out.append("")

    return "\n".join(out).rstrip() + "\n"


def safe_url(value):
    """Only external HTTP(S) links are accepted from the catalog."""
    parsed = urlsplit(value)
    if (
        parsed.scheme not in ("https", "http")
        or not parsed.netloc
        or any(ord(c) < 32 for c in value)
    ):
        raise ValueError(f"Invalid catalog URL: {value!r}")
    return escape(value, quote=True)


def render_desc(value):
    parts, last = [], 0
    for match in re.finditer(r"\[([^\]]+)\]\((https?://[^)]+)\)", value):
        parts.append(escape(value[last : match.start()]))
        parts.append(
            f'<a href="{safe_url(match[2])}" target="_blank" rel="noopener">{escape(match[1])}</a>'
        )
        last = match.end()
    parts.append(escape(value[last:]))
    return "".join(parts)


def render_site(data):
    icons = json.loads((ROOT / "templates/icons.json").read_text(encoding="utf-8"))

    def icon(key):
        paths = icons.get(key, '<circle cx="12" cy="12" r="9"/>')
        return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">{paths}</svg>'

    def chip(tag, count=None):
        badge = f'<span class="cnt">{count}</span>' if count is not None else ""
        return f'<button class="chip" data-tag="{escape(tag)}" aria-pressed="false">#{escape(tag)}{badge}</button>'

    def card(entry):
        name, url, desc = entry["name"], entry["url"], entry.get("desc", "")
        href = safe_url(url)
        parsed = urlsplit(url)
        owner = parsed.path.strip("/").split("/")[0]
        avatar = (
            f"https://github.com/{owner}.png?size=80"
            if parsed.hostname == "github.com" and owner
            else f"https://icons.duckduckgo.com/ip3/{parsed.hostname}.ico"
        )
        mono = re.search(r"[A-Za-z0-9가-힣]", name.rsplit("/", 1)[-1])
        title = escape(name)
        if "/" in name and not name.startswith("/") and not name.endswith("/"):
            first, rest = name.split("/", 1)
            title = f'<span class="owner">{escape(first)}/</span>{escape(rest)}'
        tags = "".join(chip(t) for t in entry.get("tags", []))
        description = (
            f'<p class="desc" title="{escape(desc)}">{render_desc(desc)}</p>'
            if desc
            else ""
        )
        return (
            f'<article class="card"><div class="chead"><span class="avatar"><b>{mono[0] if mono else "#"}</b>'
            f'<img data-src="{escape(avatar)}" loading="lazy" decoding="async" width="36" height="36" alt="" referrerpolicy="no-referrer"></span>'
            f'<div class="ctitle"><a href="{href}" target="_blank" rel="noopener">{title}</a>'
            '<svg class="ext" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M7 17 17 7M7 7h10v10"/></svg></div></div>'
            f'{description}<div class="tags">{tags}</div></article>'
        )

    nav, sections = [], []
    counts = Counter()
    for section in data["sections"]:
        key = section["key"]
        if not re.fullmatch(r"[a-z][a-z0-9-]*", key):
            raise ValueError(f"Invalid section key: {key!r}")
        title, total = escape(section["title"]), len(section["entries"])
        nav.append(
            f'<a class="navrow sec-{key}" data-sec="{key}" href="#sec-{key}"><span class="ic">{icon(key)}</span><span class="nm">{title}</span><span class="ct">{total}</span></a>'
        )
        cards = "\n".join(card(e) for e in section["entries"])
        sections.append(
            f'<section class="group sec-{key}" id="sec-{key}"><div class="group-head"><span class="ic">{icon(key)}</span><h2>{title}</h2><span class="badge">{total}</span></div><div class="cards">{cards}</div></section>'
        )
        counts.update(t for e in section["entries"] for t in e.get("tags", []))
    total = sum(len(s["entries"]) for s in data["sections"])
    stats = f'<span class="stat"><b>{total}</b> 항목</span><span class="stat"><b>{len(sections)}</b> 섹션</span><span class="stat"><b>{len(counts)}</b> 태그</span>'
    archive = ""
    if data.get("archived"):
        items = []
        for entry in data["archived"]:
            links = "".join(
                f'<a href="{safe_url(link["url"])}" target="_blank" rel="noopener">{escape(link["label"])} ↗</a>'
                for link in entry.get("links", [])
            )
            items.append(
                f'<div class="arc-item"><div class="nm">{escape(entry["name"])}</div><div class="reason">{escape(entry.get("reason", ""))}</div><div class="links">{links}</div></div>'
            )
        count = len(items)
        stats += f'<span class="stat">보관 <b>{count}</b></span>'
        archive = f'<details class="archive"><summary>🗄️ 보관함 <span style="color:var(--text-faint);font-weight:500">· 사라진 링크 {count}개 (이전처·미러)</span><svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><path d="m9 18 6-6-6-6"/></svg></summary><div class="abody">{"".join(items)}</div></details>'
    title = (
        re.sub(r"^[^\w]+", "", data.get("title", "Awesome Shelf")).strip()
        or "Awesome Shelf"
    )
    values = {
        "TITLE": escape(title),
        "INTRO": escape(data.get("intro", "")),
        "SITE_URL": SITE_URL,
        "NAV": "\n".join(nav),
        "STATS": stats,
        "TOTAL": str(total),
        "SECTIONS": "\n".join(sections),
        "ARCHIVE": archive,
        "TAGS": "".join(
            chip(t, c)
            for t, c in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        ),
        "FILTER_HINT": f"· 전체 {len(counts)}개 · 여러 개 선택 시 모두 포함(AND)",
    }
    template = (ROOT / "templates/index.html").read_text(encoding="utf-8")
    return re.sub(r"\{\{([A-Z_]+)\}\}", lambda m: values[m[1]], template)


def main():
    if not DATA.exists():
        print(
            f"오류: {DATA} 가 없습니다. 먼저 scripts/migrate_from_readme.py 를 실행하세요."
        )
        return 1
    data = json.loads(DATA.read_text(encoding="utf-8"))

    html = render_site(data)

    # newline="\n": OS와 무관하게 항상 LF로 저장(Windows의 CRLF 자동변환 방지).
    # 안 그러면 로컬(CRLF)과 CI 리눅스(LF)의 결과가 매번 달라져 봇이 README를 재커밋함.
    README.write_text(render_readme(data), encoding="utf-8", newline="\n")

    INDEX.write_text(html, encoding="utf-8", newline="\n")

    total = sum(len(s["entries"]) for s in data["sections"])
    print(
        f"README.md + index.html 생성 완료 "
        f"(섹션 {len(data['sections'])}개, 항목 {total}개, 보관함 {len(data.get('archived', []))}개)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
