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


@dataclass
class Deck:
    slug: str
    title: str
    slides: list[Slide]


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


def _extract_notes(chunk: str) -> Slide:
    notes = []

    def take(match: re.Match) -> str:
        inner = match.group(1).strip()
        if inner and not _DIRECTIVE.match(inner):
            notes.append(inner)
        return ""

    body = _COMMENT.sub(take, chunk).strip()
    return Slide(body=body, notes="\n\n".join(notes))


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
    text = _FRONT_MATTER.sub("", text, count=1)
    slides = [_extract_notes(c) for c in _split_slides(text)]
    slides = [s for s in slides if s.body or s.notes]
    return Deck(slug=slug, title=_title(slides, slug), slides=slides)


def list_decks() -> list[Deck]:
    base = decks_dir()
    if not base.is_dir():
        return []
    decks = [load_deck(p.stem) for p in sorted(base.glob("*.md"))]
    return [d for d in decks if d is not None]
