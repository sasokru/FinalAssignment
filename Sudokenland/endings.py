import pygame
import sys
import os
import random
import math

# ---------- Paths & Font ----------
ROOT = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(ROOT, "Assets", "fonts", "PressStart2P-Regular.ttf")

# ---------- Visuals ----------
WIDTH, HEIGHT = 800, 600
BG = (8, 10, 28)
WHITE = (255, 255, 255)

NUMBER_WORDS = ["zero","one","two","three","four","five","six","seven","eight","nine"]

# ---------- Simple portraits (matching the style you used) ----------
def draw_queen(surface, x, y):
    pygame.draw.rect(surface, (80,40,100), (x, y, 150, 180), border_radius=16)
    pygame.draw.circle(surface, (240,220,255), (x+75, y+60), 32)
    pygame.draw.polygon(surface, (255,215,0), [(x+45,y+20),(x+75,y),(x+105,y+20)])
    pygame.draw.rect(surface, (230,210,240), (x+55, y+95, 40, 60), border_radius=6)
    for ang in range(0,360,30):
        v = pygame.math.Vector2(1,0).rotate(ang)
        px = x+75 + int(58*v.x); py = y+60 + int(58*v.y)
        pygame.draw.circle(surface, (255,180,200), (px, py), 4)

def draw_confetti_banner(surface, y):
    # deko unter der headline
    for i in range(16):
        x = 60 + i*46
        col = (random.randint(150,255), random.randint(120,255), random.randint(120,255))
        pygame.draw.rect(surface, col, (x, y, 24, 6), border_radius=3)

# ---------- Particle System ----------
class Particle:
    __slots__ = ("x","y","vx","vy","life","col")
    def __init__(self, x, y, speed, angle, col):
        self.x = x; self.y = y
        self.vx = speed * math.cos(angle)
        self.vy = speed * math.sin(angle)
        self.life = random.randint(45, 70)  # frames
        self.col = col

    def update(self):
        self.vy += 0.06           # gravity
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        return self.life > 0

    def draw(self, surf):
        if self.life > 0:
            pygame.draw.circle(surf, self.col, (int(self.x), int(self.y)), 2)

class Firework:
    def __init__(self):
        self.x = random.randint(120, WIDTH-120)
        self.y = HEIGHT + 10
        self.vy = -random.uniform(5.2, 6.6)
        self.color = (random.randint(170,255), random.randint(100,220), random.randint(120,255))
        self.exploded = False
        self.particles = []

    def update(self):
        if not self.exploded:
            self.y += self.vy
            self.vy += 0.05  # slows up
            # explode near top third
            if self.vy > -0.2 or self.y < random.randint(120, 220):
                self.explode()
        else:
            self.particles[:] = [p for p in self.particles if p.update()]
        return (not self.exploded) or len(self.particles) > 0

    def explode(self):
        self.exploded = True
        cnt = random.randint(55, 85)
        for i in range(cnt):
            ang = (i / cnt) * 2*math.pi + random.uniform(-0.2, 0.2)
            spd = random.uniform(2.2, 4.5)
            col = (min(255, self.color[0]+random.randint(-30, 30)),
                   min(255, self.color[1]+random.randint(-30, 30)),
                   min(255, self.color[2]+random.randint(-30, 30)))
            self.particles.append(Particle(self.x, self.y, spd, ang, col))

    def draw(self, surf):
        if not self.exploded:
            pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), 3)
        for p in self.particles:
            p.draw(surf)

def show_fireworks():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Sudokenland – Celebration")
    try:
        title_font = pygame.font.Font(FONT_PATH, 22)
        body_font  = pygame.font.Font(FONT_PATH, 16)
    except Exception:
        title_font = pygame.font.SysFont("Courier New", 22)
        body_font  = pygame.font.SysFont("Courier New", 16)

    clock = pygame.time.Clock()

    fireworks = []
    spawn_timer = 0
    max_rockets = 9   # nicht zu pro, aber hübsch
    launched = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                running = False

        screen.fill(BG)

        # portraits (links/rechts)
        draw_queen(screen, 30, 360)

        # (kleiner goldener Rahmen rechts – symbolisch für „befreite Käfige“)
        pygame.draw.rect(screen, (220, 180, 60), (WIDTH-190, 360, 150, 180), width=3, border_radius=16)

        # headline & text
        title = title_font.render("ALL NUMBERS ARE FREE!", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 40))
        draw_confetti_banner(screen, 72)

        lines = [
            "QUEEN LEGASTHENIA THANKS YOU, HERO.",
            "THE KINGDOM REJOICES AS ZERO TO NINE RETURN.",
            "LET LETTERS AND NUMBERS LIVE IN HARMONY!",
            "PRESS ENTER TO CONTINUE."
        ]
        y = 110
        for ln in lines:
            surf = body_font.render(ln, True, (210, 210, 230))
            screen.blit(surf, (WIDTH//2 - surf.get_width()//2, y))
            y += 28

        # fireworks
        spawn_timer -= 1
        if spawn_timer <= 0 and launched < max_rockets:
            fireworks.append(Firework())
            launched += 1
            spawn_timer = random.randint(14, 24)

        fireworks[:] = [fw for fw in fireworks if fw.update()]
        for fw in fireworks:
            fw.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

# Quick test if you run this file directly:
if __name__ == "__main__":
    show_fireworks()