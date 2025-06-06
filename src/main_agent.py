from __future__ import annotations
import time, logging, argparse, json, requests, numpy as np
from minesweeper_agent import MinesweeperAgent
from tetrisagents import DownstackAgent, plan_to_commands

API_STATE = "http://localhost:3250/state"
API_COMMAND = "http://localhost:3250/command"
POLL = 0.10  # seconds

cli = argparse.ArgumentParser()
cli.add_argument("--debug-tetris", action="store_true")
args = cli.parse_args()

logging.basicConfig(level=logging.DEBUG, format="[%(name)s] %(message)s")
log = logging.getLogger("Main")

ms_agent = MinesweeperAgent()


#  board helpers
def board_grid(st):
    grid = np.zeros((22, 10), int)
    for t in st.get("board", []):
        x, y = t["x"], t["y"]
        if 0 <= x < 10 and 0 <= y < 22: grid[y, x] = 1

    active = st.get("currentPiece", {}).get("type", "")
    active = active[0].lower() if active else ""

    held = st.get("heldPiece", {}).get("type", "")
    held = held[0].lower() if held else ""

    nxt = st.get("nextPiece", {}).get("type", "")
    nxt = nxt[0].lower() if nxt else ""
    return grid, active, held, nxt


# Tetris
def tetris_cmds(state):
    grid, active, held, nxt = board_grid(state)
    if not active:  # no falling piece
        return []
    agent = DownstackAgent()
    agent.configure(grid, active, held=held, next_piece=nxt, dbg=args.debug_tetris)
    cmds = plan_to_commands(agent)
    if args.debug_tetris:
        log.debug("Tetris cmds: %s", cmds)
    return cmds


#  Minesweeper
def all_tiles(st):
    falling = {(c["x"], c["y"]) for c in st.get("currentPiece", {}).get("cells", [])}
    tiles = set()
    for k in ("leftWallTiles", "rightWallTiles", "floorTiles", "board"):
        for t in st.get(k, []):
            xy = (t["x"], t["y"])
            if xy not in falling:
                tiles.add(xy)
    return tiles


def neighbours(ts):
    n = {}
    for x, y in ts:
        n[(x, y)] = {(x + dx, y + dy)
                     for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                     if (dx or dy) and (x + dx, y + dy) in ts}
    return n


def clues(st):
    falling = {(c["x"], c["y"]) for c in st.get("currentPiece", {}).get("cells", [])}
    d = {}
    for k in ("floorTiles", "leftWallTiles", "rightWallTiles", "board"):
        for t in st.get(k, []):
            if t.get("isRevealed") and (t["x"], t["y"]) not in falling:
                d[(t["x"], t["y"])] = t["nearbyMines"]
    return d


def revealed(st):
    r = set()
    for k in ("leftWallTiles", "rightWallTiles", "floorTiles", "board"):
        r.update((t["x"], t["y"]) for t in st.get(k, []) if t.get("isRevealed"))
    return r


def flagged(st):
    f = set()
    for k in ("leftWallTiles", "rightWallTiles", "floorTiles", "board"):
        f.update((t["x"], t["y"]) for t in st.get(k, []) if t.get("isFlagged"))
    return f


def ms_cmds(st):
    # update MS agent knowledge
    ms_agent.set_neighbors(neighbours(all_tiles(st)))
    for xy, n in clues(st).items():
        ms_agent.add_knowledge(xy, n)

    rev = revealed(st)
    flg = flagged(st)
    cmds = []
    for x, y in ms_agent.safes - rev:
        cmds.append({"command": "reveal", "x": x, "y": y})
    for x, y in ms_agent.mines - flg:
        cmds.append({"command": "flag", "x": x, "y": y})
    if cmds and args.debug_tetris:
        log.debug("MS cmds: %s", cmds)
    return cmds


def fetch_state():
    try:
        r = requests.get(API_STATE, timeout=1);
        r.raise_for_status()
        return r.json() if r.text else None
    except (requests.RequestException, json.JSONDecodeError) as e:
        log.error("fetch_state %s", e)
        return None


def post_cmds(cmds):
    if not cmds: return
    try:
        requests.post(API_COMMAND, json=cmds, timeout=1).raise_for_status()
        log.debug("POST %s", cmds)
    except requests.RequestException as e:
        log.error("post_cmds %s", e)


# main loop
def main():
    prev = None
    prev_cleared = 0
    while True:
        st = fetch_state()
        if st:
            curr_cleared = st.get("linesCleared", 0)
            if curr_cleared > prev_cleared:
                ms_agent.reset()

            if st != prev:
                cmds = ms_cmds(st) + tetris_cmds(st)
                post_cmds(cmds)
                prev = st

            prev_cleared = curr_cleared
        time.sleep(POLL)


if __name__ == "__main__":
    main()
