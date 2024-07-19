from curses import A_DIM, A_BOLD, window

from .animation_utils import sleep


async def blink(canvas: window,
                row: int,
                column: int,
                symbol: str = '*',
                offset_tics: int = 0):

    await sleep(offset_tics)

    while True:
        canvas.addstr(row, column, symbol, A_DIM)
        await sleep(20)

        canvas.addstr(row, column, symbol)
        await sleep(3)

        canvas.addstr(row, column, symbol, A_BOLD)
        await sleep(5)

        canvas.addstr(row, column, symbol)
        await sleep(3)
