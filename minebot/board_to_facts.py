
import json, sys

data  = json.load(sys.stdin)
tiles = []

for key in ("board", "floorTiles", "leftWallTiles", "rightWallTiles"):
    tiles.extend(data.get(key, []))

for t in tiles:
    if t.get("aura") == "blocked": # skip outside 
        continue
    x, y     = t["x"], t["y"]
    flagged  = t["isFlagged"]
    revealed = t["isRevealed"]
    mines    = t["nearbyMines"]
    
    if not (-1 <= y <= 22):         
        continue
    if not (-1 <= x <= 10):
        continue

    if flagged:
        state = "flagged"
    elif not revealed:
        state = "hidden"
    else:
        state = f"number({mines})"

    print(f"cell({x},{y},{state}).")
