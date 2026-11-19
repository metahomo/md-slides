from django.urls import include, path

urlpatterns = [
    # 시작 페이지가 강의안 목록이다.
    path("", include("slides.urls")),
]
