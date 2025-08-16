from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Game, Move
from .serializers import GameSerializer
import random

# ======================================================================================================================
# ایجاد بازی جدید
class GameCreateView(generics.CreateAPIView):
    serializer_class = GameSerializer

    def perform_create(self, serializer):
        # موقعیت شروع استاندارد تخته نرد
        initial_board = [
            2, 0, 0, 0, 0, 5, 0, 3, 0, 0, 0, 0,
            0, 0, 0, 0, 3, 0, 5, 0, 0, 0, 0, 2
        ]
        serializer.save(
            board_state=initial_board,
            current_turn="player",
            is_finished=False
        )

# ======================================================================================================================
# مشاهده جزئیات بازی
class GameDetailView(generics.RetrieveAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

# ======================================================================================================================
# ثبت حرکت بازیکن و حرکت ربات ساده
class MakeMoveView(APIView):
    def post(self, request, pk):
        try:
            game = Game.objects.get(pk=pk)
        except Game.DoesNotExist:
            return Response({"error": "بازی پیدا نشد"}, status=status.HTTP_404_NOT_FOUND)

        if game.is_finished:
            return Response({"error": "بازی تمام شده است"}, status=status.HTTP_400_BAD_REQUEST)

        board = game.board_state
        player_move = request.data.get("move_data")

        # بررسی داده‌های ارسالی
        if not player_move or "from" not in player_move or "to" not in player_move:
            return Response({"error": "داده حرکت نامعتبر است"}, status=status.HTTP_400_BAD_REQUEST)

        from_pos = player_move["from"]
        to_pos = player_move["to"]

        # بررسی حرکت قانونی ساده
        if from_pos < 0 or from_pos > 23 or to_pos < 0 or to_pos > 23:
            return Response({"error": "خانه نامعتبر"}, status=status.HTTP_400_BAD_REQUEST)
        if board[from_pos] <= 0:
            return Response({"error": "حرکت غیرقانونی: خانه خالی است"}, status=status.HTTP_400_BAD_REQUEST)

        # اعمال حرکت بازیکن
        board[from_pos] -= 1
        board[to_pos] += 1
        Move.objects.create(game=game, player="player", move_data=player_move)

        # حرکت ربات ساده: انتخاب تصادفی خانه پر
        bot_positions = [i for i, val in enumerate(board) if val > 0]
        if bot_positions:
            bot_from = random.choice(bot_positions)
            bot_to = (bot_from + 1) % 24  # حرکت ساده: خانه بعدی
            board[bot_from] -= 1
            board[bot_to] += 1
            Move.objects.create(game=game, player="bot", move_data={"from": bot_from, "to": bot_to})

        # به‌روزرسانی وضعیت بازی
        game.board_state = board
        game.current_turn = "player"  # نوبت بازیکن
        # بررسی اتمام بازی ساده: همه مهره‌ها صفر شود
        if sum(board) == 0:
            game.is_finished = True

        game.save()
        return Response(GameSerializer(game).data)
