from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render

from slides.decks import list_decks, load_deck


def deck_list(request: HttpRequest) -> HttpResponse:
    return render(request, "slides/deck_list.html", {"decks": list_decks()})


def deck_detail(request: HttpRequest, slug: str) -> HttpResponse:
    deck = load_deck(slug)
    if deck is None:
        raise Http404("강의안을 찾을 수 없습니다.")
    return render(request, "slides/deck_detail.html", {"deck": deck})
