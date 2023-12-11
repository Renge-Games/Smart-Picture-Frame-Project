#!/usr/bin/python3
# -*- coding: utf-8 -*-

# https://stackoverflow.com/a/59100207
from PIL import Image


def sepia(image_path: str | bytes) -> Image:
    img = Image.open(image_path)
    width, height = img.size

    for py in range(height):
        for px in range(width):
            r, g, b = img.getpixel((px, py))

            tr = int(0.393 * r + 0.769 * g + 0.189 * b)
            tg = int(0.349 * r + 0.686 * g + 0.168 * b)
            tb = int(0.272 * r + 0.534 * g + 0.131 * b)

            if tr > 255:
                tr = 255

            if tg > 255:
                tg = 255

            if tb > 255:
                tb = 255

            img.putpixel((px, py), (tr, tg, tb))

    return img
