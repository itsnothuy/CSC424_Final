import curses
import random
import sys

SIZE = 4

# Define color schemes
COLOR_SCHEMES = {
    'original': [
        (8, 255), (1, 255), (2, 255), (3, 255),
        (4, 255), (5, 255), (6, 255), (7, 255),
        (9, 0), (10, 0), (11, 0), (12, 0),
        (13, 0), (14, 0), (255, 0), (255, 0)
    ],
    'blackwhite': [
        (232, 255), (234, 255), (236, 255), (238, 255),
        (240, 255), (242, 255), (244, 255), (246, 0),
        (248, 0), (249, 0), (250, 0), (251, 0),
        (252, 0), (253, 0), (254, 0), (255, 0)
    ],
    'bluered': [
        (235, 255), (63, 255), (57, 255), (93, 255),
        (129, 255), (165, 255), (201, 255), (200, 255),
        (199, 255), (198, 255), (197, 255), (196, 255),
        (196, 255), (196, 255), (196, 255), (196, 255)
    ]
}


def get_colors(value, scheme):
    # value is the exponent of 2 (e.g., 1 => 2, 2 => 4)
    if value == 0:
        return (0, 0)
    index = min(value - 1, len(scheme) - 1)
    fg, bg = scheme[index]
    return fg, bg


def init_board():
    board = [[0 for _ in range(SIZE)] for _ in range(SIZE)]
    add_random(board)
    add_random(board)
    return board


def add_random(board):
    empty_cells = [(x, y) for y in range(SIZE) for x in range(SIZE) if board[y][x] == 0]
    if empty_cells:
        x, y = random.choice(empty_cells)
        # 90% chance for '2' (value=1), 10% chance for '4' (value=2)
        board[y][x] = 1 if random.random() < 0.9 else 2


def draw_board(stdscr, board, score, scheme_name):
    stdscr.clear()
    scheme = COLOR_SCHEMES.get(scheme_name, COLOR_SCHEMES['original'])
    stdscr.addstr(f"2048.py {score} pts\n\n")

    # We won't apply color pairs here directly based on value,
    # because curses color settings with 256 colors differ from the original code.
    # You can adapt if you want different foreground/background per tile.
    # For simplicity, just print numbers.
    for y in range(SIZE):
        for x in range(SIZE):
            value = board[y][x]
            number = (1 << value) if value > 0 else 0
            cell_str = f"{number:^7}" if number > 0 else "   ·   "
            stdscr.addstr(cell_str)
        stdscr.addstr("\n")
    stdscr.addstr("\n        ←,↑,→,↓ or q        \n")
    stdscr.refresh()


def move_line(line):
    # This function merges a single line towards the left
    # line: [value, value, ...], 0 means empty
    new_line = [v for v in line if v != 0]
    merged_line = []
    score = 0
    skip = False
    for i in range(len(new_line)):
        if skip:
            skip = False
            continue
        if i + 1 < len(new_line) and new_line[i] == new_line[i + 1]:
            merged_value = new_line[i] + 1
            merged_line.append(merged_value)
            score += (1 << merged_value)
            skip = True
        else:
            merged_line.append(new_line[i])
    merged_line += [0] * (SIZE - len(merged_line))
    return merged_line, score


def transpose(board):
    # Transpose rows and columns
    return [list(row) for row in zip(*board)]


def invert(board):
    # Reverse each row (horizontal inversion)
    return [row[::-1] for row in board]


def move_board(board, direction):
    moved = False
    gained_score = 0

    # Use move_line which merges towards the left.
    # For up: transpose -> move_line -> transpose back
    # For down: transpose -> invert -> move_line -> invert -> transpose back
    # For left: move_line on each row directly
    # For right: invert -> move_line -> invert

    if direction == 'up':
        board = transpose(board)
        for i in range(SIZE):
            new_line, s = move_line(board[i])
            if new_line != board[i]:
                moved = True
            board[i] = new_line
            gained_score += s
        board = transpose(board)

    elif direction == 'down':
        board = transpose(board)
        board = invert(board)
        for i in range(SIZE):
            new_line, s = move_line(board[i])
            if new_line != board[i]:
                moved = True
            board[i] = new_line
            gained_score += s
        board = invert(board)
        board = transpose(board)

    elif direction == 'left':
        for i in range(SIZE):
            new_line, s = move_line(board[i])
            if new_line != board[i]:
                moved = True
            board[i] = new_line
            gained_score += s

    elif direction == 'right':
        board = invert(board)
        for i in range(SIZE):
            new_line, s = move_line(board[i])
            if new_line != board[i]:
                moved = True
            board[i] = new_line
            gained_score += s
        board = invert(board)

    return board, moved, gained_score


def game_over(board):
    # If there's an empty space, not over
    if any(0 in row for row in board):
        return False
    # Check for any adjacent merges possible
    for y in range(SIZE):
        for x in range(SIZE):
            if x < SIZE - 1 and board[y][x] == board[y][x + 1]:
                return False
            if y < SIZE - 1 and board[y][x] == board[y + 1][x]:
                return False
    return True


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    curses.use_default_colors()
    for i in range(1, 15):
        curses.init_pair(i, curses.COLOR_WHITE, curses.COLOR_BLACK)

    scheme_name = 'original'
    if len(sys.argv) == 2:
        if sys.argv[1] in COLOR_SCHEMES:
            scheme_name = sys.argv[1]

    board = init_board()
    score = 0
    draw_board(stdscr, board, score, scheme_name)

    while True:
        c = stdscr.getch()
        if c == -1:
            continue
        key = chr(c).lower() if c < 256 else ''

        if key == 'q':
            stdscr.addstr("        QUIT? (y/n)         \n")
            stdscr.refresh()
            c = stdscr.getch()
            if c != -1 and chr(c).lower() == 'y':
                break
            draw_board(stdscr, board, score, scheme_name)
            continue

        if key == 'r':
            stdscr.addstr("       RESTART? (y/n)       \n")
            stdscr.refresh()
            c = stdscr.getch()
            if c != -1 and chr(c).lower() == 'y':
                board = init_board()
                score = 0
            draw_board(stdscr, board, score, scheme_name)
            continue

        directions = {
            curses.KEY_UP: 'up',
            curses.KEY_DOWN: 'down',
            curses.KEY_LEFT: 'left',
            curses.KEY_RIGHT: 'right',
            ord('w'): 'up',
            ord('s'): 'down',
            ord('a'): 'left',
            ord('d'): 'right'
        }

        if c in directions:
            direction = directions[c]
            board, moved, gained = move_board(board, direction)
            if moved:
                score += gained
                add_random(board)
                draw_board(stdscr, board, score, scheme_name)
                if game_over(board):
                    stdscr.addstr("         GAME OVER          \n")
                    stdscr.refresh()
                    stdscr.nodelay(0)
                    stdscr.getch()
                    break
            else:
                # If no move was made, still check if game is over
                if game_over(board):
                    stdscr.addstr("         GAME OVER          \n")
                    stdscr.refresh()
                    stdscr.nodelay(0)
                    stdscr.getch()
                    break
        else:
            continue


if __name__ == '__main__':
    curses.wrapper(main)
