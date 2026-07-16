"""
My Game - a narrative exploration game built with Pygame.

This file contains the game so far: the title screen, the opening
catastrophe dialogue, and the desert biome (with basic player movement).
The game uses a simple state machine (the `game_state` global variable) to
decide what to draw and which inputs to listen for each frame.
"""

import pygame
import sys
import math

pygame.init()

# --- Display setup
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()

# --- Desert control hint (fades out after appearing) 
previous_game_state = None       # Tracks the last frame's game_state, to detect state changes
desert_hint_start_time = 0       # Timestamp (ms) the player entered the desert room
HINT_VISIBLE_DURATION = 2000     # How long the control hint stays fully visible (ms)
HINT_FADE_DURATION = 2000        # How long it takes to fade out after that (ms)

# --- Colours (RGB tuples) 
BARREN_BG = (120, 100, 70)
WHITE = (255, 255, 255)
HIGHLIGHT = (255, 215, 0)
BLACK = (0, 0, 0)
DESERT_BG = (194, 178, 128)

# --- Fonts 
title_font = pygame.font.SysFont(None, 64)
menu_font = pygame.font.SysFont(None, 40)
dialogue_font = pygame.font.SysFont(None, 32)
hint_font = pygame.font.SysFont(None, 20)

# --- Core state machine 
# Valid values so far: "TITLE", "DIALOGUE", "DESERT_ROOM" , "PAUSED", "SETTINGS_PLACEHOLDER"
game_state = "TITLE"

# --- Title screen menu state 
selected_option = 0
menu_options = ["New Game", "Quit"]
menu_option_rects = []

# --- Player data 
PROTAGONIST_SIZE = 40   # Width/height in pixels of the protagonist's placeholder square
PLAYER_SPEED = 4         # Pixels moved per frame while a direction key is held

protagonist = {
    "name": "Protagonist",
    "x": 1200,  # Positioned within the wider desert world, not just the screen!!
    "y": SCREEN_HEIGHT // 2,
}

# --- Pause menu state ---------------------------------------------------
pause_menu_options = ["Settings", "Save", "Quit Game"]
pause_selected_option = 0
pause_option_rects = []
paused_from_state = None  # Which gameplay state to return to when unpausing

item_popup_title = ""               # Item name shown at the top of the popup
item_popup_description = ""         # Short description/effect text shown inside the popup
item_popup_icon_path = None         # Real icon image path later; None draws a placeholder square for now
previous_state_before_popup = None  # Which state to return to once the popup closes
ITEM_POPUP_ICON_SIZE = 64           # Width/height in pixels of the icon area inside the popup

# --- Placeholder screens (Settings & Save aren't built yet) --------------
PLACEHOLDER_SCREENS = {
    "SETTINGS_PLACEHOLDER": (
        "Settings",
        "Coming soon - once real music and sound effects are added.",
    ),
    "SAVE_PLACEHOLDER": (
        "Save",
        "Coming soon - saving your progress isn't implemented yet.",
    ),
}


# --- Dialogue content ----------------------------------------------------------
CATASTROPHE_INTRO_TEXT = [
    "Long ago, this land was full of life and wonder.",
    "But a great catastrophe struck, and everything changed.",
    "You awaken to find the world forever different...",
]


# --- Dialogue system state ---------------------------------------------------------
dialogue_lines = []
current_line_index = 0
revealed_chars = 0
text_reveal_speed = 30
last_reveal_time = 0
next_state_after_dialogue = "DESERT_ROOM"

dialogue_backdrop_state = None  # Which scene (if any) to draw behind the dialogue box

# --- Desert biome placeholder text -------------------------------------------------
DESERT_ROOM_DESCRIPTION = (
    "The heat is immediate and overwhelming. Sand stretches in every "
    "direction, and a long stretch of withered flowers in the distance creates a sad, pensive atmosphere. "
    "This place is dangerous - keep an eye on your health, the heat is already starting to get to you. "
    "Look around... there might be something nearby that can help."
)

# --- Decoy flower (desert opening) ----------------------------------
DECOY_FLOWER_POS = (1400, 300)          # Shifted to match the protagonist's new spawn point
DECOY_FLOWER_RADIUS = 50
DECOY_FLOWER_COLOR = (180, 160, 90)
decoy_flower_encountered = False

# --- Adding a glow to the decoy flower as well ---------------------------
DECOY_FLOWER_GLOW_COLOR = (255, 230, 150)   # Warm, inviting gold 
DECOY_FLOWER_GLOW_MIN_RADIUS = 18
DECOY_FLOWER_GLOW_MAX_RADIUS = 26
DECOY_FLOWER_GLOW_PERIOD = 900               # Milliseconds for one full pulse in and out

ICE_FLOWER_POS = (100, 300)           # Far to the left, in the newly scrollable part of the desert
ICE_FLOWER_COLOR = (180, 220, 240)     # Pale icy blue, distinct from the decoy flower

