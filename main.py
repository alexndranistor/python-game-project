"""
My Game - a narrative exploration game built with Pygame.

This file contains the game so far: the title screen, the opening
catastrophe dialogue, and the desert biome (with basic player movement).
The game uses a simple state machine (the `game_state` global variable) to
decide what to draw and which inputs to listen for each frame.
"""

import pygame
import sys

pygame.init()

# --- Display setup ----------------------------------------------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()

# --- Desert control hint (fades out after appearing) --------------------
previous_game_state = None       # Tracks the last frame's game_state, to detect state changes
desert_hint_start_time = 0       # Timestamp (ms) the player entered the desert room
HINT_VISIBLE_DURATION = 2000     # How long the control hint stays fully visible (ms)
HINT_FADE_DURATION = 1000        # How long it takes to fade out after that (ms)

# --- Colours (RGB tuples) ----------------------------------------------
BARREN_BG = (120, 100, 70)
WHITE = (255, 255, 255)
HIGHLIGHT = (255, 215, 0)
BLACK = (0, 0, 0)
DESERT_BG = (194, 178, 128)

# --- Fonts ---------------------------------------------------------------
title_font = pygame.font.SysFont(None, 64)
menu_font = pygame.font.SysFont(None, 40)
dialogue_font = pygame.font.SysFont(None, 32)
hint_font = pygame.font.SysFont(None, 20)

# --- Core state machine ----------------------------------------------------
# Valid values so far: "TITLE", "DIALOGUE", "DESERT_ROOM".
game_state = "TITLE"

# --- Title screen menu state -------------------------------------------------
selected_option = 0
menu_options = ["New Game", "Quit"]
menu_option_rects = []

# --- Player data -------------------------------------------------------------
PROTAGONIST_SIZE = 40   # Width/height in pixels of the protagonist's placeholder square
PLAYER_SPEED = 4         # Pixels moved per frame while a direction key is held

protagonist = {
    "name": "Protagonist",
    "x": SCREEN_WIDTH // 2,
    "y": SCREEN_HEIGHT // 2,
}

# --- Dialogue content ----------------------------------------------------------
CATASTROPHE_INTRO_TEXT = [
    "Long ago, this land was full of life and wonder.",
    "But a great catastrophe struck, and everything changed.",
    "You awaken to find the world forever different...",
]
# Note: the sprite's real first-appearance dialogue will be added in the
# next change, triggered by walking into the desert's decoy flower -
# rather than shown automatically here.

# --- Dialogue system state ---------------------------------------------------------
dialogue_lines = []
current_line_index = 0
revealed_chars = 0
text_reveal_speed = 30
last_reveal_time = 0
next_state_after_dialogue = "DESERT_ROOM"

# --- Desert biome placeholder text -------------------------------------------------
DESERT_ROOM_DESCRIPTION = (
    "The heat is immediate and overwhelming. Sand stretches in every "
    "direction, broken only by the occasional withered, thirsty-looking plant."
)

def draw_title_screen():
    """
    Draw the title screen: the game's title text and the New Game / Quit
    menu, highlighting whichever option is currently selected.
    """
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
    """
    Perform whatever should happen when a title-screen menu option is
    chosen, whether by keyboard (Enter) or mouse click.

    Args:
        option_name (str): The label of the chosen option, e.g. "New Game" or "Quit".
    """
    global game_state, dialogue_lines, current_line_index
    global revealed_chars, last_reveal_time, next_state_after_dialogue

    if option_name == "New Game":
        # Start the catastrophe intro. Once it finishes, drop straight
        # into the desert biome (no separate sprite-intro screen anymore).
        dialogue_lines = CATASTROPHE_INTRO_TEXT
        current_line_index = 0
        revealed_chars = 0
        last_reveal_time = pygame.time.get_ticks()
        next_state_after_dialogue = "DESERT_ROOM"
        game_state = "DIALOGUE"
    elif option_name == "Quit":
        pygame.quit()
        sys.exit()


def handle_title_input(event):
    """
    Handle a single Pygame event while the title screen is active, covering
    both keyboard navigation and mouse hover/click.

    Args:
        event (pygame.event.Event): The event to process.
    """
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


def wrap_text(text, font, max_width):
    """
    Split a string of text into a list of lines, each narrow enough to fit
    within max_width pixels when rendered in the given font.

    Args:
        text (str): The text to wrap.
        font (pygame.font.Font): The font the text will be rendered in.
        max_width (int): The maximum width, in pixels, a single line may occupy.

    Returns:
        list[str]: The text split into wrapped lines.
    """
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
    """
    Draw the scrolling dialogue box at the bottom of the screen, containing
    the given text (wrapped to fit inside the box), plus a small hint
    telling the player how to advance the dialogue.

    Args:
        text (str): The (possibly partially revealed) text to display.
    """
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

    hint_surface = hint_font.render("Press SPACE to continue", True, (180, 180, 180))
    hint_rect = hint_surface.get_rect(bottomright=(box_rect.right - 15, box_rect.bottom - 10))
    screen.blit(hint_surface, hint_rect)


