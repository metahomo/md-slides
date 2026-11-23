# 슬라이드 작성 가이드

이 저장소(md-slides)에서 강의안·발표 MD 를 쓰는 규칙이다. 규칙이 바뀌면 **이 파일을 함께 고친다**(앱 코드·템플릿을 바꾼 커밋에 같이). 예시 덱: [`decks/md-syntax-guide.md`](../decks/md-syntax-guide.md) · 공개 화면: <https://metahomo.github.io/md-slides/md-syntax-guide/>

마지막 갱신: 2026-11-23

## 1. 화면

| 항목 | 값 | 어디서 정하나 |
|---|---|---|
| 크기 | 16:9, 1280×720 (창에 맞게 0.2~3배로 줄고 는다) | `slides/templates/slides/deck_detail.html` `Reveal.initialize` |
| 바깥 여백 | 0 (`margin: 0`) | 같은 곳 |
| 세로 정렬 | 제목(`##`)은 위에 붙고, 나머지 내용은 남은 높이의 가운데 (`center: false` + 보이는 장만 flex). `lead` 장은 아래로 내려 가운데처럼 | CSS `section.present`, `section.lead` |
| 장 안쪽 여백 | 위아래 14px · 좌우 22px | CSS `.reveal .slides section` |
| 장표 경계 | 1280×720 캔버스 안쪽 끝에 **검은 3px 네모 테두리**(창 끝에서 잘리지 않음), 바깥은 옅은 회색 — 장 크기가 보인다 | CSS `.reveal .slides::after`, `.reveal-viewport` |
| 글자 | 본문 0.95em, `#` 1.9em, `##` 1.3em, `###` 1.05em, 표 0.85em(장 폭 100%)에서 시작해 **표 폭을 글에 맞추고 글자를 키워 장 폭을 채움** — 오른쪽 빈 칸 없음(상한 본문 1.8배, 장이 넘치면 줄임), 코드 0.7em에서 시작해 **가장 긴 줄이 검은 상자 폭을 채우도록 자동으로 키움**(상한: 본문의 1.4배·장 높이의 45%). 상한에 걸려 폭이 남으면 **검은 상자를 글 폭에 맞춰 줄인다** — 빈 검은 여백 없음 | CSS |

### 주황 테마 (`theme: orange`, 2026-11-23)

덱 맨 위 front matter 에 `theme: orange` 와 `footer: 꼬리말` 을 넣으면 그 덱만 강의 슬라이드 모양으로 바뀐다(다른 덱은 위 기본 모양 그대로). 지금 쓰는 덱: `miniproject5-kms`.

| 항목 | 주황 테마 |
|---|---|
| 장표 | 흰 장 + 둥근 모서리·옅은 그림자(검은 네모 없음), 바깥 옅은 회색, 글꼴 Pretendard |
| 장 제목 `##` | 굵게, 아래 주황 막대(64×4px), 내용은 제목 바로 아래부터(가운데 몰기 없음), 안쪽 여백 위 52 · 좌우 88px |
| 글머리 | 1단 주황 점, 2단 회색 빈 원, `**굵게**` 는 진한 검정 |
| 절 구분 `lead` | 주황 바탕 · 왼쪽 정렬 · `# 1. 제목` 의 번호를 크게 따로 그린다 |
| 꼬리말 | 장마다 왼쪽 아래 `footer` 글, 오른쪽 아래 주황 쪽 번호 `3 / 30` |

`theme` 은 템플릿이 아는 이름(`orange`)만 받고, 모르는 이름은 무시한다.

덱 MD 안에 `<style>` 로 제목 크기·여백을 넣지 않는다 — 모든 덱이 템플릿 하나를 따른다.

## 2. 한 장 구성

- 한 장 = **결론 한 줄**(제목) + **표 하나** 또는 **글머리 3~5줄**
- 넘치면 장을 나눈다. 표는 6줄 안쪽, 장 폭을 다 쓴다(가운데 작은 표로 여백을 남기지 않는다)
- 장 제목 아래 설명 한 줄은 `*기울임*`
- 강조는 `**굵게**`, 코드·파일 이름은 `` `코드` ``

## 3. 문법

| 쓰는 것 | 문법 | 비고 |
|---|---|---|
| 장 나누기 | 빈 줄 사이 `---` 한 줄 | 코드 블록 안 `---` 는 구분선 아님 |
| 발표자 노트 | `<!-- 노트 -->` | 발표 중 `S` 키 |
| 제목 | `#` 표지·절 · `##` 장 · `###` 소제목 | 덱 목록 제목 = 처음 나오는 `# 제목` |
| 목록 | `-` `+` `*`, 번호 `1.` | 하위 목록은 두 칸 들여쓰기 |
| 가·나·다 목록 | 장 맨 위 `<!-- _class: hangul -->` + 번호 목록 | |
| 표지·절 구분 | `<!-- _class: lead -->` | 가운데 정렬 |
| 어두운 장 | `<!-- _class: lead invert -->` + `<!-- _backgroundColor: #0f172a -->` | 클래스 여러 개는 띄어 쓴다 |
| 글 많은 장 | `<!-- _class: small -->` | 글자 0.65em |
| 긴 칸이 많은 표 | `<!-- _class: dense -->` | 표만 0.75em — 넘칠 때 먼저 이것, 그래도 넘치면 장을 나눈다 |
| 배경 그림 | `<!-- _backgroundImage: url(주소) -->` | |
| 코드 | ` ```python ` · ` ```go ` · ` ```bash ` | 언어별 색 |
| 줄 강조 | ` ```javascript {1,2} ` | 1·2번 줄 강조 (VS Code 문법) |
| 알림 상자 | `> [!NOTE]` 다음 줄부터 `> 내용` | NOTE · TIP · IMPORTANT · WARNING · CAUTION |
| 단계별 등장 | `<p class="fragment">…</p>` | `→` 한 번 더 |
| 2단 | `<div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5em">` 안에 `<div>` 둘 | `div` 안 MD 앞뒤 빈 줄 |

쓰면 안 되는 것: reveal 의 `<!-- .element: … -->`·`<!-- .slide: … -->` (이 앱은 주석을 노트로 바꾼다 — 대신 위 `_class` 지시어), Marp `![w:300]`(→ `<img src="…" width="300">`).

## 4. 게시

| 단계 | 명령 |
|---|---|
| 미리 보기(이 서버) | `uv run python manage.py runserver 127.0.0.1:10002` → `/덱이름/` |
| 시험 | `uv run pytest` |
| 공개 | `main` 에 push → GitHub Actions 가 1~2분 뒤 <https://metahomo.github.io/md-slides/덱이름/> 갱신 |

덱은 모두 공개된다. 공유 키·비밀번호·토큰은 넣지 않는다.

## 5. 고정 주소

| 덱 | 주소 |
|---|---|
| 미니 프로젝트 5 발표 | <https://metahomo.github.io/md-slides/miniproject5-kms/> |
| 문법 안내 | <https://metahomo.github.io/md-slides/md-syntax-guide/> |
