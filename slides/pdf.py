"""덱 PDF — md 가 바뀐 판마다 한 번 만들고, 같은 판이면 만들어 둔 파일을 준다."""

import subprocess
import threading
from pathlib import Path

from django.conf import settings

CACHE = Path(settings.BASE_DIR) / ".cache" / "pdf"
TOOL = Path(settings.BASE_DIR) / "tools" / "deck_pdf.py"
_lock = threading.Lock()


def deck_pdf(slug: str, mtime_ns: int, url: str) -> Path:
    """slug 의 현재 판(md 수정 시각) PDF 경로. 없으면 만든다(약 20~30초)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    out = CACHE / f"{slug}-{mtime_ns}.pdf"
    with _lock:  # 같은 PDF 를 두 번 만들지 않게(공용 서버 — 브라우저를 한 번에 하나만)
        if not out.exists():
            tmp = out.with_suffix(".part")
            subprocess.run(
                ["uv", "run", "--quiet", "--no-project", "--with", "playwright==1.55.0", "--with", "img2pdf",
                 "python", "-I", str(TOOL), url, str(tmp)],
                check=True, timeout=300, capture_output=True,
            )
            tmp.replace(out)
            for old in CACHE.glob(f"{slug}-*.pdf"):  # 지난 판은 지운다
                if old != out:
                    old.unlink(missing_ok=True)
    return out
