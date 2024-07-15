import asyncio
from curses import window
from itertools import cycle
from pathlib import Path

from .animation_utils import get_frame_size, draw_frame, read_controls


def get_spaceship_frames(files: Path):
    frames = []
    for file in files:
        with open(file, 'r') as stream:
            frame = stream.read()
            frames.extend([frame, frame])
    return frames


async def animate_spaceship(canvas: window,
                            row: int,
                            column: int,
                            frames: list[str],
                            speed: int = 1):

    border_width = 1

    for frame in cycle(frames):
        frame_height, frame_width = get_frame_size(frame)
        canvas_height, canvas_width = canvas.getmaxyx()

        available_width = canvas_width - frame_width - border_width
        available_height = canvas_height - frame_height - border_width
        row_movement, column_movement, _ = read_controls(canvas, speed)

        column = max(column + column_movement, 1) \
            if column_movement == -1 * speed \
            else min(column + column_movement, available_width)
        row = max(row + row_movement, 1) \
            if row_movement == -1 * speed \
            else min(row + row_movement, available_height)

        draw_frame(canvas, row, column, frame)

        await asyncio.sleep(0)

        draw_frame(canvas, row, column, frame, negative=True)