def update_text_reveal():
    """
    Advance the typewriter-style text reveal by one character, if enough
    time has passed since the last character was revealed.
    """
    global revealed_chars, last_reveal_time
    current_time = pygame.time.get_ticks()
    current_line = dialogue_lines[current_line_index]

    if revealed_chars < len(current_line):
        if current_time - last_reveal_time >= text_reveal_speed:
            revealed_chars += 1
            last_reveal_time = current_time

def handle_dialogue_input(event):
    """
    Handle player input while a dialogue text box is active. Both
    pressing Enter/Space and left-clicking the mouse advance the dialogue.

    Args:
        event (pygame.event.Event): The event to process.
    """
    global current_line_index, revealed_chars, game_state

    key_pressed = event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE)
    mouse_clicked = event.type == pygame.MOUSEBUTTONDOWN and event.button == 1

    if key_pressed or mouse_clicked:
        current_line = dialogue_lines[current_line_index]

        if revealed_chars < len(current_line):
            revealed_chars = len(current_line)
        else:
            current_line_index += 1
            revealed_chars = 0
            if current_line_index >= len(dialogue_lines):
                game_state = next_state_after_dialogue


def handle_desert_movement():
    """
    Update the protagonist's position based on which movement keys are
    currently held down (arrow keys or WASD), keeping them fully on-screen.
    """
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        protagonist["x"] -= PLAYER_SPEED
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        protagonist["x"] += PLAYER_SPEED
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        protagonist["y"] -= PLAYER_SPEED
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        protagonist["y"] += PLAYER_SPEED

    half_size = PROTAGONIST_SIZE // 2
    protagonist["x"] = max(half_size, min(SCREEN_WIDTH - half_size, protagonist["x"]))
    protagonist["y"] = max(half_size, min(SCREEN_HEIGHT - half_size, protagonist["y"]))


def draw_desert_room():
    """
    Draw the desert biome: a sandy background, a short description of the
    surroundings, the protagonist at their current position, and a
    fading movement-control hint if it's still within its display window.
    """
    screen.fill(DESERT_BG)

    max_text_width = SCREEN_WIDTH - 100
    wrapped_lines = wrap_text(DESERT_ROOM_DESCRIPTION, dialogue_font, max_text_width)
    line_height = dialogue_font.get_linesize()

    for i, line in enumerate(wrapped_lines):
        line_surface = dialogue_font.render(line, True, BLACK)
        line_rect = line_surface.get_rect(topleft=(50, 50 + i * line_height))
        screen.blit(line_surface, line_rect)

    protagonist_rect = pygame.Rect(0, 0, PROTAGONIST_SIZE, PROTAGONIST_SIZE)
    protagonist_rect.center = (protagonist["x"], protagonist["y"])
    pygame.draw.rect(screen, WHITE, protagonist_rect)

    draw_control_hint()


def draw_control_hint():
    """
    Draw a temporary "Use ARROW KEYS or WASD to move" prompt near the
    bottom of the desert room, shown briefly when the player first
    arrives and then fading out - similar to the on-screen control
    reminders most games show when you enter a new area.
    """
    elapsed = pygame.time.get_ticks() - desert_hint_start_time
    total_duration = HINT_VISIBLE_DURATION + HINT_FADE_DURATION

    if elapsed >= total_duration:
        return  # The hint has fully finished; nothing left to draw.

    if elapsed <= HINT_VISIBLE_DURATION:
        alpha = 255  # Fully visible
    else:
        # Linearly fade from fully visible (255) down to invisible (0).
        fade_elapsed = elapsed - HINT_VISIBLE_DURATION
        alpha = max(0, 255 - int((fade_elapsed / HINT_FADE_DURATION) * 255))

    hint_surface = menu_font.render("Use ARROW KEYS or WASD to move", True, WHITE)
    hint_surface.set_alpha(alpha)
    hint_rect = hint_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
    screen.blit(hint_surface, hint_rect)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif game_state == "TITLE":
            handle_title_input(event)
        elif game_state == "DIALOGUE":
            handle_dialogue_input(event)

    # Detect the exact frame the player arrives in the desert room, so the
    # control hint's fade timer starts from the correct moment.
    if game_state == "DESERT_ROOM" and previous_game_state != "DESERT_ROOM":
        desert_hint_start_time = pygame.time.get_ticks()
    previous_game_state = game_state

    if game_state == "TITLE":
        draw_title_screen()
    elif game_state == "DIALOGUE":
        update_text_reveal()
        screen.fill(BARREN_BG)
        current_line = dialogue_lines[current_line_index]
        draw_text_box(current_line[:revealed_chars])
    elif game_state == "DESERT_ROOM":
        handle_desert_movement()
        draw_desert_room()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()



