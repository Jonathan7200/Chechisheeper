 #!/usr/bin/env python3
import json
import sys

def main():
    # Read JSON board state from stdin
    data = json.load(sys.stdin)
    board = data.get("board", [])

    if not board:
        print("No board data found.")
        return

    # Determine grid dimensions
    max_x = max(tile["x"] for tile in board)
    max_y = max(tile["y"] for tile in board)

    # Initialize empty grid
    grid = [[" " for _ in range(max_x + 1)] for _ in range(max_y + 1)]

    # Populate grid
    for tile in board:
        x = tile["x"]
        y = tile["y"]
        if not tile.get("isRevealed", False):
            char = "■"
        elif tile.get("isFlagged", False):
            char = "⚑"
        else:
            nm = tile.get("nearbyMines")
            char = str(nm) if nm is not None else " "
        grid[y][x] = char

    # Print rows from top to bottom
    for y in range(max_y, -1, -1):
        row = " ".join(grid[y])
        print(f"{y:2d} | {row}")

    # Print x-axis labels
    x_labels = " ".join(str(x) for x in range(max_x + 1))
    print(f"    {x_labels}")

if __name__ == "__main__":
    main()
