
def check_winner():
    """Check if there's a winner or if the game is a tie"""
    global winner

    # Check rows
    for row in range(BOARD_SIZE):
        if board[row][0] == board[row][1] == board[row][2] != '':
            winner = board[row][0]
            return True

    # Check columns
    for col in range(BOARD_SIZE):
        if board[0][col] == board[1][col] == board[2][col] != '':
            winner = board[0][col]
            return True

    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] != '':
        winner = board[0][0]
        return True
    if board[0][2] == board[1][1] == board[2][0] != '':
        winner = board[0][2]
        return True

    # Check for tie
    if all(board[row][col] != '' for row in range(BOARD_SIZE) for col in range(BOARD_SIZE)):
        winner = 'Tie'
        return True

    return False

def reset_game():
    """Reset the game state"""
    global board, current_player, winner
    board = [['' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    current_player = 'X'
    winner = None

def make_move(row, col):
    """Make a move on the board"""
    global current_player

    if board[row][col] == '' and not winner:
        board[row][col] = current_player
        if not check_winner():
            current_player = 'O' if current_player == 'X' else 'X'
        return True
    return False