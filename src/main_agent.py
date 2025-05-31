import time
import requests
import json
from minesweeper_agent import MinesweeperAgent

API_STATE = "http://localhost:3250/state"
API_COMMAND = "http://localhost:3250/command"
POLL = 0.1

ms_agent = MinesweeperAgent()

def fetch_state():
    """Fetch and parse JSON state; return None on invalid JSON or empty response."""
    try:
        r = requests.get(API_STATE, timeout=1)
        r.raise_for_status()
        if not r.text:
            return None
        return r.json()
    except (requests.RequestException, ValueError) as e:
        print(f"[MainAgent] Fetch error or invalid JSON: {e}")
        return None

def send_commands(commands):
    """Send commands to the server."""
    if not commands:
        return
    commands_json = json.dumps(commands)
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(API_COMMAND, data=commands_json, headers=headers, timeout=1)
        response.raise_for_status()
        print(f"[MainAgent] Commands sent successfully: {commands}")
    except requests.RequestException as e:
        print(f"[MainAgent] Error sending commands: {e}")

def distribute(state, prev_state=None):
    # skip if no new JSON
    if not state or state == prev_state:
        return prev_state
    
    prev_cleared = prev_state.get("linesCleared", 0) if prev_state else 0
    current_cleared = state.get("linesCleared", 0)
    if current_cleared > prev_cleared:
        print(f"[MainAgent] Lines cleared: {current_cleared - prev_cleared}")
        ms_agent.reset()
    try:
        all_tiles = extract_all_tiles(state)
        neighbors_map = compute_neighbors(all_tiles)
        ms_agent.set_neighbors(neighbors_map)
        update_minesweeper(ms_agent, state)
        commands = ms_commands(state, ms_agent)
        send_commands(commands)
    except Exception as e:
        print(f"[MainAgent] MinesweeperAgent error: {e}")
    return state

def extract_all_tiles(state):
    """
    Gather all tile coordinates from leftWallTiles, rightWallTiles, floorTiles, and board.
    """
    current_piece_cells = {
        (c["x"], c["y"])
        for c in state.get("currentPiece", {}).get("cells", [])
    }
    tiles = set()
    for key in ("leftWallTiles", "rightWallTiles", "floorTiles", "board"):
        for t in state.get(key, []):
            tile = (t["x"], t["y"])
            if tile not in current_piece_cells:
                tiles.add(tile)
    return tiles

def compute_neighbors(all_tiles):
    """
    Precompute the 8-way adjacency for every cell in all_tiles.
    """
    neigh = {}
    for x, y in all_tiles:
        neigh[(x, y)] = {
            (x + dx, y + dy)
            for dx in (-1, 0, 1)
            for dy in (-1, 0, 1)
            if not (dx == 0 and dy == 0)
            and (x + dx, y + dy) in all_tiles
        }
    return neigh

def extract_clues(state):
    """
    Pull clues from 'board', 'floorTiles', 'leftWallTiles', and 'rightWallTiles',
    skipping any cells under currentPiece.
    """
    current_piece_cells = {
        (c["x"], c["y"])
        for c in state.get("currentPiece", {}).get("cells", [])
    }

    clues = {}
    for key in ("floorTiles", "leftWallTiles", "rightWallTiles", "board"):
        for tile in state.get(key, []):
            # Only use tiles that have actually been revealed
            if not tile.get("isRevealed", False):
                continue

            coord = (tile["x"], tile["y"])
            # Skip if it's under the falling piece
            if coord in current_piece_cells:
                continue

            # Record the clue
            clues[coord] = tile["nearbyMines"]

    return clues

def update_minesweeper(agent, state):
    """
    Extract all board clues and call add_knowledge for each.
    """
    clues = extract_clues(state)
    for cell, count in clues.items():
        agent.add_knowledge(cell, count)

def get_revealed_cells(state):
    """
    Extract all revealed cells from the state.
    """
    revealed = set()
    for key in ("leftWallTiles", "rightWallTiles", "floorTiles", "board"):
        for tile in state.get(key, []):
            if tile.get("isRevealed", False):
                revealed.add((tile["x"], tile["y"]))
    return revealed

def get_flagged_cells(state):
    """
    Extract all flagged cells from the state.
    """
    flagged = set()
    for key in ("leftWallTiles", "rightWallTiles", "floorTiles", "board"):
        for tile in state.get(key, []):
            if tile.get("isFlagged", False):
                flagged.add((tile["x"], tile["y"]))
    return flagged
    

def ms_commands(state, agent):
    commands = []
    revealed = get_revealed_cells(state)
    flagged = get_flagged_cells(state)
    for cell in agent.safes:
        if cell not in revealed:
            x, y = cell
            commands.append({"command": "reveal", "x": x, "y": y})
    for cell in agent.mines:
        if cell not in flagged:
            x, y = cell
            commands.append({"command": "flag", "x": x, "y": y})
    return commands

def main():
    last = None
    while True:
        state = fetch_state()
        last = distribute(state, last)
        time.sleep(POLL)

if __name__ == '__main__':
    main()