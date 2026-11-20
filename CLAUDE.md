# CLAUDE.md

## 개요

MD 강의안을 웹 슬라이드로 보여주는 작은 Django 6.1 프로젝트(Python ≥ 3.15, `uv`). DB·로그인 없음. 프로젝트 패키지 `md_slides/`, 앱 `slides/`. 코드 주석과 화면 문구는 한국어. myproj-01과는 별개 프로젝트다.

## 명령어

```bash
uv run python manage.py runserver 127.0.0.1:10002   # 개발 서버 (Studio-C 공용 서버에서 pioneer7은 10002번)
uv run pytest
```

## 구조

- `settings.SLIDES_DIR`(기본 `decks/`, 환경 변수 `SLIDES_DIR`)의 `<slug>.md`를 `/`(목록), `/<slug>/`(발표)로 보여준다.
- `slides/decks.py`가 front matter를 버리고 코드 블록 밖의 `---` 줄로 슬라이드를 나눈다. HTML 주석은 발표자 노트가 되고, `<!-- _class: lead -->`처럼 `이름: 값` 한 줄짜리 주석은 Marp 지시어로 보고 버린다(Marp 파일과 호환).
- 슬라이드마다 `<section data-markdown><textarea data-template>`에 자동 이스케이프해 넣고, CDN의 reveal.js 5.1.0이 렌더링한다.
- slug는 `[\w-]+`만 허용하고, 경로가 폴더 안인지 확인한다. MD 안의 HTML은 그대로 렌더링되므로 신뢰하는 사람이 쓴 파일만 넣는다.

## 작성 규칙

- 슬라이드 작성 규칙의 정본은 `docs/slide-authoring.md`. 화면·문법·게시 규칙(템플릿·`decks.py`)을 바꾸면 같은 커밋에서 이 파일도 고치고 "마지막 갱신" 날짜를 바꾼다.
