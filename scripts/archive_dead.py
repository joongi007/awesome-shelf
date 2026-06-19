# -*- coding: utf-8 -*-
"""죽은 링크를 섹션에서 빼서 shelf.json의 archived[] 보관함으로 옮긴다(1회성)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "shelf.json"
d = json.loads(DATA.read_text(encoding="utf-8"))

# 보관 대상: 원본 URL -> 보관 메타
ARCHIVE = {
    "https://github.com/cloudcommunity/Free-Certifications": {
        "reason": "GitHub 저장소가 삭제됨(API 404)",
        "links": [
            {"url": "https://free-certifications.com/", "label": "공식 커뮤니티 사이트(이전처)"},
            {"url": "https://web.archive.org/web/2023*/github.com/cloudcommunity/Free-Certifications",
             "label": "Internet Archive 스냅샷"},
        ],
    },
    "https://github.com/FareedKhan-dev/all-rag-techniques": {
        "reason": "저장소가 비공개 전환/삭제됨(API 404)",
        "links": [
            {"url": "https://github.com/mbergo/all-rag-techniques", "label": "포크 미러(98★)"},
        ],
    },
}

archived = d.get("archived", [])
moved = []
for s in d["sections"]:
    keep = []
    for e in s["entries"]:
        if e["url"] in ARCHIVE:
            meta = ARCHIVE[e["url"]]
            archived.append({
                "name": e["name"],
                "url": e["url"],
                "desc": e["desc"],
                "tags": e.get("tags", []),
                "from_section": s["key"],
                "reason": meta["reason"],
                "links": meta["links"],
            })
            moved.append(e["name"])
        else:
            keep.append(e)
    s["entries"] = keep

d["archived"] = archived
DATA.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("보관함으로 이동:", moved)
print("총 항목:", sum(len(s["entries"]) for s in d["sections"]), "/ 보관함:", len(archived))
