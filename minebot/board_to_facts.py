
import json, sys

tiles = json.load(sys.stdin).get("board", [])
for t in tiles:
    x, y        = t["x"], t["y"]
    flagged     = t.get("isFlagged", False)
    revealed    = t.get("isRevealed", False)
    mines       = t.get("nearbyMines", -1)

    if flagged:
        state = "flagged"
    elif not revealed:
        state = "hidden"
    elif mines >= 0:
        state = f"number({mines})"
    else:
        continue 

    print(f"cell({x},{y},{state}).")
