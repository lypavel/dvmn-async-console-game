import asyncio
import curses
from curses import window

from .explosion import explode


async def fire(canvas: window,
               obstacles: list,
               obstacles_in_last_collision: list,
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
        for obstacle in obstacles.copy():
            if obstacle.has_collision(row, column):
                obstacles_in_last_collision.append(obstacle)
                await explode(canvas, row, column)
                return
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed
