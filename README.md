# PokeHomeScan

PokeHomeScan scans a Pokémon HOME box screenshot and returns detected Pokémon for each occupied slot.

## Current matching pipeline

- Splits the image into a 6x10 grid.
- Skips likely-empty slots using visual heuristics.
- Scores each occupied tile against the hash database with a weighted score:
  - pHash distance
  - dHash distance
  - mean color distance
- Returns top match plus confidence and top-k alternatives.

## Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install flask pillow imagehash numpy
python app.py
```

## API

### `POST /scan`

Form-data field:
- `image`: screenshot image file

Response:

```json
{
  "count": 35,
  "results": [
    {
      "slot": 0,
      "pokemon": "bulbasaur",
      "confidence": 0.91,
      "status": "ok",
      "top_k": [
        {"name": "bulbasaur", "score": 2.1},
        {"name": "ivysaur", "score": 4.7},
        {"name": "oddish", "score": 5.0}
      ]
    }
  ]
}
```

## Frontend

Open `frontend/index.html` in a browser and upload an image. Results include slot, confidence, and alternatives.
