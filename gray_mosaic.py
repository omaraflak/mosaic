import cv2
import numpy as np
from typing import Callable
from bisect import bisect_left


GrayImg = tuple[int, np.ndarray]


def read_tiles(files: list[str], tile_size: int) -> list[GrayImg]:
    tiles: list[GrayImg] = []
    for file in files:
        image = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
        image = cv2.resize(image, (tile_size, tile_size), interpolation=cv2.INTER_AREA)
        color = int(np.average(image))
        tiles.append((color, image))
    return tiles


def build_color_map(tiles: list[GrayImg]) -> Callable[[int], np.ndarray]:
    tiles.sort(key=lambda x: x[0])
    colors_in_dict: dict[int, list[np.ndarray]] = dict()
    for color, img in tiles:
        if color not in colors_in_dict:
            colors_in_dict[color] = []
        colors_in_dict[color].append(img)

    colors_list = list(colors_in_dict.keys())
    indices = [0] * len(colors_list)

    def _get_tile(gray: int) -> np.ndarray:
        i = bisect_left(colors_list, gray)
        i = min(i, len(colors_list) - 1)
        color = colors_list[i]
        index = indices[i]
        indices[i] = (indices[i] + 1) % len(colors_in_dict[color])
        return colors_in_dict[color][index]

    return _get_tile


def make_mosaic(
    file: str,
    tiles: list[str],
    tile_size: int,
    output: str
):
    get_tile = build_color_map(read_tiles(tiles, tile_size))
    original = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
    height, width = original.shape
    image = np.zeros((height, width))
    for i in range(0, height, tile_size):
        for j in range(0, width, tile_size):
            subimg = original[i:i+tile_size, j:j+tile_size]
            subcolor = np.average(subimg)
            image[i:i+tile_size, j:j+tile_size] = get_tile(subcolor)
        print(f'{int(100 * (i+tile_size)/height)}%')

    cv2.imwrite(output, image)
