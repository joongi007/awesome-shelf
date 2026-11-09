# 🛠️ Awesome Shelf 편집 가이드

이 저장소를 어떻게 유지·관리하는지 정리한 문서입니다.
**핵심 한 줄: 모든 내용은 [`data/shelf.json`](data/shelf.json) 하나에서 나옵니다. 거길 고치고 `py build.py`만 실행하면 됩니다.**

---

## 1. 한눈에 보는 구조

```
awesome-shelf/
├─ data/
│  ├─ shelf.json        ← ★ 소스 오브 트루스 (여기만 편집)
│  ├─ shelf.js          ← (자동 생성) 웹사이트가 읽는 데이터
│  ├─ verify_report.md  ← 링크 검증 리포트 (1회성 기록)
│  └─ verify_results.json
├─ index.html           ← 웹사이트 (단일 페이지, shelf.js를 읽어 렌더)
├─ README.md            ← (자동 생성) GitHub에서 보이는 목록
├─ build.py             ← ★ shelf.json → README.md + shelf.js 생성기
├─ scripts/             ← 1회성 마이그레이션·검증 도구 (평소엔 안 씀)
└─ .github/workflows/pages.yml  ← push 시 자동 빌드 + Pages 배포
```

### 데이터 흐름
```
            ┌──> README.md   (GitHub 저장소 보기용)
shelf.json ─┤
   (편집)    └──> shelf.js ──> index.html  (웹사이트)
            (py build.py 가 둘 다 생성)
```

> ⚠️ `README.md` 와 `data/shelf.js` 는 **자동 생성물**입니다. 직접 고치지 마세요 — 다음 빌드 때 덮어써집니다.

---

## 2. 항목 추가 / 수정 / 삭제

### 항목 분류 기준

| 분류 | 기준 |
|---|---|
| Awesome 리스트 | 여러 프로젝트·도구·사례를 모은 목록 |
| 오픈소스 도구 | 범용 개발·생산성·미디어 도구 |
| AI 서비스 | 웹에서 바로 이용하는 AI 서비스·호스팅 플랫폼 |
| AI 모델 | 모델·모델군과 해당 모델의 연구 구현 |
| AI 도구·개발 | AI 앱, 실행·학습·평가 도구, SDK·라이브러리·데이터셋 |
| 에이전트·스킬 | 에이전트, 에이전트 프레임워크·연동 프로토콜·MCP·스킬 |
| 프롬프트 | 프롬프트 예시·템플릿·작성 가이드 |
| 보안 | 취약점 탐색·감사·방어·보안 조사 도구와 자료 |
| 기사·자료 | 튜토리얼·원칙·실험 기록·학습 자료 |
| 기타 | 위 분류에 속하지 않는 유용한 자료 |

- 한 항목은 **주된 용도에 따라 한 곳에만** 등록합니다. 모델을 실행하는 앱은 AI 도구·개발, 에이전트가 쓸 수 있는 모델 자체는 AI 모델입니다.
- 보안 목적의 에이전트·스킬은 보안에 우선 배치합니다. 학습용 설명·예제 중심의 저장소는 기사·자료에 넣습니다.
- 이미지·음성·영상·로보틱스 같은 세부 분야는 태그로 구분합니다. 태그가 없거나 불완전할 수 있으므로 분류는 이름·설명·실제 용도를 함께 보고 결정합니다.
- 같은 URL은 중복 등록하지 않습니다. 끝의 `/`나 영문 대소문자 차이도 확인합니다.

### 태그·설명 작성 기준

- 태그는 설명에 확인된 **주요 용도·기술**에 붙입니다. `security`는 보안 기능·자료에, `note-taking`은 메모·지식 관리에 사용합니다. Jupyter 노트북이라는 이유로 `note-taking`을 붙이지 않습니다.
- `video`는 영상 제작·편집·분석·재생 등을 찾는 공통 태그이고, `video-gen`은 AI 영상 생성용 세부 태그입니다. `video-gen`에는 `video`를 함께 붙입니다.
- 음성·음악은 `audio`로 묶고, 용도에 따라 `tts`(음성 합성), `stt`(음성 인식), `music`(음악), `singing`(가창)을 함께 붙입니다. 음성 변환·복제만으로 TTS라고 분류하지 않습니다.
- `agent`는 에이전트 및 관련 도구, `skill`은 에이전트 스킬·스킬 모음에 사용합니다. 스킬을 함께 제공하는 도구에도 `skill`을 붙일 수 있습니다. `mcp`는 MCP 서버·프로토콜·연동을 찾는 태그입니다.
- 회사 태그는 개발·제공 주체 또는 주요 대상 제품을 나타냅니다. 단순 대체 제품·비교 대상·로그인 공급자라는 이유로 붙이지 않습니다.
- `open-weight`는 가중치 공개 여부를 나타내며, 상업 이용 허용이나 오픈소스 라이선스를 보장하지 않습니다. 코드·가중치·외부 에셋의 조건은 확인된 범위에서 설명에 구분해 적습니다.
- 설명은 **주요 용도 → 특징 → 확인된 공개 범위·제약** 순서로 씁니다. 정보가 없는 부분은 추정해서 채우지 않습니다. 수치·버전·지원 조건은 보존하고, 오탈자·번역투·불필요한 홍보 표현을 다듬습니다.

