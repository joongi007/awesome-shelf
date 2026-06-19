# -*- coding: utf-8 -*-
"""shelf.json을 검증용 배치 파일로 분할한다. (링크 검증 에이전트 입력용, 임시)"""
import json, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "shelf.json"
OUTDIR = ROOT / "data" / "_batches"
BATCH = 27

d = json.loads(DATA.read_text(encoding="utf-8"))
flat = []
idx = 0
for s in d["sections"]:
    for e in s["entries"]:
        flat.append({"idx": idx, "section": s["key"], "name": e["name"],
                     "url": e["url"], "desc": e["desc"], "tags": e.get("tags", [])})
        idx += 1

if OUTDIR.exists():
    shutil.rmtree(OUTDIR)
OUTDIR.mkdir(parents=True)

n = 0
for i in range(0, len(flat), BATCH):
    chunk = flat[i:i + BATCH]
    p = OUTDIR / f"batch_{n:02d}.json"
    p.write_text(json.dumps(chunk, ensure_ascii=False, indent=2), encoding="utf-8")
    n += 1

print(f"{len(flat)}개 항목 -> {n}개 배치 (배치당 최대 {BATCH}개)")
print(f"섹션 key 목록: {[s['key'] for s in d['sections']]}")
