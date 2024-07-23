import asyncio
from curses import window
from pathlib import Path

from .animation_utils import draw_frame, get_frame_size


def get_game_over_text() -> str:
    with open(Path('animation/game_over.txt')) as stream:
        game_over_text = stream.read()

    return game_over_text


async def show_game_over(canvas: window, game_over_text: str) -> None:
    canvas_height, canvas_width = canvas.getmaxyx()
    frame_height, frame_width = get_frame_size(game_over_text)

    row = (canvas_height - frame_height) // 2
    column = (canvas_width - frame_width) // 2
    while True:
        draw_frame(canvas, row, column, game_over_text)
        await asyncio.sleep(0)
