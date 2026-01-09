from django.urls import path
from . import views

app_name = "cards"

urlpatterns = [
    path("deck/<int:deck_pk>/create/", views.CardCreateView.as_view(), name="card_create"),
    path("<int:pk>/", views.card_detail_view, name="card_detail"),
    path("<int:pk>/edit/", views.CardUpdateView.as_view(), name="card_edit"),
    path("<int:pk>/delete/", views.CardDeleteView.as_view(), name="card_delete"),
]
