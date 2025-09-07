import queue  # وارد کردن ماژول صف برای مدیریت صف حرکت‌ها
import threading  # وارد کردن ماژول Thread برای اجرای بازی در پس‌زمینه
import time  # وارد کردن ماژول زمان برای ایجاد تاخیر
from random import randint  # وارد کردن تابع randint برای انتخاب تصادفی بازیکن اول
from rest_framework.views import APIView  # کلاس پایه برای ایجاد API
from rest_framework.response import Response  # کلاس پاسخ‌دهی API
# ======================================================================================================================
# وارد کردن ماژول‌های core بازی بک‌گمون
# Board: مدیریت وضعیت تخته
# Colour: رنگ مهره‌ها (WHITE/BLACK)
# Game: مدیریت جریان بازی و نوبت‌ها
# استراتژی‌ها برای Bot های مختلف
# ======================================================================================================================
from src.board import Board
from src.colour import Colour
from src.game import Game
from src.strategies import MoveFurthestBackStrategy, Strategy
from src.compare_all_moves_strategy import (
    CompareAllMovesSimple,
    CompareAllMovesWeightingDistanceAndSingles,
    CompareAllMovesWeightingDistanceAndSinglesWithEndGame,
    CompareAllMovesWeightingDistanceAndSinglesWithEndGame2
)
# ======================================================================================================================
# کلاس اصلی موتور بک‌گمون
# مدیریت وضعیت بازی، حرکات بازیکن و Bot
# ======================================================================================================================
class BackgammonEngine:
    moves_to_make = queue.Queue()  # صف حرکت‌های بازیکن
    move_results = queue.Queue()  # صف نتایج حرکات برای رندر در فرانت‌اند
    current_board = []  # وضعیت فعلی تخته
    current_roll = []  # تاس‌های جاری
    used_die_rolls = []  # تاس‌های استفاده‌شده

    # ثبت حرکت فعلی بازیکن
    @classmethod
    def set_current_move(cls, dice_roll):
        cls.current_roll.insert(0, dice_roll)  # ذخیره تاس‌های جاری
        del cls.current_roll[1:]  # حذف تاس‌های قبلی
        cls.used_die_rolls.insert(0, [])  # ایجاد لیست خالی برای تاس‌های استفاده شده
        del cls.used_die_rolls[1:]  # حذف تاس‌های استفاده شده قبلی

    # اجرای بازی در یک Thread جدا
    @classmethod
    def game_thread(cls, difficulty):
        # تعریف استراتژی بازیکن انسانی
        class ApiStrategy(Strategy):
            def __init__(self) -> None:
                self.board_after_your_last_turn = Board.create_starting_board()  # وضعیت تخته بعد از آخرین حرکت بازیکن

            # اجرای حرکت بازیکن و ثبت فعالیت‌های Bot
            def move(self, board, colour, dice_roll, make_move, opponents_activity):
                BackgammonEngine.set_current_move(dice_roll.copy())  # ثبت تاس‌های جاری
                board_json_before_opp_move = self.board_after_your_last_turn.to_json()  # وضعیت تخته قبل از حرکت حریف

                # نگاشت حرکات حریف
                def map_move(move):
                    self.board_after_your_last_turn.move_piece(
                        self.board_after_your_last_turn.get_piece_at(move["start_location"]),  # گرفتن مهره از موقعیت شروع
                        move["die_roll"],  # حرکت دادن مهره به اندازه تاس
                    )
                    move["board_after_move"] = self.board_after_your_last_turn.to_json()  # وضعیت بعد از حرکت
                    return move

                # ثبت نتایج حرکات حریف
                BackgammonEngine.move_results.put({
                    "result": "موفقیت‌آمیز",  # پیام موفقیت
                    "opponents_activity": {
                        "opponents_move": [map_move(move) for move in opponents_activity["opponents_move"]],
                        "dice_roll": opponents_activity["dice_roll"],
                    },
                    "board_after_your_last_turn": board_json_before_opp_move,
                })

                # اجرای حرکات بازیکن
                while len(dice_roll) > 0:
                    move = BackgammonEngine.moves_to_make.get()  # دریافت حرکت بعدی از صف
                    if move == "end_game":  # اگر بازی پایان یافته
                        raise Exception("بازی به پایان رسید")
                    elif move == "end_turn":  # اگر نوبت تمام شده
                        break
                    try:
                        rolls_moved = make_move(move["location"], move["die_roll"])  # انجام حرکت
                        for roll in rolls_moved:
                            dice_roll.remove(roll)  # حذف تاس استفاده شده
                            BackgammonEngine.used_die_rolls[0].append(roll)  # ثبت تاس استفاده شده

                        if len(dice_roll) > 0:
                            BackgammonEngine.move_results.put({"result": "حرکت با موفقیت انجام شد"})
                    except Exception:
                        BackgammonEngine.move_results.put({"result": "حرکت ناموفق بود"})

                # به‌روزرسانی وضعیت تخته بعد از حرکت بازیکن
                self.board_after_your_last_turn = board.create_copy()

            # ثبت وضعیت بازی پس از اتمام بازی
            def game_over(self, opponents_activity):
                board_json_before_opp_move = self.board_after_your_last_turn.to_json()

                def map_move(move):
                    self.board_after_your_last_turn.move_piece(
                        self.board_after_your_last_turn.get_piece_at(move["start_location"]),
                        move["die_roll"],
                    )
                    move["board_after_move"] = self.board_after_your_last_turn.to_json()
                    return move

                BackgammonEngine.move_results.put({
                    "result": "بازی به پایان رسید",
                    "opponents_activity": {
                        "opponents_move": [map_move(move) for move in opponents_activity["opponents_move"]],
                        "dice_roll": opponents_activity["dice_roll"],
                    },
                    "board_after_your_last_turn": board_json_before_opp_move,
                })

        # انتخاب استراتژی حریف بر اساس سختی
        if difficulty == "veryeasy":
            opponent_strategy = MoveFurthestBackStrategy()
        elif difficulty == "easy":
            opponent_strategy = CompareAllMovesSimple()
        elif difficulty == "medium":
            opponent_strategy = CompareAllMovesWeightingDistanceAndSingles()
        elif difficulty == "hard":
            opponent_strategy = CompareAllMovesWeightingDistanceAndSinglesWithEndGame()
        elif difficulty == "veryhard":
            opponent_strategy = CompareAllMovesWeightingDistanceAndSinglesWithEndGame2()
        else:
            raise Exception("سختی نامعتبر است")

        # ایجاد بازی با استراتژی‌های انتخاب‌شده
        game = Game(
            white_strategy=ApiStrategy(),
            black_strategy=opponent_strategy,
            first_player=Colour(randint(0, 1)),
        )
        cls.current_board.append(game.board)  # ذخیره وضعیت تخته
        game.run_game(verbose=False)  # اجرای بازی

        # مدیریت صف حرکت‌ها پس از پایان بازی
        while True:
            if cls.moves_to_make.get() == "end_game":
                break
            else:
                cls.move_results.put({"result": "حرکت نامعتبر"})

    # دریافت وضعیت فعلی بازی برای API
    @classmethod
    def get_state(cls, response={}):
        if len(cls.current_board) == 0:
            return {"board": "{}", "dice_roll": [], "used_rolls": []}

        board = cls.current_board[0]  # تخته فعلی
        move = cls.current_roll[0]  # تاس فعلی
        moves_left = move.copy()
        for used_move in cls.used_die_rolls[0]:
            moves_left.remove(used_move)

        state = {
            "board": board.to_json(),
            "dice_roll": move,
            "used_rolls": cls.used_die_rolls[0],
            "player_can_move": not board.no_moves_possible(Colour.WHITE, moves_left),
        }

        if board.has_game_ended():
            winner = board.who_won()
            if winner == Colour.WHITE:
                state["winner"] = "شما برنده شدید 🎉"
            else:
                state["winner"] = "شما باختید 😢"

        if "opponents_activity" in response:
            state["opp_move"] = response["opponents_activity"]["opponents_move"]
            state["opp_roll"] = response["opponents_activity"]["dice_roll"]
        if "board_after_your_last_turn" in response:
            state["board_after_your_last_turn"] = response["board_after_your_last_turn"]
        if "result" in response:
            state["result"] = response["result"]

        return state
