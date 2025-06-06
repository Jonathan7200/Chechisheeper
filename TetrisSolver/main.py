# imports
from enum import Enum
import tetrisagents


class Modes(Enum):  # ordered by complexity
    DOWNSTACK = 0   # maintain low flat board. plug holes. fill lines.
  


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

