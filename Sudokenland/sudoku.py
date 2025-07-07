## Almost the most important part and actual content of the game within the game is the game Sudoku itsself.
## This file is dedicated to the logic of the game which will be applied to all the 9/10 levels of the game.
## I will try to add an instance which signalises the user whether a move is right or wrong (but not sure yet whether during or afterwards).

# sudoku.py
# Minimal 9x9 Sudoku-Spiel für Pygame mit:
# - H = Hint (füllt eine richtige Zelle)
# - L = Auto-solve (füllt komplette Lösung, gibt "completed" zurück)
# - E = zurück zur Karte ("back")
# - ESC = komplettes Spiel beenden ("quit")
# Erwartet Aufruf aus Main:
#    start_sudoku(level_index: int, data_dir: str) -> str

from __future__ import annotations
import json
from pathlib import Path
from copy import deepcopy
import pygame

# ---------- Fenster & Layout ----------
WIDTH, HEIGHT = 1280, 720

SAFE_TOP = 90      # Platz für Titel + Hilfe oben
SAFE_BOTTOM = 50   # Platz für Statuszeile unten

# Dynamisch: Grid so groß wie möglich, mit Luft links/rechts
MAX_GRID_H = HEIGHT - SAFE_TOP - SAFE_BOTTOM
MAX_GRID_W = int(WIDTH * 0.72)      # etwas Platz seitlich lassen
CELL = min(MAX_GRID_H // 9, MAX_GRID_W // 9)
CELL = max(CELL, 40)                # Untergrenze für gut lesbare Zahlen
GRID_SIZE = CELL * 9
MARGIN_TOP = SAFE_TOP
MARGIN_LEFT = (WIDTH - GRID_SIZE) // 2

FPS = 60

# ---------- Farben ----------
BLACK  = (0, 0, 0)
WHITE  = (255, 255, 255)
GRAY   = (140, 140, 140)
LIGHT  = (200, 200, 200)
YELLOW = (240, 220, 0)
GREEN  = (0, 200, 120)
RED    = (210, 70, 70)
BLUE   = (80, 140, 220)

# ---------- Fonts ----------
def load_font(size: int) -> pygame.font.Font:
    """Versucht PressStart2P aus Assets/fonts, sonst SysFont."""
    assets_fonts = Path(__file__).parent / "Assets" / "fonts" / "PressStart2P-Regular.ttf"
    if assets_fonts.exists():
        try:
            return pygame.font.Font(str(assets_fonts), size)
        except Exception:
            pass
    return pygame.font.SysFont("Arial", size)

def load_mono(size: int) -> pygame.font.Font:
    """Monospace-Fallbacks für klare Zahlen."""
    for name in ["Consolas", "Menlo", "DejaVu Sans Mono", "Courier New", "monospace", "Courier"]:
        try:
            f = pygame.font.SysFont(name, size)
            if f:
                return f
        except Exception:
            continue
    return pygame.font.SysFont("Arial", size)

# ---------- Sudoku-Utils ----------
def find_empty(grid):
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                return r, c
    return None

def is_valid(grid, r, c, val):
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

def solve_backtrack(grid):
    g = deepcopy(grid)
    empty = find_empty(g)
    if not empty:
        return g
    r, c = empty
    for val in range(1, 10):
        if is_valid(g, r, c, val):
            g[r][c] = val
            sol = solve_backtrack(g)
            if sol is not None:
                return sol
            g[r][c] = 0
    return None

def grid_equals(a, b) -> bool:
    for r in range(9):
        for c in range(9):
            if a[r][c] != b[r][c]:
                return False
    return True

def one_hint(current, solution, fixed_mask) -> bool:
    """Füllt genau EINE korrekte Zelle (nicht-fixed). Return True wenn etwas gesetzt wurde."""
    # zuerst leere Felder, dann falsche
    for r in range(9):
        for c in range(9):
            if not fixed_mask[r][c] and current[r][c] == 0:
                current[r][c] = solution[r][c]
                return True
    for r in range(9):
        for c in range(9):
            if not fixed_mask[r][c] and current[r][c] != solution[r][c]:
                current[r][c] = solution[r][c]
                return True
    return False

def tip_text(current, solution) -> str:
    """Sehr simpler Text-Hinweis."""
    # suche erstes leeres Feld und nenne den 3x3-Block + korrekte Zahl
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            for r in range(br, br + 3):
                for c in range(bc, bc + 3):
                    if current[r][c] == 0:
                        want = solution[r][c]
                        return f"Tip: Check box ({br//3+1},{bc//3+1}). A {want} fits somewhere."
    # sonst weise auf die erste falsche Zahl hin
    for r in range(9):
        for c in range(9):
            if current[r][c] != 0 and current[r][c] != solution[r][c]:
                return f"Tip: The {current[r][c]} at row {r+1}, col {c+1} seems wrong."
    return "Tip: Scan rows/cols for singles."

# ---------- Drawing ----------
def draw_grid(surface, sel_rc, fixed_mask, current, msg_text):
    surface.fill(BLACK)

    # GRID-Hintergrund zuerst
    pygame.draw.rect(surface, (25, 25, 25), (MARGIN_LEFT, MARGIN_TOP, GRID_SIZE, GRID_SIZE))

    # Zahlen-Größe relativ zur Zelle
    num_font = load_mono(max(18, int(CELL * 0.6)))

    # Zellen & Zahlen
    for r in range(9):
        for c in range(9):
            x = MARGIN_LEFT + c * CELL
            y = MARGIN_TOP + r * CELL

            # Auswahl
            if sel_rc == (r, c):
                pygame.draw.rect(surface, (40, 40, 60), (x, y, CELL, CELL))

            v = current[r][c]
            if v != 0:
                color = WHITE if not fixed_mask[r][c] else GREEN
                txt = num_font.render(str(v), True, color)
                tr = txt.get_rect(center=(x + CELL // 2, y + CELL // 2))
                surface.blit(txt, tr)

    # Linien
    for i in range(10):
        pygame.draw.line(surface, LIGHT, (MARGIN_LEFT, MARGIN_TOP + i * CELL),
                         (MARGIN_LEFT + GRID_SIZE, MARGIN_TOP + i * CELL), 1)
        pygame.draw.line(surface, LIGHT, (MARGIN_LEFT + i * CELL, MARGIN_TOP),
                         (MARGIN_LEFT + i * CELL, MARGIN_TOP + GRID_SIZE), 1)
    for i in range(0, 10, 3):
        pygame.draw.line(surface, WHITE, (MARGIN_LEFT, MARGIN_TOP + i * CELL),
                         (MARGIN_LEFT + GRID_SIZE, MARGIN_TOP + i * CELL), 3)
        pygame.draw.line(surface, WHITE, (MARGIN_LEFT + i * CELL, MARGIN_TOP),
                         (MARGIN_LEFT + i * CELL, MARGIN_TOP + GRID_SIZE), 3)

    # Titel links oben
    title = load_font(20)
    surface.blit(title.render("Sudokenland — Sudoku", True, YELLOW), (20, 10))

    # Hilfe-Overlay (halbtransparent) – NIE vom Grid überdeckt
    help_bg = pygame.Surface((WIDTH, 44), pygame.SRCALPHA)
    help_bg.fill((0, 0, 0, 150))
    surface.blit(help_bg, (0, 40))

    small = load_font(14)
    surface.blit(small.render("Arrows/WASD: move   1-9: write   0/BACKSPACE/DEL: clear", True, (235, 235, 235)), (20, 46))
    surface.blit(small.render("H: hint   L: auto-solve   E: back to map   ESC: quit", True, (235, 235, 235)), (20, 62))

    # Statuszeile unten
    if msg_text:
        msg_font = load_font(14)
        bar = pygame.Surface((WIDTH, 28))
        bar.fill((0, 0, 0))
        surface.blit(bar, (0, HEIGHT - 30))
        surface.blit(msg_font.render(msg_text, True, BLUE), (20, HEIGHT - 26))

def _msg(screen, clock, text, ms=900, color=GREEN):
    small = load_font(14)
    t0 = pygame.time.get_ticks()
    while pygame.time.get_ticks() - t0 < ms:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return
        # untere Statuszeile
        bar = pygame.Surface((WIDTH, 28))
        bar.fill((0, 0, 0))
        screen.blit(bar, (0, HEIGHT - 30))
        screen.blit(small.render(text, True, color), (20, HEIGHT - 26))
        pygame.display.flip()
        clock.tick(FPS)

# ---------- IO ----------
def load_level(level_index: int, data_dir: str):
    path = Path(data_dir) / f"level_{level_index}.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Unterstützt: {"grid":[[...]], "solution":[[...]]} oder nur "grid"
    grid = data.get("grid") or data.get("puzzle") or data.get("board")
    if not grid or len(grid) != 9 or any(len(row) != 9 for row in grid):
        raise ValueError("JSON must contain 9x9 'grid' with 0 for empty cells.")

    solution = data.get("solution")
    if solution is None:
        solution = solve_backtrack(grid)
        if solution is None:
            raise ValueError("Puzzle is unsolvable.")

    # fixed dort, wo grid != 0
    fixed_mask = [[(grid[r][c] != 0) for c in range(9)] for r in range(9)]
    return grid, solution, fixed_mask

# ---------- Public API ----------
def start_sudoku(level_index: int, data_dir: str) -> str:
    """Zeigt das Sudoku für level_index. Return: 'completed' | 'back' | 'quit'."""
    screen = pygame.display.get_surface()
    created_screen = False
    if screen is None:
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Sudokenland — Sudoku")
        created_screen = True
    clock = pygame.time.Clock()

    try:
        start_grid, solution, fixed_mask = load_level(level_index, data_dir)
    except Exception as e:
        _msg(screen, clock, f"Level {level_index} error: {e}", ms=2000, color=RED)
        if created_screen:
            pygame.quit()
        return "back"

    current = deepcopy(start_grid)
    sel_r, sel_c = 0, 0
    hint_stage = 0  # 0 -> Zahl; 1 -> Text-Tipp; 2 -> Zahl; ...

    msg_text = ""

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                if created_screen:
                    pygame.quit()
                return "quit"
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    if created_screen:
                        pygame.quit()
                    return "quit"
                if e.key == pygame.K_e:
                    if created_screen:
                        pygame.quit()
                    return "back"

                # Bewegung
                if e.key in (pygame.K_LEFT, pygame.K_a):
                    sel_c = (sel_c - 1) % 9
                elif e.key in (pygame.K_RIGHT, pygame.K_d):
                    sel_c = (sel_c + 1) % 9
                elif e.key in (pygame.K_UP, pygame.K_w):
                    sel_r = (sel_r - 1) % 9
                elif e.key in (pygame.K_DOWN, pygame.K_s):
                    sel_r = (sel_r + 1) % 9

                # Zahlen setzen/löschen
                if not fixed_mask[sel_r][sel_c]:
                    if pygame.K_1 <= e.key <= pygame.K_9:
                        val = e.key - pygame.K_0
                        current[sel_r][sel_c] = val
                        msg_text = ""
                    elif e.key in (pygame.K_0, pygame.K_BACKSPACE, pygame.K_DELETE):
                        current[sel_r][sel_c] = 0
                        msg_text = ""

                # Hint
                if e.key == pygame.K_h:
                    if hint_stage % 2 == 0:
                        placed = one_hint(current, solution, fixed_mask)
                        msg_text = "Hint: a correct number was revealed." if placed else "No hint available."
                    else:
                        msg_text = tip_text(current, solution)
                    hint_stage += 1

                # Auto-solve
                if e.key == pygame.K_l:
                    for r in range(9):
                        for c in range(9):
                            if not fixed_mask[r][c]:
                                current[r][c] = solution[r][c]
                    draw_grid(screen, (sel_r, sel_c), fixed_mask, current, "Auto-solved.")
                    pygame.display.flip()
                    _msg(screen, clock, "Auto-solved. Level completed!", ms=1000, color=GREEN)
                    if created_screen:
                        pygame.quit()
                    return "completed"

        # Lösung erreicht?
        if grid_equals(current, solution):
            draw_grid(screen, (sel_r, sel_c), fixed_mask, current, "Solved! Well done.")
            pygame.display.flip()
            _msg(screen, clock, "Solved! Well done.", ms=900, color=GREEN)
            if created_screen:
                pygame.quit()
            return "completed"

        draw_grid(screen, (sel_r, sel_c), fixed_mask, current, msg_text)
        pygame.display.flip()
        clock.tick(FPS)

    if created_screen:
        pygame.quit()
    return "back"