ICE_FLOWER_TRIGGER_RADIUS = 60        # How close the protagonist must get to be shown the hint
ice_flower_encountered = False         # Whether the sprite has already pointed the flower out

ICE_FLOWER_GLOW_COLOR = (200, 240, 255)
ICE_FLOWER_GLOW_MIN_RADIUS = 18
ICE_FLOWER_GLOW_MAX_RADIUS = 26
ICE_FLOWER_GLOW_PERIOD = 900            # Milliseconds for one full pulse in and out

ICE_FLOWER_HINT_TEXT = [
    "\"Look - that one over there! Press E to pick it up!\"",
]

SPRITE_FLOWER_WARNING_TEXT = [
    "A tiny light darts out of nowhere and hovers right in front of you.",
    "\"Wait, wait, WAIT - don't pick that!\"",
    "\"It's just a common flower, it doesn't do anything. And with the world already this dried up, we need to let whatever can still grow, grow.\"",
    "\"Oh - sorry, I should introduce myself. I'm Sprite. I'll be keeping you out of trouble from now on, apparently.\"",
    "\"Anyway. If you want, I can show you how to deal with that heat that's been quietly cooking you this whole time.\"",
    "\"Quick - go left! There should be a flower that way that can help you.\"",
    
]

DECOY_FLOWER_EATEN_TEXT = [
    "The tiny light flickers, and her expression falls.",
    "\"...I told you not to eat that.\"",
    "\"I really thought you'd listen to me on this one.\"",
]

# --- Sprite companion (placeholder appearance for now) -------------------
SPRITE_CHAR_COLOR = (255, 240, 150)
SPRITE_CHAR_RADIUS = 10
SPRITE_CHAR_OFFSET = (35, -35)   # Position relative to the protagonist, once hovering
SPRITE_ENTRANCE_DURATION = 700    # Milliseconds for the fly-in entrance
SPRITE_ENTRANCE_START_Y = -50     # Starting y position (above the screen) for the fly-in
SPRITE_HOVER_AMPLITUDE = 6        # Pixels the sprite bobs up/down while hovering
SPRITE_HOVER_PERIOD = 1200        # Milliseconds for one full up-down bob cycle

sprite_state = "HIDDEN"           # "HIDDEN", "ENTERING", or "HOVERING"
sprite_entrance_start_time = 0
sprite_draw_pos = [0, 0]          # Current on-screen position, recalculated every frame


# --- HP ------------------------------------------------
MAX_HP = 100
hp = MAX_HP
heat_drain_active = False   # Becomes True once the sprite's warning dialogue finishes
last_hp_tick_time = 0
HP_DRAIN_INTERVAL = 1000    # Milliseconds between each 1-point HP loss
HP_BAR_POS = (20, 20)
HP_BAR_WIDTH = 200
HP_BAR_HEIGHT = 20

HP_BAR_COLOR_HIGH = "#2ECC71"    # Green - shown when HP is 70 or above
HP_BAR_COLOR_MID = "#E67E22"     # Orange - shown when HP is between 30 and 69
HP_BAR_COLOR_LOW = "#E74C3C"     # Red - shown when HP is below 30
HP_HEAL_POPUP_COLOR = "#2ECC71"  # Green - the floating "+80 HP" text shown on heal

hp_bar_visible = False   # Becomes True once heat drain first starts, and stays True for the rest of the game

hp_heal_popup_text = None         # Text to show, e.g. "+80 HP"; None means nothing is showing
hp_heal_popup_start_time = 0      # pygame.time.get_ticks() value from when it appeared
HP_HEAL_POPUP_DURATION_MS = 1500  # How long the heal callout stays on screen, in milliseconds

# --- For allowing sprite tutorial-ish intro.
dialogue_on_complete = None  

# --- This is for making "press E to interact" work:
nearby_interactable = None

# --- To stop the ice flower from being collected more than once/remaining on screen once eaten.
ice_flower_collected = False

# --- Desert world & camera scrolling --------------------------------------
DESERT_WORLD_WIDTH = 1600  # The desert extends further than a single screen
camera_x = 0                # How far the camera has scrolled from the world's left edge



# --- Arrow directing player to go left ---------------------------------------------
LEFT_ARROW_COLOR = (255, 221, 89)      # Bright gold, easy to spot against the desert
LEFT_ARROW_FLASH_PERIOD = 500           # Milliseconds for one full on/off blink cycle
LEFT_ARROW_CENTER = (80, 260)           # Screen position, above the dialogue box
LEFT_ARROW_SIZE = 40

sprite_friendship_level = 0  # How much the sprite likes/trusts the player so far
decoy_flower_eaten = False   # Whether the player has already eaten the decoy flower or not

