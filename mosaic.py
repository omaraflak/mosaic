import cv2
import numpy as np
from typing import Callable


BgrImg = tuple[float, float, float, np.ndarray]


def read_tiles(files: list[str], tile_size: int) -> list[BgrImg]:
    tiles: list[BgrImg] = []
    for file in files:
        image = cv2.imread(file, cv2.IMREAD_COLOR)
        image = cv2.resize(image, (tile_size, tile_size), interpolation=cv2.INTER_AREA)
        b, g, r = np.mean(image, axis=(0, 1), dtype=np.int32)
        tiles.append((b, g, r, image))
    return tiles


def color_distance(rgb1: tuple[int, int, int], rgb2: tuple[int, int, int]) -> float:
    rgb1 = np.array(rgb1) / 255
    rgb2 = np.array(rgb2) / 255
    rm = 0.5 * (rgb1[0] + rgb2[0])
    d = sum((2 + rm, 4, 3 - rm) * (rgb1 - rgb2) ** 2) ** 0.5
    return d


def build_color_map(tiles: list[BgrImg]) -> Callable[[int, int, int], np.ndarray]:
    def _get_image(b: int, g: int, r: int) -> np.ndarray:
        x = min(tiles, key=lambda x: color_distance((x[2], x[1], x[0]), (r, g, b)))
        return x[3]

    return _get_image


def make_mosaic(
    file: str,
    tiles: list[str],
    tile_size: int,
    output: str
):
    get_tile = build_color_map(read_tiles(tiles, tile_size))
    original = cv2.imread(file, cv2.IMREAD_COLOR)
    height, width, _ = original.shape
    image = np.zeros((height, width, 3))
    for i in range(0, height, tile_size):
        for j in range(0, width, tile_size):
            subimg = original[i:i+tile_size, j:j+tile_size]
            subcolor = np.mean(subimg, axis=(0, 1))
            image[i:i+tile_size, j:j+tile_size] = get_tile(*subcolor)
        print(f'{int(100 * (i+tile_size)/height)}%')

    cv2.imwrite(output, image)
