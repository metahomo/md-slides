from django.http import FileResponse, Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from slides.decks import deck_path, list_decks, load_deck


def deck_list(request: HttpRequest) -> HttpResponse:
    return render(request, "slides/deck_list.html", {"decks": list_decks()})


def deck_detail(request: HttpRequest, slug: str) -> HttpResponse:
    deck = load_deck(slug)
    if deck is None:
        raise Http404("강의안을 찾을 수 없습니다.")
    # live: 서버에서 볼 때만 — md 를 고치면 저절로 새로 고침, PDF 버튼. 정적 사이트(build_site)에는 없다.
    return render(request, "slides/deck_detail.html", {"deck": deck, "live": True})


def deck_mtime(request: HttpRequest, slug: str) -> JsonResponse:
    """md 수정 시각 — 열린 슬라이드가 1초마다 물어보고, 바뀌면 다시 읽는다."""
    path = deck_path(slug)
    if path is None:
        raise Http404("강의안을 찾을 수 없습니다.")
    return JsonResponse({"mtime": path.stat().st_mtime_ns})


def deck_pdf_view(request: HttpRequest, slug: str) -> FileResponse:
    """화면 그대로의 PDF 를 내려준다. md 판마다 한 번 만들고(약 20~30초) 같은 판이면 바로 준다."""
    from slides.pdf import deck_pdf

    path = deck_path(slug)
    if path is None:
        raise Http404("강의안을 찾을 수 없습니다.")
    url = request.build_absolute_uri(reverse("deck_detail", args=[slug]))
    pdf = deck_pdf(slug, path.stat().st_mtime_ns, url)
    return FileResponse(pdf.open("rb"), as_attachment=True, filename=f"{slug}.pdf", content_type="application/pdf")
