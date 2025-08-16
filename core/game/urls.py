from django.urls import path
from .views import GameCreateView, GameDetailView, MakeMoveView
# ======================================================================================================================
urlpatterns = [
    path("games/", GameCreateView.as_view(), name="create-game"),
    path("games/<int:pk>/", GameDetailView.as_view(), name="game-detail"),
    path("games/<int:pk>/move/", MakeMoveView.as_view(), name="make-move"),
]
# ======================================================================================================================