import curses
import random
import sys

SIZE = 4

# Define color schemes (not heavily used in this simplified version)
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
    # value is the exponent (1 -> 2, 2 -> 4, etc.)
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
        board[y][x] = 1 if random.random() < 0.9 else 2  # 90% chance 2, 10% chance 4

def draw_board(stdscr, board, score, scheme_name):
    stdscr.clear()
    stdscr.addstr(f"2048.py {score} pts\n\n")

    # Color scheme currently not deeply integrated into drawing.
    # Just print the numbers. You can enhance if desired.
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
    # Merge towards left
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
    return [list(row) for row in zip(*board)]

def invert(board):
    # Reverse each row
    return [row[::-1] for row in board]

def move_board(board, direction):
    moved = False
    gained_score = 0

    # Directions:
    # Up: transpose -> move_line -> transpose
    # Down: transpose -> invert -> move_line -> invert -> transpose
    # Left: move_line directly
    # Right: invert -> move_line -> invert
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
    # Check if there are empty spaces
    if any(0 in row for row in board):
        return False
    # Check for merges
    for y in range(SIZE):
        for x in range(SIZE):
            if x < SIZE - 1 and board[y][x] == board[y][x + 1]:
                return False
            if y < SIZE - 1 and board[y][x] == board[y + 1][x]:
                return False
    return True

def get_key_input(c):
    # Handle keys safely:
    # If c is an ASCII character key (0-255), we can use chr().
    # If it's a special key like arrow keys, handle directly.
    if c in (curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT):
        return c
    # ASCII keys
    if 0 <= c < 256:
        return chr(c).lower()
    return ''  # Unknown key outside ASCII range

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    curses.use_default_colors()
    for i in range(1, 15):
        curses.init_pair(i, curses.COLOR_WHITE, curses.COLOR_BLACK)

    scheme_name = 'original'
    if len(sys.argv) == 2 and sys.argv[1] in COLOR_SCHEMES:
        scheme_name = sys.argv[1]

    board = init_board()
    score = 0
    draw_board(stdscr, board, score, scheme_name)

    # Mapping arrow keys directly:
    directions_map = {
        curses.KEY_UP: 'up',
        curses.KEY_DOWN: 'down',
        curses.KEY_LEFT: 'left',
        curses.KEY_RIGHT: 'right'
    }

    while True:
        c = stdscr.getch()
        if c == -1:
            continue
        key = get_key_input(c)

        # Handle special keys (arrows)
        if c in directions_map:
            direction = directions_map[c]
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
                if game_over(board):
                    stdscr.addstr("         GAME OVER          \n")
                    stdscr.refresh()
                    stdscr.nodelay(0)
                    stdscr.getch()
                    break
            continue

        # Handle WASD and other ASCII keys:
        if key in ['w', 'a', 's', 'd']:
            if key == 'w':
                direction = 'up'
            elif key == 's':
                direction = 'down'
            elif key == 'a':
                direction = 'left'
            elif key == 'd':
                direction = 'right'

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
                if game_over(board):
                    stdscr.addstr("         GAME OVER          \n")
                    stdscr.refresh()
                    stdscr.nodelay(0)
                    stdscr.getch()
                    break
            continue

        if key == 'q':
            stdscr.addstr("        QUIT? (y/n)         \n")
            stdscr.refresh()
            c2 = stdscr.getch()
            if c2 != -1:
                k2 = get_key_input(c2)
                if k2 == 'y':
                    break
            draw_board(stdscr, board, score, scheme_name)
            continue

        if key == 'r':
            stdscr.addstr("       RESTART? (y/n)       \n")
            stdscr.refresh()
            c2 = stdscr.getch()
            if c2 != -1:
                k2 = get_key_input(c2)
                if k2 == 'y':
                    board = init_board()
                    score = 0
            draw_board(stdscr, board, score, scheme_name)
            continue

if __name__ == '__main__':
    curses.wrapper(main)
