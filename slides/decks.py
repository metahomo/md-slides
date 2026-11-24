"""MD 강의안 파일을 읽어 슬라이드 단위로 나눈다.

작성 규칙(Marp와 호환):
- 맨 위의 YAML front matter(`---` ~ `---`)는 무시한다.
- `---` 한 줄이 슬라이드 구분선이다. 코드 블록(```) 안의 `---`는 구분선으로 보지 않는다.
- HTML 주석 `<!-- ... -->`은 발표자 노트가 된다.
  단 `<!-- _class: lead -->`처럼 `이름: 값` 한 줄짜리 주석은 Marp 지시어로 보고 버린다.
"""

import re
from dataclasses import dataclass
from pathlib import Path

from django.conf import settings

_FRONT_MATTER = re.compile(r"\A---\s*\n.*?\n---\s*(\n|\Z)", re.DOTALL)
_COMMENT = re.compile(r"<!--(.*?)-->", re.DOTALL)
# Marp 지시어 이름만 지시어로 본다. "출처: ADR-002" 같은 한 줄 노트까지 버리지 않도록 이름을 정해 둔다.
_MARP_DIRECTIVES = (
    "marp|theme|style|headingDivider|size|math|title|description|author|image|keywords|url|lang"
    "|paginate|header|footer|class|color|backgroundColor|backgroundImage|backgroundPosition"
    "|backgroundRepeat|backgroundSize"
)
_DIRECTIVE = re.compile(rf"^\s*_?(?:{_MARP_DIRECTIVES})\s*:[^\n]*$")
_SLUG = re.compile(r"^[\w-]+$")


@dataclass
class Slide:
    body: str
    notes: str
    cls: str = ""          # Marp `_class` / `class` 지시어 → <section class="…">
    bg_color: str = ""     # Marp `_backgroundColor` → data-background-color
    bg_image: str = ""     # Marp `_backgroundImage: url(…)` → data-background-image


@dataclass
class Deck:
    slug: str
    title: str
    slides: list[Slide]
    theme: str = ""        # front matter `theme: orange` → <body class="theme-orange">
    footer: str = ""       # front matter `footer: …` → 장마다 왼쪽 아래 글 (theme 이 그릴 때)
    logos: tuple[str, ...] = ()  # front matter `logos: assets/a.png, assets/b.png` → 장마다 오른쪽 위 (theme 이 그릴 때)


# front matter 에서 읽는 값 — 테마 이름은 템플릿이 아는 것만 받는다
_THEMES = {"orange", "starbucks"}  # starbucks = 주황 테마 틀 + 스타벅스 색(2026-11-24)
_FM_LINE = re.compile(r"^(theme|footer|logos)\s*:\s*(.*?)\s*$", re.MULTILINE)
# 로고는 decks/assets/ 안의 그림만 받는다(경로 밖·스크립트 금지)
_LOGO = re.compile(r"^assets/[\w.-]+\.(?:png|jpe?g|svg|webp)$")


def _front_matter(text: str) -> dict[str, str]:
    m = _FRONT_MATTER.match(text)
    if not m:
        return {}
    return {k: v.strip("'\"") for k, v in _FM_LINE.findall(m.group(0))}


def decks_dir() -> Path:
    return Path(settings.SLIDES_DIR)


def deck_path(slug: str) -> Path | None:
    """slug에 해당하는 .md 파일 경로. 없거나 폴더 밖을 가리키면 None."""
    if not _SLUG.match(slug):
        return None
    base = decks_dir().resolve()
    path = (base / f"{slug}.md").resolve()
    if path.parent != base or not path.is_file():
        return None
    return path


def _split_slides(text: str) -> list[str]:
    chunks, current, in_fence = [], [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        if not in_fence and line.strip() == "---":
            chunks.append("\n".join(current))
            current = []
        else:
            current.append(line)
    chunks.append("\n".join(current))
    return [c for c in chunks if c.strip()]


_SAFE_VALUE = re.compile(r"^[\w\s#(),.%:/-]+$")
# GitHub 알림 문법 `> [!NOTE]` — VS Code·nvim 미리 보기와 같은 모양으로 슬라이드에도 그린다
_ALERT = re.compile(r"^> \[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\][ \t]*\n((?:>.*(?:\n|$))*)", re.MULTILINE)
_ALERT_LABEL = {"NOTE": "ℹ️ Note", "TIP": "💡 Tip", "IMPORTANT": "❗ Important", "WARNING": "⚠️ Warning", "CAUTION": "🛑 Caution"}
# 코드 줄 강조 ```js {1,3-4}  →  reveal.js 문법 ```js [1,3-4]
_CODE_LINES = re.compile(r"^(```[\w+-]+)[ \t]*\{([\d,\s|-]+)\}[ \t]*$", re.MULTILINE)


def _alerts(body: str) -> str:
    def to_html(m: re.Match) -> str:
        kind = m.group(1)
        inner = "\n".join(line[1:].lstrip() if line.startswith(">") else line for line in m.group(2).rstrip("\n").splitlines())
        return (f'<div class="callout callout-{kind.lower()}">\n<p class="callout-title">{_ALERT_LABEL[kind]}</p>\n\n'
                f"{inner.strip()}\n\n</div>\n")
    return _ALERT.sub(to_html, body)


def _code_lines(body: str) -> str:
    return _CODE_LINES.sub(lambda m: f"{m.group(1)} [{m.group(2).replace(' ', '')}]", body)


def _extract_notes(chunk: str) -> Slide:
    notes, directives = [], {}

    def take(match: re.Match) -> str:
        inner = match.group(1).strip()
        if not inner:
            return ""
        if _DIRECTIVE.match(inner):
            key, _, value = inner.partition(":")
            directives[key.strip().lstrip("_")] = value.strip().strip("'\"")
        else:
            notes.append(inner)
        return ""

    body = _COMMENT.sub(take, chunk).strip()
    body = _code_lines(_alerts(body))
    safe = lambda v: v if v and _SAFE_VALUE.match(v) else ""
    image = re.sub(r"^url\((.*)\)$", r"\1", directives.get("backgroundImage", "")).strip("'\"")
    return Slide(body=body, notes="\n\n".join(notes), cls=safe(directives.get("class", "")),
                 bg_color=safe(directives.get("backgroundColor", "")), bg_image=safe(image))


def _title(slides: list[Slide], fallback: str) -> str:
    for slide in slides:
        for line in slide.body.splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    return fallback


def load_deck(slug: str) -> Deck | None:
    path = deck_path(slug)
    if path is None:
        return None
    text = path.read_text(encoding="utf-8")
    fm = _front_matter(text)
    text = _FRONT_MATTER.sub("", text, count=1)
    slides = [_extract_notes(c) for c in _split_slides(text)]
    slides = [s for s in slides if s.body or s.notes]
    theme = fm.get("theme", "")
    return Deck(slug=slug, title=_title(slides, slug), slides=slides,
                theme=theme if theme in _THEMES else "", footer=fm.get("footer", "")[:120],
                logos=tuple(x for x in (v.strip() for v in fm.get("logos", "").split(",")) if _LOGO.match(x))[:5])


def list_decks() -> list[Deck]:
    base = decks_dir()
    if not base.is_dir():
        return []
    decks = [load_deck(p.stem) for p in sorted(base.glob("*.md"))]
    return [d for d in decks if d is not None]
