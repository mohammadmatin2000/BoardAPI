import queue
import threading
import time
from random import randint
from rest_framework.views import APIView
from rest_framework.response import Response
# core imports از backgammon
from src.board import Board          # مدیریت وضعیت تخته
from src.colour import Colour        # رنگ مهره‌ها (WHITE/BLACK)
from src.game import Game            # مدیریت نوبت‌ها و بازی
from src.strategies import (
    # استراتژی بازیکن انسانی
    MoveFurthestBackStrategy,                  # Bot ساده
    Strategy                                   # کلاس پایه استراتژی
)
from src.compare_all_moves_strategy import (       # استراتژی‌های Bot پیشرفته
    CompareAllMovesSimple,
    CompareAllMovesWeightingDistanceAndSingles,
    CompareAllMovesWeightingDistanceAndSinglesWithEndGame,
    CompareAllMovesWeightingDistanceAndSinglesWithEndGame2
)


# ======================================================================================================================
class BackgammonEngine:
    moves_to_make = queue.Queue()
    move_results = queue.Queue()
    current_board = []
    current_roll = []
    used_die_rolls = []

    @classmethod
    def set_current_move(cls, dice_roll):
        cls.current_roll.insert(0, dice_roll)
        del cls.current_roll[1:]
        cls.used_die_rolls.insert(0, [])
        del cls.used_die_rolls[1:]

    @classmethod
    def game_thread(cls, difficulty):
        class ApiStrategy(Strategy):
            def __init__(self) -> None:
                self.board_after_your_last_turn = Board.create_starting_board()

            def move(self, board, colour, dice_roll, make_move, opponents_activity):
                BackgammonEngine.set_current_move(dice_roll.copy())
                board_json_before_opp_move = self.board_after_your_last_turn.to_json()

                def map_move(move):
                    self.board_after_your_last_turn.move_piece(
                        self.board_after_your_last_turn.get_piece_at(move["start_location"]),
                        move["die_roll"],
                    )
                    move["board_after_move"] = self.board_after_your_last_turn.to_json()
                    return move

                BackgammonEngine.move_results.put({
                    "result": "success",
                    "opponents_activity": {
                        "opponents_move": [map_move(move) for move in opponents_activity["opponents_move"]],
                        "dice_roll": opponents_activity["dice_roll"],
                    },
                    "board_after_your_last_turn": board_json_before_opp_move,
                })

                while len(dice_roll) > 0:
                    move = BackgammonEngine.moves_to_make.get()
                    if move == "end_game":
                        raise Exception("Game ended")
                    elif move == "end_turn":
                        break
                    try:
                        rolls_moved = make_move(move["location"], move["die_roll"])
                        for roll in rolls_moved:
                            dice_roll.remove(roll)
                            BackgammonEngine.used_die_rolls[0].append(roll)

                        if len(dice_roll) > 0:
                            BackgammonEngine.move_results.put({"result": "success"})
                    except Exception:
                        BackgammonEngine.move_results.put({"result": "move_failed"})

                self.board_after_your_last_turn = board.create_copy()

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
                    "result": "success",
                    "opponents_activity": {
                        "opponents_move": [map_move(move) for move in opponents_activity["opponents_move"]],
                        "dice_roll": opponents_activity["dice_roll"],
                    },
                    "board_after_your_last_turn": board_json_before_opp_move,
                })

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
            raise Exception("Not a valid strategy")

        game = Game(
            white_strategy=ApiStrategy(),
            black_strategy=opponent_strategy,
            first_player=Colour(randint(0, 1)),
        )
        cls.current_board.append(game.board)
        game.run_game(verbose=False)

        while True:
            if cls.moves_to_make.get() == "end_game":
                break
            else:
                cls.move_results.put({"result": "move_failed"})

    @classmethod
    def get_state(cls, response={}):
        if len(cls.current_board) == 0:
            return {"board": "{}", "dice_roll": [], "used_rolls": []}
        board = cls.current_board[0]
        move = cls.current_roll[0]
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
            state["winner"] = str(board.who_won())
        if "opponents_activity" in response:
            state["opp_move"] = response["opponents_activity"]["opponents_move"]
            state["opp_roll"] = response["opponents_activity"]["dice_roll"]
        if "board_after_your_last_turn" in response:
            state["board_after_your_last_turn"] = response["board_after_your_last_turn"]
        if "result" in response:
            state["result"] = response["result"]
        return state


# ======================================================================
#   کلاس‌های API برای هر endpoint
# ======================================================================
class StartGameView(APIView):
    def get(self, request):
        return Response(BackgammonEngine.get_state())


class MovePieceView(APIView):
    def get(self, request):
        location = request.query_params.get("location", 1)
        die_roll = request.query_params.get("die-roll", 1)
        end_turn = request.query_params.get("end-turn", "")

        if end_turn == "true":
            BackgammonEngine.moves_to_make.put("end_turn")
        else:
            BackgammonEngine.moves_to_make.put({
                "location": int(location),
                "die_roll": int(die_roll),
            })

        response = BackgammonEngine.move_results.get()
        return Response(BackgammonEngine.get_state(response))
# ======================================================================================================================
class NewGameView(APIView):
    def get(self, request):
        difficulty = request.query_params.get("difficulty", "hard")
        if len(BackgammonEngine.current_board) != 0:
            BackgammonEngine.moves_to_make.put("end_game")
        BackgammonEngine.current_board.clear()
        BackgammonEngine.current_roll.clear()
        time.sleep(1)
        threading.Thread(target=BackgammonEngine.game_thread, args=[difficulty]).start()
        response = BackgammonEngine.move_results.get()
        return Response(BackgammonEngine.get_state(response))
# ======================================================================================================================