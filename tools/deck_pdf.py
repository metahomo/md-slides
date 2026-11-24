"""덱 한 개를 화면 그대로 PDF 로 만든다 — 장마다 1280×720(2배) 캡처를 이어 붙인다.

reveal.js 인쇄 모드(?print-pdf)는 주황 테마의 표지·꼬리말·글자 맞춤이 어긋나서 쓰지 않는다(2026-11-24 확인).
실행: uv run --no-project --with playwright==1.55.0 --with img2pdf python -I tools/deck_pdf.py URL OUT.pdf
(playwright 1.55 = 이 서버에 받아 둔 chromium_headless_shell-1187)
"""

import sys
import tempfile
from pathlib import Path

import img2pdf
from playwright.sync_api import sync_playwright

HIDE = ".back, .pdf-btn { display: none !important; }"


def main(url: str, out: str) -> None:
    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 720}, device_scale_factor=2)
        page.goto(url, wait_until="networkidle")
        page.wait_for_function("window.Reveal && Reveal.isReady()", timeout=30000)
        page.add_style_tag(content=HIDE)
        page.evaluate("Reveal.configure({transition: 'none', backgroundTransition: 'none'})")  # 넘김 효과 중간을 찍지 않게
        total = page.evaluate("Reveal.getTotalSlides()")
        shots = []
        for i in range(total):
            page.evaluate(f"Reveal.slide({i})")
            page.wait_for_timeout(350)  # slidechanged 뒤 글자 맞춤(fitAll)이 끝나도록
            shot = Path(tmp) / f"{i:03d}.png"
            page.screenshot(path=str(shot))
            shots.append(str(shot))
        browser.close()
        layout = img2pdf.get_layout_fun((img2pdf.mm_to_pt(338.67), img2pdf.mm_to_pt(190.5)))
        Path(out).write_bytes(img2pdf.convert(shots, layout_fun=layout))
    print(f"{total}장 → {out}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
