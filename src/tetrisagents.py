

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict
import numpy as np

from pathfinding import find_all_paths, piece_squares  
CMD = {                       
    "l": "moveleft",
    "r": "moveright",
    "d": "softdrop",
    "c": "rotate",
    "a": "rotateccw",
    "h": "hold",
}

def plan_to_commands(agent) -> List[Dict[str, str]]:
    return [{"command": CMD[ch]} for ch in iter(agent.next_letter, None)]

class Agent(ABC):
    @abstractmethod
    def config(self, field_state: np.ndarray, hold_available: bool,
            active_piece: str, held_piece: str, next_list: list): ...
    @abstractmethod
    def suggest_action(self, active_piece): ...

class DownstackAgent(Agent):
    def __init__(self):
        self.move_plan: str = ""
        self.idx: int = 0

    def _best_for_piece(self, grid: np.ndarray, piece: str):
        landings = find_all_paths(grid, piece)
        best_key, best_score = None, 1e9
        for k, path in landings.items():
            g2 = grid.copy()
            for i, j in piece_squares[piece]:
                if k[2] == 0:   g2[k[1]+j, k[0]+i] = 1
                elif k[2] == 1: g2[k[1]-i, k[0]+j] = 1
                elif k[2] == 2: g2[k[1]-j, k[0]-i] = 1
                else:           g2[k[1]+i, k[0]-j] = 1
            top_row = int(np.argmax(np.all(g2 == 0, axis=1)))
            holes   = np.sum((g2[:-1] == 0) & (g2[1:] == 1))
            score   = top_row + 4 * holes
            if score < best_score:
                best_key, best_score = k, score
        return landings[best_key], best_score

    def config(self, field_state, hold_available, active_piece,
            held_piece="", next_list=None):
        plan_active, score_active = self._best_for_piece(field_state, active_piece)

        if hold_available and held_piece:
            plan_hold, score_hold = self._best_for_piece(field_state, held_piece)
            if score_hold < score_active:
                plan_active = "h" + plan_hold 

        self.move_plan = plan_active + "d"  
        self.idx = 0

    def next_letter(self):
        if self.idx >= len(self.move_plan):
            return None
        ch = self.move_plan[self.idx]
        self.idx += 1
        return ch

    def suggest_action(self, active_piece):     
        return self.next_letter()

def _configure_kw(self,
                grid: np.ndarray,
                active_piece: str,
                *,
                held: str = "",
                next_piece: str = "",
                dbg: bool = False,
                hold_available: bool = True,
                **_ignored):
    self.config(grid, hold_available, active_piece, held, [next_piece] if next_piece else [])
    if dbg:
        print("[DownstackAgent] move_plan =", self.move_plan)

DownstackAgent.configure = _configure_kw        
