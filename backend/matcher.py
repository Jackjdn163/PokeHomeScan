import os
import json
import imagehash
from PIL import Image
import numpy as np

HASH_DB_PATH = "../hashes.json"
SPRITE_PATH = "sprites/"

with open(HASH_DB_PATH, "r") as f:
    HASH_DB = json.load(f)


def split_grid(img, rows=6, cols=10):
    w, h = img.size
    tile_w = w // cols
    tile_h = h // rows

    tiles = []
    for r in range(rows):
        for c in range(cols):
            crop = img.crop((
                c * tile_w,
                r * tile_h,
                (c+1) * tile_w,
                (r+1) * tile_h
            ))
            tiles.append(crop)
    return tiles


def match_tile(tile):
    tile = tile.resize((64, 64))
    tile_hash = imagehash.phash(tile)

    best_match = None
    best_score = 999

    for name, h in HASH_DB.items():
        db_hash = imagehash.hex_to_hash(h)
        score = tile_hash - db_hash

        if score < best_score:
            best_score = score
            best_match = name

    return best_match


def is_empty(tile):
    arr = np.array(tile)
    return np.std(arr) < 10  # low variation = empty


def process_image(file):
    img = Image.open(file).convert("RGB")

    tiles = split_grid(img)
    results = []

    for tile in tiles:
        if is_empty(tile):
            continue

        match = match_tile(tile)
        results.append(match.replace(".png", ""))

    return results
