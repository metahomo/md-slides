from django.conf import settings
from django.urls import include, path, re_path
from django.views.static import serve


def deck_asset(request, path):
    # SLIDES_DIR 는 시험에서 문자열로 바뀌므로 요청 때 경로를 만든다
    from pathlib import Path

    return serve(request, path, document_root=Path(settings.SLIDES_DIR) / "assets")


urlpatterns = [
    # 시작 페이지가 강의안 목록이다.
    # 덱 그림(로고 등) — 개발 서버용. 정적 사이트는 build_site 가 assets/ 를 복사한다
    re_path(r"^assets/(?P<path>[\w.-]+)$", deck_asset),
    path("", include("slides.urls")),
]
