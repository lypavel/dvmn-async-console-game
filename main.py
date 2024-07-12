import asyncio
import curses
from curses import A_DIM, A_BOLD, window
from itertools import cycle
from random import randint, choice
import time

TIC_TIMEOUT = 0.1


async def fire(canvas: window,
               start_row: int,
               start_column: int,
               rows_speed: float = -0.3,
               columns_speed: int = 0) -> None:
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def blink(canvas: window, row: int, column: int, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, A_DIM)
        for _ in range(randint(0, 20)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(randint(0, 3)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, A_BOLD)
        for _ in range(randint(0, 5)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(randint(0, 3)):
            await asyncio.sleep(0)


def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Draw multiline text fragment on canvas, erase text instead of drawing if negative=True is specified."""

    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break

            if symbol == ' ':
                continue

            # Check that current position it is not in a lower right corner of the window
            # Curses will raise exception in that case. Don`t ask why…
            # https://docs.python.org/3/library/curses.html#curses.window.addch
            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


async def animate_spaceship(canvas: window, row, column, frames: list[str]):
    for frame in cycle(frames):
        draw_frame(canvas, row, column, frame, negative=True)
        await asyncio.sleep(0)


def draw(canvas: window) -> None:

    symbols = '+*.:'
    height, width = canvas.getmaxyx()
    stars_number = randint(50, 200)

    spaceship_frames = []
    for file in ('rocket_frame_1.txt', 'rocket_frame_2.txt'):
        with open(file, 'r', encoding='utf-8') as stream:
            frame = stream.read()
            spaceship_frames.append(frame)

    coroutines = [blink(
        canvas, randint(1, height-2), randint(1, width-2), choice(symbols)
    ) for _ in range(1, stars_number + 1)]

    coroutines.append(fire(canvas, height // 2, width // 2))
    coroutines.append(animate_spaceship(canvas, height // 2, width // 2, spaceship_frames))

    while True:
        curses.curs_set(False)
        canvas.border()
        for coroutine in coroutines:
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


def main():
    curses.update_lines_cols()
    curses.wrapper(draw)


if __name__ == '__main__':
    main()
