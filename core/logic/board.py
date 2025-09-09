from random import shuffle  # برای مخلوط کردن لیست مهره‌ها (جهت تصادفی کردن انتخاب)
import copy  # برای کپی عمیق (deepcopy) از وضعیت تخته
import json  # برای تبدیل وضعیت تخته به JSON
from logic.colour import Colour  # کلاس رنگ مهره‌ها (سفید/سیاه)
from logic.piece import Piece  # کلاس مهره
# ======================================================================================================================
class Board:
    """
    کلاس Board مسئول مدیریت وضعیت تخته‌ی بک‌گمون است.
    این کلاس وظایف زیر را برعهده دارد:
    - ایجاد تخته شروع
    - اضافه و جابجایی مهره‌ها
    - بررسی امکان حرکت‌ها
    - تشخیص پایان بازی
    - تبدیل تخته به JSON برای ارسال به فرانت‌اند
    """

    def __init__(self):
        self.__pieces = []  # لیست همه مهره‌های موجود روی تخته

    # ===================================================================================
    # ایجاد تخته اولیه بازی (شروع استاندارد بک‌گمون)
    # ===================================================================================
    @classmethod
    def create_starting_board(cls):
        board = Board()
        # اضافه کردن مهره‌ها در موقعیت‌های استاندارد شروع
        board.add_many_pieces(2, Colour.WHITE, 1)
        board.add_many_pieces(5, Colour.BLACK, 6)
        board.add_many_pieces(3, Colour.BLACK, 8)
        board.add_many_pieces(5, Colour.WHITE, 12)
        board.add_many_pieces(5, Colour.BLACK, 13)
        board.add_many_pieces(3, Colour.WHITE, 17)
        board.add_many_pieces(5, Colour.WHITE, 19)
        board.add_many_pieces(2, Colour.BLACK, 24)
        return board

    # اضافه کردن چند مهره در یک خانه خاص
    def add_many_pieces(self, number_of_pieces, colour, location):
        for _ in range(number_of_pieces):
            self.__pieces.append(Piece(colour, location))

    # ===================================================================================
    # بررسی امکان حرکت یک مهره بر اساس مقدار تاس
    # ===================================================================================
    def is_move_possible(self, piece, die_roll):
        # اگر مهره‌ای خورده شده باشد باید اول آن را از خانه‌ی taken حرکت داد
        if len(self.pieces_at(self.__taken_location(piece.colour))) > 0:
            if piece.location != self.__taken_location(piece.colour):
                return False

        # اگر مهره سیاه باشد حرکت معکوس است
        if piece.colour == Colour.BLACK:
            die_roll = -die_roll

        # محاسبه موقعیت جدید
        new_location = piece.location + die_roll

        # بررسی خروج از تخته (bearing off)
        if new_location <= 0 or new_location >= 25:
            if not self.can_move_off(piece.colour):
                return False
            # جلوگیری از پرش بیش از حد
            if new_location not in (0, 25):
                return not any(
                    x.spaces_to_home() >= abs(die_roll)
                    for x in self.get_pieces(piece.colour)
                )
            return True

        # بررسی امکان قرار گرفتن در خانه جدید
        pieces_at_new_location = self.pieces_at(new_location)
        if len(pieces_at_new_location) in (0, 1):
            return True
        return pieces_at_new_location[0].colour == piece.colour

    # بررسی اینکه هیچ حرکتی ممکن نیست
    def no_moves_possible(self, colour, dice_roll):
        piece_locations = list(set(x.location for x in self.get_pieces(colour)))
        dice_roll = list(set(dice_roll))

        pieces = [self.get_piece_at(loc) for loc in piece_locations]

        for die in dice_roll:
            for piece in pieces:
                if self.is_move_possible(piece, die):
                    return False
        return True

    # بررسی اینکه آیا بازیکن می‌تواند مهره‌ای را از زمین خارج کند یا نه
    def can_move_off(self, colour):
        return all(x.spaces_to_home() <= 6 for x in self.get_pieces(colour))

    # ===================================================================================
    # حرکت دادن یک مهره
    # ===================================================================================
    def move_piece(self, piece, die_roll):
        if piece not in self.__pieces:
            raise Exception('این مهره متعلق به این تخته نیست')
        if not self.is_move_possible(piece, die_roll):
            raise Exception('این حرکت معتبر نیست')

        # اگر مهره سیاه باشد حرکت معکوس است
        if piece.colour == Colour.BLACK:
            die_roll = -die_roll

        new_location = piece.location + die_roll

        # اگر مهره خارج شد (bearing off)
        if new_location <= 0 or new_location >= 25:
            self.__remove_piece(piece)

        # اگر خانه مقصد فقط یک مهره حریف داشته باشد → آن مهره زده می‌شود
        pieces_at_new_location = self.pieces_at(new_location)
        if len(pieces_at_new_location) == 1 and pieces_at_new_location[0].colour != piece.colour:
            piece_to_take = pieces_at_new_location[0]
            piece_to_take.location = self.__taken_location(piece_to_take.colour)

        # به‌روزرسانی موقعیت مهره
        piece.location = new_location
        return new_location

    # ===================================================================================
    # متدهای کمکی
    # ===================================================================================
    def pieces_at(self, location):
        """برگرداندن لیست مهره‌ها در یک خانه خاص"""
        return [x for x in self.__pieces if x.location == location]

    def get_piece_at(self, location):
        """برگرداندن یک مهره از خانه موردنظر"""
        pieces = self.pieces_at(location)
        return pieces[0] if pieces else None

    def get_pieces(self, colour):
        """برگرداندن تمام مهره‌های یک رنگ"""
        pieces = [x for x in self.__pieces if x.colour == colour]
        shuffle(pieces)  # برای جلوگیری از انتخاب تکراری
        return pieces

    def get_taken_pieces(self, colour):
        """برگرداندن مهره‌های خورده شده"""
        return self.pieces_at(self.__taken_location(colour))

    def has_game_ended(self):
        """بررسی پایان بازی (تمام شدن مهره‌های یک بازیکن)"""
        return len(self.get_pieces(Colour.WHITE)) == 0 or len(self.get_pieces(Colour.BLACK)) == 0

    def who_won(self):
        """برگرداندن برنده بازی"""
        if not self.has_game_ended():
            raise Exception('بازی هنوز تمام نشده است')
        return Colour.WHITE if len(self.get_pieces(Colour.WHITE)) == 0 else Colour.BLACK

    def create_copy(self):
        """ایجاد یک کپی عمیق از وضعیت تخته"""
        return copy.deepcopy(self)

    def get_move_lambda(self):
        """برگرداندن تابع کمکی برای حرکت مهره‌ها"""
        return lambda l, r: self.move_piece(self.get_piece_at(l), r)

    # ===================================================================================
    # چاپ متنی تخته (برای دیباگ)
    # ===================================================================================
    def print_board(self):
        print("  13                  18   19                  24   25")
        print("---------------------------------------------------")
        line = "|"
        for i in range(13, 19):
            line += self.__pieces_at_text(i)
        line += "|"
        for i in range(19, 25):
            line += self.__pieces_at_text(i)
        line += "|"
        line += self.__pieces_at_text(self.__taken_location(Colour.BLACK))
        print(line)

        for _ in range(3):
            print("|                        |                        |")

        line = "|"
        for i in reversed(range(7, 13)):
            line += self.__pieces_at_text(i)
        line += "|"
        for i in reversed(range(1, 7)):
            line += self.__pieces_at_text(i)
        line += "|"
        line += self.__pieces_at_text(self.__taken_location(Colour.WHITE))
        print(line)

        print("---------------------------------------------------")
        print("  12                  7    6                   1    0")

    # ===================================================================================
    # تبدیل وضعیت تخته به JSON برای فرانت‌اند
    # ===================================================================================
    def to_json(self):
        data = {}
        for location in range(26):  # از 0 تا 25
            pieces = self.pieces_at(location)
            if pieces:
                data[location] = {
                    'colour': str(pieces[0].colour),
                    'count': len(pieces)
                }
        return json.dumps(data)

    # ===================================================================================
    # متدهای خصوصی
    # ===================================================================================
    def __taken_location(self, colour):
        """برگرداندن موقعیت مهره‌های خورده‌شده (0 برای سفید، 25 برای سیاه)"""
        return 0 if colour == Colour.WHITE else 25

    def __pieces_at_text(self, location):
        """نمایش متنی مهره‌ها در خانه (برای print_board)"""
        pieces = self.pieces_at(location)
        if not pieces:
            return " .  "
        return f" {len(pieces)}{'W' if pieces[0].colour == Colour.WHITE else 'B'} "

    def __remove_piece(self, piece):
        """حذف مهره از تخته (برای خروج یا خورده شدن)"""
        self.__pieces.remove(piece)
# ======================================================================================================================