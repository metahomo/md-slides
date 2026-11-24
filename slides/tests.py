import json
import os
import tempfile
from pathlib import Path

from django.test import SimpleTestCase, override_settings

from slides.decks import _extract_notes, load_deck

DECK = """---
marp: true
paginate: true
---

<!-- _class: lead -->
# 첫 강의
부제

---

# 코드
```yaml
a: 1
---
b: 2
```

<!-- 여기는 발표자 노트 -->

---

# <script>alert(1)</script>
"""


class SlidesTest(SimpleTestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        Path(self.tmp.name, "intro.md").write_text(DECK, encoding="utf-8")
        Path(self.tmp.name, "secret.txt").write_text("비밀", encoding="utf-8")
        override = override_settings(SLIDES_DIR=self.tmp.name)
        override.enable()
        self.addCleanup(override.disable)

    def test_deck_is_split_and_front_matter_removed(self):
        deck = load_deck("intro")
        self.assertEqual(deck.title, "첫 강의")
        self.assertEqual(len(deck.slides), 3)
        self.assertNotIn("marp", deck.slides[0].body)
        # Marp 지시어 주석은 버리고 노트로 쓰지 않는다.
        self.assertNotIn("_class", deck.slides[0].body)
        self.assertEqual(deck.slides[0].notes, "")

    def test_separator_inside_code_fence_is_kept(self):
        slide = load_deck("intro").slides[1]
        self.assertIn("a: 1\n---\nb: 2", slide.body)
        self.assertEqual(slide.notes, "여기는 발표자 노트")

    def test_one_line_note_with_colon_is_kept(self):
        Path(self.tmp.name, "colon.md").write_text(
            "# 제목\n\n<!-- 출처: ADR-002 -->\n<!-- _paginate: false -->\n", encoding="utf-8"
        )
        self.assertEqual(load_deck("colon").slides[0].notes, "출처: ADR-002")

    def test_list_page(self):
        html = self.client.get("/").content.decode()
        self.assertIn("첫 강의", html)
        self.assertIn("/intro/", html)
        self.assertNotIn("secret", html)

    def test_detail_page_escapes_markdown(self):
        res = self.client.get("/intro/")
        self.assertEqual(res.status_code, 200)
        html = res.content.decode()
        self.assertEqual(html.count("<section data-markdown"), 3)
        # textarea 안에서 닫는 태그로 탈출하지 못하도록 이스케이프된다.
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;script&gt;", html)

    def test_build_site_writes_pages_under_base_path(self):
        from django.core.management import call_command

        out = Path(self.tmp.name, "site")
        call_command("build_site", "--out", str(out), "--base-path", "/md-slides", stdout=open(os.devnull, "w"))
        index = (out / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="/md-slides/intro/"', index)
        detail = (out / "intro" / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="/md-slides/"', detail)
        self.assertTrue((out / ".nojekyll").exists())
        # 빌드 뒤에도 일반 요청의 주소는 그대로다.
        self.assertIn('href="/intro/"', self.client.get("/").content.decode())

    def test_missing_or_invalid_slug_is_404(self):
        for url in ["/nope/", "/secret/", "/..%2Fsecret/"]:
            self.assertEqual(self.client.get(url).status_code, 404, url)


class MarkdownExtrasTests(SimpleTestCase):
    """화이트보드 문법: Marp 지시어(_class 등), GitHub 알림, 코드 줄 강조."""

    def test_marp_class_and_background_directives_apply_to_slide(self):
        s = _extract_notes("<!-- _class: lead -->\n<!-- _backgroundColor: #123456 -->\n# 표지\n<!-- 발표자 노트 -->")
        self.assertEqual((s.cls, s.bg_color), ("lead", "#123456"))
        self.assertEqual(s.notes, "발표자 노트")
        self.assertNotIn("_class", s.body)

    def test_unsafe_directive_value_is_dropped(self):
        s = _extract_notes('<!-- _class: x" onclick="alert(1) -->\n# t')
        self.assertEqual(s.cls, "")

    def test_github_alert_becomes_callout(self):
        s = _extract_notes("> [!NOTE]\n> VS Code 와 nvim 에서도 보인다\n> 둘째 줄\n\n뒤 문단")
        self.assertIn('<div class="callout callout-note">', s.body)
        self.assertIn("VS Code 와 nvim 에서도 보인다\n둘째 줄", s.body)
        self.assertIn("뒤 문단", s.body)

    def test_code_line_highlight_braces_to_reveal_brackets(self):
        s = _extract_notes("```javascript {1,2}\nimport os\n```")
        self.assertTrue(s.body.startswith("```javascript [1,2]"))


class ThemeTest(SimpleTestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        override = override_settings(SLIDES_DIR=self.tmp.name)
        override.enable()
        self.addCleanup(override.disable)

    def _write(self, front: str):
        Path(self.tmp.name, "t.md").write_text(f"---\n{front}\n---\n\n# 제목\n", encoding="utf-8")

    def test_orange_theme_and_footer_from_front_matter(self):
        self._write("theme: orange\nfooter: 꼬리 <b>말</b>")
        deck = load_deck("t")
        self.assertEqual((deck.theme, deck.footer), ("orange", "꼬리 <b>말</b>"))
        html = self.client.get("/t/").content.decode()
        self.assertIn('class="theme-orange"', html)
        self.assertIn('data-footer="꼬리 &lt;b&gt;말&lt;/b&gt;"', html)  # 꼬리말은 이스케이프

    def test_unknown_theme_is_ignored(self):
        self._write("theme: gaia")
        self.assertEqual(load_deck("t").theme, "")
        self.assertNotIn("theme-", self.client.get("/t/").content.decode().split("<body", 1)[1].split(">", 1)[0])


class LogoTest(SimpleTestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        override = override_settings(SLIDES_DIR=self.tmp.name)
        override.enable()
        self.addCleanup(override.disable)
        Path(self.tmp.name, "assets").mkdir()
        Path(self.tmp.name, "assets", "a.png").write_bytes(b"\x89PNG\r\n")
        Path(self.tmp.name, "t.md").write_text(
            "---\ntheme: orange\nlogos: assets/a.png, ../x.png, assets/b.js, assets/c.svg\n---\n\n# 제목\n", encoding="utf-8")

    def test_only_asset_images_are_kept_in_order(self):
        self.assertEqual(load_deck("t").logos, ("assets/a.png", "assets/c.svg"))
        self.assertIn('data-logos="assets/a.png,assets/c.svg"', self.client.get("/t/").content.decode())

    def test_asset_is_served_and_copied_by_build(self):
        self.assertEqual(self.client.get("/assets/a.png").status_code, 200)
        self.assertEqual(self.client.get("/assets/..%2Ft.md").status_code, 404)
        out = Path(self.tmp.name, "_out")
        from django.core.management import call_command
        call_command("build_site", out=str(out), base_path="/x/")
        self.assertTrue((out / "assets" / "a.png").is_file())


class LiveTests(SimpleTestCase):
    """서버에서 볼 때만 — md 수정 시각 조회·자동 새로 고침·PDF 버튼 (2026-11-24). 정적 사이트에는 없다."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        Path(self.tmp.name, "t.md").write_text("# 하나\n\n---\n\n# 둘\n", encoding="utf-8")
        self.override = override_settings(SLIDES_DIR=self.tmp.name)
        self.override.enable()

    def tearDown(self):
        self.override.disable()
        self.tmp.cleanup()

    def test_mtime_changes_when_md_is_edited(self):
        first = self.client.get("/t/mtime").json()["mtime"]
        p = Path(self.tmp.name, "t.md")
        os.utime(p, ns=(first + 10**9, first + 10**9))
        self.assertNotEqual(self.client.get("/t/mtime").json()["mtime"], first)
        self.assertEqual(self.client.get("/nope/mtime").status_code, 404)

    def test_live_page_has_reload_and_pdf_button(self):
        html = self.client.get("/t/").content.decode()
        self.assertIn('href="/t.pdf"', html)
        self.assertIn("/t/mtime", html)

    def test_static_site_watches_version_and_links_pdf(self):
        out = Path(self.tmp.name, "_out")
        from django.core.management import call_command
        call_command("build_site", out=str(out), base_path="/x/")
        html = (out / "t" / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="/x/t.pdf"', html)  # PDF 는 배포 때 Actions 가 만든다
        self.assertIn('"version.json"', html)
        self.assertNotIn("/mtime", html)
        v1 = json.loads((out / "t" / "version.json").read_text(encoding="utf-8"))["version"]
        Path(self.tmp.name, "t.md").write_text("# 하나\n\n---\n\n# 셋\n", encoding="utf-8")
        call_command("build_site", out=str(out), base_path="/x/")
        self.assertNotEqual(json.loads((out / "t" / "version.json").read_text(encoding="utf-8"))["version"], v1)

    def test_pdf_of_unknown_deck_is_404(self):
        self.assertEqual(self.client.get("/nope.pdf").status_code, 404)