def draw_title_screen():
    """
    the game's title text and the New Game / Quit
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
    global dialogue_backdrop_state

    if option_name == "New Game":
        # Start the catastrophe intro. Once it finishes, drop straight
        # into the desert biome (no separate sprite-intro screen anymore).
        dialogue_lines = CATASTROPHE_INTRO_TEXT
        current_line_index = 0
        revealed_chars = 0
        last_reveal_time = pygame.time.get_ticks()
        next_state_after_dialogue = "DESERT_ROOM"
        dialogue_backdrop_state = None  # No gameplay scene exists yet behind the intro
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
    global current_line_index, revealed_chars, game_state, dialogue_on_complete

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
                if dialogue_on_complete == "START_HEAT_DRAIN":
                    activate_heat_drain()
                dialogue_on_complete = None

def handle_desert_movement():
    """
    Update the protagonist's position based on which movement keys are
    currently held down (arrow keys or WASD), keeping them within the
    bounds of the wider desert world (not just the visible screen).
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
    protagonist["x"] = max(half_size, min(DESERT_WORLD_WIDTH - half_size, protagonist["x"]))
    protagonist["y"] = max(half_size, min(SCREEN_HEIGHT - half_size, protagonist["y"]))


def draw_desert_room():
    """
    Draw the desert biome: a sandy background, a short description of the
    surroundings, the decoy flower (hidden once eaten), the ice flower
    placeholder (with its attention-grabbing glow, hidden once
    collected), the sprite companion, the protagonist, a "Press E"
    interaction hint, and a fading movement-control hint. The HP bar is
    drawn separately by the main loop, since it needs to stay visible
    across every game state, not just this one.
    """
    screen.fill(DESERT_BG)

    max_text_width = SCREEN_WIDTH - 100
    wrapped_lines = wrap_text(DESERT_ROOM_DESCRIPTION, dialogue_font, max_text_width)
    line_height = dialogue_font.get_linesize()
    for i, line in enumerate(wrapped_lines):
        line_surface = dialogue_font.render(line, True, BLACK)
        line_rect = line_surface.get_rect(topleft=(50, 50 + i * line_height))
        screen.blit(line_surface, line_rect)

    if not decoy_flower_eaten:
        draw_decoy_flower_glow()
        draw_decoy_flower()
    if not ice_flower_collected:
        if ice_flower_encountered:
            draw_ice_flower_glow()
        draw_ice_flower()
    draw_interaction_hint()

    protagonist_screen_x, protagonist_screen_y = world_to_screen(protagonist["x"], protagonist["y"])
    protagonist_rect = pygame.Rect(0, 0, PROTAGONIST_SIZE, PROTAGONIST_SIZE)
    protagonist_rect.center = (int(protagonist_screen_x), int(protagonist_screen_y))
    pygame.draw.rect(screen, WHITE, protagonist_rect)

    draw_sprite_character()
    draw_control_hint()

