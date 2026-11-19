from django.urls import path

from slides.views import deck_detail, deck_list

urlpatterns = [
    path("", deck_list, name="deck_list"),
    path("<slug:slug>/", deck_detail, name="deck_detail"),
]
