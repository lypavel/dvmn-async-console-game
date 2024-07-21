import asyncio

from .animation_utils import draw_frame, get_frame_size
from .obstacles import Obstacle, show_obstacles


async def fly_garbage(canvas,
                      coroutines,
                      obstacles,
                      obstacles_in_last_collision,
                      column,
                      garbage_frame,
                      speed=0.5):
    """Animate garbage, flying from top to bottom.
    Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 1

    rows, columns = get_frame_size(garbage_frame)
    obstacle = Obstacle(row, column, rows, columns)
    obstacles.append(obstacle)

    coroutines.append(show_obstacles(canvas, obstacles))

    try:
        while row < rows_number:
            if obstacle in obstacles_in_last_collision:
                obstacles_in_last_collision.remove(obstacle)
                return
            draw_frame(canvas, row, column, garbage_frame)
            await asyncio.sleep(0)
            draw_frame(canvas, row, column, garbage_frame, negative=True)
            row += speed
            obstacle.row += speed
    finally:
        obstacles.remove(obstacle)
