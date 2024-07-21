import asyncio
from pathlib import Path

from .animation_utils import draw_frame, get_frame_size


async def show_game_over(canvas):
    with open(Path('animation/game_over.txt')) as stream:
        game_over_text = stream.read()

    canvas_height, canvas_width = canvas.getmaxyx()
    frame_height, frame_width = get_frame_size(game_over_text)

    row = canvas_height // 2 - frame_height // 2
    column = canvas_width // 2 - frame_width // 2
    while True:
        draw_frame(canvas, row, column, game_over_text)
        await asyncio.sleep(0)
