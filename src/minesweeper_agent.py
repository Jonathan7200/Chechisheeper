import json

class Tileset:
    """
    A set of cells with a count of mines.
    This represents a logical sentence in the Minesweeper knowledge base.
    Cells are represented as tuples (x, y).
    """
    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def mark_safe(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)

    def mark_mine(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def is_empty(self):
        return not self.cells

    def __repr__(self):
        return f"{self.count} mine(s) in {self.cells}"


class MinesweeperAgent:
    def __init__(self,):
        self.neighbors  = None
        self.moves_made = set()     # cells we've clicked
        self.safes      = set()     # cells known to be safe
        self.mines      = set()     # cells known to be mines
        self.knowledge  = []        # list of Tileset sentences

    def set_neighbors(self, neighbors):
        """
        Set the neighbors map for this agent.
        `neighbors` is a dict mapping each cell to its 8-way neighbors.
        """
        self.neighbors = neighbors
    
    def mark_safe(self, cell):
        """
        Record that `cell` is known safe.  Remove it from all sentences.
        If that cell is already known to be a mine, ignore.
        """
        if cell in self.mines:
            return
        if cell not in self.safes:
            self.safes.add(cell)
            for s in self.knowledge:
                s.mark_safe(cell)

    def mark_mine(self, cell):
        """
        Record that `cell` is known to be a mine.  Remove it from all sentences,
        decrementing their counts.  If that cell is already known to be safe, ignore.
        """
        if cell in self.safes:
            return
        if cell not in self.mines:
            self.mines.add(cell)
            for s in self.knowledge:
                s.mark_mine(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the game reports “cell has been revealed with clue=count.”
        """

        # 1) Record the move
        self.moves_made.add(cell)

        # 2) Mark the clicked cell safe
        self.mark_safe(cell)

        # 3) Gather this cell’s neighbors:
        neigh = self.neighbors[cell]

        # Separate out which neighbors we already know to be mines/safes:
        known_mines = {n for n in neigh if n in self.mines}
        known_safes = {n for n in neigh if n in self.safes}

        # The undetermined neighbors are those not yet in safes or mines:
        undetermined = neigh - known_mines - known_safes

        # 4) Compute the “effective count” by subtracting out known mines
        effective_count = count - len(known_mines)

        # If effective_count == 0, all undetermined neighbors are safe:
        if effective_count == 0 and undetermined:
            for n in undetermined:
                self.mark_safe(n)

        # Otherwise, if effective_count > 0, add a new sentence about the undetermined cells:
        elif effective_count > 0 and undetermined:
            new_sentence = Tileset(undetermined, effective_count)
            print(f"Adding sentence: {new_sentence}  (orig={count}, known_mines={len(known_mines)})")
            self.knowledge.append(new_sentence)

        # 5) Run inference to fixpoint
        self._infer()

    def _infer(self):
        """
        Stop when no new facts or sentences can be added.  Then prune any empty/invalid sentences.
        """
        changed = True
        while changed:
            changed = False

            # A) Zero‐count rule: if count == 0, all those cells are safe
            for s in list(self.knowledge):
                if s.count == 0 and s.cells:
                    for c in list(s.cells):
                        if c not in self.safes:
                            self.mark_safe(c)
                            changed = True

            # B) Full‐count rule: if count == |cells|, all those cells are mines
            for s in list(self.knowledge):
                if s.count == len(s.cells) and s.cells:
                    for c in list(s.cells):
                        if c not in self.mines:
                            self.mark_mine(c)
                            changed = True

            # C) Subset‐difference rule
            for s1 in self.knowledge:
                for s2 in self.knowledge:
                    if s1 is s2:
                        continue
                    if s1.cells and s1.cells.issubset(s2.cells):
                        new_cells = s2.cells - s1.cells
                        new_count = s2.count - s1.count
                        if new_cells and 0 <= new_count <= len(new_cells):
                            derived = Tileset(new_cells, new_count)
                            # avoid duplicate
                            if not any(
                                derived.cells == s.cells and derived.count == s.count
                                for s in self.knowledge
                            ):
                                self.knowledge.append(derived)
                                changed = True

            # Prune any empty or invalid sentences
            self.knowledge = [
                s for s in self.knowledge
                if s.cells and 0 <= s.count <= len(s.cells)
            ]
    
    def reset(self):
        """
        Reset the agent's knowledge base.
        """
        self.moves_made = set()
        self.safes = set()
        self.mines = set()
        self.knowledge = []
