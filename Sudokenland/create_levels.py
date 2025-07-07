# File: create_levels.py
# Run once to generate Assets/data/level_0.json ... level_9.json with verbose logging

# create_levels.py
# Erzeugt 10 Sudoku-Levels (0..9) als JSON in Assets/data/ mit eindeutiger Lösung.
# Format: { "level": int, "clues": int, "grid": [[...]], "solution": [[...]] }
# Nutzung:
#   python create_levels.py            -> erzeugt fehlende Files
#   python create_levels.py --force    -> überschreibt existierende Files


from __future__ import annotations
import json
import random
from pathlib import Path
import argparse
from copy import deepcopy
from typing import Optional, Tuple

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "Assets" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Ziel-Anzahl an vorgegebenen Zellen pro Level (0 leicht -> 9 schwerer)
# Passe das gern an: mehr clues = leichter
LEVEL_CLUES = [60, 52, 48, 44, 40, 36, 34, 32, 30, 28]

# ---------- Sudoku Kern (Backtracking) ----------
def find_empty(grid) -> Optional[Tuple[int, int]]:
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                return r, c
    return None

def is_valid(grid, r, c, val) -> bool:
    # Row
    if any(grid[r][x] == val for x in range(9)):
        return False
    # Col
    if any(grid[x][c] == val for x in range(9)):
        return False
    # Box
    br, bc = (r // 3) * 3, (c // 3) * 3
    for rr in range(br, br + 3):
        for cc in range(bc, bc + 3):
            if grid[rr][cc] == val:
                return False
    return True

def solve_grid(grid) -> Optional[list[list[int]]]:
    """Standard-Solver: liefert eine Lösung oder None."""
    grid = deepcopy(grid)
    empty = find_empty(grid)
    if not empty:
        return grid
    r, c = empty
    nums = list(range(1, 10))
    random.shuffle(nums)
    for val in nums:
        if is_valid(grid, r, c, val):
            grid[r][c] = val
            sol = solve_grid(grid)
            if sol is not None:
                return sol
            grid[r][c] = 0
    return None

def count_solutions(grid, limit=2) -> int:
    """Zählt Lösungen bis zu 'limit' (Frühabbruch, um Eindeutigkeit zu checken)."""
    count = 0
    work = deepcopy(grid)

    def backtrack():
        nonlocal count, work
        if count >= limit:
            return
        empty = find_empty(work)
        if not empty:
            count += 1
            return
        r, c = empty
        # feste Reihenfolge genügt hier für die Zählung
        for val in range(1, 10):
            if is_valid(work, r, c, val):
                work[r][c] = val
                backtrack()
                if count >= limit:
                    return
                work[r][c] = 0

    backtrack()
    return count

def generate_full_solution() -> list[list[int]]:
    """Erzeugt ein zufälliges gelöstes Sudoku."""
    grid = [[0] * 9 for _ in range(9)]
    # optional: diagonale 3x3-Blöcke füllen -> schneller
    for br in range(0, 9, 3):
        nums = list(range(1, 10))
        random.shuffle(nums)
        idx = 0
        for r in range(br, br + 3):
            for c in range(br, br + 3):
                grid[r][c] = nums[idx]
                idx += 1
    sol = solve_grid(grid)
    if sol is None:
        # fallback: reiner Backtracking-Versuch
        sol = solve_grid([[0]*9 for _ in range(9)])
    assert sol is not None
    return sol

def make_puzzle(solution: list[list[int]], clues_target: int, max_tries: int = 10000) -> list[list[int]]:
    """Maskiert Zellen aus 'solution' bis zur gewünschten Anzahl 'clues_target', bewahrt eindeutige Lösung."""
    puzzle = deepcopy(solution)
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)
    clues = 81

    tries = 0
    for r, c in cells:
        if clues <= clues_target:
            break
        if puzzle[r][c] == 0:
            continue
        backup = puzzle[r][c]
        puzzle[r][c] = 0

        # Eindeutigkeit prüfen
        sols = count_solutions(puzzle, limit=2)
        if sols == 1:
            clues -= 1
        else:
            puzzle[r][c] = backup

        tries += 1
        if tries > max_tries:
            break

    # sanfter Fallback für den seltenen Fall, dass wir das Ziel knapp verfehlen
    remaining_to_remove = max(0, clues - clues_target)
    if remaining_to_remove > 0:
        extra_cells = [(r, c) for r in range(9) for c in range(9) if puzzle[r][c] != 0]
        random.shuffle(extra_cells)
        for r, c in extra_cells:
            if remaining_to_remove == 0:
                break
            backup = puzzle[r][c]
            puzzle[r][c] = 0
            if solve_grid(puzzle) is not None:
                remaining_to_remove -= 1
            else:
                puzzle[r][c] = backup

    return puzzle

# ---------- Pipeline ----------
def build_level(level_index: int, clues: int, seed: Optional[int] = None):
    if seed is not None:
        random.seed(seed)

    solution = generate_full_solution()
    puzzle = make_puzzle(solution, clues_target=clues)

    # Sicherheitscheck
    assert solve_grid(puzzle) is not None, "Puzzle ist nicht lösbar."
    assert count_solutions(puzzle, limit=2) == 1, "Puzzle ist nicht eindeutig."

    return {
        "level": level_index,
        "clues": clues,
        "grid": puzzle,
        "solution": solution,
    }

def main(force: bool, only: Optional[int]):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    targets = [only] if only is not None else list(range(10))
    for i in targets:
        if i < 0 or i > 9:
            print(f"[skip] Level-Index {i} außerhalb 0..9")
            continue

        clues = LEVEL_CLUES[i] if i < len(LEVEL_CLUES) else 34
        out_path = DATA_DIR / f"level_{i}.json"

        if out_path.exists() and not force:
            print(f"[skip] {out_path.name} existiert bereits. (Nutze --force zum Überschreiben)")
            continue

        seed = 20250910 + i * 37
        try:
            level_data = build_level(i, clues=clues, seed=seed)
        except AssertionError as e:
            print(f"[retry] Level {i}: {e} -> neuer Versuch")
            level_data = build_level(i, clues=clues, seed=seed + 999)

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(level_data, f, ensure_ascii=False, indent=2)
        print(f"[ok]   {out_path.name} (clues={clues}) geschrieben.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Sudoku levels into Assets/data/")
    parser.add_argument("--force", action="store_true", help="Overwrite existing JSON files")
    parser.add_argument("--only", type=int, help="Generate only a single level index 0..9")
    args = parser.parse_args()
    main(force=args.force, only=args.only)
