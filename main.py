import pygame
import sys

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()

BARREN_BG = (120, 100, 70)
WHITE = (255, 255, 255)
HIGHLIGHT = (255, 215, 0)

title_font = pygame.font.SysFont(None, 64)
menu_font = pygame.font.SysFont(None, 40)

game_state = "TITLE"
selected_option = 0
menu_options = ["New Game", "Quit"]
menu_option_rects = []

def draw_title_screen():
    global menu_option_rects
    screen.fill(BARREN_BG)

    title_surface = title_font.render("MY GAME TITLE", True, WHITE)
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 150))
    screen.blit(title_surface, title_rect)

    menu_option_rects = []
    for i, option in enumerate(menu_options):
        color = HIGHLIGHT if i == selected_option else WHITE
        option_surface = menu_font.render(option, True, color)
        option_rect = option_surface.get_rect(center=(SCREEN_WIDTH // 2, 300 + i * 60))
        screen.blit(option_surface, option_rect)
        menu_option_rects.append(option_rect)

def activate_menu_option(option_name):
    global game_state
    if option_name == "New Game":
        game_state = "GAME"
    elif option_name == "Quit":
        pygame.quit()
        sys.exit()

def handle_title_input(event):
    global selected_option
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP:
            selected_option = (selected_option - 1) % len(menu_options)
        elif event.key == pygame.K_DOWN:
            selected_option = (selected_option + 1) % len(menu_options)
        elif event.key == pygame.K_RETURN:
            activate_menu_option(menu_options[selected_option])
    elif event.type == pygame.MOUSEMOTION:
        for i, rect in enumerate(menu_option_rects):
            if rect.collidepoint(event.pos):
                selected_option = i
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for i, rect in enumerate(menu_option_rects):
            if rect.collidepoint(event.pos):
                activate_menu_option(menu_options[i])

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

