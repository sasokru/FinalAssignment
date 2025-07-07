## There will be around 10 levels (for the number 0-9), that have different levels of difficulty.
## I plan on using JSON- Files to load and create Sudoku boards. Also, the results must be saved here.

# I plan on doing so by creating lists in a sudoku arrangement.

# File: levels/level_management.py
# Datei: levels/level_management.py
import pygame
import sys
from sudoku import start_sudoku   # ✅ Import Sudoku

WIDTH, HEIGHT = 800, 600
BG = (10, 10, 25)
TEXT = (255, 255, 255)
DIM = (180, 180, 200)

def load_level(level_number: int):
    """Platzhalter: zeigt einen einfachen Level-Screen und startet Sudoku mit ENTER."""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(f"Level {level_number}")

    font_path = "Assets/fonts/PressStart2P-Regular.ttf"
    font = pygame.font.Font(font_path, 22)
    small = pygame.font.Font(font_path, 16)

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # ESC zurück zur Weltkarte
                if event.key == pygame.K_ESCAPE:
                    running = False
                # ENTER startet Sudoku
                if event.key == pygame.K_RETURN:
                    start_sudoku(level_number)

        screen.fill(BG)
        title = font.render(f"LEVEL {level_number}", True, TEXT)
        screen.blit(title, (280, 220))

        hint = small.render("ENTER = Start Sudoku | ESC = Back to World", True, DIM)
        screen.blit(hint, (100, 300))

        pygame.display.flip()
        clock.tick(60)

    # zurück zur Weltkarte
    return
