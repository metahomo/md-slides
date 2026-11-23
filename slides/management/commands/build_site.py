"""강의안을 정적 HTML 사이트로 내보낸다 (GitHub Pages 등에 올리는 용도).

    uv run python manage.py build_site --out _site --base-path /md-slides/

결과: <out>/index.html (목록), <out>/<slug>/index.html (발표 화면)
"""

import shutil
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string
from django.urls import get_script_prefix, set_script_prefix

from slides.decks import decks_dir, list_decks


class Command(BaseCommand):
    help = "강의안을 정적 HTML 사이트로 내보낸다."

    def add_arguments(self, parser):
        parser.add_argument("--out", default="_site", help="출력 폴더 (기존 내용은 지운다)")
        parser.add_argument(
            "--base-path",
            default="/",
            help="사이트가 올라갈 경로. GitHub Pages 프로젝트 사이트면 /<저장소 이름>/",
        )

    def handle(self, *args, out, base_path, **options):
        if not base_path.startswith("/"):
            raise CommandError("--base-path 는 / 로 시작해야 합니다.")
        base_path = base_path.rstrip("/") + "/"
        out_dir = Path(out)
        if out_dir.exists():
            shutil.rmtree(out_dir)
        out_dir.mkdir(parents=True)

        decks = list_decks()
        # {% url %} 이 base_path 아래 주소를 만들도록 접두사를 바꿔 둔다.
        old_prefix = get_script_prefix()
        set_script_prefix(base_path)
        try:
            (out_dir / "index.html").write_text(
                render_to_string("slides/deck_list.html", {"decks": decks}), encoding="utf-8"
            )
            for deck in decks:
                page = out_dir / deck.slug / "index.html"
                page.parent.mkdir()
                page.write_text(
                    render_to_string("slides/deck_detail.html", {"deck": deck}), encoding="utf-8"
                )
        finally:
            set_script_prefix(old_prefix)

        # 덱 그림(로고 등) — decks/assets/ → <out>/assets/
        assets = decks_dir() / "assets"
        if assets.is_dir():
            shutil.copytree(assets, out_dir / "assets")
        # GitHub Pages 가 _ 로 시작하는 폴더를 숨기지 않도록 한다.
        (out_dir / ".nojekyll").write_text("", encoding="utf-8")
        self.stdout.write(f"강의안 {len(decks)}개 → {out_dir}/ (기준 경로 {base_path})")
