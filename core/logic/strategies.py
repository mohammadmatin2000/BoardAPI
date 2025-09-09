import time  # برای ایجاد تاخیر در بازی انسان
from random import shuffle  # برای جابجایی تصادفی مهره‌ها در استراتژی تصادفی
from logic.piece import Piece  # وارد کردن کلاس Piece
from logic.move_not_possible_exception import MoveNotPossibleException  # وارد کردن استثنا برای حرکت غیرمجاز
# ======================================================================================================================
class Strategy:
    """کلاس پایه برای همه استراتژی‌ها"""

    def move(self, board, colour, dice_roll, make_move, opponents_activity):
        """متد move باید توسط کلاس‌های فرزند پیاده‌سازی شود"""
        raise NotImplementedError()

    def game_over(self, opponents_activity):
        """می‌تواند توسط استراتژی‌ها هنگام پایان بازی استفاده شود"""
        pass
# ======================================================================================================================
class MoveFurthestBackStrategy(Strategy):
    """استراتژی حرکت مهره‌ای که در عقب‌ترین موقعیت است"""

    @staticmethod
    def get_difficulty():
        return "Medium"  # سطح سختی متوسط

    def move(self, board, colour, dice_roll, make_move, opponents_activity):
        """اجرای حرکت بر اساس استراتژی"""
        could_not_move_first_roll = False

        # تلاش برای هر تاس در نوبت
        for i, die_roll in enumerate(dice_roll):
            moved = self.move_die_roll(board, colour, die_roll, make_move)
            if not moved and i == 0:
                could_not_move_first_roll = True

        # اگر اولین تاس نتوانست حرکت کند، دوباره تلاش کن
        if could_not_move_first_roll:
            self.move_die_roll(board, colour, dice_roll[0], make_move)

    @staticmethod
    def move_die_roll(board, colour, die_roll, make_move):
        """حرکت دادن یک مهره با یک تاس مشخص"""
        valid_pieces = board.get_pieces(colour)
        valid_pieces.sort(key=Piece.spaces_to_home, reverse=True)  # مهره‌های عقب‌تر اول

        for piece in valid_pieces:
            if board.is_move_possible(piece, die_roll):
                make_move(piece.location, die_roll)  # اجرای حرکت
                return True

        return False  # هیچ حرکت معتبری وجود نداشت
# ======================================================================================================================
class HumanStrategy(Strategy):
    """استراتژی برای بازیکن انسانی"""

    def __init__(self, name):
        self.__name = name  # نام بازیکن

    @staticmethod
    def get_difficulty():
        return "N/A"  # سطح سختی ندارد

    def move(self, board, colour, dice_roll, make_move, opponents_activity):
        """اجرای حرکت توسط بازیکن"""
        print("نوبت %s است، شما %s هستید، تاس شما %s" % (self.__name, colour, dice_roll))

        while len(dice_roll) > 0 and not board.has_game_ended():
            board.print_board()  # چاپ وضعیت تخته

            # بررسی اینکه حرکت ممکن است یا خیر
            if board.no_moves_possible(colour, dice_roll):
                print("هیچ حرکت معتبری وجود ندارد. نوبت شما به پایان رسید.")
                time.sleep(3)
                break

            print("تاس‌های باقی‌مانده: %s" % dice_roll)
            location = self.get_location(board, colour)
            piece = board.get_piece_at(location)

            while True:
                try:
                    value = int(input("چند خانه حرکت کند (یا 0 برای انتخاب مهره دیگر)؟\n"))
                    if value == 0:
                        break
                    rolls_moved = make_move(piece.location, value)
                    for roll in rolls_moved:
                        dice_roll.remove(roll)
                    print("\n")
                    break
                except ValueError:
                    print("عدد وارد نشده است! دوباره تلاش کنید")
                except MoveNotPossibleException as e:
                    print(str(e))

        print("نوبت شما پایان یافت!")


    def get_location(self, board, colour):
        """دریافت موقعیت مهره‌ای که بازیکن می‌خواهد حرکت دهد"""
        value = None
        while value is None:
            try:
                location = int(input("موقعیت مهره‌ای که می‌خواهید حرکت دهید را وارد کنید:\n"))
                piece_at_location = board.get_piece_at(location)
                if piece_at_location is None or piece_at_location.colour != colour:
                    print("شما مهره‌ای در این موقعیت ندارید: %s" % location)
                else:
                    value = location
            except ValueError:
                print("عدد وارد نشده است! دوباره تلاش کنید")
        return value
# ======================================================================================================================
class MoveRandomPiece(Strategy):
    """استراتژی حرکت یک مهره تصادفی"""

    @staticmethod
    def get_difficulty():
        return "Easy"  # سطح آسان

    def move(self, board, colour, dice_roll, make_move, opponents_activity):
        """اجرای حرکت مهره تصادفی برای هر تاس"""
        for die_roll in dice_roll:
            valid_pieces = board.get_pieces(colour)
            shuffle(valid_pieces)  # جابجایی مهره‌ها به صورت تصادفی
            for piece in valid_pieces:
                if board.is_move_possible(piece, die_roll):
                    make_move(piece.location, die_roll)
                    break
# ======================================================================================================================