import tempfile
from pathlib import Path

from django.test import SimpleTestCase, override_settings

from slides.decks import load_deck

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

    def test_missing_or_invalid_slug_is_404(self):
        for url in ["/nope/", "/secret/", "/..%2Fsecret/"]:
            self.assertEqual(self.client.get(url).status_code, 404, url)
