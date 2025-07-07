##
## As the name says, here I will write the code that shows the differenet characters (male and female version of the inventor of Sudoku)
## who was called Howard Garns. The character will be Howard or Howardice and the player must choose, so the choice will be daved for
## the rest of the game.

import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Choose Your Character")

# 🎨 Nintendo-Style Font laden
font_path = "Assets/fonts/PressStart2P-Regular.ttf"
font = pygame.font.Font(font_path, 18)  # 18 ist besser lesbar für diesen Font
clock = pygame.time.Clock()

# Charaktere
characters = ["Howard", "Howardese"]
selected_index = 0


def draw_screen():
    screen.fill((20, 20, 20))

    # Titeltext
    title = font.render("CHOOSE YOUR CHARACTER", True, (255, 255, 255))
    screen.blit(title, (70, 80))

    # Charakteroptionen anzeigen
    for i, name in enumerate(characters):
        # Ausgewählter Charakter → Rot, andere Grau
        color = (255, 0, 0) if i == selected_index else (200, 200, 200)
        text = font.render(name, True, color)
        screen.blit(text, (300, 250 + i * 60))

    # Hinweis unten
    prompt = font.render("USE ARROWS | ENTER TO SELECT", True, (150, 150, 150))
    screen.blit(prompt, (80, 520))


def choose_character():
    global selected_index
    choosing = True
    while choosing:
        draw_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(characters)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(characters)
                elif event.key == pygame.K_RETURN:
                    chosen = characters[selected_index]
                    print("You chose:", chosen)

                    # Speichere die Auswahl in einer Datei
                    with open("selected_character.txt", "w") as f:
                        f.write(chosen)

                    choosing = False  # Fenster schließen → zurück zum Hauptspiel

        pygame.display.flip()
        clock.tick(60)
