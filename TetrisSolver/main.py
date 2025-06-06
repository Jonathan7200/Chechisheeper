# imports
from enum import Enum
import tetrisagents


class Modes(Enum):  # ordered by complexity
    DOWNSTACK = 0   # maintain low flat board. plug holes. fill lines.
    # STALL = 1     # delay lock as long as possible (let fall, rotate/move, hold). revert if board is fully swept.
    # TETRI = 2     # stack pieces in C1-C9. if ≥4 rows ready, fill C10 with i-piece and switch to stall mode.
    # LOOP = 3      # use repeatable 7-bag setup. (tbd, probably pj-dpc.)
    # RECOVER = 4   # maximize region that gets swept before lock, esp sweeping from top.


def scan_board():
    # todo
    return None, None, None, None


def select_mode(field_state):
    # todo
    return Modes.DOWNSTACK


def main():
    agents = [None, None, None, None, None]
    while True:
        piece_active = True
        hold_available = True
        field_state, active_piece, held_piece, next_list = scan_board()
        mode = select_mode(field_state)
        agent = agents[mode.value()]
        agent.config(field_state, hold_available, active_piece, held_piece, next_list)
        while piece_active:
            agent.suggest_action(active_piece)

