import curses
from curses import window
from pathlib import Path
from random import choice, randint
import time

from animation.space_garbage import fly_garbage
from animation.spaceship import animate_spaceship, get_spaceship_frames
from animation.stars import blink
from animation.animation_utils import sleep

TIC_TIMEOUT = 0.1

COROUTINES = []
OBSTACLES = []
OBSTACLES_IN_LAST_COLLISION = []

import logging
logger = logging.getLogger('g')
logging.basicConfig(filename='log.log')


async def fill_orbit_with_garbage(canvas, width):
    garbage = []

    for file in Path('animation/garbage').glob('*.txt'):
        with open(file, 'r') as stream:
            garbage.append(stream.read())

    while True:
        garbage_piece = choice(garbage)

        COROUTINES.append(
            fly_garbage(canvas,
                        COROUTINES,
                        OBSTACLES,
                        OBSTACLES_IN_LAST_COLLISION,
                        randint(1, width),
                        garbage_piece)
        )

        await sleep(10)


def draw(canvas: window) -> None:

    symbols = '+*.:'
    height, width = canvas.getmaxyx()
    stars_number = randint(50, 200)

    COROUTINES.extend([
        blink(canvas,
              randint(1, height - 2),
              randint(1, width - 2),
              choice(symbols),
              randint(0, 50))
        for _ in range(1, stars_number + 1)
        ])

    COROUTINES.append(
        animate_spaceship(
            canvas,
            COROUTINES,
            OBSTACLES,
            OBSTACLES_IN_LAST_COLLISION,
            height // 2,
            width // 2,
            get_spaceship_frames(
                Path('animation/spaceship_frames/').glob('*.txt')
            )
        )
    )
    COROUTINES.append(fill_orbit_with_garbage(canvas, width))

    logger.error(COROUTINES)

    while True:
        curses.curs_set(False)
        canvas.border()
        canvas.nodelay(True)

        for coroutine in COROUTINES.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                COROUTINES.remove(coroutine)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


def main():
    curses.update_lines_cols()
    curses.wrapper(draw)


if __name__ == '__main__':
    main()
