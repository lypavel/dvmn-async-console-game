import asyncio
import curses
from curses import window
from itertools import cycle
from pathlib import Path
from random import choice, randint
import time

from animation.animation_utils import draw_frame, get_frame_size, \
    read_controls, sleep
from animation.explosion import explode
from animation.physics import update_speed
from animation.show_game_over import get_game_over_text, show_game_over
from animation.space_garbage import get_garbage_delay_tics, get_garbage_frames
from animation.spaceship import get_spaceship_frames
from animation.stars import blink
from animation.obstacles import Obstacle

TIC_TIMEOUT = 0.1
YEAR = 1957

PHRASES = {
    1957: 'First Sputnik',
    1961: 'Gagarin flew!',
    1969: 'Armstrong got on the moon!',
    1971: 'First orbital space station Salute-1',
    1981: 'Flight of the shuttle Columbia',
    1998: 'ISS start building',
    2011: 'Messenger launch to Mercury',
    2020: 'Take the plasma gun! Shoot the garbage!',
}

COROUTINES = []
OBSTACLES = []
OBSTACLES_IN_LAST_COLLISION = []


async def count_years(year_field: window) -> None:
    global YEAR

    while True:
        event = PHRASES.get(YEAR, '')
        message = f'{YEAR} - {event}' if event else str(YEAR)
        year_field.addstr(1, 1, message)
        await sleep(20)
        YEAR += 1


async def fill_orbit_with_garbage(canvas: window, canvas_width: int) -> None:
    garbage = get_garbage_frames(
        Path('animation/garbage').glob('*.txt')
    )

    while True:
        delay = get_garbage_delay_tics(YEAR)
        if not delay:
            await asyncio.sleep(0)
            continue

        garbage_piece = choice(garbage)
        _, garbage_width = get_frame_size(garbage_piece)
        border_width = 1
        max_column = canvas_width - garbage_width - border_width

        COROUTINES.append(
            fly_garbage(canvas,
                        randint(1, max_column),
                        garbage_piece)
        )

        await sleep(delay)


async def fly_garbage(canvas: window,
                      column: int,
                      garbage_frame: str,
                      speed=0.5) -> None:
    """Animate garbage, flying from top to bottom.
    Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 1

    rows, columns = get_frame_size(garbage_frame)
    obstacle = Obstacle(row, column, rows, columns)
    OBSTACLES.append(obstacle)

    try:
        while row < rows_number:
            if obstacle in OBSTACLES_IN_LAST_COLLISION:
                OBSTACLES_IN_LAST_COLLISION.remove(obstacle)
                return
            draw_frame(canvas, row, column, garbage_frame)
            await asyncio.sleep(0)
            draw_frame(canvas, row, column, garbage_frame, negative=True)
            row += speed
            obstacle.row += speed
    finally:
        OBSTACLES.remove(obstacle)


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
        for obstacle in OBSTACLES.copy():
            if obstacle.has_collision(row, column):
                OBSTACLES_IN_LAST_COLLISION.append(obstacle)
                await explode(canvas, row, column)
                return

        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def animate_spaceship(canvas: window,
                            row: int,
                            column: int,
                            frames: list[str],
                            speed: int = 1) -> None:

    border_width = 1

    row_speed, column_speed = 0, 0
    for frame in cycle(frames):
        for obstacle in OBSTACLES:
            if obstacle.has_collision(row, column):
                COROUTINES.append(
                    show_game_over(canvas,
                                   get_game_over_text())
                )
                return

        frame_height, frame_width = get_frame_size(frame)
        canvas_height, canvas_width = canvas.getmaxyx()

        available_width = canvas_width - frame_width - border_width
        available_height = canvas_height - frame_height - border_width
        row_movement, column_movement, space_pressed = read_controls(canvas,
                                                                     speed)

        if space_pressed and YEAR >= 2020:
            COROUTINES.append(fire(canvas,
                                   row,
                                   column + 2))

        row_speed, column_speed = update_speed(
            row_speed, column_speed, row_movement, column_movement
        )

        column = max(column + column_speed, 1) \
            if column_speed < 0 \
            else min(column + column_speed, available_width)
        row = max(row + row_speed, 1) \
            if row_speed < 0 \
            else min(row + row_speed, available_height)

        draw_frame(canvas, row, column, frame)

        await asyncio.sleep(0)

        draw_frame(canvas, row, column, frame, negative=True)


def draw(canvas: window) -> None:
    canvas_height, canvas_width = canvas.getmaxyx()

    year_field_height = 3
    year_field_width = 50
    year_field = canvas.derwin(
        canvas_height - year_field_height, canvas_width - year_field_width
    )

    COROUTINES.append(count_years(year_field))

    symbols = '+*.:'
    stars_number = randint(50, 200)

    COROUTINES.extend([
        blink(canvas,
              randint(1, canvas_height - 2),
              randint(1, canvas_width - 2),
              choice(symbols),
              randint(0, 50))
        for _ in range(1, stars_number + 1)
        ])

    COROUTINES.append(
        animate_spaceship(
            canvas,
            canvas_height // 2,
            canvas_width // 2,
            get_spaceship_frames(
                Path('animation/spaceship_frames/').glob('*.txt')
            )
        )
    )
    COROUTINES.append(fill_orbit_with_garbage(canvas, canvas_width))

    while True:
        curses.curs_set(False)
        canvas.border()
        year_field.border()
        canvas.nodelay(True)

        for coroutine in COROUTINES.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                COROUTINES.remove(coroutine)
        canvas.refresh()
        year_field.refresh()
        time.sleep(TIC_TIMEOUT)


def main():
    curses.update_lines_cols()
    curses.wrapper(draw)


if __name__ == '__main__':
    main()
