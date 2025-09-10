from logic.strategies import Strategy  # کلاس پایه برای همه‌ی استراتژی‌ها
from logic.piece import Piece  # برای کار با مهره‌ها


# ======================================================================
# استراتژی اصلی: بررسی همه حرکات ممکن (CompareAllMoves)
# این استراتژی تمام حالات حرکت را امتحان می‌کند و بهترین را انتخاب می‌کند
# ======================================================================
class CompareAllMoves(Strategy):

    @staticmethod
    def get_difficulty():
        """
        سطح سختی این استراتژی را برمی‌گرداند.
        """
        return "Hard"

    # ------------------------------------------------------------------
    def assess_board(self, colour, myboard):
        """
        وضعیت فعلی تخته را ارزیابی می‌کند و معیارهای مختلف را حساب می‌کند:
        - فاصله‌ها تا خانه
        - تعداد مهره‌های تنها (singles)
        - تعداد خانه‌های اشغال‌شده
        - فاصله مهره‌های حریف
        """
        pieces = myboard.get_pieces(colour)  # گرفتن مهره‌های بازیکن
        pieces_on_board = len(pieces)  # تعداد مهره‌های روی تخته
        sum_distances = 0  # مجموع فاصله‌ها تا خانه
        number_of_singles = 0  # تعداد مهره‌های تنها
        number_occupied_spaces = 0  # تعداد خانه‌های اشغال‌شده با بیش از ۱ مهره
        sum_single_distance_away_from_home = 0  # فاصله مهره‌های تنها از خانه
        sum_distances_to_endzone = 0  # مجموع فاصله تا محدوده آخر (endzone)

        # بررسی مهره‌ها
        for piece in pieces:
            sum_distances += piece.spaces_to_home()
            if piece.spaces_to_home() > 6:
                sum_distances_to_endzone += piece.spaces_to_home() - 6

        # بررسی خانه‌ها از 1 تا 24
        for location in range(1, 25):
            pieces = myboard.pieces_at(location)
            if len(pieces) != 0 and pieces[0].colour == colour:
                if len(pieces) == 1:
                    number_of_singles += 1
                    sum_single_distance_away_from_home += (
                        25 - pieces[0].spaces_to_home()
                    )
                elif len(pieces) > 1:
                    number_occupied_spaces += 1

        # بررسی مهره‌های گرفته‌شده‌ی حریف
        opponents_taken_pieces = len(myboard.get_taken_pieces(colour.other()))

        # مجموع فاصله مهره‌های حریف تا خانه
        opponent_pieces = myboard.get_pieces(colour.other())
        sum_distances_opponent = sum(
            piece.spaces_to_home() for piece in opponent_pieces
        )

        return {
            "number_occupied_spaces": number_occupied_spaces,
            "opponents_taken_pieces": opponents_taken_pieces,
            "sum_distances": sum_distances,
            "sum_distances_opponent": sum_distances_opponent,
            "number_of_singles": number_of_singles,
            "sum_single_distance_away_from_home": sum_single_distance_away_from_home,
            "pieces_on_board": pieces_on_board,
            "sum_distances_to_endzone": sum_distances_to_endzone,
        }

    # ------------------------------------------------------------------
    def move(self, board, colour, dice_roll, make_move, opponents_activity):
        """
        اجرای حرکت:
        - همه حرکات ممکن بررسی می‌شود
        - بهترین انتخاب می‌شود
        - سپس حرکت روی تخته اعمال می‌شود
        """
        result = self.move_recursively(board, colour, dice_roll)

        # اگر تاس دابل نباشد، باید ترتیب حرکات هم بررسی شود
        not_a_double = len(dice_roll) == 2
        if not_a_double:
            new_dice_roll = dice_roll.copy()
            new_dice_roll.reverse()
            result_swapped = self.move_recursively(
                board, colour, dice_rolls=new_dice_roll
            )

            if result_swapped["best_value"] < result["best_value"] and len(
                result_swapped["best_moves"]
            ) >= len(result["best_moves"]):
                result = result_swapped

        # اجرای بهترین حرکات
        if len(result["best_moves"]) != 0:
            for move in result["best_moves"]:
                make_move(move["piece_at"], move["die_roll"])

    # ------------------------------------------------------------------
    def move_recursively(self, board, colour, dice_rolls):
        """
        بررسی بازگشتی حرکات:
        - یکی یکی تاس‌ها استفاده می‌شوند
        - تمام حالات ممکن بررسی می‌شود
        - بهترین حالت (با کمترین ارزش برد) انتخاب می‌شود
        """
        best_board_value = float("inf")
        best_pieces_to_move = []

        # مهره‌های یکتا روی تخته
        pieces_to_try = list(
            set([x.location for x in board.get_pieces(colour)])
        )

        # گرفتن مهره‌های قابل بازی
        valid_pieces = [
            board.get_piece_at(piece_location)
            for piece_location in pieces_to_try
        ]
        valid_pieces.sort(
            key=Piece.spaces_to_home, reverse=True
        )  # مرتب‌سازی بر اساس فاصله

        dice_rolls_left = dice_rolls.copy()
        die_roll = dice_rolls_left.pop(0)

        for piece in valid_pieces:
            if board.is_move_possible(piece, die_roll):
                board_copy = board.create_copy()
                new_piece = board_copy.get_piece_at(piece.location)
                board_copy.move_piece(new_piece, die_roll)

                # اگر هنوز تاس باقی‌مانده بررسی بازگشتی انجام می‌شود
                if len(dice_rolls_left) > 0:
                    result = self.move_recursively(
                        board_copy, colour, dice_rolls_left
                    )
                    if len(result["best_moves"]) == 0:
                        board_value = self.evaluate_board(board_copy, colour)
                        if (
                            board_value < best_board_value
                            and len(best_pieces_to_move) < 2
                        ):
                            best_board_value = board_value
                            best_pieces_to_move = [
                                {
                                    "die_roll": die_roll,
                                    "piece_at": piece.location,
                                }
                            ]
                    elif result["best_value"] < best_board_value:
                        new_best_moves_length = len(result["best_moves"]) + 1
                        if new_best_moves_length >= len(best_pieces_to_move):
                            best_board_value = result["best_value"]
                            move = {
                                "die_roll": die_roll,
                                "piece_at": piece.location,
                            }
                            best_pieces_to_move = [move] + result[
                                "best_moves"
                            ]
                else:
                    # آخرین حرکت
                    board_value = self.evaluate_board(board_copy, colour)
                    if (
                        board_value < best_board_value
                        and len(best_pieces_to_move) < 2
                    ):
                        best_board_value = board_value
                        best_pieces_to_move = [
                            {"die_roll": die_roll, "piece_at": piece.location}
                        ]

        return {
            "best_value": best_board_value,
            "best_moves": best_pieces_to_move,
        }


