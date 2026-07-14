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
BLACK = (0, 0, 0)

title_font = pygame.font.SysFont(None, 64)
menu_font = pygame.font.SysFont(None, 40)
dialogue_font = pygame.font.SysFont(None, 32)

game_state = "TITLE"
selected_option = 0
menu_options = ["New Game", "Quit"]
menu_option_rects = []

protagonist = {
    "name": "Protagonist",
    "x": SCREEN_WIDTH // 2,
    "y": SCREEN_HEIGHT // 2,
}

CATASTROPHE_INTRO_TEXT = [
    "Long ago, this land was full of life and wonder.",
    "But a great catastrophe struck, and everything changed.",
    "You awaken to find the world forever different...",
]

SPRITE_INTRO_TEXT = [
    "A tiny light flickers in front of you, and a small voice pipes up.",
    "\"Oh! You're awake. Finally, someone worth talking to around here.\"",
    "\"I'm your guide now, whether you like it or not. Call me Sprite.\"",
    "\"That magic humming under your skin? That's no accident, dear.\"",
    "\"Come on then. Let's see what you're made of.\"",
]

dialogue_lines = []
current_line_index = 0
revealed_chars = 0
text_reveal_speed = 30
last_reveal_time = 0
next_state_after_dialogue = "GAME"

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
    global game_state, dialogue_lines, current_line_index
    global revealed_chars, last_reveal_time, next_state_after_dialogue

    if option_name == "New Game":
        dialogue_lines = CATASTROPHE_INTRO_TEXT
        current_line_index = 0
        revealed_chars = 0
        last_reveal_time = pygame.time.get_ticks()
        next_state_after_dialogue = "SPRITE_INTRO_START"
        game_state = "DIALOGUE"
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


def draw_game_screen():
    screen.fill((30, 30, 30))

    protagonist_rect = pygame.Rect(0, 0, 40, 40)
    protagonist_rect.center = (protagonist["x"], protagonist["y"])
    pygame.draw.rect(screen, WHITE, protagonist_rect)

    name_surface = menu_font.render(protagonist["name"], True, WHITE)
    name_rect = name_surface.get_rect(center=(protagonist["x"], protagonist["y"] - 40))
    screen.blit(name_surface, name_rect)

def wrap_text(text, font, max_width):
    words = text.split(" ")
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line.rstrip())
            current_line = word + " "

    if current_line:
        lines.append(current_line.rstrip())

    return lines



def draw_text_box(text):
    box_rect = pygame.Rect(50, 420, SCREEN_WIDTH - 100, 150)
    pygame.draw.rect(screen, BLACK, box_rect)
    pygame.draw.rect(screen, WHITE, box_rect, 3)

    max_text_width = box_rect.width - 40
    wrapped_lines = wrap_text(text, dialogue_font, max_text_width)
    line_height = dialogue_font.get_linesize()

    for i, line in enumerate(wrapped_lines):
        line_surface = dialogue_font.render(line, True, WHITE)
        line_rect = line_surface.get_rect(topleft=(box_rect.x + 20, box_rect.y + 20 + i * line_height))
        screen.blit(line_surface, line_rect)





def update_text_reveal():
    global revealed_chars, last_reveal_time
    current_time = pygame.time.get_ticks()
    current_line = dialogue_lines[current_line_index]

    if revealed_chars < len(current_line):
        if current_time - last_reveal_time >= text_reveal_speed:
            revealed_chars += 1
            last_reveal_time = current_time

def handle_dialogue_input(event):
    global current_line_index, revealed_chars, game_state

    if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
        current_line = dialogue_lines[current_line_index]
        if revealed_chars < len(current_line):
            revealed_chars = len(current_line)
        else:
            current_line_index += 1
            revealed_chars = 0
            if current_line_index >= len(dialogue_lines):
                game_state = next_state_after_dialogue

def start_sprite_intro():
    global dialogue_lines, current_line_index, revealed_chars
    global last_reveal_time, next_state_after_dialogue, game_state

    dialogue_lines = SPRITE_INTRO_TEXT
    current_line_index = 0
    revealed_chars = 0
    last_reveal_time = pygame.time.get_ticks()
    next_state_after_dialogue = "GAME"
    game_state = "DIALOGUE"

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif game_state == "TITLE":
            handle_title_input(event)
        elif game_state == "DIALOGUE":
            handle_dialogue_input(event)

    if game_state == "SPRITE_INTRO_START":
        start_sprite_intro()

    if game_state == "TITLE":
        draw_title_screen()
    elif game_state == "DIALOGUE":
        update_text_reveal()
        screen.fill(BARREN_BG)
        current_line = dialogue_lines[current_line_index]
        draw_text_box(current_line[:revealed_chars])
    elif game_state == "GAME":
        draw_game_screen()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()



