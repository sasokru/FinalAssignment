# File: verify_levels.py
# verify_levels.py
# Checkt alle Sudoku-JSONs in Assets/data:
# - 9x9-Form, Werte 0..9
# - lösbar
# - eindeutige Lösung (genau 1)
# - vorhandene "solution" stimmt exakt (falls vorhanden)
# Nutzung:
#   python verify_levels.py
#   python verify_levels.py --dir Assets/data --write-solution

from __future__ import annotations
import argparse, json, sys
from copy import deepcopy
from pathlib import Path
from typing import Optional, Tuple

def is_9x9(mat) -> bool:
    return isinstance(mat, list) and len(mat) == 9 and all(isinstance(r, list) and len(r) == 9 for r in mat)

def ints_in_range(mat, lo, hi) -> bool:
    try:
        for r in mat:
            for v in r:
                if not isinstance(v, int) or v < lo or v > hi:
                    return False
        return True
    except Exception:
        return False

def find_empty(g) -> Optional[Tuple[int,int]]:
    for r in range(9):
        for c in range(9):
            if g[r][c] == 0:
                return r, c
    return None

def is_valid(g, r, c, v) -> bool:
    # row
    for x in range(9):
        if g[r][x] == v:
            return False
    # col
    for x in range(9):
        if g[x][c] == v:
            return False
    # box
    br, bc = (r//3)*3, (c//3)*3
    for rr in range(br, br+3):
        for cc in range(bc, bc+3):
            if g[rr][cc] == v:
                return False
    return True

def solve_one(g) -> Optional[list[list[int]]]:
    g = deepcopy(g)
    empty = find_empty(g)
    if not empty:
        return g
    r, c = empty
    for v in range(1, 10):
        if is_valid(g, r, c, v):
            g[r][c] = v
            sol = solve_one(g)
            if sol is not None:
                return sol
            g[r][c] = 0
    return None

def count_solutions(g, limit=2) -> int:
    g = deepcopy(g)
    cnt = 0
    def bt():
        nonlocal cnt, g
        if cnt >= limit:
            return
        pos = find_empty(g)
        if not pos:
            cnt += 1
            return
        r, c = pos
        for v in range(1, 10):
            if is_valid(g, r, c, v):
                g[r][c] = v
                bt()
                if cnt >= limit:
                    return
                g[r][c] = 0
    bt()
    return cnt

def equal(a, b) -> bool:
    for r in range(9):
        for c in range(9):
            if a[r][c] != b[r][c]:
                return False
    return True

def validate_file(path: Path, write_solution=False) -> tuple[bool, str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return False, f"JSON fehlerhaft: {e}"

    grid = data.get("grid") or data.get("puzzle") or data.get("board")
    if not is_9x9(grid) or not ints_in_range(grid, 0, 9):
        return False, "Grid muss 9x9 sein mit Werten 0..9 (0 = leer)."

    # Wenn solution vorhanden: Form prüfen 1..9
    solution = data.get("solution")
    if solution is not None:
        if not is_9x9(solution) or not ints_in_range(solution, 1, 9):
            return False, "Solution muss 9x9 sein mit Werten 1..9."
        # gegebenes Puzzle darf der Lösung nicht widersprechen
        for r in range(9):
            for c in range(9):
                if grid[r][c] != 0 and grid[r][c] != solution[r][c]:
                    return False, f"Vorbelegung an ({r+1},{c+1}) widerspricht solution."

    # Lösbar?
    solved = solve_one(grid)
    if solved is None:
        return False, "Puzzle ist nicht lösbar."

    # Eindeutig?
    n = count_solutions(grid, limit=2)
    if n != 1:
        return False, f"Puzzle hat {n} Lösungen (sollte 1 sein)."

    # Falls solution vorhanden: muss exakt mit Solver übereinstimmen
    if solution is not None and not equal(solution, solved):
        return False, "Gegebene solution stimmt nicht mit gefundener Lösung überein."

    # Optional: Lösung in Datei schreiben, wenn keine vorhanden
    if solution is None and write_solution:
        data["solution"] = solved
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return True, "OK (solution hinzugefügt)."

    return True, "OK"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default=str(Path(__file__).parent / "Assets" / "data"),
                        help="Verzeichnis mit level_*.json")
    parser.add_argument("--write-solution", action="store_true",
                        help="Fehlende Lösung automatisch berechnen & ins JSON schreiben")
    args = parser.parse_args()

    data_dir = Path(args.dir)
    files = sorted(data_dir.glob("level_*.json"))
    if not files:
        print(f"Keine Dateien level_*.json in {data_dir}")
        sys.exit(2)

    print(f"Prüfe {len(files)} Dateien in {data_dir} …")
    ok_all = True
    for p in files:
        ok, msg = validate_file(p, write_solution=args.write_solution)
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {p.name}: {msg}")
        if not ok:
            ok_all = False

    if not ok_all:
        sys.exit(1)

if __name__ == "__main__":
    main()