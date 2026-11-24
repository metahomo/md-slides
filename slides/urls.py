from django.urls import path

from slides.views import deck_detail, deck_list, deck_mtime, deck_pdf_view

urlpatterns = [
    path("", deck_list, name="deck_list"),
    path("<slug:slug>/", deck_detail, name="deck_detail"),
    path("<slug:slug>/mtime", deck_mtime, name="deck_mtime"),
    path("<slug:slug>.pdf", deck_pdf_view, name="deck_pdf"),
]
