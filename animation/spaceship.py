from pathlib import Path


def get_spaceship_frames(files: Path):
    frames = []
    for file in files:
        with open(file, 'r') as stream:
            frame = stream.read()
            frames.extend([frame, frame])
    return frames
