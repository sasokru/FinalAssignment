## This is the file where it all comes together hopefully.
import json
from pathlib import Path
from typing import Optional
import pygame
from ascii_assets import ASCII, render_ascii_surface

#Paths
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "Assets"
DATA_DIR = ASSETS_DIR / "data"
FONTS_DIR = ASSETS_DIR / "fonts"
FONT_PATH = FONTS_DIR / "PressStart2P-Regular.ttf"  # fallback to system font if missing

#Layout

WIDTH, HEIGHT = 1280, 720
FPS = 60

BLACK  = (0, 0, 0)
WHITE  = (255, 255, 255)
GRAY   = (120, 120, 120)
YELLOW = (240, 220, 0)
GREEN  = (0, 200, 120)
RED    = (210, 70, 70)
BLUE   = (80, 140, 220)

# Save files
PROGRESS_FILE = DATA_DIR / "progress.json"
SELECTED_FILE = BASE_DIR / "selected_character.txt"

# ---------- Helpers ----------
def load_font(size: int) -> pygame.font.Font:
    if FONT_PATH.exists():
        try:
            return pygame.font.Font(str(FONT_PATH), size)
        except Exception:
            pass
    return pygame.font.SysFont("Arial", size)

def draw_centered_text(surface, text: str, y: int, font: pygame.font.Font, color=WHITE):
    txt = font.render(text, True, color)
    rect = txt.get_rect(center=(WIDTH // 2, y))
    surface.blit(txt, rect)

def save_progress(unlocked_until: int):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump({"unlocked_until": int(unlocked_until)}, f)

def load_progress() -> int:
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return int(data.get("unlocked_until", 0))
    except FileNotFoundError:
        return 0

def save_selected_character(name: str):
    with open(SELECTED_FILE, "w", encoding="utf-8") as f:
        f.write(name)

def load_selected_character() -> Optional[str]:
    try:
        val = SELECTED_FILE.read_text(encoding="utf-8").strip()
        return val or None
    except FileNotFoundError:
        return None

def available_level_files() -> list[int]:
    """Return list of level indices for which a JSON file exists (0..9 expected)."""
    levels = []
    for i in range(10):
        if (DATA_DIR / f"level_{i}.json").exists():
            levels.append(i)
    return levels

def reset_all_progress():
    """Setzt Spielfortschritt zurück und löscht die Charakterwahl."""
    try:
        PROGRESS_FILE.unlink()
    except FileNotFoundError:
        pass
    try:
        SELECTED_FILE.unlink()
    except FileNotFoundError:
        pass
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump({"unlocked_until": 0}, f)

def confirm_prompt(screen, clock, question: str) -> bool:
    """Zeigt eine Y/N-Bestätigung. True = Ja."""
    big = load_font(24)
    small = load_font(16)
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_y, pygame.K_RETURN):
                    return True
                if e.key in (pygame.K_n, pygame.K_ESCAPE):
                    return False
        screen.fill(BLACK)
        draw_centered_text(screen, question, HEIGHT//2 - 10, big, YELLOW)
        draw_centered_text(screen, "(Y)es  /  (N)o", HEIGHT//2 + 26, small, GRAY)
        pygame.display.flip()
        clock.tick(FPS)

# Queen messages
def get_queen_message(level_index: int) -> str:
    """Exact, level-specific lines for 0..8. Level 9 goes straight to ending."""
    messages = {
        0: "Well done! The first digit returns to the realm.",
        1: "Strong one! Order grows stronger in Sudokenland.",
        2: "Twogether we can do this. Dyskalkulo trembles.",
        3: "Threelling! The scribes can count again.",
        4: "FourEver four the numbers!",
        5: "Give me five!",
        6: "Sixy save!",
        7: "Seven- almost there! Even Dyskalkulo must admire that solve.",
        8: "Greight job!",
    }
    return messages.get(level_index, "Well done!")

# ---------- Screens ----------
def screen_title(screen, clock):
    big = load_font(48)
    small = load_font(20)
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return "quit"
                if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    return "character_select"
                if e.key == pygame.K_r:
                    if confirm_prompt(screen, clock, "Reset all progress and start a new game?"):
                        reset_all_progress()
                        msg_screen(screen, clock, "Progress reset.", 900, GREEN)
                        return "character_select"

        screen.fill(BLACK)
        draw_centered_text(screen, "SUDOKENLAND", HEIGHT//2 - 70, big, YELLOW)
        draw_centered_text(screen, "Press ENTER", HEIGHT//2 + 10, small)
        draw_centered_text(screen, "ESC: quit  ·  R: reset progress", HEIGHT//2 + 45, small, GRAY)
        pygame.display.flip()
        clock.tick(FPS)

def screen_character_select(screen, clock):
    title = load_font(28)
    small = load_font(16)
    label = load_font(14)
    index = 0
    names = ["Howard", "Howardice"]

    asc_howard = render_ascii_surface(ASCII["howard"], size=16)
    asc_howardice = render_ascii_surface(ASCII["howardice"], size=16)

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit", None
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return "title", None
                if e.key in (pygame.K_LEFT, pygame.K_a):
                    index = (index - 1) % 2
                if e.key in (pygame.K_RIGHT, pygame.K_d):
                    index = (index + 1) % 2
                if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    save_selected_character(names[index])
                    return "story", names[index]

        screen.fill(BLACK)
        draw_centered_text(screen, "Choose your hero", 60, title, YELLOW)

        card_w, card_h = 320, 340
        gap = 80
        x0 = WIDTH//2 - card_w - gap//2
        y0 = 120
        x1 = WIDTH//2 + gap//2

        pygame.draw.rect(screen, (45, 60, 100) if index == 0 else (30, 30, 30),
                         (x0, y0, card_w, card_h), border_radius=14)
        r_h = asc_howard.get_rect(center=(x0 + card_w//2, y0 + 160))
        screen.blit(asc_howard, r_h)
        nm1 = label.render("Howard", True, WHITE)
        screen.blit(nm1, nm1.get_rect(center=(x0 + card_w//2, y0 + card_h - 24)))

        pygame.draw.rect(screen, (45, 60, 100) if index == 1 else (30, 30, 30),
                         (x1, y0, card_w, card_h), border_radius=14)
        r_hi = asc_howardice.get_rect(center=(x1 + card_w//2, y0 + 160))
        screen.blit(asc_howardice, r_hi)
        nm2 = label.render("Howardice", True, WHITE)
        screen.blit(nm2, nm2.get_rect(center=(x1 + card_w//2, y0 + card_h - 24)))

        draw_centered_text(screen, "←/→ choose · ENTER confirm · ESC back", HEIGHT-30, small, GRAY)
        pygame.display.flip()
        clock.tick(FPS)

def screen_story(screen, clock, selected_name: str):
    big = load_font(24)
    small = load_font(16)
    label = load_font(14)

    text_lines = [
        "Hero, the land of Sudokenland needs your cleverness.",
        "The villain Dyskalkulo stole all numbers and locked them away.",
        "Queen Legasthenia begs for your help to restore order.",
        "For each Sudoku you solve, one number (0-9) is freed."
    ]
    ask = "Will you help?  (Y)es / (N)o"

    asc_queen = render_ascii_surface(ASCII["queen"], size=16)
    asc_villain = render_ascii_surface(ASCII["dyskalkulo"], size=16)

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit", False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return "title", False
                if e.key == pygame.K_y:
                    return "world", True
                if e.key == pygame.K_n:
                    msg_screen(screen, clock, "You are not feeling well. The world is turning... You black out.", 4000)
                    return "title", False

        screen.fill(BLACK)
        draw_centered_text(screen, f"Queen Legasthenia speaks to {selected_name}:", 60, big, YELLOW)

        r_q = asc_queen.get_rect(center=(WIDTH//2 - 260, 190))
        screen.blit(asc_queen, r_q)
        cap_q = label.render("Queen Legasthenia", True, WHITE)
        screen.blit(cap_q, cap_q.get_rect(center=(WIDTH//2 - 260, r_q.bottom + 14)))

        r_v = asc_villain.get_rect(center=(WIDTH//2 + 260, 190))
        screen.blit(asc_villain, r_v)
        cap_v = label.render("Dyskalkulo", True, WHITE)
        screen.blit(cap_v, cap_v.get_rect(center=(WIDTH//2 + 260, r_v.bottom + 14)))

        y = 320
        for line in text_lines:
            draw_centered_text(screen, line, y, small)
            y += 28

        draw_centered_text(screen, ask, HEIGHT-60, small, GREEN)
        draw_centered_text(screen, "ESC back to title", HEIGHT-30, small, GRAY)
        pygame.display.flip()
        clock.tick(FPS)

def msg_screen(screen, clock, message: str, ms: int = 1200, color=WHITE):
    small = load_font(16)
    start = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start < ms:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return
        screen.fill(BLACK)
        draw_centered_text(screen, message, HEIGHT//2, small, color)
        pygame.display.flip()
        clock.tick(FPS)

def screen_world_map(screen, clock, unlocked_until: int):
    """World map with clamped movement up to the unlocked level.
       Free play (choose any) only after all 10 digits are freed."""
    title = load_font(28)
    small = load_font(16)
    node_font = load_font(20)

    levels = available_level_files()
    if not levels:
        msg_screen(screen, clock, "No level JSON files found in Assets/data.", 1800, RED)
        return "title", None

    # Clamp movement:
    free_play = unlocked_until >= 10
    max_selectable = max(levels) if free_play else min(max(levels), unlocked_until)
    index = min(max_selectable, max(0, min(unlocked_until, max(levels))))

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit", None
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return "title", None
                if e.key in (pygame.K_LEFT, pygame.K_a):
                    index = max(0, index - 1)
                if e.key in (pygame.K_RIGHT, pygame.K_d):
                    index = min(max_selectable, index + 1)  # hard clamp
                if e.key == pygame.K_r:
                    if confirm_prompt(screen, clock, "Reset progress and return to title?"):
                        reset_all_progress()
                        msg_screen(screen, clock, "Progress reset.", 900, GREEN)
                        return "title", None
                if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if index not in levels:
                        msg_screen(screen, clock, f"Missing file: level_{index}.json", 1500, RED)
                    elif (not free_play) and index > unlocked_until:
                        msg_screen(screen, clock, f"Level {index} is locked. Solve {unlocked_until} first.", 1500, RED)
                    else:
                        return "run_level", index

        screen.fill(BLACK)
        draw_centered_text(screen, "World Map — free all numbers", 70, title, YELLOW)

        # Draw 10 nodes (0..9)
        start_x = 120
        step = (WIDTH - 240) // 9
        y = HEIGHT // 2

        for i in range(10):
            x = start_x + i * step

            # Ring color by progression
            if free_play:
                ring_color = GREEN if i in levels else GRAY
            else:
                if i < unlocked_until:
                    ring_color = GREEN       # already completed
                elif i == unlocked_until:
                    ring_color = YELLOW      # next playable
                else:
                    ring_color = GRAY        # locked

            # Selection ring
            if i == index:
                pygame.draw.circle(screen, YELLOW, (x, y), 28)

            # Node ring
            pygame.draw.circle(screen, ring_color, (x, y), 22, width=3)

            # Digit label
            lbl_color = WHITE if i in levels else (100, 100, 100)
            label = node_font.render(str(i), True, lbl_color)
            r = label.get_rect(center=(x, y))
            screen.blit(label, r)

        # HUD info
        if free_play:
            draw_centered_text(screen, "All digits are free — replay any level!", HEIGHT - 96, small, GREEN)
        else:
            draw_centered_text(screen, f"Next playable: Level {unlocked_until}", HEIGHT - 96, small, WHITE)

        draw_centered_text(screen, "←/→ choose level · ENTER start", HEIGHT - 64, small, WHITE)
        draw_centered_text(screen, "ESC: back to title · R: reset progress", HEIGHT - 32, small, GRAY)

        pygame.display.flip()
        clock.tick(FPS)

def screen_level_done(screen, clock, level_index: int):
    """Short celebration screen after levels 0..8."""
    small = load_font(18)
    big = load_font(28)
    queen_line = get_queen_message(level_index)
    t0 = pygame.time.get_ticks()
    while pygame.time.get_ticks() - t0 < 1600:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return
        screen.fill(BLACK)
        draw_centered_text(screen, f"Level {level_index} done!", HEIGHT//2 - 28, big, GREEN)
        draw_centered_text(screen, f"Queen: {queen_line}", HEIGHT//2 + 16, small, YELLOW)
        pygame.display.flip()
        clock.tick(FPS)

def screen_ending(screen, clock):
    """Final fireworks, then epilog text, then back to title."""
    big = load_font(30)
    small = load_font(18)

    # --- Phase 1: Fireworks + Queen line ---
    particles = [[WIDTH//2, HEIGHT//2, i*4, (i*17)%WIDTH, (i*23)%HEIGHT] for i in range(120)]
    t0 = pygame.time.get_ticks()
    while pygame.time.get_ticks() - t0 < 2800:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
        screen.fill(BLACK)
        draw_centered_text(screen, "All numbers are free!", 90, big, GREEN)
        draw_centered_text(screen, "Queen: Magnificent! All digits are free — thank you, hero!", 130, small, YELLOW)
        for _, p in enumerate(particles):
            pygame.draw.circle(screen, (255, 255, 255), (p[3], p[4]), 2)
        pygame.display.flip()
        clock.tick(FPS)

    # kurze Schwarzblende
    fade_ms = 350
    t1 = pygame.time.get_ticks()
    while pygame.time.get_ticks() - t1 < fade_ms:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
        screen.fill(BLACK)
        pygame.display.flip()
        clock.tick(FPS)

    # --- Phase 2: Epilog ---
    epilog_lines = [
        "You feel happy, but dizzy suddenly.",
        "The world starts turning in front of your eyes and you faint.",
    ]
    show_ms = 5000
    t2 = pygame.time.get_ticks()
    while pygame.time.get_ticks() - t2 < show_ms:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
        screen.fill(BLACK)
        draw_centered_text(screen, epilog_lines[0], HEIGHT//2 - 14, small, WHITE)
        draw_centered_text(screen, epilog_lines[1], HEIGHT//2 + 14, small, WHITE)
        pygame.display.flip()
        clock.tick(FPS)

    return "title"


# ---------- Sudoku integration ----------
def run_sudoku_level(level_index: int) -> str:
    """
    Delegate to sudoku.start_sudoku(level_index, DATA_DIR)
    Returns:
      - "completed" -> solved successfully
      - "back"      -> E pressed (back to map)
      - "quit"      -> ESC pressed (quit game)
    """
    from sudoku import start_sudoku  # local import avoids circular imports
    try:
        result = start_sudoku(level_index, str(DATA_DIR))
        return result if result in {"completed", "back", "quit"} else "back"
    except Exception as exc:
        print("[Sudokenland] Error running sudoku:", exc)
        return "back"

#Main Loop
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Sudokenland")
    clock = pygame.time.Clock()

    state = "title"
    selected = load_selected_character() or "Hero"
    unlocked_until = load_progress()  # default 0

    running = True
    while running:
        if state == "title":
            nxt = screen_title(screen, clock)
            if nxt == "quit":
                running = False
            else:
                state = "character_select"

        elif state == "character_select":
            nxt, selected = screen_character_select(screen, clock)
            if nxt == "quit":
                running = False
            elif nxt == "title":
                state = "title"
            else:
                state = "story"

        elif state == "story":
            nxt, accepted = screen_story(screen, clock, selected or "Hero")
            if nxt == "quit":
                running = False
            elif nxt == "title":
                state = "title"
            else:
                state = "world" if accepted else "title"

        elif state == "world":
            nxt, payload = screen_world_map(screen, clock, unlocked_until)
            if nxt == "quit":
                running = False
            elif nxt == "title":
                state = "title"
            elif nxt == "run_level":
                level_index = int(payload)
                result = run_sudoku_level(level_index)
                if result == "quit":
                    running = False
                elif result == "completed":
                    if level_index == 9:
                        # finale: directly to ending, no level-done screen
                        unlocked_until = 10
                        save_progress(unlocked_until)
                        state = "ending"
                    else:
                        screen_level_done(screen, clock, level_index)
                        unlocked_until = min(10, max(unlocked_until, level_index + 1))
                        save_progress(unlocked_until)
                        state = "world"
                else:  # "back"
                    state = "world"
            else:
                state = "title"

        elif state == "ending":
            nxt = screen_ending(screen, clock)
            if nxt == "quit":
                running = False
            else:
                state = "title"

        else:
            running = False

        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()