def draw_control_hint():
    """
    Draw a temporary "Use ARROW KEYS or WASD to move" prompt near the
    bottom of the desert room, shown briefly when the player first
    arrives and then fading out, similar to the on-screen control
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

def handle_desert_room_input(event):
    """
    Handle discrete (single-press) events while the desert room is
    active - currently just opening the pause menu with ESCAPE. Continuous
    movement is handled separately in handle_desert_movement().

    Args:
        event (pygame.event.Event): The event to process.
    """
    global game_state, paused_from_state, pause_selected_option

    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        paused_from_state = "DESERT_ROOM"
        pause_selected_option = 0
        game_state = "PAUSED"
    
    elif event.type == pygame.KEYDOWN and event.key == pygame.K_e:
        handle_interaction_key()
        


def draw_pause_menu():
    """
    Draw the pause menu: a simple dark screen with "Paused" and three
    selectable options (Settings, Save, Quit Game), shown when the player
    presses ESCAPE during gameplay.
    """
    global pause_option_rects
    screen.fill((20, 20, 20))

    title_surface = title_font.render("Paused", True, WHITE)
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 150))
    screen.blit(title_surface, title_rect)

    pause_option_rects = []
    for i, option in enumerate(pause_menu_options):
        color = HIGHLIGHT if i == pause_selected_option else WHITE
        option_surface = menu_font.render(option, True, color)
        option_rect = option_surface.get_rect(center=(SCREEN_WIDTH // 2, 300 + i * 60))
        screen.blit(option_surface, option_rect)
        pause_option_rects.append(option_rect)

    hint_surface = hint_font.render("Press ESC to resume", True, (180, 180, 180))
    hint_rect = hint_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
    screen.blit(hint_surface, hint_rect)

def activate_pause_option(option_name):
    """
    Perform whatever should happen when a pause menu option is chosen.

    Args:
        option_name (str): The label of the chosen option.
    """
    global game_state

    if option_name == "Settings":
        game_state = "SETTINGS_PLACEHOLDER"
    elif option_name == "Save":
        game_state = "SAVE_PLACEHOLDER"
    elif option_name == "Quit Game":
        pygame.quit()
        sys.exit()


def handle_pause_input(event):
    """
    Handle a single Pygame event while the pause menu is active: keyboard
    navigation, mouse hover/click, and resuming with ESCAPE.

    Args:
        event (pygame.event.Event): The event to process.
    """
    global pause_selected_option, game_state

    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            game_state = paused_from_state  # Resume the paused gameplay state
        elif event.key == pygame.K_UP:
            pause_selected_option = (pause_selected_option - 1) % len(pause_menu_options)
        elif event.key == pygame.K_DOWN:
            pause_selected_option = (pause_selected_option + 1) % len(pause_menu_options)
        elif event.key == pygame.K_RETURN:
            activate_pause_option(pause_menu_options[pause_selected_option])

    elif event.type == pygame.MOUSEMOTION:
        for i, rect in enumerate(pause_option_rects):
            if rect.collidepoint(event.pos):
                pause_selected_option = i

    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for i, rect in enumerate(pause_option_rects):
            if rect.collidepoint(event.pos):
                activate_pause_option(pause_menu_options[i])


def draw_placeholder_screen():
    """
    Draw a simple "coming soon" screen for a feature that doesn't exist
    yet (Settings or Save), using the title/message stored in
    PLACEHOLDER_SCREENS for whichever placeholder state is currently active.
    """
    screen.fill((20, 20, 20))
    title_text, message_text = PLACEHOLDER_SCREENS[game_state]

    title_surface = title_font.render(title_text, True, WHITE)
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 200))
    screen.blit(title_surface, title_rect)

    wrapped_lines = wrap_text(message_text, dialogue_font, SCREEN_WIDTH - 100)
    line_height = dialogue_font.get_linesize()
    for i, line in enumerate(wrapped_lines):
        line_surface = dialogue_font.render(line, True, WHITE)
        line_rect = line_surface.get_rect(center=(SCREEN_WIDTH // 2, 300 + i * line_height))
        screen.blit(line_surface, line_rect)

    hint_surface = hint_font.render("Press ESC to go back", True, (180, 180, 180))
    hint_rect = hint_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
    screen.blit(hint_surface, hint_rect)

def handle_placeholder_input(event):
    """
    Handle input on a placeholder screen (Settings or Save): pressing
    ESCAPE returns to the pause menu.

    Args:
        event (pygame.event.Event): The event to process.
    """
    global game_state
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        game_state = "PAUSED"

def draw_decoy_flower():
    """
    Draw the desert's decoy flower, a plain, common-looking flower that
    has no real use, placed to tempt the player into picking it before
    the sprite stops them.
    """
    screen_x, screen_y = world_to_screen(*DECOY_FLOWER_POS)
    pygame.draw.circle(screen, DECOY_FLOWER_COLOR, (int(screen_x), int(screen_y)), 12)

def check_decoy_flower_trigger():
    """
    Check whether the protagonist has walked close enough to the decoy
    flower to trigger the sprite's warning dialogue. Only fires once per
    playthrough, tracked via decoy_flower_encountered.
    """
    global decoy_flower_encountered, dialogue_lines, current_line_index
    global revealed_chars, last_reveal_time, next_state_after_dialogue, game_state
    global dialogue_backdrop_state, dialogue_on_complete
    global sprite_state, sprite_entrance_start_time

    if decoy_flower_encountered:
        return

    dx = protagonist["x"] - DECOY_FLOWER_POS[0]
    dy = protagonist["y"] - DECOY_FLOWER_POS[1]
    distance = math.hypot(dx, dy)

    if distance <= DECOY_FLOWER_RADIUS:
        decoy_flower_encountered = True
        dialogue_lines = SPRITE_FLOWER_WARNING_TEXT
        current_line_index = 0
        revealed_chars = 0
        last_reveal_time = pygame.time.get_ticks()
        next_state_after_dialogue = "DESERT_ROOM"
        dialogue_backdrop_state = "DESERT_ROOM"
        dialogue_on_complete = None
        sprite_state = "ENTERING"
        sprite_entrance_start_time = pygame.time.get_ticks()
        game_state = "DIALOGUE"

def draw_sprite_character():
    """
    Draw the sprite companion at her current animated position (see
    update_sprite_animation), converted from world to screen coordinates,
    once she's made her first appearance.
    """
    if sprite_state == "HIDDEN":
        return
    screen_x, screen_y = world_to_screen(sprite_draw_pos[0], sprite_draw_pos[1])
    pygame.draw.circle(screen, SPRITE_CHAR_COLOR, (int(screen_x), int(screen_y)), SPRITE_CHAR_RADIUS)

def activate_heat_drain():
    """
    Turn on the desert heat's HP drain and reset its internal timer.
    Called as soon as the player first enters the desert room (see the
    main loop), so the heat starts affecting them right away rather
    than waiting for the sprite's warning dialogue to finish.
    """
    global heat_drain_active, last_hp_tick_time

    heat_drain_active = True
    last_hp_tick_time = pygame.time.get_ticks()




def update_heat_drain():
    """
    Drain the protagonist's HP by 1 point per second while heat_drain_active
    is True, simulating the desert heat's ongoing effect until it's cured.
    HP is floored at 0.
    """
    global hp, last_hp_tick_time

    if not heat_drain_active or hp <= 0:
        return

    current_time = pygame.time.get_ticks()
    if current_time - last_hp_tick_time >= HP_DRAIN_INTERVAL:
        hp -= 1
        last_hp_tick_time = current_time


def update_sprite_animation():
    """
    Update the sprite companion's on-screen position: fly in from above
    the screen when she first appears, then settle into a gentle
    up-and-down hover near the protagonist, like a bird flying on the spot.
    """
    global sprite_state, sprite_draw_pos

    if sprite_state == "HIDDEN":
        return

    target_x = protagonist["x"] + SPRITE_CHAR_OFFSET[0]
    target_y = protagonist["y"] + SPRITE_CHAR_OFFSET[1]

    if sprite_state == "ENTERING":
        elapsed = pygame.time.get_ticks() - sprite_entrance_start_time
        progress = min(1.0, elapsed / SPRITE_ENTRANCE_DURATION)

        sprite_draw_pos[0] = target_x
        sprite_draw_pos[1] = SPRITE_ENTRANCE_START_Y + (target_y - SPRITE_ENTRANCE_START_Y) * progress

        if progress >= 1.0:
            sprite_state = "HOVERING"

    elif sprite_state == "HOVERING":
        bob_angle = (pygame.time.get_ticks() % SPRITE_HOVER_PERIOD) / SPRITE_HOVER_PERIOD * 2 * math.pi
        bob_offset = math.sin(bob_angle) * SPRITE_HOVER_AMPLITUDE

        sprite_draw_pos[0] = target_x
        sprite_draw_pos[1] = target_y + bob_offset

def world_to_screen(world_x, world_y):
    """
    Convert a position in world coordinates (used for gameplay logic,
    e.g. distance checks) into screen coordinates (used for drawing),
    by subtracting the camera's current horizontal scroll offset.
    """
    return world_x - camera_x, world_y


def update_camera():
    """
    Keeping the camera roughly centred on the protagonist as they move
    through the desert world, clamped so it never scrolls past either
    edge of that world.
    """
    global camera_x
    target_camera_x = protagonist["x"] - SCREEN_WIDTH // 2
    camera_x = max(0, min(DESERT_WORLD_WIDTH - SCREEN_WIDTH, target_camera_x))


def draw_ice_flower():
    """
    Draw a placeholder for the ice flower: a pale, icy-coloured circle
    marking where the real ice flower (and its logic) will be built
    in a future step.
    """
    screen_x, screen_y = world_to_screen(*ICE_FLOWER_POS)
    pygame.draw.circle(screen, ICE_FLOWER_COLOR, (int(screen_x), int(screen_y)), 12)

def check_ice_flower_trigger():
    """
    Once the protagonist gets close enough to the ice flower, have the
    sprite point it out (which also starts the glow, since that's drawn
    conditionally on ice_flower_encountered). Only happens once.
    """
    global game_state, dialogue_lines, current_line_index, revealed_chars
    global last_reveal_time, next_state_after_dialogue, dialogue_backdrop_state
    global dialogue_on_complete, ice_flower_encountered

    if ice_flower_encountered:
        return

    distance = math.hypot(
        protagonist["x"] - ICE_FLOWER_POS[0],
        protagonist["y"] - ICE_FLOWER_POS[1],
    )
    if distance <= ICE_FLOWER_TRIGGER_RADIUS:
        ice_flower_encountered = True
        dialogue_lines = ICE_FLOWER_HINT_TEXT
        current_line_index = 0
        revealed_chars = 0
        last_reveal_time = pygame.time.get_ticks()
        next_state_after_dialogue = "DESERT_ROOM"
        dialogue_backdrop_state = "DESERT_ROOM"
        dialogue_on_complete = None
        game_state = "DIALOGUE"

def draw_ice_flower_glow():
    """
    Draw a soft, pulsing glow around the ice flower to draw the player's
    eye to it, once the sprite has pointed it out. The radius oscillates
    smoothly between a min and max value using a sine wave, the same
    technique used for the sprite's idle hover.
    """
    pulse_progress = (pygame.time.get_ticks() % ICE_FLOWER_GLOW_PERIOD) / ICE_FLOWER_GLOW_PERIOD
    pulse = math.sin(pulse_progress * 2 * math.pi)  # Oscillates between -1 and 1
    radius = int(
        ICE_FLOWER_GLOW_MIN_RADIUS
        + (pulse + 1) / 2 * (ICE_FLOWER_GLOW_MAX_RADIUS - ICE_FLOWER_GLOW_MIN_RADIUS)
    )

    # A separate surface with per-pixel alpha lets the glow be semi-transparent,
    # which a plain pygame.draw.circle() straight onto the screen can't do.
    glow_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(glow_surface, (*ICE_FLOWER_GLOW_COLOR, 90), (radius, radius), radius)

    screen_x, screen_y = world_to_screen(*ICE_FLOWER_POS)
    glow_rect = glow_surface.get_rect(center=(int(screen_x), int(screen_y)))
    screen.blit(glow_surface, glow_rect)

def draw_decoy_flower_glow():
    """
    Draw a soft, pulsing glow around the decoy flower, visible from the
    very start, to entice the player into walking toward it before the
    sprite ever shows up to stop them.
    """
    pulse_progress = (pygame.time.get_ticks() % DECOY_FLOWER_GLOW_PERIOD) / DECOY_FLOWER_GLOW_PERIOD
    pulse = math.sin(pulse_progress * 2 * math.pi)  # Oscillates between -1 and 1
    radius = int(
        DECOY_FLOWER_GLOW_MIN_RADIUS
        + (pulse + 1) / 2 * (DECOY_FLOWER_GLOW_MAX_RADIUS - DECOY_FLOWER_GLOW_MIN_RADIUS)
    )

    glow_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(glow_surface, (*DECOY_FLOWER_GLOW_COLOR, 90), (radius, radius), radius)

    screen_x, screen_y = world_to_screen(*DECOY_FLOWER_POS)
    glow_rect = glow_surface.get_rect(center=(int(screen_x), int(screen_y)))
    screen.blit(glow_surface, glow_rect)

def draw_left_arrow_hint():
    """
    Draw a flashing, left-pointing arrow to reinforce the
    sprite's "go left" line. It blinks on and off by checking the
    current time against LEFT_ARROW_FLASH_PERIOD, the same trick
    used elsewhere for the fading control hint.
    """
    is_visible = (pygame.time.get_ticks() % LEFT_ARROW_FLASH_PERIOD) < (LEFT_ARROW_FLASH_PERIOD // 2)
    if not is_visible:
        return

    center_x, center_y = LEFT_ARROW_CENTER
    half = LEFT_ARROW_SIZE // 2
    arrow_points = [
        (center_x - half, center_y),        # Left tip
        (center_x + half, center_y - half),  # Top right corner
        (center_x + half, center_y + half),  # Bottom right corner
    ]
    pygame.draw.polygon(screen, LEFT_ARROW_COLOR, arrow_points)


def update_nearby_interactable():
    """
    Every frame, re-checks how close the protagonist currently is to each
    interactable object in the desert room, and updates nearby_interactable
    to whichever single one (if any) is currently in range. Runs
    independently of the one-off dialogue triggers in
    check_ice_flower_trigger() and check_decoy_flower_trigger(), so E
    keeps working correctly every time the player is back in range.

    """
    global nearby_interactable

    ice_distance = math.hypot(
        protagonist["x"] - ICE_FLOWER_POS[0],
        protagonist["y"] - ICE_FLOWER_POS[1],
    )
    decoy_distance = math.hypot(
        protagonist["x"] - DECOY_FLOWER_POS[0],
        protagonist["y"] - DECOY_FLOWER_POS[1],
    )

    if ice_flower_encountered and not ice_flower_collected and ice_distance <= ICE_FLOWER_TRIGGER_RADIUS:
        nearby_interactable = "ice_flower"
    elif not decoy_flower_eaten and decoy_distance <= DECOY_FLOWER_RADIUS:
        nearby_interactable = "decoy_flower"
    else:
        nearby_interactable = None


def handle_interaction_key():
    """
    Runs whatever E should do, based on nearby_interactable.
    """
    if nearby_interactable == "ice_flower":
        consume_ice_flower()
    elif nearby_interactable == "decoy_flower":
        consume_decoy_flower()

def consume_ice_flower():
    """
    Eating the ice flower restores 80 HP (capped at MAX_HP) and stops the
    ongoing heat drain, then shows the item info popup and a floating
    "+80 HP" callout explaining what just happened.
    """
    global ice_flower_collected, hp, heat_drain_active

    ice_flower_collected = True
    hp = min(MAX_HP, hp + 80)
    heat_drain_active = False

    show_item_popup(
        title="Ice Flower",
        description="A pale, icy-cool flower. Eating it soothes the desert heat and restores 80 HP.",
        icon_path=None,
    )
    show_hp_heal_popup(80)

def consume_decoy_flower():
    """
    Reaction to eating the decoy flower after being warned not to. Costs
    the player one friendship point with the sprite (floored at 0) and
    triggers her disappointed reaction dialogue. Only happens once.
    """
    global decoy_flower_eaten, sprite_friendship_level
    global dialogue_lines, current_line_index, revealed_chars, last_reveal_time
    global next_state_after_dialogue, dialogue_backdrop_state, dialogue_on_complete, game_state

    if decoy_flower_eaten:
        return

    decoy_flower_eaten = True
    sprite_friendship_level = max(0, sprite_friendship_level - 1)

    dialogue_lines = DECOY_FLOWER_EATEN_TEXT
    current_line_index = 0
    revealed_chars = 0
    last_reveal_time = pygame.time.get_ticks()
    next_state_after_dialogue = "DESERT_ROOM"
    dialogue_backdrop_state = "DESERT_ROOM"
    dialogue_on_complete = None
    game_state = "DIALOGUE"

def draw_interaction_hint():
    """
    Draws a 'Press E' prompt above the protagonist when something interactable is in range.
    
    """
    if nearby_interactable is None:
        return

    screen_x, screen_y = world_to_screen(protagonist["x"], protagonist["y"])
    hint_surface = hint_font.render("Press E", True, WHITE)
    hint_rect = hint_surface.get_rect(center=(int(screen_x), int(screen_y) - PROTAGONIST_SIZE))
    screen.blit(hint_surface, hint_rect)

def show_item_popup(title, description, icon_path=None):
    """
    Opens the small item-info popup window: a title, a short description,
    and either a real icon image (once icon_path points to a real file)
    or a placeholder square for now. Used for any item that should show
    information the moment it's consumed, like the ice flower.
    """
    global item_popup_title, item_popup_description, item_popup_icon_path
    global previous_state_before_popup, game_state

    item_popup_title = title
    item_popup_description = description
    item_popup_icon_path = icon_path
    previous_state_before_popup = "DESERT_ROOM"
    game_state = "ITEM_POPUP"

def draw_item_popup():
    """
    Draws the desert scene behind a centered popup box containing the
    item's icon (a placeholder square until real art exists), title, and
    wrapped description text, plus a hint to close it.
    """
    draw_desert_room()

    box_rect = pygame.Rect(0, 0, 400, 220)
    box_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    pygame.draw.rect(screen, BLACK, box_rect)
    pygame.draw.rect(screen, WHITE, box_rect, 3)

    icon_rect = pygame.Rect(box_rect.x + 20, box_rect.y + 20, ITEM_POPUP_ICON_SIZE, ITEM_POPUP_ICON_SIZE)
    if item_popup_icon_path is None:
        pygame.draw.rect(screen, (150, 150, 150), icon_rect)  # Placeholder until real art exists
    else:
        icon_surface = pygame.image.load(item_popup_icon_path).convert_alpha()
        icon_surface = pygame.transform.scale(icon_surface, (ITEM_POPUP_ICON_SIZE, ITEM_POPUP_ICON_SIZE))
        screen.blit(icon_surface, icon_rect)

    title_surface = dialogue_font.render(item_popup_title, True, WHITE)
    title_rect = title_surface.get_rect(topleft=(icon_rect.right + 20, box_rect.y + 20))
    screen.blit(title_surface, title_rect)

    max_text_width = box_rect.width - 40
    wrapped_lines = wrap_text(item_popup_description, hint_font, max_text_width)
    line_height = hint_font.get_linesize()
    for i, line in enumerate(wrapped_lines):
        line_surface = hint_font.render(line, True, WHITE)
        line_rect = line_surface.get_rect(topleft=(box_rect.x + 20, icon_rect.bottom + 20 + i * line_height))
        screen.blit(line_surface, line_rect)

    hint_surface = hint_font.render("Press SPACE to close", True, (180, 180, 180))
    hint_rect = hint_surface.get_rect(bottomright=(box_rect.right - 15, box_rect.bottom - 10))
    screen.blit(hint_surface, hint_rect)

def handle_item_popup_input(event):
    """
    Closes the item popup on Space/Enter or a mouse click, returning to
    whichever state was active before it opened.
    """
    global game_state

    key_pressed = event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE)
    mouse_clicked = event.type == pygame.MOUSEBUTTONDOWN and event.button == 1

    if key_pressed or mouse_clicked:
        game_state = previous_state_before_popup

def get_hp_bar_color(current_hp):
    """
    Returns the hex color the HP bar should currently be drawn in, based
    on fixed thresholds: green at 70+, orange from 30-69, and red below
    30.
    """
    if current_hp >= 70:
        return HP_BAR_COLOR_HIGH
    elif current_hp >= 30:
        return HP_BAR_COLOR_MID
    else:
        return HP_BAR_COLOR_LOW

def draw_hp_bar():
    """
    Draws the HP bar in the corner of the screen: a white outline, a
    fill proportional to current HP colored using get_hp_bar_color()
    (green/orange/red based on fixed thresholds), and a numeric
    "HP: x/100" readout underneath. Called every frame once
    hp_bar_visible is True, regardless of game state, so it stays on
    screen for the rest of the game.
    """
    bar_x, bar_y = HP_BAR_POS
    outline_rect = pygame.Rect(bar_x, bar_y, HP_BAR_WIDTH, HP_BAR_HEIGHT)
    pygame.draw.rect(screen, WHITE, outline_rect, 2)

    fill_width = int(HP_BAR_WIDTH * (hp / MAX_HP))
    fill_rect = pygame.Rect(bar_x, bar_y, fill_width, HP_BAR_HEIGHT)
    pygame.draw.rect(screen, pygame.Color(get_hp_bar_color(hp)), fill_rect)

    hp_text_surface = hint_font.render(f"HP: {hp}/{MAX_HP}", True, WHITE)
    hp_text_rect = hp_text_surface.get_rect(topleft=(bar_x, bar_y + HP_BAR_HEIGHT + 4))
    screen.blit(hp_text_surface, hp_text_rect)

def show_hp_heal_popup(amount_healed):
    """
    Starts a short-lived floating "+<amount> HP" text callout, shown in
    green just under the HP bar to confirm a heal just happened.
    """
    global hp_heal_popup_text, hp_heal_popup_start_time

    hp_heal_popup_text = f"+{amount_healed} HP"
    hp_heal_popup_start_time = pygame.time.get_ticks()

def render_outlined_text(text, font, fill_color, outline_color, outline_width=2):
    """
    Renders text with a solid outline behind it, by drawing the outline
    colour at a ring of offsets around the text and the fill colour on
    top, dead centre. Used for the HP heal callout so it stays readable
    against any background colour.
    """
    base_surface = font.render(text, True, fill_color)
    outline_surface = pygame.Surface(
        (base_surface.get_width() + outline_width * 2, base_surface.get_height() + outline_width * 2),
        pygame.SRCALPHA,
    )

    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx == 0 and dy == 0:
                continue
            outline_text = font.render(text, True, outline_color)
            outline_surface.blit(outline_text, (outline_width + dx, outline_width + dy))

    outline_surface.blit(base_surface, (outline_width, outline_width))
    return outline_surface


def draw_hp_heal_popup():
    """
    Draws the floating "+80 HP" text (green fill, black outline) just
    above the sprite while it's still within its display duration, then
    stops automatically once that time has passed.
    """
    if hp_heal_popup_text is None:
        return

    elapsed = pygame.time.get_ticks() - hp_heal_popup_start_time
    if elapsed > HP_HEAL_POPUP_DURATION_MS:
        return

    popup_surface = render_outlined_text(
        hp_heal_popup_text, hint_font, pygame.Color(HP_HEAL_POPUP_COLOR), BLACK
    )
    sprite_screen_x, sprite_screen_y = world_to_screen(sprite_draw_pos[0], sprite_draw_pos[1])
    popup_rect = popup_surface.get_rect(
        center=(int(sprite_screen_x), int(sprite_screen_y) - SPRITE_CHAR_RADIUS - 20)
    )
    screen.blit(popup_surface, popup_rect)



running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif game_state == "TITLE":
            handle_title_input(event)
        elif game_state == "DIALOGUE":
            handle_dialogue_input(event)
        elif game_state == "DESERT_ROOM":
            handle_desert_room_input(event)
        elif game_state == "ITEM_POPUP":
            handle_item_popup_input(event)
        elif game_state == "PAUSED":
            handle_pause_input(event)
        elif game_state in ("SETTINGS_PLACEHOLDER", "SAVE_PLACEHOLDER"):
            handle_placeholder_input(event)

    if game_state == "DESERT_ROOM":
        handle_desert_movement()
        update_camera()
        check_decoy_flower_trigger()
        check_ice_flower_trigger()
        update_nearby_interactable()

    if game_state not in ("PAUSED", "SETTINGS_PLACEHOLDER", "SAVE_PLACEHOLDER", "ITEM_POPUP"):
        update_heat_drain()
        update_sprite_animation()

    if game_state == "DESERT_ROOM" and previous_game_state != "DESERT_ROOM":
        desert_hint_start_time = pygame.time.get_ticks()
        hp_bar_visible = True
        activate_heat_drain()
    previous_game_state = game_state

    if game_state == "TITLE":
        draw_title_screen()
    elif game_state == "DIALOGUE":
        update_text_reveal()
        if dialogue_backdrop_state == "DESERT_ROOM":
            draw_desert_room()
        else:
            screen.fill(BARREN_BG)
        current_line = dialogue_lines[current_line_index]
        if current_line == "\"Quick - go left! There should be a flower that way that can help you.\"":
            draw_left_arrow_hint()
        draw_text_box(current_line[:revealed_chars])
    elif game_state == "DESERT_ROOM":
        draw_desert_room()
    elif game_state == "ITEM_POPUP":
        draw_item_popup()
    elif game_state == "PAUSED":
        draw_pause_menu()
    elif game_state in ("SETTINGS_PLACEHOLDER", "SAVE_PLACEHOLDER"):
        draw_placeholder_screen()

    if hp_bar_visible:
        draw_hp_bar()
        draw_hp_heal_popup()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