# ======================================================================================================================
# API VIEW ها برای تعامل فرانت‌اند با بازی
# ======================================================================================================================
# شروع بازی جدید
class StartGameView(APIView):
    def get(self, request):
        return Response(BackgammonEngine.get_state())  # برگرداندن وضعیت فعلی بازی
# ======================================================================================================================
# حرکت دادن مهره
class MovePieceView(APIView):
    def get(self, request):
        location = request.query_params.get("location", 1)  # گرفتن موقعیت مهره
        die_roll = request.query_params.get("die-roll", 1)  # گرفتن مقدار تاس
        end_turn = request.query_params.get("end-turn", "")  # بررسی پایان نوبت

        # ثبت حرکت در صف
        if end_turn == "true":
            BackgammonEngine.moves_to_make.put("end_turn")
        else:
            BackgammonEngine.moves_to_make.put({
                "location": int(location),
                "die_roll": int(die_roll),
            })

        # دریافت نتیجه حرکت و بازگرداندن وضعیت جدید
        response = BackgammonEngine.move_results.get()
        return Response(BackgammonEngine.get_state(response))
# ======================================================================================================================
# شروع بازی جدید با سختی انتخاب‌شده
class NewGameView(APIView):
    def get(self, request):
        difficulty = request.query_params.get("difficulty", "hard")  # گرفتن سختی بازی
        if len(BackgammonEngine.current_board) != 0:
            BackgammonEngine.moves_to_make.put("end_game")  # پایان بازی قبلی

        BackgammonEngine.current_board.clear()  # پاک کردن تخته قبلی
        BackgammonEngine.current_roll.clear()  # پاک کردن تاس‌ها
        time.sleep(1)  # تاخیر کوتاه قبل از شروع بازی جدید
        threading.Thread(target=BackgammonEngine.game_thread, args=[difficulty]).start()  # اجرای بازی در Thread جدید
        response = BackgammonEngine.move_results.get()  # دریافت نتیجه اولین حرکت
        return Response(BackgammonEngine.get_state(response))  # بازگرداندن وضعیت بازی
# ======================================================================================================================