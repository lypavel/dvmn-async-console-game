import asyncio
from curses import A_DIM, A_BOLD, window
from random import choice, randint


async def blink(canvas: window,
                row: int,
                column: int,
                symbols: list | str = '*'):
    symbol = choice(symbols)

    row = randint(1, row - 2)
    column = randint(1, column - 2)

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
