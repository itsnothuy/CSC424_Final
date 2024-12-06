# 2048 in Python 3 for Beginners (Alpha Version)
# By @TokyoEdTech
# Modified to add 'q' to quit and 'r' to restart

import turtle
import random

# Set up the screen
wn = turtle.Screen()
wn.title("2048 by @TokyoEdTech")
wn.bgcolor("black")
wn.setup(width=450, height=400)
wn.tracer(0)

# Score
score = 0

# Grid list
grid = [
    [0, 0, 0, 16],
    [0, 0, 8, 0],
    [0, 4, 0, 0],
    [2, 4, 8, 16]
]

grid_merged = [
    [False, False, False, False],
    [False, False, False, False],
    [False, False, False, False],
    [False, False, False, False]
]

# Pen
pen = turtle.Turtle()
pen.speed(0)
pen.shape("square")
pen.color("white")
pen.penup()
pen.hideturtle()
pen.turtlesize(stretch_wid=2, stretch_len=2, outline=2)
pen.goto(0, 260)

colors = {
    0: "white",
    2: "yellow",
    4: "orange",
    8: "pink",
    16: "red",
    32: "light green",
    64: "green",
    128: "violet",  # Changed from "light purple" to a known color
    256: "purple",
    512: "gold",
    1024: "silver",
    2048: "black"
}

def draw_grid():
    grid_y = 0
    y = 120
    pen.clear()
    pen.goto(0, 260)
    pen.color("white")
    pen.write(f"2048 - Score: {score}", align="center", font=("Courier", 18, "bold"))
    for row in grid:
        grid_x = 0
        x = -120
        y -= 45
        for column in row:
            x += 45
            pen.goto(x, y)

            value = grid[grid_y][grid_x]
            color = colors[value]
            pen.color(color)
            pen.stamp()

            pen.color("blue")
            if column == 0:
                number = ""
            else:
                number = str(column)

            pen.sety(pen.ycor() - 10)
            pen.write(number, align="center", font=("Courier", 14, "bold"))
            pen.sety(pen.ycor() + 10)

            grid_x += 1
        
        grid_y += 1
    wn.update()

def add_random():
    added = False
    while not added:
        x = random.randint(0, 3)
        y = random.randint(0, 3)
        value = random.choice([2, 4])
        if grid[y][x] == 0:
            grid[y][x] = value
            added = True

def reset_grid_merged():
    global grid_merged
    grid_merged = [
        [False, False, False, False],
        [False, False, False, False],
        [False, False, False, False],
        [False, False, False, False]
    ]

def up():
    for x in range(0, 4):
        for y in range(1, 4):
            if grid[y-1][x] == 0:
                grid[y-1][x] = grid[y][x]
                for y2 in range(y, 3):
                    grid[y][x] = grid[y+1][x]
                grid[2][x] = grid[3][x]
                grid[y][x] = 0
                y = 0
                continue

            if grid[y-1][x] == grid[y][x] and not grid_merged[y-1][x]:
                # Combine
                grid[y-1][x] = grid[y][x] * 2
                grid_merged[y-1][x] = True
                grid[y][x] = 0
                y = 0
                continue

    reset_grid_merged()
    print("UP")
    add_random()
    draw_grid()

def down():
    for _ in range(4):
        for y in range(2, -1, -1):
            for x in range(0, 4):
                if grid[y+1][x] == 0:
                    grid[y+1][x] = grid[y][x]
                    grid[y][x] = 0
                    x -= 1
                    continue
            
                if grid[y+1][x] == grid[y][x] and not grid_merged[y+1][x]:
                    grid[y+1][x] = grid[y][x] * 2
                    grid_merged[y+1][x] = True
                    grid[y][x] = 0
                    x -= 1
                    continue
    reset_grid_merged()
    print("DOWN")
    add_random()
    draw_grid()

def left():
    for y in range(0,4):
        for x in range(1,4):
            if grid[y][x-1] == 0:
                grid[y][x-1] = grid[y][x]
                for x2 in range(x, 3):
                    grid[y][x2] = grid[y][x2+1]
                grid[y][3] = 0
                x = 0
                continue

            if grid[y][x-1] == grid[y][x] and not grid_merged[y][x-1]:
                grid[y][x-1] = grid[y][x]*2
                grid_merged[y][x-1] = True
                for x2 in range(x, 3):
                    grid[y][x2] = grid[y][x2+1]
                grid[y][3] = 0
                x = 0
                continue

    reset_grid_merged()
    print("LEFT")
    add_random()
    draw_grid()

def right():
    for y in range(0,4):
        for x in range(2, -1, -1):
            if grid[y][x+1] == 0:
                grid[y][x+1] = grid[y][x]
                for x2 in range(x,0,-1):
                    grid[y][x2] = grid[y][x2-1]
                grid[y][0] = 0
                x = 3
                continue

            if grid[y][x+1] == grid[y][x] and not grid_merged[y][x+1]:
                grid[y][x+1] = grid[y][x]*2
                grid_merged[y][x+1] = True
                for x2 in range(x,0,-1):
                    grid[y][x2] = grid[y][x2-1]
                grid[y][0] = 0
                x = 3
                continue

    reset_grid_merged()
    print("RIGHT")
    add_random()
    draw_grid()

def quit_game():
    # Close the turtle window and exit the game
    print("Quitting the game...")
    wn.bye()

def restart():
    # Reset the grid and score, then add two random tiles and redraw
    global grid, score, grid_merged
    grid = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]
    score = 0
    reset_grid_merged()
    add_random()
    add_random()
    draw_grid()
    print("Game restarted.")

draw_grid()

# Keyboard bindings
wn.listen()
wn.onkeypress(left, "Left")
wn.onkeypress(right, "Right")
wn.onkeypress(up, "Up")
wn.onkeypress(down, "Down")
wn.onkeypress(quit_game, "q")   # Press 'q' to quit
wn.onkeypress(restart, "r")     # Press 'r' to restart

wn.mainloop()
