# md-slides

Markdown으로 쓴 강의안을 웹 슬라이드로 보여주는 작은 Django 프로젝트입니다. `decks/` 폴더에 `.md` 파일을 넣으면 바로 발표 화면이 되고, 파일을 고친 뒤 새로고침하면 반영됩니다. 슬라이드는 [reveal.js](https://revealjs.com/) 5.1.0이 그립니다.

- DB와 로그인이 없습니다. 강의안은 파일로만 관리합니다.
- [Marp](https://marp.app/) 형식의 MD 파일을 그대로 넣어도 됩니다.

## 시작하기

[uv](https://docs.astral.sh/uv/)와 Python 3.15 이상이 필요합니다.

```bash
git clone https://github.com/metahomo/md-slides.git
cd md-slides
uv sync
uv run python manage.py runserver 127.0.0.1:10002
```

브라우저에서 `http://127.0.0.1:10002` 를 열면 강의안 목록이 나옵니다.

| 주소 | 화면 |
|---|---|
| `/` | 강의안 목록 (제목, 슬라이드 수) |
| `/<파일 이름>/` | 발표 화면. 예: `decks/sample-lecture.md` → `/sample-lecture/` |

발표 중 단축키: 방향키로 이동, **F** 전체화면, **S** 발표자 화면(노트, 다음 장, 타이머), **Esc** 전체 보기.

## 외부 공개 (GitHub Pages)

`main`에 push하면 GitHub Actions(`.github/workflows/pages.yml`)가 테스트를 돌린 뒤 강의안을 정적 HTML로 만들어 GitHub Pages에 배포합니다. 서버를 띄우지 않아도 누구나 볼 수 있습니다.

- 사이트: https://metahomo.github.io/md-slides/
- 로컬에서 정적 사이트 만들기: `uv run python manage.py build_site --out _site --base-path /md-slides/`

`decks/`에 넣은 강의안은 모두 공개됩니다. 공개하면 안 되는 자료는 넣지 마세요.

## 강의안 작성 규칙

```markdown
---
marp: true
paginate: true
---

# 첫 슬라이드 제목

- 일반 Markdown 문법 그대로: 목록, **굵게**, 표, 코드, 이미지

<!-- 이 주석은 발표자 노트가 됩니다 -->

---

# 두 번째 슬라이드
```

- `---` 한 줄이 슬라이드 구분선입니다. 코드 블록 안의 `---`는 구분선으로 보지 않습니다.
- 맨 위의 front matter(`---`로 감싼 설정 블록)는 무시합니다.
- HTML 주석 `<!-- ... -->`는 발표자 노트가 됩니다.
- `<!-- _class: lead -->`, `<!-- paginate: false -->` 같은 Marp 지시어 주석은 무시합니다.
- 목록에 표시되는 제목은 파일에서 처음 나오는 `# 제목`입니다. 없으면 파일 이름을 씁니다.
- 파일 이름은 영문, 숫자, `_`, `-`만 쓸 수 있습니다.

### 더 쓸 수 있는 문법 (VS Code · nvim 미리 보기와 같은 MD)

| 문법 | 슬라이드에서 |
|---|---|
| `<!-- _class: lead -->` | 그 장만 가운데 정렬 표지·절 구분. `invert`(밝은 글자), `hangul`(번호 목록 가·나·다), `small`(작은 글자). 여러 개는 띄어 쓴다 |
| `<!-- _backgroundColor: #0f172a -->` · `<!-- _backgroundImage: url(…) -->` | 그 장의 배경 |
| `> [!NOTE]` · `[!TIP]` · `[!IMPORTANT]` · `[!WARNING]` · `[!CAUTION]` | GitHub 알림 상자 |
| ` ```javascript {1,2} ` | 1·2번 줄 강조(reveal.js `[1,2]` 로 바꿔 넣음) |
| `<p class="fragment">` · `<div style="display:grid;…">` | 단계별 등장 · 2단 (`div` 안 MD 앞뒤 빈 줄) |

화면은 16:9(1280×720), 바깥 여백 0, 위부터 채운다. **작성 규칙 전체: [`docs/slide-authoring.md`](docs/slide-authoring.md)** · 예시: [`decks/md-syntax-guide.md`](decks/md-syntax-guide.md)

예시는 [`decks/sample-lecture.md`](decks/sample-lecture.md)와 [`decks/miniproject5-kms.md`](decks/miniproject5-kms.md)를 보세요.

## 설정 (환경 변수)

| 변수 | 기본값 | 설명 |
|---|---|---|
| `SLIDES_DIR` | `decks/` | 강의안 MD 파일을 읽을 폴더 |
| `DJANGO_DEBUG` | `1` | `0`이면 운영 모드 |
| `DJANGO_SECRET_KEY` | 개발용 값 | 운영 모드에서는 반드시 설정 |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | 쉼표로 구분 |

## 구조

```text
md_slides/        Django 프로젝트 설정
slides/
  decks.py        MD 파일을 슬라이드와 발표자 노트로 나눈다
  views.py        목록과 발표 화면
  templates/      목록(Tailwind)과 발표 화면(reveal.js)
  tests.py        테스트
decks/            강의안 MD 파일
```

## 테스트

```bash
uv run pytest
```

## 주의

MD 안에 쓴 HTML은 그대로 화면에 나옵니다. 그래서 믿을 수 있는 사람이 쓴 파일만 `decks/`에 넣으세요. 파일 이름은 검사해서 `decks/` 폴더 밖의 파일은 열지 않습니다.
