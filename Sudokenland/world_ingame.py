## Here the world in which the game takes place (called Sudekenland) will be defined. It should
## be a connection of levels (the number piles) and the places inbetween those. It's also with integrated navigation
## and the documentation of the current status within the game.

# Datei: world_ingame.py
import pygame

def launch_world():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Sudokenland – The World")

    font = pygame.font.SysFont(None, 40)

    # Gelesenen Charakter anzeigen
    try:
        with open("selected_character.txt", "r") as f:
            character = f.read()
    except FileNotFoundError:
        character = "Unknown"

    running = True
    while running:
        screen.fill((50, 50, 80))
        text = font.render(f"You are: {character}", True, (255, 255, 255))
        screen.blit(text, (250, 250))

        info = font.render("World map coming soon...", True, (200, 200, 200))
        screen.blit(info, (200, 350))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()

    pygame.quit()
