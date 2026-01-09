from django.urls import path
from . import views

app_name = "decks"

urlpatterns = [
    path("", views.DeckListView.as_view(), name="deck_list"),
    path("create/", views.DeckCreateView.as_view(), name="deck_create"),
    path("<int:pk>/", views.deck_detail_view, name="deck_detail"),
    path("<int:pk>/edit/", views.DeckUpdateView.as_view(), name="deck_edit"),
    path("<int:pk>/delete/", views.DeckDeleteView.as_view(), name="deck_delete"),
]
