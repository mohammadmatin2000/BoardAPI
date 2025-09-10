from django.urls import path
from .views import StartGameView, MovePieceView, NewGameView

# ======================================================================================================================
urlpatterns = [
    path("backgammon/start/", StartGameView.as_view()),
    path("backgammon/move/", MovePieceView.as_view()),
    path("backgammon/new/", NewGameView.as_view()),
]
# ======================================================================================================================
