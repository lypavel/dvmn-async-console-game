import curses
from curses import window
from pathlib import Path
from random import randint
import time

from animation.fire import fire
from animation.spaceship import animate_spaceship, get_spaceship_frames
from animation.stars import blink

TIC_TIMEOUT = 0.1


def draw(canvas: window) -> None:

    symbols = '+*.:'
    height, width = canvas.getmaxyx()
    stars_number = randint(50, 200)

    coroutines = [blink(canvas, height, width, symbols)
                  for _ in range(1, stars_number + 1)]

    coroutines.append(fire(canvas, height // 2, width // 2))
    coroutines.append(
        animate_spaceship(
            canvas,
            height // 2,
            width // 2,
            get_spaceship_frames(
                Path('animation/spaceship_frames/').glob('*.txt')
            )
        )
    )

    while True:
        curses.curs_set(False)
        canvas.border()
        canvas.nodelay(True)

        for coroutine in coroutines.copy():
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
