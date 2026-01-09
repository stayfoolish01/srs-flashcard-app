"""
学習機能のURL設定
"""

from django.urls import path

from . import views

app_name = "study"

urlpatterns = [
    path("<int:deck_pk>/", views.study_session, name="session"),
    path("<int:deck_pk>/card/<int:card_pk>/", views.study_card, name="card"),
    path("<int:deck_pk>/answer/<int:card_pk>/", views.answer_card, name="answer"),
    path("<int:deck_pk>/complete/", views.study_complete, name="complete"),
]
