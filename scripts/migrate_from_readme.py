# -*- coding: utf-8 -*-
"""기존 README.md를 파싱해서 data/shelf.json(소스 오브 트루스)을 1회 생성한다.

이후로는 data/shelf.json을 직접 수정하고 `py build.py`로 README를 재생성한다.
이 스크립트는 마이그레이션 용도이므로 보통 한 번만 실행한다.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
OUT = ROOT / "data" / "shelf.json"

# 헤딩(이모지 포함) -> (key, emoji, title) 매핑
SECTION_MAP = {
    "Awesome 리스트 저장소": ("awesome-list", "📦", "Awesome 리스트 저장소"),
    "좋아 보이는 오픈소스": ("open-source", "🛠️", "좋아 보이는 오픈소스"),
    "좋아 보이는 AI 서비스": ("ai-service", "🤖", "좋아 보이는 AI 서비스"),
    "좋아 보이는 AI 관련 프로젝트 또는 모델": ("ai-project", "🧠", "좋아 보이는 AI 관련 프로젝트 또는 모델"),
    "프롬프트": ("prompt", "✏️", "프롬프트"),
    "보안": ("security", "🚨", "보안"),
    "기사, 블로그 또는 자료": ("article", "📖", "기사, 블로그 또는 자료"),
    "이 외의 것": ("misc", "🧩", "이 외의 것"),
}

# (정규식 패턴, 태그) — name+desc 소문자 문자열에 매칭되면 태그 부여
TAG_RULES = [
    (r"\brust\b|러스트|rust로", "rust"),
    (r"\bgolang\b|\bgo로|go언어", "go"),
    (r"파이썬|python", "python"),
    (r"typescript|타입스크립트", "typescript"),
    (r"\breact\b|리액트", "react"),
    (r"next\.?js|nextjs", "nextjs"),
    (r"자체 호스팅|self.?host|셀프 호스팅|self hosted", "self-hosted"),
    (r"\bcli\b|터미널|명령(어|줄)|command.?line|셸 명령", "cli"),
    (r"데스크톱|desktop", "desktop"),
    (r"대시보드|dashboard", "dashboard"),
    (r"\bui\b|ui 키트|컴포넌트|아이콘", "ui"),
    (r"프레임워크|framework", "framework"),
    (r"라이브러리|library", "library"),
    (r"템플릿|template", "template"),
    (r"\bapi\b", "api"),
    (r"\bmcp\b|model context protocol", "mcp"),
    (r"에이전트|\bagent", "agent"),
    (r"\bllm\b|언어 ?모델|대규모 언어|language model|챗봇|chatbot", "llm"),
    (r"\brag\b|retrieval.?augmented", "rag"),
    (r"음성 ?(합성|변환|생성)|\btts\b|text.?to.?speech", "tts"),
    (r"음성 ?인식|\basr\b|speech.?to.?text|\bstt\b|자막", "stt"),
    (r"오디오|audio|음악|음성", "audio"),
    (r"이미지 ?(생성|편집)|text.?to.?image|이미지를 생성", "image-gen"),
    (r"비디오 ?(생성|제작)|동영상|영상 ?(생성|제작)|video ?(생성|generation)|text.?to.?video", "video-gen"),
    (r"\bocr\b|문서를 .*구조화|문자 인식", "ocr"),
    (r"번역|translat", "translation"),
    (r"자동화|automation|워크플로우|workflow", "automation"),
    (r"모니터링|monitor|트래픽", "monitoring"),
    (r"스토리지|storage|파일 서버|object stor", "storage"),
    (r"데이터베이스|database|\bdb\b|\bsql\b|er 다이어그램", "database"),
    (r"다이어그램|diagram", "diagram"),
    (r"보안|security|취약|침투|피싱|phish|트로이|랫|\brat\b|exploit|payload|cve|악성", "security"),
    (r"침투 ?테스트|pentest|penetration", "pentest"),
    (r"\bdevops\b|데브옵스", "devops"),
    (r"쿠버네티스|kubernetes|k8s", "kubernetes"),
    (r"도커|docker|컨테이너|container", "docker"),
    (r"미세 ?조정|fine.?tun|파인튜닝", "fine-tuning"),
    (r"데이터 ?세트|dataset|레이블|주석|annotation", "dataset"),
    (r"로드맵|roadmap", "roadmap"),
    (r"튜토리얼|자습서|tutorial|레슨|수업|강의|교육|course", "tutorial"),
    (r"\bpdf\b", "pdf"),
    (r"메모|note.?taking|노트", "note-taking"),
    (r"금융|finance|포트폴리오|주식", "finance"),
    (r"로봇|robot", "robotics"),
    (r"\bwindows\b|윈도우|작업 표시줄", "windows"),
    (r"애니메이션|animation", "animation"),
    (r"\b3d\b|three\.js|cad", "3d"),
    (r"프롬프트|prompt", "prompt"),
    (r"탈옥|jailbreak|유출된|leaked|\bdan\b", "jailbreak"),
    (r"프레젠테이션|슬라이드|presentation|slide", "presentation"),
    (r"게임|game", "game"),
    (r"데이터 ?엔지니어|data engineer", "data-engineering"),
    (r"알고리즘|algorithm", "algorithm"),
    (r"vision|컴퓨터 비전|객체 검출|이미지 편집|얼굴", "vision"),
    (r"openai|chatgpt|gpt|codex|\bsora\b", "openai"),
    (r"anthropic|claude", "anthropic"),
    (r"구글|google|gemini|gemma", "google"),
    (r"마이크로소프트|microsoft|copilot", "microsoft"),
    (r"바이트댄스|bytedance|capcut|캡컷", "bytedance"),
    (r"네이버|naver|clova|클로바|한국|korean|수능", "korean"),
]

LINE_RE = re.compile(r"^- \[(?P<name>[^\]]+)\]\((?P<url>[^)]+)\)\s*[-–—]?\s*(?P<desc>.*)$")


def auto_tags(name: str, desc: str) -> list:
    text = f"{name} {desc}".lower()
    tags = []
    for pat, tag in TAG_RULES:
        if re.search(pat, text):
            if tag not in tags:
                tags.append(tag)
    return tags


def main():
    text = README.read_text(encoding="utf-8")
    lines = text.splitlines()

    sections = []  # [{key, emoji, title, note, entries:[]}]
    current = None
    pending_note = None
    seen_urls = {}
    dupes = []

    for raw in lines:
        line = raw.rstrip()
        if line.startswith("## "):
            head = line[3:].strip()
            # 앞쪽 이모지 제거하고 텍스트만 추출
            key = None
            for title_text, (k, emoji, title) in SECTION_MAP.items():
                if title_text in head:
                    key = k
                    current = {"key": k, "emoji": emoji, "title": title, "note": "", "entries": []}
                    sections.append(current)
                    pending_note = "await"
                    break
            if key is None:
                current = None
            continue

        if current is None:
            continue

        if pending_note == "await" and line.startswith(">"):
            current["note"] = line.lstrip("> ").strip()
            pending_note = None
            continue

        m = LINE_RE.match(line)
        if m:
            name = m.group("name").strip()
            url = m.group("url").strip()
            desc = m.group("desc").strip()
            entry = {
                "name": name,
                "url": url,
                "desc": desc,
                "tags": auto_tags(name, desc),
            }
            if url in seen_urls:
                dupes.append((url, seen_urls[url], current["key"]))
            else:
                seen_urls[url] = current["key"]
            current["entries"].append(entry)

    title_line = lines[0].lstrip("# ").strip() if lines else "Awesome Shelf"
    intro = ""
    for line in lines[1:6]:
        if line.startswith(">"):
            intro = line.lstrip("> ").strip()
            break

    data = {
        "title": title_line,
        "intro": intro,
        "sections": sections,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    total = sum(len(s["entries"]) for s in sections)
    print(f"섹션 {len(sections)}개, 항목 {total}개 -> {OUT.relative_to(ROOT)}")
    for s in sections:
        print(f"  [{s['key']}] {len(s['entries'])}개")
    if dupes:
        print("\n중복 URL(여러 섹션/위치에 등장):")
        for url, first, where in dupes:
            print(f"  - {url} (먼저: {first}, 또: {where})")


if __name__ == "__main__":
    sys.exit(main())