# ======================================================================
# نسخه‌های مختلف استراتژی بر اساس معیارهای متفاوت ارزیابی
# ======================================================================
class CompareAllMovesSimple(CompareAllMoves):
    """
    نسخه ساده‌تر استراتژی: فقط فاصله‌ها و تعداد مهره‌های تنها را در نظر می‌گیرد.
    """

    def evaluate_board(self, myboard, colour):
        board_stats = self.assess_board(colour, myboard)
        board_value = (
            board_stats["sum_distances"]
            + 2 * board_stats["number_of_singles"]
            - board_stats["number_occupied_spaces"]
            - board_stats["opponents_taken_pieces"]
        )
        return board_value


# ======================================================================================================================
class CompareAllMovesWeightingDistance(CompareAllMoves):
    """
    وزن‌دهی بیشتر به فاصله‌ها (برای خودی و حریف).
    """

    def evaluate_board(self, myboard, colour):
        board_stats = self.assess_board(colour, myboard)
        board_value = (
            board_stats["sum_distances"]
            - float(board_stats["sum_distances_opponent"]) / 3
            + 2 * board_stats["number_of_singles"]
            - board_stats["number_occupied_spaces"]
            - board_stats["opponents_taken_pieces"]
        )
        return board_value


# ======================================================================================================================
class CompareAllMovesWeightingDistanceAndSingles(CompareAllMoves):
    """
    در نظر گرفتن فاصله مهره‌های تنها از خانه + وزن فاصله‌ها.
    """

    def evaluate_board(self, myboard, colour):
        board_stats = self.assess_board(colour, myboard)
        board_value = (
            board_stats["sum_distances"]
            - float(board_stats["sum_distances_opponent"]) / 3
            + float(board_stats["sum_single_distance_away_from_home"]) / 6
            - board_stats["number_occupied_spaces"]
            - board_stats["opponents_taken_pieces"]
        )
        return board_value


# ======================================================================================================================
class CompareAllMovesWeightingDistanceAndSinglesWithEndGame(CompareAllMoves):
    """
    نسخه مخصوص اواخر بازی (EndGame):
    مهره‌های باقی‌مانده اهمیت بیشتری دارند.
    """

    def evaluate_board(self, myboard, colour):
        board_stats = self.assess_board(colour, myboard)
        board_value = (
            board_stats["sum_distances"]
            - float(board_stats["sum_distances_opponent"]) / 3
            + float(board_stats["sum_single_distance_away_from_home"]) / 6
            - board_stats["number_occupied_spaces"]
            - board_stats["opponents_taken_pieces"]
            + 3 * board_stats["pieces_on_board"]
        )
        return board_value


# ======================================================================================================================
class CompareAllMovesWeightingDistanceAndSinglesWithEndGame2(CompareAllMoves):
    """
    نسخه پیشرفته‌تر EndGame:
    علاوه بر تعداد مهره‌ها، فاصله از محدوده آخر هم حساب می‌شود.
    """

    def evaluate_board(self, myboard, colour):
        board_stats = self.assess_board(colour, myboard)
        board_value = (
            board_stats["sum_distances"]
            - float(board_stats["sum_distances_opponent"]) / 3
            + float(board_stats["sum_single_distance_away_from_home"]) / 6
            - board_stats["number_occupied_spaces"]
            - board_stats["opponents_taken_pieces"]
            + 3 * board_stats["pieces_on_board"]
            + float(board_stats["sum_distances_to_endzone"]) / 6
        )
        return board_value


# ======================================================================================================================
