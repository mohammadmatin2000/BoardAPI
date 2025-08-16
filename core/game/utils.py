# AI ساده برای بازی تخته با Minimax محدود
import copy

PLAYER = "X"  # بازیکن
AI = "O"      # هوش مصنوعی

def check_winner(board, win_length=3):
    """
    بررسی برنده بازی
    خروجی:
    - "X" اگر بازیکن ببرد
    - "O" اگر AI ببرد
    - "D" اگر مساوی باشد
    - None اگر بازی ادامه دارد
    """
    size = len(board)
    for i in range(size):
        for j in range(size):
            # افقی
            if j <= size - win_length and all(board[i][j+k] == PLAYER for k in range(win_length)):
                return PLAYER
            if j <= size - win_length and all(board[i][j+k] == AI for k in range(win_length)):
                return AI
            # عمودی
            if i <= size - win_length and all(board[i+k][j] == PLAYER for k in range(win_length)):
                return PLAYER
            if i <= size - win_length and all(board[i+k][j] == AI for k in range(win_length)):
                return AI
            # مورب راست
            if i <= size - win_length and j <= size - win_length and all(board[i+k][j+k] == PLAYER for k in range(win_length)):
                return PLAYER
            if i <= size - win_length and j <= size - win_length and all(board[i+k][j+k] == AI for k in range(win_length)):
                return AI
            # مورب چپ
            if i <= size - win_length and j >= win_length-1 and all(board[i+k][j-k] == PLAYER for k in range(win_length)):
                return PLAYER
            if i <= size - win_length and j >= win_length-1 and all(board[i+k][j-k] == AI for k in range(win_length)):
                return AI

    # چک مساوی
    if all(cell != "" for row in board for cell in row):
        return "D"
    return None

# ==========================================================================================================
def evaluate(board):
    """
    امتیازدهی ساده برای AI
    """
    winner = check_winner(board)
    if winner == AI:
        return 10
    elif winner == PLAYER:
        return -10
    return 0

def minimax(board, depth, is_ai_turn, max_depth=2):
    score = evaluate(board)
    if abs(score) == 10 or depth == max_depth or check_winner(board) == "D":
        return score

    size = len(board)
    if is_ai_turn:
        best_score = -float("inf")
        for i in range(size):
            for j in range(size):
                if board[i][j] == "":
                    board[i][j] = AI
                    best_score = max(best_score, minimax(board, depth+1, False, max_depth))
                    board[i][j] = ""
        return best_score
    else:
        best_score = float("inf")
        for i in range(size):
            for j in range(size):
                if board[i][j] == "":
                    board[i][j] = PLAYER
                    best_score = min(best_score, minimax(board, depth+1, True, max_depth))
                    board[i][j] = ""
        return best_score

# ==========================================================================================================
def best_move(board, max_depth=2):
    move = None
    best_score = -float("inf")
    size = len(board)
    for i in range(size):
        for j in range(size):
            if board[i][j] == "":
                board[i][j] = AI
                score = minimax(board, 0, False, max_depth)
                board[i][j] = ""
                if score > best_score:
                    best_score = score
                    move = (i, j)
    return move
# ==========================================================================================================