"""
My Game - a narrative exploration game built with Pygame.

This file contains the game so far: the title screen, the opening dialogue
sequence (the catastrophe intro and the sprite's introduction), and a
placeholder desert biome room. The game uses a simple state machine (the
`game_state` global variable) to decide what to draw and which inputs to
listen for each frame.
"""

import pygame
import sys

# Initialise all of Pygame's internal modules (fonts, display, etc.).
# This must be called before creating the window or fonts.
pygame.init()

# --- Display setup ----------------------------------------------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("My Game")

# Controls the game's frame rate (see clock.tick(60) in the main loop).
clock = pygame.time.Clock()

# --- Colours (RGB tuples) ----------------------------------------------
BARREN_BG = (120, 100, 70)   # Dry, barren background used on the title screen
WHITE = (255, 255, 255)
HIGHLIGHT = (255, 215, 0)    # Gold highlight colour for the selected menu option
BLACK = (0, 0, 0)
DESERT_BG = (194, 178, 128)  # Sandy background colour for the desert biome

# --- Fonts ---------------------------------------------------------------
title_font = pygame.font.SysFont(None, 64)
menu_font = pygame.font.SysFont(None, 40)
dialogue_font = pygame.font.SysFont(None, 32)

# --- Core state machine ----------------------------------------------------
# game_state controls which screen is drawn and which input handler runs
# each frame. Valid values so far: "TITLE", "DIALOGUE", "GAME", "DESERT_ROOM".
game_state = "TITLE"

# --- Title screen menu state -------------------------------------------------
selected_option = 0                 # Index of the currently highlighted menu option
menu_options = ["New Game", "Quit"]
menu_option_rects = []              # Clickable pygame.Rect for each menu option, rebuilt every frame

# --- Player data -------------------------------------------------------------
# Hardcoded default protagonist (real character customisation is deferred,
# per the project's First Build Session Plan).
protagonist = {
    "name": "Protagonist",
    "x": SCREEN_WIDTH // 2,
    "y": SCREEN_HEIGHT // 2,
}

# --- Dialogue content ----------------------------------------------------------
# Each of these is a list of strings; one string is shown at a time in the
# scrolling text box (see draw_text_box / update_text_reveal / handle_dialogue_input).
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

# --- Dialogue system state ---------------------------------------------------------
# These track progress through whichever dialogue is currently active
# (set to CATASTROPHE_INTRO_TEXT, SPRITE_INTRO_TEXT, or any future dialogue list).
dialogue_lines = []                   # The list of lines currently being shown
current_line_index = 0                # Which line of dialogue_lines is currently displayed
revealed_chars = 0                    # How many characters of the current line have "typed" in so far
text_reveal_speed = 30                # Milliseconds between each newly revealed character
last_reveal_time = 0                  # Timestamp (ms) the last character was revealed, for timing the effect
next_state_after_dialogue = "GAME"    # Which game_state to switch to once the dialogue finishes

# --- Desert biome placeholder text -------------------------------------------------
DESERT_ROOM_DESCRIPTION = (
    "The heat is immediate and overwhelming. Sand stretches in every "
    "direction, broken only by the occasional withered, thirsty-looking plant."
)

