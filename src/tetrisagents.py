from abc import ABC, abstractmethod
from pathfinding import find_all_paths, piece_squares
# from server import move_l, move_r, soft_drop, hard_drop, rotate_cw, rotate_ccw, hold, wait
import numpy as np

class Agent(ABC):
    @abstractmethod
    def config(self, field_state: np.ndarray, hold_available: bool, active_piece: str, held_piece: str, next_list: list):
        pass
    @abstractmethod
    def suggest_action(self, active_piece):
        pass

class DownstackAgent(Agent):
    move_plan = ""
    ind = 0

    move_methods = {"l": None,  # move_l,
                    "r": None,  # move_r,
                    "d": None,  # soft_drop,
                    "c": None,  # rotate_cw,
                    "a": None}  # rotate_ccw}
    def config(self, field_state, hold_available, active_piece, held_piece, next_list):
        f = find_all_paths(field_state, 't')
        min_score = 2048
        min_key = None
        for k in reversed(f.keys()):
            # print(k, end=" ")
            grid2 = np.copy(field_state)
            for (i, j) in piece_squares['t']:
                if k[2] == 0:
                    grid2[k[1] + j, k[0] + i] = 1
                elif k[2] == 1:
                    grid2[k[1] - i, k[0] + j] = 1
                elif k[2] == 2:
                    grid2[k[1] - j, k[0] - i] = 1
                elif k[2] == 3:
                    grid2[k[1] + i, k[0] - j] = 1
            score = int(np.argmax(np.all(grid2 == 0, axis=1)))
            score -= int(np.argmax(np.any(grid2 == 0, axis=1)))
            if score == 0:
                score = 3
            # print(score, end=" ")
            if score > min_score:
                # print()
                continue
            score += 4 * len(np.where(grid2[:-1] < grid2[1:])[0])
            # print(score)
            if score < min_score:
                min_score = score
                min_key = k
        # print(min_key, min_score, f[min_key])
        self.move_plan = f[min_key]
        self.ind = 0

    def suggest_action(self, active_piece):
        if self.ind > len(self.move_plan):
            return None
        move = self.move_methods[self.move_plan[self.ind]]
        self.ind += 1
        return move

# class StallAgent(Agent):
#
# class TetriAgent(Agent):
#
# class LoopAgent(Agent):
#
# class RecoverAgent(Agent):
