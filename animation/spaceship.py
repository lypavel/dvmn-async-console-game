import asyncio
from curses import window
from itertools import cycle
from pathlib import Path

from .animation_utils import get_frame_size, draw_frame, read_controls
from .fire import fire
from .show_game_over import show_game_over
from .physics import update_speed


def get_spaceship_frames(files: Path):
    frames = []
    for file in files:
        with open(file, 'r') as stream:
            frame = stream.read()
            frames.extend([frame, frame])
    return frames


async def animate_spaceship(canvas: window,
                            coroutines: list,
                            obstacles: list,
                            obstacles_in_last_collision: list,
                            row: int,
                            column: int,
                            frames: list[str],
                            speed: int = 1):

    border_width = 1

    row_speed, column_speed = 0, 0
    for frame in cycle(frames):
        for obstacle in obstacles:
            if obstacle.has_collision(row, column):
                coroutines.append(show_game_over(canvas))
                return
        frame_height, frame_width = get_frame_size(frame)
        canvas_height, canvas_width = canvas.getmaxyx()

        available_width = canvas_width - frame_width - border_width
        available_height = canvas_height - frame_height - border_width
        row_movement, column_movement, space_pressed = read_controls(canvas,
                                                                     speed)

        if space_pressed:
            coroutines.append(fire(canvas,
                                   obstacles,
                                   obstacles_in_last_collision,
                                   row,
                                   column + 2))

        row_speed, column_speed = update_speed(
            row_speed, column_speed, row_movement, column_movement
        )

        column = max(column + column_speed, 1) \
            if column_movement == -1 * speed \
            else min(column + column_speed, available_width)
        row = max(row + row_speed, 1) \
            if row_movement == -1 * speed \
            else min(row + row_speed, available_height)

        draw_frame(canvas, row, column, frame)

        await asyncio.sleep(0)

        draw_frame(canvas, row, column, frame, negative=True)