def draw_title_screen():
    """
    Draw the title screen: the game's title text and the New Game / Quit
    menu, highlighting whichever option is currently selected.

    Also rebuilds `menu_option_rects` every frame, so that mouse clicks and
    hovering (handled in handle_title_input) always line up with where the
    menu text is actually drawn on screen.
    """
    global menu_option_rects
    screen.fill(BARREN_BG)

    # Draw the game's title near the top of the screen.
    title_surface = title_font.render("MY GAME TITLE", True, WHITE)
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 150))
    screen.blit(title_surface, title_rect)

    # Draw each menu option, highlighting the currently selected one in gold.
    menu_option_rects = []
    for i, option in enumerate(menu_options):
        color = HIGHLIGHT if i == selected_option else WHITE
        option_surface = menu_font.render(option, True, color)
        option_rect = option_surface.get_rect(center=(SCREEN_WIDTH // 2, 300 + i * 60))
        screen.blit(option_surface, option_rect)
        # Store this option's rectangle so mouse input can check hover/clicks against it.
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
        # Start the catastrophe intro dialogue. Once it finishes, move on
        # to the sprite's introduction (see next_state_after_dialogue).
        dialogue_lines = CATASTROPHE_INTRO_TEXT
        current_line_index = 0
        revealed_chars = 0
        last_reveal_time = pygame.time.get_ticks()
        next_state_after_dialogue = "SPRITE_INTRO_START"
        game_state = "DIALOGUE"
    elif option_name == "Quit":
        # Cleanly shut down Pygame before exiting the program.
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
            # Move selection up, wrapping around to the bottom option with %.
            selected_option = (selected_option - 1) % len(menu_options)
        elif event.key == pygame.K_DOWN:
            # Move selection down, wrapping around to the top option with %.
            selected_option = (selected_option + 1) % len(menu_options)
        elif event.key == pygame.K_RETURN:
            activate_menu_option(menu_options[selected_option])

    elif event.type == pygame.MOUSEMOTION:
        # Update the selected option to whichever one the mouse is hovering over.
        for i, rect in enumerate(menu_option_rects):
            if rect.collidepoint(event.pos):
                selected_option = i

    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        # Left mouse button clicked: activate the option under the cursor, if any.
        for i, rect in enumerate(menu_option_rects):
            if rect.collidepoint(event.pos):
                activate_menu_option(menu_options[i])


def draw_game_screen():
    """
    Draw a temporary placeholder "in-game" screen: a plain square standing
    in for the protagonist's sprite, labelled with their name. This exists
    purely to prove the protagonist data is being read and used, ahead of
    real sprite art and real gameplay rooms.
    """
    screen.fill((30, 30, 30))

    # A simple square standing in for the protagonist until real art exists.
    protagonist_rect = pygame.Rect(0, 0, 40, 40)
    protagonist_rect.center = (protagonist["x"], protagonist["y"])
    pygame.draw.rect(screen, WHITE, protagonist_rect)

    # Print the protagonist's name just above the square.
    name_surface = menu_font.render(protagonist["name"], True, WHITE)
    name_rect = name_surface.get_rect(center=(protagonist["x"], protagonist["y"] - 40))
    screen.blit(name_surface, name_rect)

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
        # font.size() measures how wide this text would be if rendered, in pixels.
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            # Adding this word would overflow the box, so close off the
            # current line and start a new one with this word.
            lines.append(current_line.rstrip())
            current_line = word + " "

    if current_line:
        lines.append(current_line.rstrip())

    return lines

def draw_text_box(text):
    """
    Draw the scrolling dialogue box at the bottom of the screen, containing
    the given text, wrapped to fit inside the box.

    Args:
        text (str): The (possibly partially revealed) text to display.
    """
    box_rect = pygame.Rect(50, 420, SCREEN_WIDTH - 100, 150)
    pygame.draw.rect(screen, BLACK, box_rect)
    pygame.draw.rect(screen, WHITE, box_rect, 3)  # 3px border

    # Leave 20px of padding on each side of the box for the wrapped text.
    max_text_width = box_rect.width - 40
    wrapped_lines = wrap_text(text, dialogue_font, max_text_width)
    line_height = dialogue_font.get_linesize()

    for i, line in enumerate(wrapped_lines):
        line_surface = dialogue_font.render(line, True, WHITE)
        line_rect = line_surface.get_rect(topleft=(box_rect.x + 20, box_rect.y + 20 + i * line_height))
        screen.blit(line_surface, line_rect)

def update_text_reveal():
    """
    Advance the typewriter-style text reveal by one character, if enough
    time has passed since the last character was revealed.

    Reads and updates the dialogue system's global state (current_line_index,
    revealed_chars, last_reveal_time).
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
    Handle player input while a dialogue text box is active.

    Pressing Enter/Space either instantly finishes revealing the current
    line (if it's still "typing"), or advances to the next line (if the
    current line has already finished). Once the final line finishes, the
    game moves on to whichever state next_state_after_dialogue specifies.

    Args:
        event (pygame.event.Event): The event to process.
    """
    global current_line_index, revealed_chars, game_state

    if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
        current_line = dialogue_lines[current_line_index]

        if revealed_chars < len(current_line):
            # Line hasn't finished "typing" yet: skip straight to showing it in full.
            revealed_chars = len(current_line)
        else:
            # Line has finished: move on to the next one.
            current_line_index += 1
            revealed_chars = 0
            if current_line_index >= len(dialogue_lines):
                # No more lines left: hand control over to whatever comes next.
                game_state = next_state_after_dialogue

def start_sprite_intro():
    """
    Set up and start the sprite's introduction dialogue. Called once the
    catastrophe intro dialogue finishes (see next_state_after_dialogue).
    """
    global dialogue_lines, current_line_index, revealed_chars
    global last_reveal_time, next_state_after_dialogue, game_state

    dialogue_lines = SPRITE_INTRO_TEXT
    current_line_index = 0
    revealed_chars = 0
    last_reveal_time = pygame.time.get_ticks()
    # Once the sprite's introduction finishes, move on to the desert biome.
    next_state_after_dialogue = "DESERT_ROOM"
    game_state = "DIALOGUE" 


def draw_desert_room():
    """
    Draw a placeholder version of the desert biome: a plain sandy
    background with a wrapped block of descriptive text.

    This is intentionally simple (no puzzle logic, no real art yet) - its
    only job is to prove the full chain (title -> intro -> sprite ->
    desert) runs start to finish, before any real desert gameplay is built.
    """
    screen.fill(DESERT_BG)

    max_text_width = SCREEN_WIDTH - 100
    wrapped_lines = wrap_text(DESERT_ROOM_DESCRIPTION, dialogue_font, max_text_width)
    line_height = dialogue_font.get_linesize()

    for i, line in enumerate(wrapped_lines):
        line_surface = dialogue_font.render(line, True, BLACK)
        line_rect = line_surface.get_rect(topleft=(50, 50 + i * line_height))
        screen.blit(line_surface, line_rect)

running = True
while running:
    # --- Handle input events --------------------------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif game_state == "TITLE":
            handle_title_input(event)
        elif game_state == "DIALOGUE":
            handle_dialogue_input(event)

    # --- One-frame "trigger" state: sets up the sprite intro, then hands
    # off to the DIALOGUE state before anything is drawn this frame. ------
    if game_state == "SPRITE_INTRO_START":
        start_sprite_intro()

    # --- Draw whichever screen matches the current game_state -----------
    if game_state == "TITLE":
        draw_title_screen()
    elif game_state == "DIALOGUE":
        update_text_reveal()
        screen.fill(BARREN_BG)
        current_line = dialogue_lines[current_line_index]
        draw_text_box(current_line[:revealed_chars])
    elif game_state == "GAME":
        draw_game_screen()
    elif game_state == "DESERT_ROOM":
        draw_desert_room()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()