### 추가
[`data/shelf.json`](data/shelf.json)에서 원하는 섹션의 `entries` 배열에 객체 하나를 추가합니다.

```jsonc
{
  "name": "owner/repo",                         // 표시 이름 (GitHub면 owner/repo 권장)
  "url": "https://github.com/owner/repo",       // 링크
  "desc": "한 줄 설명",                          // 간결하게
  "tags": ["rust", "cli"]                        // 태그(소문자, 0개 이상)
}
```

### 수정 / 삭제
해당 객체의 값을 고치거나, 객체를 통째로 지우면 됩니다.

### 반영
```bash
py build.py
```
→ `README.md`와 `data/shelf.js`가 다시 생성됩니다. 끝.

> JSON이라 **쉼표·따옴표**에 주의하세요. 빌드가 실패하면 보통 콤마 누락/잉여가 원인입니다.

---

## 3. 데이터 스키마

### 최상위
| 키 | 설명 |
|----|------|
| `title` | 제목 (앞 이모지는 사이트/탭에서 자동 제거되고 favicon·사이드바 아이콘으로 대체) |
| `intro` | 소개 문구 |
| `sections` | 섹션 배열 |
| `archived` | 보관함(사라진 링크) 배열 |

### 섹션 (`sections[]`)
| 키 | 설명 |
|----|------|
| `key` | 고유 식별자(영문 kebab-case). 사이트의 아이콘·색상이 이 키로 매핑됨 |
| `emoji` | README 헤딩용 이모지 |
| `title` | 섹션 이름 |
| `note` | 섹션 설명(한 줄) |
| `entries` | 항목 배열 |

### 항목 (`entries[]`)
`name`, `url`, `desc`, `tags[]` — 위 2번 참고.

---

## 4. 새 섹션 추가하기

1. `shelf.json`의 `sections`에 새 객체 추가:
   ```jsonc
   { "key": "tools", "emoji": "🧰", "title": "도구", "note": "잡다한 도구", "entries": [] }
   ```
2. (선택) 사이트에서 전용 **아이콘**과 **색상**을 주려면 [`index.html`](index.html)에서:
   - `ICONS` 객체에 `"tools": SVG('<path .../>')` 추가 (없으면 기본 원형 아이콘)
   - CSS의 `.sec-… { --h: 숫자 }` 목록에 `.sec-tools { --h: 180; }` 추가 (색조 0~360)
3. `py build.py` 실행.

> 아이콘은 [lucide.dev](https://lucide.dev)에서 SVG `<path>`만 복사해 쓰면 통일감이 좋습니다.

---

## 5. 죽은 링크 → 보관함(Archive)

링크가 삭제/비공개되면 지우지 말고 `shelf.json`의 `archived` 배열로 옮깁니다.

```jsonc
{
  "name": "owner/repo",
  "url": "https://github.com/owner/repo",   // 원본(취소선으로 표시됨)
  "desc": "원래 설명",
  "tags": [],
  "from_section": "article",                 // 원래 있던 섹션 key
  "reason": "저장소 삭제됨(404)",
  "links": [                                 // 이전처·미러
    { "url": "https://...", "label": "포크 미러(98★)" }
  ]
}
```

→ README와 사이트의 **🗄️ 보관함**에 자동 표시됩니다.

---

## 6. 로컬에서 보기

`index.html`을 **더블클릭**하면 됩니다. (데이터를 `shelf.js`의 전역 변수로 읽어서 `file://`에서도 동작 — 별도 서버 불필요)

> 폰트·아바타는 인터넷에서 불러오므로, 오프라인이면 기본 폰트와 모노그램(첫 글자)으로 대체됩니다.

---

## 7. 웹에 배포 (GitHub Pages)

최초 1회만 설정하면 그 뒤로는 자동입니다.

1. GitHub 저장소 → **Settings → Pages**
2. **Source**를 **"GitHub Actions"**로 선택
3. `main` 브랜치에 push

이후 push할 때마다 [`.github/workflows/pages.yml`](.github/workflows/pages.yml)이:
1. `python build.py`로 README/shelf.js 재생성
2. README가 바뀌었으면 자동 커밋
3. `index.html` + `data/`를 **Pages에 배포**

배포 주소: `https://<사용자명>.github.io/awesome-shelf/`

---

## 8. scripts/ 폴더 (평소엔 안 씀)

최초 마이그레이션·링크 검증에 쓴 **1회성 도구**들입니다. 일상 편집에는 필요 없습니다.

| 파일 | 용도 |
|------|------|
| `migrate_from_readme.py` | (과거) 기존 README → `shelf.json` 변환 + 자동 태그 |
| `split_batches.py` | 링크 검증 시 항목을 배치로 분할 |
| `make_report.py` | 검증 결과 → `data/verify_report.md` 생성 |
| `archive_dead.py` | 죽은 링크를 `archived`로 이동 |

---

## 9. 치트시트

```bash
# 항목 추가/수정 후 반영
py build.py

# 로컬 미리보기
#   index.html 더블클릭

# 배포
git add -A
git commit -m "추가 - owner/repo"
git push          # → Actions가 빌드 + Pages 배포
```

**기억할 것 하나: `data/shelf.json`만 고치고 `py build.py`.**
