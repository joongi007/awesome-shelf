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
