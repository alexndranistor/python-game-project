import pygame
import sys

# ---------- Setup ----------
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()

# Colors (placeholders until real art is ready)
BARREN_BG = (120, 100, 70)   # dull brown, represents the withered world
WHITE = (255, 255, 255)
HIGHLIGHT = (255, 215, 0)    # gold, for the selected menu option

# Fonts
title_font = pygame.font.SysFont(None, 64)
menu_font = pygame.font.SysFont(None, 40)

# ---------- Global game state ----------
game_state = "TITLE"           # tracks which "screen" we're on: TITLE, GAME, etc.
selected_option = 0            # 0 = New Game, 1 = Quit
menu_options = ["New Game", "Quit"]

def draw_title_screen():
    screen.fill(BARREN_BG)
    title_surface = title_font.render("MY GAME TITLE", True, WHITE)
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 150))
    screen.blit(title_surface, title_rect)
    for i, option in enumerate(menu_options):
        color = HIGHLIGHT if i == selected_option else WHITE
        option_surface = menu_font.render(option, True, color)
        option_rect = option_surface.get_rect(center=(SCREEN_WIDTH // 2, 300 + i * 60))
        screen.blit(option_surface, option_rect)


def handle_title_input(event):
    global selected_option, game_state
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP:
            selected_option = (selected_option - 1) % len(menu_options)
        elif event.key == pygame.K_DOWN:
            selected_option = (selected_option + 1) % len(menu_options)
        elif event.key == pygame.K_RETURN:
            if menu_options[selected_option] == "New Game":
                game_state = "GAME"
            elif menu_options[selected_option] == "Quit":
                pygame.quit()
                sys.exit()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif game_state == "TITLE":
            handle_title_input(event)

    if game_state == "TITLE":
        draw_title_screen()
    elif game_state == "GAME":
        screen.fill((30, 30, 30))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()      