from rest_framework import viewsets
from .models import Game, Move
from .serializers import GameSerializer, MoveSerializer
# ======================================================================================================================
# ViewSet برای بازی‌ها
class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
# ======================================================================================================================
# ViewSet برای حرکت‌ها
class MoveViewSet(viewsets.ModelViewSet):
    queryset = Move.objects.all()
    serializer_class = MoveSerializer
# ======================================================================================================================