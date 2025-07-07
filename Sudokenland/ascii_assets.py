from __future__ import annotations
import pygame

ASCII = {
    "queen": r"""
      .-^^-.
     /_/_\_\
      \___/
     ( o o )
      \_-_/
     /|   |\
    /_|___|_\
""",
    "dyskalkulo": r"""
    .------.
   / 9 8 7 \
  | 6 D 5  |
  | 4 K 3  |
   \_2_1_0_/
    /|\/|\
    \_|__/
""",
    "howard": r"""
   .------.
  |  o  o |
  |   __  |
  |  '--' |
   '------'
     /|\
    _/ \_
""",
    "howardice": r"""
   .------.
  |  o  o |
  |   ~~  |
  |  '--' |
   '------'
    \| |/
     / \
"""
}

def _get_mono(size: int) -> pygame.font.Font:
    for name in ["Courier New", "Consolas", "Menlo", "DejaVu Sans Mono", "monospace", "Courier"]:
        f = pygame.font.SysFont(name, size)
        if f:
            return f
    return pygame.font.SysFont(None, size)

def render_ascii_surface(ascii_str: str, size: int = 16, color=(255, 255, 255), bg=None) -> pygame.Surface:
    lines = [ln.rstrip("\n") for ln in ascii_str.strip("\n").splitlines()]
    font = _get_mono(size)
    line_h = font.get_height()
    max_w = max((font.size(ln)[0] for ln in lines), default=0)
    surf = pygame.Surface((max_w, line_h * len(lines)), pygame.SRCALPHA)
    if bg is not None:
        surf.fill(bg)
    y = 0
    for ln in lines:
        surf.blit(font.render(ln, True, color), (0, y))
        y += line_h
    return surf