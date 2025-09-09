import json  # برای ذخیره‌سازی وضعیت برد به صورت JSON
from random import randint  # برای تولید تاس تصادفی

from logic.board import Board  # کلاس اصلی برد
from logic.colour import Colour  # کلاس رنگ (سفید/سیاه)
from logic.strategies import Strategy  # استراتژی‌های بازی
from logic.move_not_possible_exception import MoveNotPossibleException  # خطا در صورت حرکت غیرمجاز
# ======================================================================================================================
# ======================================================================
# کلاس ReadOnlyBoard
# این کلاس فقط اجازه خواندن از برد رو میده، نه تغییر مستقیمش.
# اینطوری استراتژی‌ها نمی‌تونن تقلب کنن و مستقیماً برد رو تغییر بدن.
# ======================================================================
class ReadOnlyBoard:
    board: Board

    def __init__(self, board):
        self.board = board  # نگهداری برد اصلی

    # واگذاری (delegate) متدهای خواندنی به کلاس اصلی برد
    def __getattr__(self, name):
        if hasattr(self.board, name) and callable(getattr(self.board, name)):
            return getattr(self.board, name)
        return super(ReadOnlyBoard, self).__getattr__(name)

    # جلوگیری از اضافه کردن مهره‌ها (حرکت غیرمجاز)
    def add_many_pieces(self, number_of_pieces, colour, location):
        self.__raise_exception__()

    # جلوگیری از حرکت مهره‌ها مستقیم
    def move_piece(self, piece, die_roll):
        self.__raise_exception__()

    # خطا در صورت هر نوع تغییر غیرمجاز
    def __raise_exception__(self):
        raise Exception("Do not try and change the board directly, use the make_move parameter instead")
# ======================================================================================================================
# ======================================================================
# کلاس Game
# مدیریت اجرای کل بازی (تاس، حرکت مهره‌ها، برد/باخت)
# ======================================================================
class Game:
    def __init__(self, white_strategy: Strategy, black_strategy: Strategy, first_player: Colour):
        """
        سازنده بازی:
        white_strategy -> استراتژی بازیکن سفید
        black_strategy -> استراتژی بازیکن سیاه
        first_player -> بازیکنی که بازی رو شروع می‌کنه
        """
        self.board = Board.create_starting_board()  # ساختن برد اولیه
        self.first_player = first_player  # بازیکن شروع‌کننده
        self.strategies = {  # نگهداری استراتژی بازیکنان
            Colour.WHITE: white_strategy,
            Colour.BLACK: black_strategy
        }

    # ------------------------------------------------------------------
    def run_game(self, verbose=True):
        """
        اجرای بازی تا زمانی که برنده مشخص شود
        """
        if verbose:
            print('%s goes first' % self.first_player)
            self.board.print_board()

        i = self.first_player.value  # تعیین نوبت بازیکن
        moves = []  # ذخیره حرکات انجام شده
        full_dice_roll = []  # ذخیره آخرین تاس‌ها

        while True:
            # -------------------------------
            # ریختن تاس
            previous_dice_roll = full_dice_roll.copy()
            dice_roll = [randint(1, 6), randint(1, 6)]
            if dice_roll[0] == dice_roll[1]:  # اگر تاس جفت شد
                dice_roll = [dice_roll[0]] * 4
            full_dice_roll = dice_roll.copy()
            colour = Colour(i % 2)  # تعیین رنگ بازیکن فعلی

            if verbose:
                print("%s rolled %s" % (colour, dice_roll))

            # -------------------------------
            # متد داخلی برای انجام یک حرکت
            def handle_move(location, die_roll):
                rolls_to_move = self.get_rolls_to_move(location, die_roll, dice_roll)
                if rolls_to_move is None:
                    raise MoveNotPossibleException("You cannot move that piece %d" % die_roll)

                for roll in rolls_to_move:
                    piece = self.board.get_piece_at(location)  # گرفتن مهره در موقعیت
                    original_location = location
                    location = self.board.move_piece(piece, roll)  # حرکت مهره
                    dice_roll.remove(roll)  # حذف تاس مصرف‌شده
                    moves.append({'start_location': original_location, 'die_roll': roll, 'end_location': location})
                    previous_dice_roll.append(roll)
                return rolls_to_move

            # -------------------------------
            # ذخیره وضعیت فعلی برد
            board_snapshot = self.board.to_json()
            dice_roll_snapshot = dice_roll.copy()
            opponents_moves = moves.copy()
            moves.clear()

            # -------------------------------
            # اجرای استراتژی بازیکن فعلی
            self.strategies[colour].move(
                ReadOnlyBoard(self.board),  # برد فقط خواندنی
                colour,  # رنگ بازیکن
                dice_roll.copy(),  # تاس‌ها
                lambda location, die_roll: handle_move(location, die_roll),  # تابع حرکت
                {'dice_roll': previous_dice_roll, 'opponents_move': opponents_moves}  # اطلاعات نوبت قبل
            )

            # -------------------------------
            # اگر بازیکن حرکت‌هاشو کامل استفاده نکرد
            if verbose and len(dice_roll) > 0:
                print('FYI not all moves were made. %s playing %s did not move %s' % (
                    colour,
                    self.strategies[colour].__class__.__name__,
                    dice_roll))
                self.board.print_board()
                state = {
                    'board': json.loads(board_snapshot),
                    'dice_roll': dice_roll_snapshot,
                    'colour_to_move': colour.__str__(),
                    'strategy': self.strategies[colour].__class__.__name__,
                }
                print(json.dumps(state))

            if verbose:
                self.board.print_board()

            # -------------------------------
            # تغییر نوبت بازیکن
            i = i + 1

            # -------------------------------
            # بررسی پایان بازی
            if self.board.has_game_ended():
                if verbose:
                    print('%s has won!' % self.board.who_won())
                self.strategies[colour.other()].game_over({
                    'dice_roll': full_dice_roll,
                    'opponents_move': moves
                })
                break

    # ------------------------------------------------------------------
    def get_rolls_to_move(self, location, requested_move, available_rolls):
        """
        بررسی می‌کنه چه ترکیبی از تاس‌ها می‌تونه حرکت درخواستی رو بسازه
        """
        # اگر دقیقا یکی از تاس‌ها برابر حرکت خواسته شده باشه
        if available_rolls.__contains__(requested_move):
            if self.board.is_move_possible(self.board.get_piece_at(location), requested_move):
                return [requested_move]
            return None

        # اگر فقط یک تاس مونده و حرکت قابل انجام نیست
        if len(available_rolls) == 1:
            return None

        # ساخت یک کپی از برد برای تست کردن حرکت
        board = self.board.create_copy()
        rolls_to_move = []
        current_location = location

        # اگر اولین تاس قابل استفاده نباشه، ترتیب تاس‌ها رو برعکس کن
        if not board.is_move_possible(board.get_piece_at(current_location), available_rolls[0]):
            available_rolls = available_rolls.copy()
            available_rolls.reverse()

        # تست همه تاس‌ها
        for roll in available_rolls:
            piece = board.get_piece_at(current_location)
            if not board.is_move_possible(piece, roll):
                break
            current_location = board.move_piece(piece, roll)
            rolls_to_move.append(roll)
            if sum(rolls_to_move) == requested_move:
                return rolls_to_move
        return None

    # ------------------------------------------------------------------
    def who_started(self):
        """برمی‌گردونه چه کسی بازی رو شروع کرده"""
        return self.first_player

    def who_won(self):
        """برمی‌گردونه چه کسی برنده بازی شده"""
        return self.board.who_won()
# ======================================================================================================================