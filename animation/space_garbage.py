from pathlib import Path


def get_garbage_delay_tics(year):
    if year < 1961:
        return None
    elif year < 1969:
        return 20
    elif year < 1981:
        return 14
    elif year < 1995:
        return 10
    elif year < 2010:
        return 8
    elif year < 2020:
        return 6
    else:
        return 2


def get_garbage_frames(files: Path) -> list:
    frames = []

    for file in files:
        with open(file, 'r') as stream:
            frame = stream.read()
            frames.append(frame)
    return frames
