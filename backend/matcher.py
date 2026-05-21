import json
from pathlib import Path

import imagehash
import numpy as np
from PIL import Image, ImageOps

ROOT_DIR = Path(__file__).resolve().parent.parent
HASH_DB_PATH = ROOT_DIR / "hashes.json"

with HASH_DB_PATH.open("r", encoding="utf-8") as f:
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
                (c + 1) * tile_w,
                (r + 1) * tile_h,
            ))
            tiles.append(crop)
    return tiles


def crop_inner(tile, margin_ratio=0.12):
    w, h = tile.size
    mx = int(w * margin_ratio)
    my = int(h * margin_ratio)
    return tile.crop((mx, my, w - mx, h - my))


def tile_features(tile):
    base = ImageOps.autocontrast(tile.resize((64, 64)).convert("RGB"))
    gray = base.convert("L")
    phash = imagehash.phash(gray)
    dhash = imagehash.dhash(gray)

    arr = np.asarray(base).reshape(-1, 3)
    mean_rgb = arr.mean(axis=0)
    return phash, dhash, mean_rgb


def _hash_distance(db_hash_hex, target_hash):
    return imagehash.hex_to_hash(db_hash_hex) - target_hash


def score_candidate(db_entry, target_phash, target_dhash, target_rgb):
    if isinstance(db_entry, dict):
        phash_hex = db_entry.get("phash")
        dhash_hex = db_entry.get("dhash", phash_hex)
        db_rgb = np.array(db_entry.get("rgb", [127, 127, 127]), dtype=float)
    else:
        phash_hex = db_entry
        dhash_hex = db_entry
        db_rgb = np.array([127, 127, 127], dtype=float)

    phash_dist = _hash_distance(phash_hex, target_phash)
    dhash_dist = _hash_distance(dhash_hex, target_dhash)
    rgb_dist = np.linalg.norm(target_rgb - db_rgb) / 30.0

    return phash_dist + 0.75 * dhash_dist + rgb_dist


def match_tile(tile, top_k=3):
    tile = crop_inner(tile)
    target_phash, target_dhash, target_rgb = tile_features(tile)

    scored = []
    for name, db_entry in HASH_DB.items():
        score = score_candidate(db_entry, target_phash, target_dhash, target_rgb)
        scored.append((name, float(score)))

    scored.sort(key=lambda item: item[1])
    top = scored[:top_k]

    best_name, best_score = top[0]
    second_score = top[1][1] if len(top) > 1 else best_score + 999
    margin = second_score - best_score

    confidence = max(0.0, min(1.0, 1 - (best_score / 30.0)))
    if margin >= 4:
        confidence = min(1.0, confidence + 0.15)

    return {
        "name": best_name.replace(".png", ""),
        "score": round(best_score, 3),
        "confidence": round(confidence, 3),
        "margin": round(margin, 3),
        "top_k": [
            {"name": n.replace(".png", ""), "score": round(s, 3)} for n, s in top
        ],
    }


def is_empty(tile):
    inner = crop_inner(tile, margin_ratio=0.18)
    arr = np.asarray(inner.convert("RGB"))

    std = float(np.std(arr))
    saturation = float(np.std(arr, axis=2).mean())
    edge_strength = float(
        np.mean(np.abs(np.diff(arr.astype(np.int16), axis=0)))
        + np.mean(np.abs(np.diff(arr.astype(np.int16), axis=1)))
    )

    return std < 14 and saturation < 10 and edge_strength < 20


def process_image(file):
    img = Image.open(file).convert("RGB")

    tiles = split_grid(img)
    results = []

    for index, tile in enumerate(tiles):
        if is_empty(tile):
            continue

        match = match_tile(tile)
        status = "ok" if match["confidence"] >= 0.55 else "uncertain"

        results.append(
            {
                "slot": index,
                "pokemon": match["name"],
                "confidence": match["confidence"],
                "status": status,
                "top_k": match["top_k"],
            }
        )

    return results
