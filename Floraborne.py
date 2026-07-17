"""
Floraborne, a narrative exploration game built with Pygame.

"""
import pygame
import sys
import math

pygame.init()

# --- Display setup
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Floraborne")
clock = pygame.time.Clock()

# --- Desert control hint (fades out after appearing)
previous_game_state = None
desert_hint_start_time = 0
HINT_VISIBLE_DURATION = 2000
HINT_FADE_DURATION = 2000

# --- Colours (RGB tuples) - softened, flower-inspired palette
BARREN_BG = (238, 200, 190)
WHITE = (255, 248, 240)
HIGHLIGHT = (240, 130, 60)
BLACK = (45, 35, 40)
DESERT_BG = (194, 178, 128)
SWAMP_BG = (70, 90, 60)
TITLE_BG_TOP = (255, 226, 214)
TITLE_BG_BOTTOM = (240, 188, 205)
TITLE_TEXT_COLOR = (196, 74, 132)
SOFT_HINT_COLOR = (205, 175, 185)
STATS_TEXT_COLOR = (120, 30, 60)

# --- Fonts (pygame doesn't ship a dedicated pixel font, so this tries a
# few common blocky/monospace system fonts for a more retro feel, and
# falls back to the plain default font if none of them are installed)
def get_pixel_font(size):
    pixel_font_candidates = ["couriernew", "consolas", "menlo", "monaco", "dejavusansmono"]
    available_fonts = pygame.font.get_fonts()
    for candidate in pixel_font_candidates:
        if candidate in available_fonts:
            return pygame.font.SysFont(candidate, size, bold=True)
    return pygame.font.SysFont(None, size)


title_font = get_pixel_font(52)
menu_font = get_pixel_font(30)
dialogue_font = get_pixel_font(20)
hint_font = get_pixel_font(16)

# --- Core state machine
# Valid values so far: "TITLE", "DIALOGUE", "DIALOGUE_CHOICE", "ROOM", "ITEM_POPUP", "PAUSED", "SETTINGS_PLACEHOLDER", "SAVE_PLACEHOLDER", "GAME_OVER", "WIN"
game_state = "TITLE"

# --- Title screen menu state
selected_option = 0
menu_options = ["New Game", "Quit"]
menu_option_rects = []

# --- Player data
PROTAGONIST_SIZE = 130
PROTAGONIST_HEIGHT = 190
PLAYER_SPEED = 4
protagonist = {
    "name": "Protagonist",
    "x": 1200,
    "y": SCREEN_HEIGHT // 2,
}
protagonist_facing = "right"  # "right" or "left" - flips her sprite horizontally while walking left

# --- Pause menu state ---------------------------------------------------
pause_menu_options = ["Settings", "Save", "Quit Game"]
pause_selected_option = 0
pause_option_rects = []
paused_from_state = None

item_popup_title = ""
item_popup_description = ""
item_popup_icon_image = None
previous_state_before_popup = None
ITEM_POPUP_ICON_SIZE = 64

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
next_state_after_dialogue = "ROOM"
dialogue_backdrop_state = None
DIALOGUE_BOX_HEIGHT = 150  # Fixed height so the box never grows to fit long text; overflow scrolls instead.
dialogue_black_backdrop = False  # True only during the desert-to-swamp loading screen (see start_loading_screen_dialogue)

# --- Desert biome opening dialogue -------------------------------------------------
DESERT_INTRO_TEXT = [
    "The heat is immediate and overwhelming.",
    "Sand stretches in every direction.",
    "A long stretch of withered flowers sits in the distance, sad and pensive.",
    "This place is dangerous - keep an eye on your health.",
    "The heat is already starting to get to you.",
    "Look around... maybe that glowing flower over there could help?",
]

# --- Decoy flower (desert opening) ----------------------------------
DECOY_FLOWER_POS = (1400, 300)
DECOY_FLOWER_RADIUS = 50
DECOY_FLOWER_COLOR = (180, 160, 90)
decoy_flower_encountered = False

# --- Adding a glow to the decoy flower as well ---------------------------
DECOY_FLOWER_GLOW_COLOR = (255, 230, 150)
DECOY_FLOWER_GLOW_MIN_RADIUS = 18
DECOY_FLOWER_GLOW_MAX_RADIUS = 26
DECOY_FLOWER_GLOW_PERIOD = 900

ICE_FLOWER_POS = (100, 300)
ICE_FLOWER_COLOR = (180, 220, 240)
ICE_FLOWER_TRIGGER_RADIUS = 60
ice_flower_encountered = False
ICE_FLOWER_GLOW_COLOR = (200, 240, 255)
ICE_FLOWER_GLOW_MIN_RADIUS = 18
ICE_FLOWER_GLOW_MAX_RADIUS = 26
ICE_FLOWER_GLOW_PERIOD = 900
ICE_FLOWER_HINT_TEXT = [
    "\"Look - that one over there! Press E to pick it up!\"",
]
WRONG_FLOWER_BEFORE_ICE_TEXT = [
    "\"Does that look like the right flower to you? Gosh, your botanical knowledge is poor. Keep going left!\"",
]
SPRITE_FLOWER_WARNING_TEXT = [
    "A small butterfly darts out of nowhere, wings glowing faintly, and hovers right in front of you.",
    "\"Wait, wait, WAIT - don't pick that!\"",
    "\"It's just a common flower, it doesn't do anything. And with the world already this dried up, we need to let whatever can still grow, grow.\"",
    "\"Oh - sorry, I should introduce myself. I'm Sprite. I'll be keeping you out of trouble from now on, apparently.\"",
    "\"Anyway. If you want, I can show you how to deal with that heat that's been quietly cooking you this whole time.\"",
    "\"Quick - go left! There should be a flower that way that can help you.\"",
]
DECOY_FLOWER_EATEN_TEXT = [
    "Her wings flicker and dim, and her expression falls.",
    "\"...I told you not to eat that.\"",
    "\"I really thought you'd listen to me on this one.\"",
]

# --- Sprite companion (placeholder appearance for now) -------------------
SPRITE_CHAR_COLOR = (255, 240, 150)
SPRITE_CHAR_RADIUS = 15
SPRITE_CHAR_OFFSET = (35, -35)
SPRITE_ENTRANCE_DURATION = 700
SPRITE_ENTRANCE_START_Y = -50
SPRITE_HOVER_AMPLITUDE = 6
SPRITE_HOVER_PERIOD = 1200
sprite_state = "HIDDEN"
sprite_entrance_start_time = 0
sprite_draw_pos = [0, 0]

# --- HP ------------------------------------------------
MAX_HP = 100
hp = MAX_HP
heat_drain_active = False
heat_immune = False
last_hp_tick_time = 0
HP_DRAIN_INTERVAL = 700  # Bumped down from 1000 so the heat drains HP slightly quicker and feels more urgent
HP_BAR_POS = (20, 20)
HP_BAR_WIDTH = 200
HP_BAR_HEIGHT = 20
HP_BAR_COLOR_HIGH = "#2ECC71"
HP_BAR_COLOR_MID = "#E67E22"
HP_BAR_COLOR_LOW = "#E74C3C"
HP_HEAL_POPUP_COLOR = "#2ECC71"
hp_bar_visible = False
hp_heal_popup_text = None
hp_heal_popup_start_time = 0
HP_HEAL_POPUP_DURATION_MS = 1500

# --- For allowing sprite tutorial-ish intro.
dialogue_on_complete = None

# --- This is for making "press E to interact" work:
nearby_interactable = None

# --- To stop the ice flower from being collected more than once/remaining on screen once eaten.
ice_flower_collected = False

# --- Desert world & camera scrolling --------------------------------------
DESERT_WORLD_WIDTH = 1600
SWAMP_WORLD_WIDTH = 1650  # Bumped up slightly so the bigger exit door has room to fit fully on-screen
camera_x = 0

# --- Room system (background/world width driven by whichever room is active) ---
current_room = "desert"
ROOM_CONFIG = {
    "desert": {
        "bg_color": DESERT_BG,
        "world_width": DESERT_WORLD_WIDTH,
    },
    "swamp": {
        "bg_color": SWAMP_BG,
        "world_width": SWAMP_WORLD_WIDTH,
    },
}

# --- Arrow directing player to go left ---------------------------------------------
LEFT_ARROW_COLOR = (255, 221, 89)
LEFT_ARROW_FLASH_PERIOD = 500
LEFT_ARROW_CENTER = (80, 260)
LEFT_ARROW_SIZE = 40

sprite_friendship_level = 0
decoy_flower_eaten = False
rat_friendship_level = 0

# --- Sprite's true introduction (View 7) --------------------------------
sprite_true_intro_played = False
SPRITE_TRUE_INTRO_TEXT = [
    "\"See? All better now!\" She does a little spin in the air, clearly pleased with herself.",
    "\"That's lesson one: nature can heal just as easily as it can hurt you - if you actually bother to ask it properly.\"",
    "\"Right. Since you're not actively dying anymore, I suppose I owe you a proper introduction.\" She clears her throat, mock-formal. \"I am - or rather, I was - a fully trained, very seasoned herbalist. Tinctures, remedies, the occasional bit of showing off. I was good.\"",
    "\"I was brewing something at home, actually, the exact moment that whole 'gigantic surge of magic' business happened. Whatever I was holding in my hands at the time didn't exactly play nice with all that raw power in the air.\"",
    "\"Next thing I know - poof. This.\" She gestures at her small glowing wings, thoroughly unimpressed. \"A butterfly. No hands, no proper body to speak of, and somehow still expected to fix everything.\"",
    "\"Which is a problem, considering I can't so much as hold a mixing spoon anymore, let alone brew a potion myself. And Floraborne isn't exactly going to save itself.\"",
    "\"So. Lucky you. I need actual hands, and you've apparently got magic to spare. Whether that's enough to be useful remains... to be seen.\"",
    "\"So? Are you in properly, or is this going to be a waste of both our time?\"",
]
SPRITE_CHOICE_1_OPTIONS = [
    "I'm in. Whatever it takes to save this place.",
    "I'll try my best, I guess.",
    "Can't you just figure out some way to do it yourself?",
]
SPRITE_CHOICE_1_DELTAS = [3, 1, 0]
SPRITE_CHOICE_1_REACTIONS = [
    "\"Huh. Wasn't expecting that much enthusiasm out of you.\" A small, genuine smile creeps in despite prior reservations. \"...Don't make me regret this.\"",
    "\"...I'll take it. Better than nothing, I suppose.\"",
    "\"...Did you not hear literally anything I just said? No hands. No body. That's rather the point.\" She sighs. \"Congratulations. You're stuck with the job anyway.\"",
]
SPRITE_BETWEEN_CHOICES_TEXT = [
    "She's already back to business, tone brisk. \"Anyway. Since we're apparently doing this together now-\"",
    "\"-let me ask you something.\"",
    "\"If we're going to have any hope of putting the balance back together, I need to know you actually care about what we're fixing - not just about getting to the other side of it. So. Does any of this-\" she gestures at the withered dunes \"-actually mean something to you?\"",
]
SPRITE_CHOICE_2_OPTIONS = [
    "It means everything. The balance of nature is what keeps a place like this alive.",
    "I don't understand it the way you do yet. But I want to.",
    "Honestly? I just want to get through this as fast as possible.",
]
SPRITE_CHOICE_2_DELTAS = [3, 1, 0]
SPRITE_CHOICE_2_REACTIONS = [
    "Her light glows warmer, softer. \"...Okay. Good answer. Maybe you're not completely hopeless after all.\"",
    "\"Fair enough. I suppose that's what I'm here for - to help you actually understand it.\"",
    "\"Wow. Okay.\" A pause, stung. \"Remind me again why I'm bothering to help you?\"",
]

# --- Potion recipe & checklist introduction (View 8) --------------------
POTION_RECIPE_INTRO_TEXT = [
    "\"Right, business time.\" She hovers upright, suddenly all business. \"Good news: there's a way out of this desert.\"",
    "\"Bad news: it's a swamp now. Used to be the most beautiful lakes and rivers in all of Floraborne, before everything got ruined. These days it's just poison fog and mud, unless we're careful.\"",
    "\"Lucky for you, I happen to know the recipe for an anti-poison potion that'll get us through it safely.\"",
    "A small checklist flickers into the top-right corner of your vision - two flowers, both unticked.",
    "\"There. Now you've got a list, and I've got approximately zero patience left for standing around. Go find the first one!\"",
    "\"Go on, then. Sniff it out like the little magic bloodhound you apparently are.\"",
]

# --- Reusable dialogue-choice component ---------------------------------
choice_options = []
choice_deltas = []
choice_reactions = []
choice_friendship_target = None
choice_on_complete = None
choice_selected_option = 0
choice_option_rects = []

# --- Potion checklist widget ---------------------------------------------
checklist_visible = False
CHECKLIST_RIGHT_MARGIN = 20
CHECKLIST_POS = (SCREEN_WIDTH - 210, 20)
CHECKLIST_WIDTH = 190  # Fallback only now - each checklist's real width is computed from its longest item name so text always fits
CHECKLIST_LINE_HEIGHT = 26
CHECKLIST_CHECKBOX_SIZE = 14

# --- Room timer (90-second countdown, starts once View 8 finishes) -------
ROOM_TIMER_DURATION_MS = 90000
room_timer_active = False
room_timer_start_time = 0

# --- Ingredient flowers (View 8's checklist puzzle) ----------------------
INGREDIENT_FLOWER_1_NAME = "Sunroot Bloom"
INGREDIENT_FLOWER_2_NAME = "Cactus Blossom"
INGREDIENT_FLOWER_1_POS = (700, 220)
INGREDIENT_FLOWER_2_POS = (1020, 380)
INGREDIENT_FLOWER_TRIGGER_RADIUS = 50
INGREDIENT_FLOWER_WITHERED_COLOR = (150, 130, 90)
INGREDIENT_FLOWER_BLOOMED_COLOR = (255, 140, 180)
ingredient_flower_1_collected = False
ingredient_flower_2_collected = False
DECOY_WEED_POS = (860, 380)
DECOY_WEED_TRIGGER_RADIUS = 50
DECOY_WEED_COLOR = (120, 110, 70)
decoy_weed_interacted = False
INGREDIENT_WATERED_REACTION = "Sprite's light dips toward the flower, and it blooms back to life in an instant. One down!"
DECOY_WEED_REACTION = "\"That one's just a common weed - no use to us. Keep looking.\""
SWAMP_TRANSITION_TEXT = [
    "\"That's both ingredients - let's get this brewed before that fog gets any worse.\"",
    "A moment later, the potion's mixed and swallowed. The air already feels a little safer to breathe.",
    "\"Right - that's the swamp taken care of, mostly. Let's move. The sooner we're through, the better.\"",
]

# --- Loading screen between the desert and the swamp ----------------------
LOADING_TEXT = [
    "Time passes as the two of you make your way onward, the desert's heat finally fading behind you.",
    "The ground grows softer underfoot, the air heavier and damper with every step.",
    "By the time the sand gives way completely, the swamp is already waiting ahead.",
]

# --- Hearts / lives system (confirmed core system) ------------------------
MAX_HEARTS = 3
hearts = MAX_HEARTS
checkpoint_state = "ROOM"  # Only one checkpoint exists so far (desert)
GAME_OVER_TEXT = "You've run out of hearts. Take a breath, then try again."
WIN_TEXT = "You've crossed the swamp safely, potion in hand. Floraborne's balance is one step closer to being restored."

# --- Room timer display (clock icon + repositioned "Time left" text) -----
CLOCK_ICON_SIZE = 36  # Bumped up so it reads clearly bigger than a single heart container icon
TIME_LEFT_TEXT_COLOR = (255, 221, 130)

# --- Heart container icon (replaces the old plain circle hearts) ---------
HEART_ICON_SIZE = 24

# --- Session statistics (global counters, per the project's code requirements) ---
# Deliberately not reset by reset_run_state - these track the whole session,
# not just the current attempt.
games_played = 0
total_deaths = 0
total_wins = 0
fastest_win_time_ms = None
last_run_time_ms = 0
run_start_time = 0
friendship_points_gained = 0

# --- Friendship counter box & flash-on-change effect ----------------------
FRIENDSHIP_BOX_WIDTH = 220
FRIENDSHIP_BOX_HEIGHT = 34
FRIENDSHIP_FLASH_DURATION_MS = 900
FRIENDSHIP_FLASH_COLOR_UP = (46, 204, 113)
FRIENDSHIP_FLASH_COLOR_DOWN = (231, 76, 60)
FRIENDSHIP_TEXT_COLOR = (255, 230, 200)
friendship_flash_start_time = 0
friendship_flash_color = None

# --- Swamp ingredient puzzle (Commit 11) ---------------------------------
SWAMP_CHECKLIST_POS = CHECKLIST_POS  # Reuses the same on-screen slot as the desert checklist, since only one is ever visible at a time
SWAMP_INGREDIENT_FLOWER_1_NAME = "Marshglow Lily"
SWAMP_INGREDIENT_FLOWER_2_NAME = "Bogroot Bell"
SWAMP_INGREDIENT_FLOWER_3_NAME = "Mistpetal Reed"
SWAMP_INGREDIENT_FLOWER_1_POS = (250, 220)
SWAMP_INGREDIENT_FLOWER_2_POS = (600, 380)
SWAMP_INGREDIENT_FLOWER_3_POS = (980, 220)
SWAMP_INGREDIENT_WITHERED_COLOR = (90, 100, 70)
SWAMP_INGREDIENT_BLOOMED_COLOR = (200, 150, 220)
swamp_checklist_visible = False
swamp_potion_brewed = False
swamp_ingredient_flower_1_collected = False
swamp_ingredient_flower_2_collected = False
swamp_ingredient_flower_3_collected = False

# --- Swamp harmful decoys: some now cost HP instead of doing nothing ----
SWAMP_HARMFUL_HP_LOSS = 25
SWAMP_HARMFUL_FLOWER_NAME = "Blistercap Bloom"
SWAMP_HARMFUL_WEED_NAME = "Stingmoss Tangle"
SWAMP_HARMFUL_FLOWER_POS = (420, 320)
SWAMP_HARMFUL_WEED_POS = (800, 400)
SWAMP_HARMFUL_COLOR = (170, 40, 40)
swamp_harmful_flower_eaten = False
swamp_harmful_weed_eaten = False
SWAMP_DECOY_WEED_POS = (150, 380)
SWAMP_DECOY_WEED_COLOR = (80, 90, 60)
swamp_decoy_weed_eaten = False
SWAMP_HARMFUL_FLOWER_REACTION_DESC = (
    "A lurid, blistered bloom that looks almost too vivid to be safe - because "
    "it isn't. Eating it raw burns on the way down and costs you HP. Whatever "
    "it's good for, it isn't this."
)
SWAMP_HARMFUL_WEED_REACTION_DESC = (
    "A tangle of stinging moss disguised as an ordinary weed. It bites back "
    "the moment you swallow it, costing you HP for the trouble."
)
SWAMP_DECOY_WEED_REACTION = "\"That one's just a bit of ordinary swamp weed - no use to us. Keep looking.\""
SWAMP_INGREDIENT_WATERED_REACTION = "Sprite's light dips toward the flower, and it blooms back to life just like the others. One more down!"

# --- HP damage popup (mirrors the existing heal popup, but for harm) -----
HP_DAMAGE_POPUP_COLOR = "#E74C3C"
hp_damage_popup_text = None
hp_damage_popup_start_time = 0
HP_DAMAGE_POPUP_DURATION_MS = 1500

SWAMP_ENTRY_TEXT = [
    "The moment you step onto the mud, Sprite's glow dims slightly, like even she's uneasy here.",
    "\"Alright. That anti-poison potion is the only reason either of us is still breathing in this fog - but breathing isn't the same as getting through.\"",
    "\"If we actually want to cross this place and start putting Floraborne's balance back together, we're going to need something stronger. A real potion - and this one needs three ingredients, not two.\"",
    "A checklist flickers into view - three flowers, all unticked.",
    "\"This swamp isn't going to make it easy, either. Some of what's growing out here isn't just useless - a few of them will actively hurt you if you're careless enough to eat them raw. Look properly before you go grabbing anything.\"",
]
SWAMP_POTION_BREWED_TEXT = [
    "\"That's all three - let's get this potion mixed properly this time.\"",
    "A moment later, it's done: something for genuinely restoring balance, not just neutralizing poison.",
    "\"Now we just need to find our way across... that bridge up ahead isn't going to fix itself.\"",
]

# --- Bridge repair puzzle (Commit 12) ------------------------------------
SWAMP_BRIDGE_X = 1100
BRIDGE_WIDTH = 24
BRIDGE_TRIGGER_RADIUS = 80  # Bumped up from 60: while the bridge is unfixed, movement is clamped to 65px away from it, so 60 made it impossible to ever get within range
BRIDGE_BROKEN_COLOR = (60, 50, 45)
BRIDGE_FIXED_COLOR = (150, 110, 70)
BRIDGE_GAP_HEIGHT = 120  # Height of the missing chunk in the middle of the unfixed bridge, so the background shows through it
swamp_bridge_fixed = False
TINKER_ITEM_1_NAME = "Rusty Cog"
TINKER_ITEM_2_NAME = "Vine-Bound Plank"
TINKER_ITEM_1_POS = (1000, 200)
TINKER_ITEM_2_POS = (1050, 380)
TINKER_ITEM_COLOR = (140, 140, 150)
tinker_item_1_collected = False
tinker_item_2_collected = False
swamp_bridge_checklist_visible = False
swamp_tinker_potion_brewed = False
TINKER_ITEM_COLLECTED_REACTION = "Sprite scoops the piece up in a flicker of light and tucks it away. \"That's one - just need the other.\""
BRIDGE_INTRO_TEXT = [
    "Sprite hovers toward the broken bridge ahead, her light dimming at the sight of it.",
    "\"That's... not going to hold anyone's weight like that. We need something to patch it up properly - a tinkering potion, this time, not another ingredient brew.\"",
    "\"I've seen scraps of exactly the kind of thing we'd need scattered around here - some old metal, something sturdy enough to bind it.\"",
    "A checklist flickers into view - two scavenged parts, both unticked.",
    "\"Go on then. Two pieces should do it.\"",
]
TINKER_POTION_BREWED_TEXT = [
    "\"That's both pieces - let's get this tinkering potion mixed.\"",
    "A moment later, it's done: something to hold rusted metal and old wood together like it was never broken.",
    "\"Now, let's go patch up that bridge.\"",
]
BRIDGE_FIXED_TEXT = [
    "A few taps with the tinkering potion, and the planks knit themselves back together, solid as new.",
    "\"There - that ought to hold. Let's keep moving.\"",
]

# --- The Rat encounter & backstory (Commit 13) ---------------------------
RAT_POS = (1450, 330)
RAT_COLOR = (90, 80, 70)
RAT_TRIGGER_RADIUS = 140  # Tuned to match the distance at which he should notice the protagonist and start talking on his own, no E press needed
rat_encountered = False
rat_resolved = False
rat_outcome = None  # None, "died", "bitter", or "helped"
rat_facing = "right"  # "right" or "left" - flips his sprite horizontally to face the protagonist, then always mirrors her own facing while following
RAT_FRIENDSHIP_LOW_THRESHOLD = 3   # at or below this -> lowest tier (he runs off and dies)
RAT_FRIENDSHIP_HIGH_THRESHOLD = 8  # at or above this -> highest tier (healed and helping); between the two -> healed but bitter
RAT_ENCOUNTER_TEXT = [
    "Past the bridge, huddled in the shadow of a fallen log, something small and hunched flinches at the sound of your footsteps.",
    "A rat - or what's left of one. Fur matted, one eye swollen shut, breathing shallow and ragged.",
    "\"...Go away.\" His voice is hoarse, more growl than word. \"Don't need help. Don't want it either.\"",
    "Sprite's light dims, hovering carefully at a distance. \"...He's in a bad way. But pushing straight in isn't going to get us anywhere. Try talking to him properly.\"",
]
RAT_PRODDING_INTRO_TEXT = [
    "\"What happened to you?\" you ask, careful to keep your voice gentle.",
    "The rat's good eye narrows, suspicious. \"Why do you care.\" It isn't really a question.",
]
RAT_CHOICE_1_OPTIONS = [
    "I just want to understand what happened to you.",
    "You look like you could use someone to talk to.",
    "Fine - suit yourself. I'll leave you be.",
]
RAT_CHOICE_1_DELTAS = [3, 1, -1]
RAT_CHOICE_1_REACTIONS = [
    "He studies you a long moment, like he's waiting for the catch. There isn't one, apparently. \"...Tch. Fine. Wasn't always like this, you know. Had a life. A den. Things I was proud of.\"",
    "\"...Didn't ask for company.\" But he doesn't tell you to leave again, either. \"There was a den. A life, before. Guess that's gone now, same as everything else.\"",
    "\"...Fine.\" He curls tighter into himself and says nothing else, but doesn't stop you when you crouch down anyway.",
]
RAT_BETWEEN_CHOICES_1_TEXT = [
    "\"I used to run the trade routes through this whole swamp,\" he mutters, almost to himself. \"Knew every safe path, every shortcut. Everyone came to me.\"",
    "\"Then the surge hit. Overnight the whole place turned to poison and mud, and everyone who used to need me just... left. Or didn't make it.\"",
    "\"Didn't have anywhere left to run trade to. So I stayed. Because someone had to know what this place used to be.\"",
]
RAT_CHOICE_2_OPTIONS = [
    "That's not your fault. None of this was.",
    "That sounds really lonely.",
    "Sounds like you just felt sorry for yourself.",
]
RAT_CHOICE_2_DELTAS = [3, 1, -1]
RAT_CHOICE_2_REACTIONS = [
    "Something in his shoulders loosens, just slightly. \"...Wish that were true. But I wasn't just watching, near the end. I made it worse.\"",
    "\"...Lonely doesn't cover it.\" A pause. \"But you're not wrong, either.\"",
    "His good eye snaps back to you, sharp. \"You don't know anything about it.\" But he keeps talking anyway - like he needs to, even now.",
]
RAT_BETWEEN_CHOICES_2_TEXT = [
    "\"Started hoarding, is what I did. Whatever herbs and roots still grew clean, I took for myself instead of sharing them out. Told myself it was just sense - survival.\"",
    "\"But there were others who needed that stuff worse than I did. Sick. Starving. Didn't matter to me at the time.\"",
    "\"By the time I actually looked around at what I'd done, there wasn't anyone left close enough to make it right with.\"",
]
RAT_CHOICE_3_OPTIONS = [
    "Everyone deserves a chance to make things right.",
    "You can still do something about it now.",
    "Sounds like you got what you deserved.",
]
RAT_CHOICE_3_DELTAS = [3, 1, -1]
RAT_CHOICE_3_REACTIONS = [
    "For the first time, his voice properly cracks. \"...Do they. Do I.\" He doesn't sound like he believes it. But he wants to.",
    "\"...Maybe.\" It's barely a whisper. \"Don't know where I'd even start.\"",
    "\"...Yeah.\" He looks away, and for a moment he looks smaller than the state he's already in. \"Yeah, guess I did.\"",
]
RAT_BETWEEN_CHOICES_3_TEXT = [
    "Sprite drifts a little closer, quiet for once. \"For what it's worth - the balance potion we've been carrying was actually meant for this. For healing things this swamp broke.\"",
    "The rat's good eye flicks toward you, then away again. \"...You'd waste that. On me.\"",
    "\"That depends,\" you say, \"on whether you'll actually let us.\"",
    "\"...There's something you should know either way,\" he adds, quieter. \"Past here, there's a door. Whatever's rotting this whole swamp from the inside is holed up behind it, and it isn't going anywhere on its own.\"",
    "\"I've tried facing it myself before. Once. That's half of why I look like this.\" He shakes his head. \"I'm not enough on my own. Whatever happens with us, that door's not staying shut forever.\"",
]
RAT_CHOICE_4_OPTIONS = [
    "We're not leaving until you let us help. Please.",
    "It's your choice. But we came all this way for you.",
    "Forget it - clearly you don't want it.",
]
RAT_CHOICE_4_DELTAS = [3, 1, -1]
RAT_CHOICE_4_REACTIONS = [
    "Something in him finally breaks - not in anger, this time. \"...Okay.\" It's barely audible. \"Okay. Do it, then. Before I change my mind.\"",
    "A long silence. Then, grudgingly: \"...Fine. Do what you're going to do.\"",
    "He flinches, curling away from you entirely. \"...Knew it. Knew you didn't actually mean it.\"",
]
RAT_OUTCOME_DIED_TEXT = [
    "Before you can move, he's already scrambling backward, favouring his bad leg, refusing to look at you.",
    "\"...Don't. I mean it.\" And then he's gone, vanishing into the reeds before either of you can stop him.",
    "Sprite doesn't say anything for a long moment. \"...We should keep moving,\" she finally says, quieter than usual.",
]
RAT_OUTCOME_BITTER_TEXT = [
    "He doesn't pull away this time. The balance potion does its work quickly - his breathing eases, the swelling in his eye already fading.",
    "\"...There.\" He gets shakily to his feet, testing his own weight like he doesn't quite trust it. \"Healed. Happy now?\"",
    "\"Don't expect me to come along, though.\" He won't quite meet your eyes. \"Healed's not the same as forgiven. Not from where I'm standing.\"",
    "He limps off without another word, healed but no less alone than he was before.",
]
RAT_OUTCOME_HELPED_TEXT = [
    "He doesn't pull away this time. The balance potion does its work quickly - his breathing eases, the swelling in his eye fading, his whole body finally unclenching.",
    "He gets to his feet, and for a long moment just... stands there, like he isn't sure what to do with the feeling.",
    "\"...Nobody's asked about any of that in a long time.\" His voice wavers, and he doesn't bother hiding it. \"Or bothered enough to stick around for the answer.\"",
    "\"I'm sorry. For all of it - the hoarding, the running, all of it. I mean that.\"",
    "\"...Let me come with you. Least I can do is help undo some of what I helped break.\"",
    "Sprite's light flares, warm and genuine. \"...Welcome aboard, then.\"",
]

# --- Rat companion, swamp exit door & final battle endings (Commit 14) ---
RAT_FOLLOW_OFFSET = (-35, -35)
rat_state = "HIDDEN"  # "HIDDEN" or "FOLLOWING"
rat_draw_pos = [0, 0]
DOOR_POS = (1580, 300)
DOOR_TRIGGER_RADIUS = 70
DOOR_WIDTH = 110
DOOR_HEIGHT = 260
DOOR_COLOR = (40, 35, 30)
DOOR_TRIM_COLOR = (90, 20, 20)
DOOR_GLOW_COLOR = (220, 40, 40)
DOOR_GLOW_MIN_RADIUS = 70
DOOR_GLOW_MAX_RADIUS = 95
DOOR_GLOW_PERIOD = 1400
door_encountered = False
SPRITE_FRIENDSHIP_HELP_THRESHOLD = 4  # sprite_friendship_level at or above this -> she helps in the final battle
game_over_text_override = None
win_ending_type = None
FINAL_BATTLE_INTRO_TEXT = [
    "Ahead, past where the mud finally turns to solid stone, a heavy door stands sealed into the ruins of an old wall.",
    "Sprite's light flickers uneasily. \"...That's it, isn't it. Whatever's actually been keeping Floraborne broken.\"",
    "Everything the Rat told you about this place comes back at once - something ancient, feeding on all this rot, sitting right behind that door.",
    "\"We're not going to fix any of this from out here,\" Sprite says quietly. \"Whatever's through there, we go in and put a stop to it. Together, if we're doing this at all.\"",
]
ENDING_BOTH_HELP_TEXT = [
    "Sprite's light flares bright, and beside her the Rat sets his jaw, falling into step without hesitation.",
    "\"...Fine. All three of us, then,\" the Rat mutters. \"Let's see this thing off properly.\"",
    "Together, the three of you push through the door - and whatever waited in the dark doesn't stand a chance against you working as one. The last of it dissolves, and the poison finally starts lifting from the whole swamp.",
    "Balance settles back over Floraborne, slow and real - and the surge that took Sprite's and the Rat's human forms finally unwinds too.",
    "They don't waste time deciding what comes next: a new apothecary, built together, right where it all started to heal. Somewhere between all that rebuilding, the two of them fall properly in love - and between the two of them, they teach you absolutely everything they know.",
]
ENDING_SPRITE_ONLY_TEXT = [
    "Sprite's light steadies, resolute. \"...I'm coming. Wherever this goes.\"",
    "The Rat only watches from a distance, and doesn't follow.",
    "Together, you and Sprite push through the door - and between her knowledge and your own resolve, it's enough. Whatever waited in the dark finally goes still.",
    "Floraborne's balance settles back into place, and your journey with Sprite carries on from here.",
    "Somewhere along the way, though, quiet whispers reach you both about the Rat - about a sad, lonely ending that never got the chance to be anything else.",
]
ENDING_RAT_ONLY_TEXT = [
    "The Rat steps forward without a word, jaw set. Sprite's light dims, hanging back. \"...I'm sorry. I can't.\"",
    "So it's just the two of you who push through the door.",
    "Without Sprite's expertise, restoring the balance costs you more than you expected - somewhere in the fight, the same magic that twisted the Rat once catches up to you too.",
    "By the time it's over, Floraborne's balance is restored - and you're a rat, same as him.",
    "\"...Told you nature doesn't forgive carelessness,\" he mutters, though there's no real bite in it anymore. \"Guess you didn't learn a thing from my mistakes.\"",
    "Still, you stay together after that - two rats, sharing whatever life is left to live in a slowly-healing Floraborne.",
]
ENDING_NEITHER_HELP_TEXT = [
    "Neither Sprite nor the Rat move to follow you.",
    "\"...I don't think I can,\" Sprite admits quietly. And the Rat says nothing at all.",
    "You go in anyway, alone - and it isn't enough. Whatever's behind that door was always going to need more than potions.",
    "It needed people who actually trusted each other. And by the time it matters, you never gave either of them a reason to.",
]
SELFISH_LOSS_TEXT = "Neither Sprite nor the Rat trusted you enough to help when it mattered. The potions alone were never going to be enough - not without people willing to stand with you."

# --- Image loading helpers (graceful fallback to the existing plain shapes if a
# file is missing, corrupted, or the wrong format - this also doubles as this
# project's required error-handling for unexpected/bad input) ----------------
def load_image_safe(path, size=None):
    """
    Loads a single-image PNG and optionally scales it. Returns None (instead of
    raising) if the file is missing or can't be read, so callers can fall back
    to drawing the original plain shape instead of crashing the game.
    """
    try:
        image = pygame.image.load(path).convert_alpha()
        if size is not None:
            image = pygame.transform.scale(image, size)
        return image
    except (pygame.error, FileNotFoundError):
        return None


def load_sheet_frame(path, crop_box, size=None):
    """
    Loads one frame out of a larger spritesheet PNG, using pixel coordinates
    (x, y, width, height) rather than a separately-cropped file. Returns None
    on any failure (missing file, bad crop box, unreadable image), the same
    as load_image_safe.
    """
    try:
        sheet = pygame.image.load(path).convert_alpha()
        frame = sheet.subsurface(pygame.Rect(*crop_box)).copy()
        if size is not None:
            frame = pygame.transform.scale(frame, size)
        return frame
    except (pygame.error, FileNotFoundError, ValueError):
        return None


# --- All graphics currently supplied via the asset checklist, loaded once at
# startup. Anything not yet supplied simply stays None, and every draw
# function below already falls back to its original plain shape in that case.
IMAGES = {
    "protagonist": load_image_safe("assets/protagonist.png", (PROTAGONIST_SIZE, PROTAGONIST_HEIGHT)),
    "sprite": load_sheet_frame("assets/sprite_spritesheet.png", (2, 2, 16, 12), (SPRITE_CHAR_RADIUS * 2, SPRITE_CHAR_RADIUS * 2)),
    "rat": load_sheet_frame("assets/grumpy_rat.png", (0, 0, 32, 32), (32, 32)),
    "decoy_flower_desert": load_image_safe("assets/Flower 8 - PINK.png", (32, 32)),
    "ice_flower": load_image_safe("assets/ice_flower.png", (32, 32)),
    "sunroot_bloom": load_image_safe("assets/Flower 8 - ORANGE.png", (32, 32)),
    "cactus_blossom": load_image_safe("assets/Flower 2 - MAGENTA.png", (32, 32)),
    "decoy_weed_desert": load_image_safe("assets/Flower 12 - RED.png", (32, 32)),
    "marshglow_lily": load_image_safe("assets/Flower 12 - YELLOW.png", (32, 32)),
    "bogroot_bell": load_image_safe("assets/Flower 7 - PURPLE.png", (32, 32)),
    "mistpetal_reed": load_image_safe("assets/Flower 7 - BLUE.png", (32, 32)),
    "blistercap_bloom": load_image_safe("assets/Flower 8 - RED.png", (32, 32)),
    "stingmoss_tangle": load_image_safe("assets/Flower 10 - PURPLE.png", (32, 32)),
    "swamp_decoy_weed": load_image_safe("assets/Flower 6 - PINK 2.png", (32, 32)),
    "gear": load_image_safe("assets/gear.png", (32, 32)),
    "log_good": load_image_safe("assets/log_good.png", (32, 32)),
    "clock": load_image_safe("assets/Clock.png", (CLOCK_ICON_SIZE, CLOCK_ICON_SIZE)),
    "heart_container": load_image_safe("assets/heart_container.png", (HEART_ICON_SIZE, HEART_ICON_SIZE)),
}

# A pre-flipped copy of the protagonist sprite, used while she's walking
# left so she visibly faces the direction she's actually moving instead of
# always facing right.
IMAGES["protagonist_flipped"] = (
    pygame.transform.flip(IMAGES["protagonist"], True, False)
    if IMAGES["protagonist"] is not None
    else None
)

# Same idea for the Rat: a pre-flipped copy so he can visibly turn to face
# the protagonist when they first meet, then keep facing whichever way she
# does while he's following her.
IMAGES["rat_flipped"] = (
    pygame.transform.flip(IMAGES["rat"], True, False)
    if IMAGES["rat"] is not None
    else None
)


def draw_image_or_circle(image, world_pos, fallback_color, radius=12):
    """
    Shared helper for every small world object: blits the given pre-loaded
    image centered at world_pos if it loaded successfully, otherwise falls
    back to the original pygame.draw.circle placeholder at the same spot.
    """
    screen_x, screen_y = world_to_screen(*world_pos)
    if image is not None:
        image_rect = image.get_rect(center=(int(screen_x), int(screen_y)))
        screen.blit(image, image_rect)
    else:
        pygame.draw.circle(screen, fallback_color, (int(screen_x), int(screen_y)), radius)


def draw_vertical_gradient(top_color, bottom_color):
    """
    Fills the whole screen with a vertical colour gradient - used as the base
    layer for the desert and swamp backgrounds instead of a single flat fill.
    """
    for y in range(SCREEN_HEIGHT):
        ratio = y / SCREEN_HEIGHT
        color = (
            int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio),
            int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio),
            int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio),
        )
        pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))


# --- Improvised procedural backgrounds (no PNG assets supplied for these yet,
# so these use pygame's own drawing functions to give each biome some depth
# instead of one flat fill colour) --------------------------------------------
DESERT_BG_TOP = (226, 206, 156)
DESERT_BG_BOTTOM = (176, 148, 94)
DESERT_DUNE_COLOR = (163, 138, 88)
DESERT_DUNE_WORLD_X_POSITIONS = [150, 500, 850, 1150, 1450]

SWAMP_BG_TOP = (60, 80, 62)
SWAMP_BG_BOTTOM = (32, 46, 38)
SWAMP_MUD_COLOR = (46, 58, 40)
SWAMP_MUD_WORLD_X_POSITIONS = [250, 600, 950, 1300]
SWAMP_FOG_COLOR = (150, 170, 140)
SWAMP_FOG_WORLD_X_POSITIONS = [100, 450, 800, 1150, 1500]


def draw_desert_background():
    """
    Draws a sandy gradient with a few soft dune shapes (scrolling with the
    camera like everything else in the room) and a fixed sun in the corner,
    standing in for a proper desert background image.
    """
    draw_vertical_gradient(DESERT_BG_TOP, DESERT_BG_BOTTOM)

    for dune_x in DESERT_DUNE_WORLD_X_POSITIONS:
        screen_x, _ = world_to_screen(dune_x, 0)
        pygame.draw.ellipse(
            screen, DESERT_DUNE_COLOR,
            pygame.Rect(int(screen_x) - 140, SCREEN_HEIGHT - 90, 280, 140),
        )

    sun_center = (SCREEN_WIDTH - 90, 80)
    sun_ray_color = (255, 244, 200)
    for ray_angle_degrees in range(0, 360, 30):
        ray_angle = math.radians(ray_angle_degrees)
        inner_x = sun_center[0] + math.cos(ray_angle) * 52
        inner_y = sun_center[1] + math.sin(ray_angle) * 52
        outer_x = sun_center[0] + math.cos(ray_angle) * 72
        outer_y = sun_center[1] + math.sin(ray_angle) * 72
        pygame.draw.line(screen, sun_ray_color, (inner_x, inner_y), (outer_x, outer_y), 4)
    pygame.draw.circle(screen, (255, 236, 179), sun_center, 45)
    pygame.draw.circle(screen, (255, 250, 214), sun_center, 45, 3)


def draw_swamp_background():
    """
    Draws a murky gradient with soft fog patches and darker mud patches
    (both scrolling with the camera), standing in for a proper swamp
    background image.
    """
    draw_vertical_gradient(SWAMP_BG_TOP, SWAMP_BG_BOTTOM)

    for mud_x in SWAMP_MUD_WORLD_X_POSITIONS:
        screen_x, _ = world_to_screen(mud_x, 0)
        pygame.draw.ellipse(
            screen, SWAMP_MUD_COLOR,
            pygame.Rect(int(screen_x) - 100, SCREEN_HEIGHT - 70, 220, 100),
        )

    for fog_x in SWAMP_FOG_WORLD_X_POSITIONS:
        screen_x, _ = world_to_screen(fog_x, 0)
        fog_surface = pygame.Surface((260, 120), pygame.SRCALPHA)
        pygame.draw.ellipse(fog_surface, (*SWAMP_FOG_COLOR, 60), fog_surface.get_rect())
        screen.blit(fog_surface, (int(screen_x) - 130, 130))


def draw_title_screen():
    """
    Draw the game's title text and the New Game / Quit
    menu, highlighting whichever option is currently selected. Also
    shows this session's running statistics (games played and wins)
    underneath the menu once at least one game has been played.
    """
    global menu_option_rects
    draw_vertical_gradient(TITLE_BG_TOP, TITLE_BG_BOTTOM)

    title_surface = title_font.render("FLORABORNE", True, TITLE_TEXT_COLOR)
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 150))
    screen.blit(title_surface, title_rect)

    menu_option_rects = []
    for i, option in enumerate(menu_options):
        color = HIGHLIGHT if i == selected_option else WHITE
        option_surface = menu_font.render(option, True, color)
        option_rect = option_surface.get_rect(center=(SCREEN_WIDTH // 2, 300 + i * 60))
        screen.blit(option_surface, option_rect)
        menu_option_rects.append(option_rect)

    if games_played > 0:
        stats_surface = hint_font.render(
            f"Games played: {games_played}   Wins: {total_wins}", True, STATS_TEXT_COLOR
        )
        stats_rect = stats_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
        screen.blit(stats_surface, stats_rect)


def activate_menu_option(option_name):
    """
    Perform whatever should happen when a title-screen menu option is
    chosen, whether by keyboard (Enter) or mouse click. Choosing "New
    Game" also counts as one more played game for the session's
    statistics, and starts this run's own timer (used for the win
    screen's "time taken" and the session's fastest-win tracking).
    """
    global game_state, dialogue_lines, current_line_index
    global revealed_chars, last_reveal_time, next_state_after_dialogue
    global dialogue_backdrop_state, dialogue_on_complete
    global games_played, run_start_time, friendship_points_gained

    if option_name == "New Game":
        games_played += 1
        friendship_points_gained = 0
        run_start_time = pygame.time.get_ticks()
        dialogue_lines = CATASTROPHE_INTRO_TEXT
        current_line_index = 0
        revealed_chars = 0
        last_reveal_time = pygame.time.get_ticks()
        next_state_after_dialogue = "ROOM"
        dialogue_backdrop_state = None
        dialogue_on_complete = "START_DESERT_INTRO"
        game_state = "DIALOGUE"
    elif option_name == "Quit":
        pygame.quit()
        sys.exit()


def handle_title_input(event):
    """
    Handle a single Pygame event while the title screen is active.
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
    Draw the dialogue box at the bottom of the screen. The box is always
    the same fixed size (DIALOGUE_BOX_HEIGHT) rather than growing to fit
    however much text is currently revealed - once the revealed text has
    more wrapped lines than the box can hold, only the most recently
    revealed lines are shown (older lines scroll out of view as more text
    is typed out), so long lines never spill past the box edges or
    collide with the "Press SPACE to continue" hint or anything else on
    screen. While dialogue_black_backdrop is True (the desert-to-swamp
    loading screen), this also paints the whole screen black first so
    nothing behind the box is visible.
    """
    if dialogue_black_backdrop:
        screen.fill(BLACK)

    box_width = SCREEN_WIDTH - 100
    max_text_width = box_width - 40
    wrapped_lines = wrap_text(text, dialogue_font, max_text_width)
    line_height = dialogue_font.get_linesize()

    box_height = DIALOGUE_BOX_HEIGHT
    box_bottom = SCREEN_HEIGHT - 30
    box_top = box_bottom - box_height
    box_rect = pygame.Rect(50, box_top, box_width, box_height)

    pygame.draw.rect(screen, BLACK, box_rect, border_radius=18)
    pygame.draw.rect(screen, WHITE, box_rect, 3, border_radius=18)

    max_visible_lines = max(1, (box_height - 50) // line_height)
    visible_lines = wrapped_lines[-max_visible_lines:]

    for i, line in enumerate(visible_lines):
        line_surface = dialogue_font.render(line, True, WHITE)
        line_rect = line_surface.get_rect(topleft=(box_rect.x + 20, box_rect.y + 20 + i * line_height))
        screen.blit(line_surface, line_rect)

    hint_surface = hint_font.render("Press SPACE to continue", True, SOFT_HINT_COLOR)
    hint_rect = hint_surface.get_rect(bottomright=(box_rect.right - 15, box_rect.bottom - 10))
    screen.blit(hint_surface, hint_rect)


def update_text_reveal():
    """
    Advance the typewriter-style text reveal by one character.
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
    Three dialogues reveal their checklist mid-conversation rather than
    waiting for the whole thing to finish: the potion recipe intro
    (desert, View 8), the swamp's entry dialogue (Commit 11), and the
    bridge-intro dialogue (Commit 12). On the final line,
    dialogue_on_complete decides what happens next: it either chains
    straight into another dialogue, switches rooms, or simply switches
    to next_state_after_dialogue as normal.

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

            if dialogue_lines is POTION_RECIPE_INTRO_TEXT and current_line_index == 3 and not checklist_visible:
                show_ingredient_checklist()
            elif dialogue_lines is SWAMP_ENTRY_TEXT and current_line_index == 3 and not swamp_checklist_visible:
                show_swamp_checklist()
            elif dialogue_lines is BRIDGE_INTRO_TEXT and current_line_index == 3 and not swamp_bridge_checklist_visible:
                show_swamp_bridge_checklist()

            if current_line_index >= len(dialogue_lines):
                if dialogue_on_complete == "START_DESERT_INTRO":
                    dialogue_on_complete = None
                    start_desert_intro_dialogue()
                elif dialogue_on_complete == "SPRITE_CHOICE_1":
                    dialogue_on_complete = None
                    start_sprite_choice_1()
                elif dialogue_on_complete == "SPRITE_BETWEEN_CHOICES":
                    dialogue_on_complete = None
                    start_sprite_between_choices_dialogue()
                elif dialogue_on_complete == "SPRITE_CHOICE_2":
                    dialogue_on_complete = None
                    start_sprite_choice_2()
                elif dialogue_on_complete == "START_POTION_RECIPE_INTRO":
                    dialogue_on_complete = None
                    start_potion_recipe_intro_dialogue()
                elif dialogue_on_complete == "START_LOADING_SCREEN":
                    dialogue_on_complete = None
                    start_loading_screen_dialogue()
                elif dialogue_on_complete == "START_SWAMP_ROOM":
                    dialogue_on_complete = None
                    start_swamp_room()
                    start_swamp_entry_dialogue()
                elif dialogue_on_complete == "START_BRIDGE_INTRO":
                    dialogue_on_complete = None
                    start_bridge_intro_dialogue()
                elif dialogue_on_complete == "RAT_PRODDING_INTRO":
                    dialogue_on_complete = None
                    start_rat_prodding_intro_dialogue()
                elif dialogue_on_complete == "RAT_CHOICE_1":
                    dialogue_on_complete = None
                    start_rat_choice_1()
                elif dialogue_on_complete == "RAT_BETWEEN_CHOICES_1":
                    dialogue_on_complete = None
                    start_rat_between_choices_1_dialogue()
                elif dialogue_on_complete == "RAT_CHOICE_2":
                    dialogue_on_complete = None
                    start_rat_choice_2()
                elif dialogue_on_complete == "RAT_BETWEEN_CHOICES_2":
                    dialogue_on_complete = None
                    start_rat_between_choices_2_dialogue()
                elif dialogue_on_complete == "RAT_CHOICE_3":
                    dialogue_on_complete = None
                    start_rat_choice_3()
                elif dialogue_on_complete == "RAT_BETWEEN_CHOICES_3":
                    dialogue_on_complete = None
                    start_rat_between_choices_3_dialogue()
                elif dialogue_on_complete == "RAT_CHOICE_4":
                    dialogue_on_complete = None
                    start_rat_choice_4()
                elif dialogue_on_complete == "START_RAT_FOLLOWING":
                    dialogue_on_complete = None
                    start_rat_following()
                elif dialogue_on_complete == "RESOLVE_FINAL_BATTLE":
                    dialogue_on_complete = None
                    resolve_final_battle()
                elif dialogue_on_complete == "ACTIVATE_WIN_ENDING":
                    dialogue_on_complete = None
                    activate_win_ending()
                elif dialogue_on_complete == "ACTIVATE_SELFISH_LOSS":
                    dialogue_on_complete = None
                    activate_selfish_loss()
                elif dialogue_on_complete == "RESOLVE_RAT_OUTCOME":
                    dialogue_on_complete = None
                    resolve_rat_outcome()
                else:
                    game_state = next_state_after_dialogue
                    dialogue_on_complete = None


def start_swamp_entry_dialogue():
    """
    Plays the swamp's entry dialogue (Commit 11): Sprite explains that
    crossing this area for real requires a stronger, three-ingredient
    potion, and warns that some of what's growing here is actively
    harmful. The checklist for this potion pops in mid-dialogue, handled
    in handle_dialogue_input, the same way the desert's did. Also turns
    off the loading screen's black backdrop, now that it's done its job.
    """
    global dialogue_lines, current_line_index, revealed_chars, last_reveal_time
    global next_state_after_dialogue, dialogue_backdrop_state, dialogue_on_complete, game_state
    global dialogue_black_backdrop

    dialogue_black_backdrop = False
    dialogue_lines = SWAMP_ENTRY_TEXT
    current_line_index = 0
    revealed_chars = 0
    last_reveal_time = pygame.time.get_ticks()
    next_state_after_dialogue = "ROOM"
    dialogue_backdrop_state = "ROOM"
    dialogue_on_complete = None
    game_state = "DIALOGUE"


def show_swamp_checklist():
    """
    Makes the swamp's 3-ingredient checklist visible. Called the instant
    the swamp entry dialogue reaches the line about it appearing (see
    handle_dialogue_input). Unlike the desert's checklist, this one has
    no countdown timer.
    """
    global swamp_checklist_visible
    swamp_checklist_visible = True


def start_bridge_intro_dialogue():
    """
    Plays the bridge-intro dialogue (Commit 12): Sprite spots the broken
    bridge and explains that crossing it needs a tinkering potion made
    from two scavenged parts. The checklist for those parts pops in
    mid-dialogue, handled in handle_dialogue_input, the same way the
    swamp's own ingredient checklist did.
    """
    global dialogue_lines, current_line_index, revealed_chars, last_reveal_time
    global next_state_after_dialogue, dialogue_backdrop_state, dialogue_on_complete, game_state

    dialogue_lines = BRIDGE_INTRO_TEXT
    current_line_index = 0
    revealed_chars = 0
    last_reveal_time = pygame.time.get_ticks()
    next_state_after_dialogue = "ROOM"
    dialogue_backdrop_state = "ROOM"
    dialogue_on_complete = None
    game_state = "DIALOGUE"


def show_swamp_bridge_checklist():
    """
    Makes the bridge-repair checklist visible. Called the instant the
    bridge-intro dialogue reaches the line about it appearing (see
    handle_dialogue_input). Reuses the same on-screen slot as the
    swamp's own ingredient checklist, since that one is already hidden
    by the time this appears.
    """
    global swamp_bridge_checklist_visible
    swamp_bridge_checklist_visible = True


def start_desert_intro_dialogue():
    """
    Kicks off the desert's own opening dialogue (DESERT_INTRO_TEXT).
    """
    global dialogue_lines, current_line_index, revealed_chars, last_reveal_time
    global next_state_after_dialogue, dialogue_backdrop_state, game_state

    dialogue_lines = DESERT_INTRO_TEXT
    current_line_index = 0
    revealed_chars = 0
    last_reveal_time = pygame.time.get_ticks()
    next_state_after_dialogue = "ROOM"
    dialogue_backdrop_state = "ROOM"
    game_state = "DIALOGUE"


def start_loading_screen_dialogue():
    """
    Plays a short black loading-style screen between the desert and the
    swamp: a few lines about time passing on the journey, shown over a
    plain black background instead of the room (see dialogue_black_backdrop
    and draw_text_box). Chains straight into the swamp room once the text
    finishes.
    """
    global dialogue_lines, current_line_index, revealed_chars, last_reveal_time
    global next_state_after_dialogue, dialogue_backdrop_state, dialogue_on_complete
    global dialogue_black_backdrop, game_state

    dialogue_lines = LOADING_TEXT
    current_line_index = 0
    revealed_chars = 0
    last_reveal_time = pygame.time.get_ticks()
    next_state_after_dialogue = "ROOM"
    dialogue_backdrop_state = "ROOM"
    dialogue_black_backdrop = True
    dialogue_on_complete = "START_SWAMP_ROOM"
    game_state = "DIALOGUE"

def handle_room_movement():
    """
    Update the protagonist's position based on which movement keys are
    currently held down (arrow keys or WASD), bounded by the current
    room's world width, and further clamped at the swamp's bridge until
    it's been repaired (Commit 12) so the player can't just walk across
    the broken gap. Also tracks protagonist_facing so her sprite can be
    flipped horizontally in draw_room() while she's walking left, rather
    than always facing right.
    """
    global protagonist_facing

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        protagonist["x"] -= PLAYER_SPEED
        protagonist_facing = "left"
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        protagonist["x"] += PLAYER_SPEED
        protagonist_facing = "right"
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        protagonist["y"] -= PLAYER_SPEED
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        protagonist["y"] += PLAYER_SPEED

    room_width = ROOM_CONFIG[current_room]["world_width"]
    half_width = PROTAGONIST_SIZE // 2
    half_height = PROTAGONIST_HEIGHT // 2
    protagonist["x"] = max(half_width, min(room_width - half_width, protagonist["x"]))
    protagonist["y"] = max(half_height, min(SCREEN_HEIGHT - half_height, protagonist["y"]))

    if current_room == "swamp" and not swamp_bridge_fixed:
        protagonist["x"] = min(protagonist["x"], SWAMP_BRIDGE_X - half_width)


def draw_room():
    """
    Draw whichever biome is currently active (current_room): the shared
    background/scaffolding (fill colour from ROOM_CONFIG, protagonist,
    sprite companion, interaction hint, control hint) plus that room's
    own one-off story elements. That's the desert's decoy flower, ice
    flower, and ingredient checklist puzzle, or the swamp's own
    3-ingredient puzzle, harmful decoys (Commit 11), bridge/tinker
    items (Commit 12), the Rat past the bridge (Commit 13), and the
    exit door once he's resolved (Commit 14). The Rat is drawn at his
    fixed spot until he's a following companion, at which point
    draw_rat_companion() takes over instead, alongside Sprite.
    """
    if current_room == "desert":
        draw_desert_background()
        if not decoy_flower_eaten:
            draw_decoy_flower_glow()
            draw_decoy_flower()
        if not ice_flower_collected:
            draw_ice_flower_glow()
            draw_ice_flower()
        draw_ingredient_flowers()
    elif current_room == "swamp":
        draw_swamp_background()
        draw_swamp_flowers()
        draw_tinker_items()
        draw_bridge()
        if swamp_bridge_fixed and rat_state != "FOLLOWING":
            draw_rat()
        if rat_resolved:
            draw_door()
    else:
        screen.fill(ROOM_CONFIG[current_room]["bg_color"])

    draw_interaction_hint()

    protagonist_screen_x, protagonist_screen_y = world_to_screen(protagonist["x"], protagonist["y"])
    protagonist_rect = pygame.Rect(0, 0, PROTAGONIST_SIZE, PROTAGONIST_HEIGHT)
    protagonist_rect.center = (int(protagonist_screen_x), int(protagonist_screen_y))
    protagonist_image = IMAGES["protagonist_flipped"] if protagonist_facing == "left" else IMAGES["protagonist"]
    if protagonist_image is not None:
        screen.blit(protagonist_image, protagonist_rect)
    else:
        pygame.draw.rect(screen, WHITE, protagonist_rect)

    draw_sprite_character()
    if rat_state == "FOLLOWING":
        draw_rat_companion()
    draw_friendship_points_counter()
    draw_control_hint()

def draw_control_hint():
    """
    Draw a temporary "Use ARROW KEYS or WASD to move" prompt. Only shown
    while actually free to move around the room, so it can never overlap a
    dialogue box or any other overlay.
    """
    if game_state != "ROOM":
        return

    elapsed = pygame.time.get_ticks() - desert_hint_start_time
    total_duration = HINT_VISIBLE_DURATION + HINT_FADE_DURATION

    if elapsed >= total_duration:
        return

    if elapsed <= HINT_VISIBLE_DURATION:
        alpha = 255
    else:
        fade_elapsed = elapsed - HINT_VISIBLE_DURATION
        alpha = max(0, 255 - int((fade_elapsed / HINT_FADE_DURATION) * 255))

    hint_surface = menu_font.render("Use ARROW KEYS or WASD to move", True, WHITE)
    hint_surface.set_alpha(alpha)
    hint_rect = hint_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
    screen.blit(hint_surface, hint_rect)


def draw_friendship_points_counter():
    """
    Draws this run's running total of friendship points gained (from every
    Sprite/Rat dialogue choice so far this game) inside a small box in the
    top-centre of the screen, clear of the HP bar/hearts on the left and
    the checklist on the right. Briefly flashes/sparkles green when the
    total just went up, or red when it just went down, fading back to its
    normal look shortly after (see trigger_friendship_flash).
    """
    box_rect = pygame.Rect(0, 0, FRIENDSHIP_BOX_WIDTH, FRIENDSHIP_BOX_HEIGHT)
    box_rect.center = (SCREEN_WIDTH // 2, 30)

    border_color = SOFT_HINT_COLOR
    elapsed = pygame.time.get_ticks() - friendship_flash_start_time
    if friendship_flash_color is not None and elapsed <= FRIENDSHIP_FLASH_DURATION_MS:
        sparkle_progress = (elapsed % 220) / 220
        sparkle_pulse = abs(math.sin(sparkle_progress * math.pi))
        fade = 1 - (elapsed / FRIENDSHIP_FLASH_DURATION_MS)
        glow_radius = int(6 + sparkle_pulse * 10 * fade)
        glow_rect = box_rect.inflate(glow_radius * 2, glow_radius * 2)
        glow_surface = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
        glow_alpha = int(140 * fade)
        pygame.draw.rect(glow_surface, (*friendship_flash_color, glow_alpha), glow_surface.get_rect(), border_radius=14)
        screen.blit(glow_surface, glow_rect)
        border_color = friendship_flash_color

    pygame.draw.rect(screen, BLACK, box_rect, border_radius=10)
    pygame.draw.rect(screen, border_color, box_rect, 2, border_radius=10)

    counter_surface = hint_font.render(
        f"Friendship gained: {friendship_points_gained}", True, FRIENDSHIP_TEXT_COLOR
    )
    counter_rect = counter_surface.get_rect(center=box_rect.center)
    screen.blit(counter_surface, counter_rect)


def handle_room_input(event):
    """
    Handle discrete (single-press) events while the current room is active.
    """
    global game_state, paused_from_state, pause_selected_option

    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        paused_from_state = "ROOM"
        pause_selected_option = 0
        game_state = "PAUSED"
    
    elif event.type == pygame.KEYDOWN and event.key == pygame.K_e:
        handle_interaction_key()
        


def draw_pause_menu():
    """
    Draw the pause menu.
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

    hint_surface = hint_font.render("Press ESC to resume", True, SOFT_HINT_COLOR)
    hint_rect = hint_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
    screen.blit(hint_surface, hint_rect)

def activate_pause_option(option_name):
    """
    Perform whatever should happen when a pause menu option is chosen.
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
    Handle a single Pygame event while the pause menu is active.
    """
    global pause_selected_option, game_state

    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            game_state = paused_from_state
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
    Draw a simple "coming soon" screen for Settings or Save.
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

    hint_surface = hint_font.render("Press ESC to go back", True, SOFT_HINT_COLOR)
    hint_rect = hint_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
    screen.blit(hint_surface, hint_rect)

def handle_placeholder_input(event):
    """
    Handle input on a placeholder screen.
    """
    global game_state
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        game_state = "PAUSED"

def draw_decoy_flower():
    """
    Draw the desert's decoy flower.
    """
    draw_image_or_circle(IMAGES["decoy_flower_desert"], DECOY_FLOWER_POS, DECOY_FLOWER_COLOR, 12)

def check_decoy_flower_trigger():
    """
    Check whether the protagonist has walked close enough to the decoy
    flower to trigger the sprite's warning dialogue.
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
        next_state_after_dialogue = "ROOM"
        dialogue_backdrop_state = "ROOM"
        dialogue_on_complete = None
        sprite_state = "ENTERING"
        sprite_entrance_start_time = pygame.time.get_ticks()
        game_state = "DIALOGUE"

def draw_sprite_character():
    """
    Draw the sprite companion at her current animated position.
    """
    if sprite_state == "HIDDEN":
        return
    draw_image_or_circle(IMAGES["sprite"], sprite_draw_pos, SPRITE_CHAR_COLOR, SPRITE_CHAR_RADIUS)

def activate_heat_drain():
    """
    Turn on the desert heat's HP drain and reset its internal timer.
    """
    global heat_drain_active, last_hp_tick_time

    if heat_immune:
        return

    heat_drain_active = True
    last_hp_tick_time = pygame.time.get_ticks()




def update_heat_drain():
    """
    Drain the protagonist's HP by 1 point every HP_DRAIN_INTERVAL ms (now a
    bit faster than once per second) while heat_drain_active is True.
    """
    global hp, last_hp_tick_time

    if heat_immune or not heat_drain_active or hp <= 0:
        return

    current_time = pygame.time.get_ticks()
    if current_time - last_hp_tick_time >= HP_DRAIN_INTERVAL:
        hp -= 1
        last_hp_tick_time = current_time


def handle_hp_depleted():
    """
    Runs the moment the desert heat drains HP to 0: costs 1 heart and
    respawns at the last checkpoint with HP restored, the same way
    running out of time on the ingredient timer already does. Losing
    the final heart triggers the game-over screen instead. Every heart
    lost also counts toward this session's total_deaths statistic.
    """
    global hearts, hp, game_state, total_deaths

    hearts -= 1
    hp = MAX_HP
    total_deaths += 1

    if hearts <= 0:
        game_state = "GAME_OVER"
    else:
        game_state = checkpoint_state
        activate_heat_drain()


def update_sprite_animation():
    """
    Update the sprite companion's on-screen position.
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
    Convert a position in world coordinates into screen coordinates.
    """
    return world_x - camera_x, world_y


def update_camera():
    """
    Keep the camera roughly centred on the protagonist, bounded by
    whichever room's world width is currently active.
    """
    global camera_x
    room_width = ROOM_CONFIG[current_room]["world_width"]
    target_camera_x = protagonist["x"] - SCREEN_WIDTH // 2
    camera_x = max(0, min(room_width - SCREEN_WIDTH, target_camera_x))


def draw_ice_flower():
    """
    Draw the ice flower (or its fallback placeholder).
    """
    draw_image_or_circle(IMAGES["ice_flower"], ICE_FLOWER_POS, ICE_FLOWER_COLOR, 12)

def check_ice_flower_trigger():
    """
    Once the protagonist gets close enough to the ice flower, have the
    sprite point it out.
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
        next_state_after_dialogue = "ROOM"
        dialogue_backdrop_state = "ROOM"
        dialogue_on_complete = None
        game_state = "DIALOGUE"

def draw_ice_flower_glow():
    """
    Draw a soft, pulsing glow around the ice flower.
    """
    pulse_progress = (pygame.time.get_ticks() % ICE_FLOWER_GLOW_PERIOD) / ICE_FLOWER_GLOW_PERIOD
    pulse = math.sin(pulse_progress * 2 * math.pi)
    radius = int(
        ICE_FLOWER_GLOW_MIN_RADIUS
        + (pulse + 1) / 2 * (ICE_FLOWER_GLOW_MAX_RADIUS - ICE_FLOWER_GLOW_MIN_RADIUS)
    )

    glow_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(glow_surface, (*ICE_FLOWER_GLOW_COLOR, 90), (radius, radius), radius)

    screen_x, screen_y = world_to_screen(*ICE_FLOWER_POS)
    glow_rect = glow_surface.get_rect(center=(int(screen_x), int(screen_y)))
    screen.blit(glow_surface, glow_rect)

def draw_decoy_flower_glow():
    """
    Draw a soft, pulsing glow around the decoy flower.
    """
    pulse_progress = (pygame.time.get_ticks() % DECOY_FLOWER_GLOW_PERIOD) / DECOY_FLOWER_GLOW_PERIOD
    pulse = math.sin(pulse_progress * 2 * math.pi)
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
    Draw a flashing, left-pointing arrow.
    """
    is_visible = (pygame.time.get_ticks() % LEFT_ARROW_FLASH_PERIOD) < (LEFT_ARROW_FLASH_PERIOD // 2)
    if not is_visible:
        return

    center_x, center_y = LEFT_ARROW_CENTER
    half = LEFT_ARROW_SIZE // 2
    arrow_points = [
        (center_x - half, center_y),
        (center_x + half, center_y - half),
        (center_x + half, center_y + half),
    ]
    pygame.draw.polygon(screen, LEFT_ARROW_COLOR, arrow_points)


def update_nearby_interactable():
    """
    Every frame, re-checks how close the protagonist currently is to each
    interactable object in the current room, and updates nearby_interactable
    to whichever single one (if any) is currently in range. The desert's
    ingredient flowers and decoy weed only become interactable once its
    checklist is visible; the swamp's three ingredient flowers, its two
    harmful decoys, and its harmless decoy weed only become interactable
    once its own checklist is visible (Commit 11). The two tinkering
    parts only become interactable once the bridge checklist is visible,
    the bridge itself only becomes interactable once the tinkering
    potion is brewed and it isn't already fixed (Commit 12), the Rat
    only becomes interactable once the bridge is fixed and he hasn't been
    encountered yet (Commit 13), and the exit door only becomes
    interactable once the Rat's encounter is resolved and the door
    hasn't already been used (Commit 14).
    """
    global nearby_interactable

    if current_room == "desert":
        ice_distance = math.hypot(
            protagonist["x"] - ICE_FLOWER_POS[0],
            protagonist["y"] - ICE_FLOWER_POS[1],
        )
        decoy_distance = math.hypot(
            protagonist["x"] - DECOY_FLOWER_POS[0],
            protagonist["y"] - DECOY_FLOWER_POS[1],
        )
        ingredient_1_distance = math.hypot(
            protagonist["x"] - INGREDIENT_FLOWER_1_POS[0],
            protagonist["y"] - INGREDIENT_FLOWER_1_POS[1],
        )
        ingredient_2_distance = math.hypot(
            protagonist["x"] - INGREDIENT_FLOWER_2_POS[0],
            protagonist["y"] - INGREDIENT_FLOWER_2_POS[1],
        )
        decoy_weed_distance = math.hypot(
            protagonist["x"] - DECOY_WEED_POS[0],
            protagonist["y"] - DECOY_WEED_POS[1],
        )

        if ice_flower_encountered and not ice_flower_collected and ice_distance <= ICE_FLOWER_TRIGGER_RADIUS:
            nearby_interactable = "ice_flower"
        elif not decoy_flower_eaten and decoy_distance <= DECOY_FLOWER_RADIUS:
            nearby_interactable = "decoy_flower"
        elif not ice_flower_collected and ingredient_1_distance <= INGREDIENT_FLOWER_TRIGGER_RADIUS:
            nearby_interactable = "early_ingredient_flower_1"
        elif not ice_flower_collected and ingredient_2_distance <= INGREDIENT_FLOWER_TRIGGER_RADIUS:
            nearby_interactable = "early_ingredient_flower_2"
        elif not ice_flower_collected and decoy_weed_distance <= DECOY_WEED_TRIGGER_RADIUS:
            nearby_interactable = "early_decoy_weed"
        elif checklist_visible and not ingredient_flower_1_collected and ingredient_1_distance <= INGREDIENT_FLOWER_TRIGGER_RADIUS:
            nearby_interactable = "ingredient_flower_1"
        elif checklist_visible and not ingredient_flower_2_collected and ingredient_2_distance <= INGREDIENT_FLOWER_TRIGGER_RADIUS:
            nearby_interactable = "ingredient_flower_2"
        elif checklist_visible and not decoy_weed_interacted and decoy_weed_distance <= DECOY_WEED_TRIGGER_RADIUS:
            nearby_interactable = "decoy_weed"
        else:
            nearby_interactable = None

    elif current_room == "swamp":
        swamp_ingredient_1_distance = math.hypot(
            protagonist["x"] - SWAMP_INGREDIENT_FLOWER_1_POS[0],
            protagonist["y"] - SWAMP_INGREDIENT_FLOWER_1_POS[1],
        )
        swamp_ingredient_2_distance = math.hypot(
            protagonist["x"] - SWAMP_INGREDIENT_FLOWER_2_POS[0],
            protagonist["y"] - SWAMP_INGREDIENT_FLOWER_2_POS[1],
        )
        swamp_ingredient_3_distance = math.hypot(
            protagonist["x"] - SWAMP_INGREDIENT_FLOWER_3_POS[0],
            protagonist["y"] - SWAMP_INGREDIENT_FLOWER_3_POS[1],
        )
        swamp_harmful_flower_distance = math.hypot(
            protagonist["x"] - SWAMP_HARMFUL_FLOWER_POS[0],
            protagonist["y"] - SWAMP_HARMFUL_FLOWER_POS[1],
        )
        swamp_harmful_weed_distance = math.hypot(
            protagonist["x"] - SWAMP_HARMFUL_WEED_POS[0],
            protagonist["y"] - SWAMP_HARMFUL_WEED_POS[1],
        )
        swamp_decoy_weed_distance = math.hypot(
            protagonist["x"] - SWAMP_DECOY_WEED_POS[0],
            protagonist["y"] - SWAMP_DECOY_WEED_POS[1],
        )
        tinker_item_1_distance = math.hypot(
            protagonist["x"] - TINKER_ITEM_1_POS[0],
            protagonist["y"] - TINKER_ITEM_1_POS[1],
        )
        tinker_item_2_distance = math.hypot(
            protagonist["x"] - TINKER_ITEM_2_POS[0],
            protagonist["y"] - TINKER_ITEM_2_POS[1],
        )
        bridge_distance = abs(protagonist["x"] - SWAMP_BRIDGE_X)
        door_distance = math.hypot(
            protagonist["x"] - DOOR_POS[0],
            protagonist["y"] - DOOR_POS[1],
        )

        if swamp_checklist_visible and not swamp_ingredient_flower_1_collected and swamp_ingredient_1_distance <= INGREDIENT_FLOWER_TRIGGER_RADIUS:
            nearby_interactable = "swamp_ingredient_flower_1"
        elif swamp_checklist_visible and not swamp_ingredient_flower_2_collected and swamp_ingredient_2_distance <= INGREDIENT_FLOWER_TRIGGER_RADIUS:
            nearby_interactable = "swamp_ingredient_flower_2"
        elif swamp_checklist_visible and not swamp_ingredient_flower_3_collected and swamp_ingredient_3_distance <= INGREDIENT_FLOWER_TRIGGER_RADIUS:
            nearby_interactable = "swamp_ingredient_flower_3"
        elif swamp_checklist_visible and not swamp_harmful_flower_eaten and swamp_harmful_flower_distance <= INGREDIENT_FLOWER_TRIGGER_RADIUS:
            nearby_interactable = "swamp_harmful_flower"
        elif swamp_checklist_visible and not swamp_harmful_weed_eaten and swamp_harmful_weed_distance <= INGREDIENT_FLOWER_TRIGGER_RADIUS:
            nearby_interactable = "swamp_harmful_weed"
        elif swamp_checklist_visible and not swamp_decoy_weed_eaten and swamp_decoy_weed_distance <= DECOY_WEED_TRIGGER_RADIUS:
            nearby_interactable = "swamp_decoy_weed"
        elif swamp_bridge_checklist_visible and not tinker_item_1_collected and tinker_item_1_distance <= INGREDIENT_FLOWER_TRIGGER_RADIUS:
            nearby_interactable = "tinker_item_1"
        elif swamp_bridge_checklist_visible and not tinker_item_2_collected and tinker_item_2_distance <= INGREDIENT_FLOWER_TRIGGER_RADIUS:
            nearby_interactable = "tinker_item_2"
        elif swamp_tinker_potion_brewed and not swamp_bridge_fixed and bridge_distance <= BRIDGE_TRIGGER_RADIUS:
            nearby_interactable = "bridge"
        elif rat_resolved and not door_encountered and door_distance <= DOOR_TRIGGER_RADIUS:
            nearby_interactable = "door"
        else:
            nearby_interactable = None

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
    elif nearby_interactable in ("early_ingredient_flower_1", "early_ingredient_flower_2", "early_decoy_weed"):
        react_to_wrong_flower_before_ice()
    elif nearby_interactable == "ingredient_flower_1":
        consume_ingredient_flower("ingredient_flower_1")
    elif nearby_interactable == "ingredient_flower_2":
        consume_ingredient_flower("ingredient_flower_2")
    elif nearby_interactable == "decoy_weed":
        consume_decoy_weed()
    elif nearby_interactable in ("swamp_ingredient_flower_1", "swamp_ingredient_flower_2", "swamp_ingredient_flower_3"):
        consume_swamp_ingredient_flower(nearby_interactable)
    elif nearby_interactable == "swamp_harmful_flower":
        consume_swamp_harmful_flower()
    elif nearby_interactable == "swamp_harmful_weed":
        consume_swamp_harmful_weed()
    elif nearby_interactable == "swamp_decoy_weed":
        consume_swamp_decoy_weed()
    elif nearby_interactable in ("tinker_item_1", "tinker_item_2"):
        consume_tinker_item(nearby_interactable)
    elif nearby_interactable == "bridge":
        repair_bridge()
    elif nearby_interactable == "door":
        trigger_final_battle()

def consume_ice_flower():
    """
    Eating the ice flower restores 80 HP and grants permanent immunity to
    the desert heat.
    """
    global ice_flower_collected, hp, heat_drain_active, heat_immune

    ice_flower_collected = True
    hp = min(MAX_HP, hp + 80)
    heat_drain_active = False
    heat_immune = True

    show_item_popup(
        title="Ice Flower",
        description="A pale, icy-cool flower. Eating it soothes the desert heat, restores 80 HP, and grants lasting immunity to the heat for the rest of your journey.",
        icon_image=IMAGES["ice_flower"],
    )
    show_hp_heal_popup(80)

def consume_decoy_flower():
    """
    Reaction to eating the decoy flower after being warned not to.
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
    next_state_after_dialogue = "ROOM"
    dialogue_backdrop_state = "ROOM"
    dialogue_on_complete = None
    game_state = "DIALOGUE"

def react_to_wrong_flower_before_ice():
    """
    Reaction to trying to interact with any of the desert's other flowers
    (the two later ingredient flowers, or the decoy weed) before the ice
    flower has actually been picked up. Purely a flavour line redirecting
    the player back toward the ice flower - it doesn't collect or affect
    anything, and can happen as many times as the player keeps trying.
    """
    global dialogue_lines, current_line_index, revealed_chars, last_reveal_time
    global next_state_after_dialogue, dialogue_backdrop_state, dialogue_on_complete, game_state

    dialogue_lines = WRONG_FLOWER_BEFORE_ICE_TEXT
    current_line_index = 0
    revealed_chars = 0
    last_reveal_time = pygame.time.get_ticks()
    next_state_after_dialogue = "ROOM"
    dialogue_backdrop_state = "ROOM"
    dialogue_on_complete = None
    game_state = "DIALOGUE"

def draw_interaction_hint():
    """
    Draws a 'Press E' prompt directly above whichever interactable object is
    currently in range (the actual flower/item/character the player is about
    to interact with), rather than always above the protagonist. Only shown
    while actually free to move around the room, so it can never end up
    peeking out from behind a dialogue box, choice menu, item popup, or the
    pause menu. The bridge is the one interactable without a single fixed
    point (it spans the full screen height), so its hint is positioned at
    the protagonist's current height instead.
    """
    if game_state != "ROOM" or nearby_interactable is None:
        return

    interactable_world_positions = {
        "ice_flower": ICE_FLOWER_POS,
        "decoy_flower": DECOY_FLOWER_POS,
        "ingredient_flower_1": INGREDIENT_FLOWER_1_POS,
        "ingredient_flower_2": INGREDIENT_FLOWER_2_POS,
        "decoy_weed": DECOY_WEED_POS,
        "early_ingredient_flower_1": INGREDIENT_FLOWER_1_POS,
        "early_ingredient_flower_2": INGREDIENT_FLOWER_2_POS,
        "early_decoy_weed": DECOY_WEED_POS,
        "swamp_ingredient_flower_1": SWAMP_INGREDIENT_FLOWER_1_POS,
        "swamp_ingredient_flower_2": SWAMP_INGREDIENT_FLOWER_2_POS,
        "swamp_ingredient_flower_3": SWAMP_INGREDIENT_FLOWER_3_POS,
        "swamp_harmful_flower": SWAMP_HARMFUL_FLOWER_POS,
        "swamp_harmful_weed": SWAMP_HARMFUL_WEED_POS,
        "swamp_decoy_weed": SWAMP_DECOY_WEED_POS,
        "tinker_item_1": TINKER_ITEM_1_POS,
        "tinker_item_2": TINKER_ITEM_2_POS,
        "door": DOOR_POS,
    }

    if nearby_interactable == "bridge":
        hint_world_pos = (SWAMP_BRIDGE_X, protagonist["y"])
    else:
        hint_world_pos = interactable_world_positions.get(nearby_interactable, (protagonist["x"], protagonist["y"]))

    screen_x, screen_y = world_to_screen(*hint_world_pos)
    hint_surface = hint_font.render("Press E to Interact", True, WHITE)
    hint_rect = hint_surface.get_rect(center=(int(screen_x), int(screen_y) - 40))
    screen.blit(hint_surface, hint_rect)

def show_item_popup(title, description, icon_image=None):
    """
    Opens the small item-info popup window.
    """
    global item_popup_title, item_popup_description, item_popup_icon_image
    global previous_state_before_popup, game_state

    item_popup_title = title
    item_popup_description = description
    item_popup_icon_image = icon_image
    previous_state_before_popup = "ROOM"
    game_state = "ITEM_POPUP"

def draw_item_popup():
    """
    Draws the desert scene behind a centered popup box.
    """
    draw_room()

    box_rect = pygame.Rect(0, 0, 400, 220)
    box_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    pygame.draw.rect(screen, BLACK, box_rect, border_radius=18)
    pygame.draw.rect(screen, WHITE, box_rect, 3, border_radius=18)

    icon_rect = pygame.Rect(box_rect.x + 20, box_rect.y + 20, ITEM_POPUP_ICON_SIZE, ITEM_POPUP_ICON_SIZE)
    if item_popup_icon_image is None:
        pygame.draw.rect(screen, (150, 150, 150), icon_rect, border_radius=10)
    else:
        icon_surface = pygame.transform.scale(item_popup_icon_image, (ITEM_POPUP_ICON_SIZE, ITEM_POPUP_ICON_SIZE))
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

    hint_surface = hint_font.render("Press SPACE to close", True, SOFT_HINT_COLOR)
    hint_rect = hint_surface.get_rect(bottomright=(box_rect.right - 15, box_rect.bottom - 10))
    screen.blit(hint_surface, hint_rect)

def handle_item_popup_input(event):
    """
    Closes the item popup on Space/Enter or a mouse click. Normally
    returns to whichever state was active before it opened - but the
    very first time the ice flower's popup is closed, it instead chains
    straight into View 7 (Sprite's true introduction), rather than
    dropping the player back into free movement.
    """
    global game_state, sprite_true_intro_played

    key_pressed = event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE)
    mouse_clicked = event.type == pygame.MOUSEBUTTONDOWN and event.button == 1

    if key_pressed or mouse_clicked:
        if item_popup_title == "Ice Flower" and not sprite_true_intro_played:
            sprite_true_intro_played = True
            start_sprite_true_intro_dialogue()
        else:
            game_state = previous_state_before_popup

def get_hp_bar_color(current_hp):
    """
    Returns the hex color the HP bar should currently be drawn in.
    """
    if current_hp >= 70:
        return HP_BAR_COLOR_HIGH
    elif current_hp >= 30:
        return HP_BAR_COLOR_MID
    else:
        return HP_BAR_COLOR_LOW

def draw_hp_bar():
    """
    Draws the HP bar in the corner of the screen.
    """
    bar_x, bar_y = HP_BAR_POS
    outline_rect = pygame.Rect(bar_x, bar_y, HP_BAR_WIDTH, HP_BAR_HEIGHT)
    pygame.draw.rect(screen, WHITE, outline_rect, 2, border_radius=8)

    fill_width = int(HP_BAR_WIDTH * (hp / MAX_HP))
    fill_rect = pygame.Rect(bar_x, bar_y, fill_width, HP_BAR_HEIGHT)
    pygame.draw.rect(screen, pygame.Color(get_hp_bar_color(hp)), fill_rect, border_radius=8)

    hp_text_surface = hint_font.render(f"HP: {hp}/{MAX_HP}", True, WHITE)
    hp_text_rect = hp_text_surface.get_rect(topleft=(bar_x, bar_y + HP_BAR_HEIGHT + 4))
    screen.blit(hp_text_surface, hp_text_rect)

def draw_hearts():
    """
    Draws the player's remaining hearts using the heart_container image
    (assets/heart_container.png) below the HP bar and its numeric
    readout, with enough vertical clearance below the HP text (computed
    from the font's own line size, rather than a fixed guess) that the
    two never overlap. Lost hearts simply disappear now, instead of
    showing an empty outline. Falls back to the original filled-circle
    placeholder if the image hasn't been supplied yet.
    """
    heart_radius = HEART_ICON_SIZE // 2
    start_x = HP_BAR_POS[0] + heart_radius
    hp_text_bottom = HP_BAR_POS[1] + HP_BAR_HEIGHT + 4 + hint_font.get_linesize()
    start_y = hp_text_bottom + heart_radius + 10

    for i in range(MAX_HEARTS):
        if i >= hearts:
            continue

        center = (start_x + i * (HEART_ICON_SIZE + 6), start_y)
        if IMAGES["heart_container"] is not None:
            heart_rect = IMAGES["heart_container"].get_rect(center=center)
            screen.blit(IMAGES["heart_container"], heart_rect)
        else:
            pygame.draw.circle(screen, (231, 76, 60), center, heart_radius)

def show_hp_heal_popup(amount_healed):
    """
    Starts a short-lived floating "+<amount> HP" text callout.
    """
    global hp_heal_popup_text, hp_heal_popup_start_time

    hp_heal_popup_text = f"+{amount_healed} HP"
    hp_heal_popup_start_time = pygame.time.get_ticks()

def render_outlined_text(text, font, fill_color, outline_color, outline_width=2):
    """
    Renders text with a solid outline behind it.
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
    Draws the floating "+80 HP" text while it's still within its display duration.
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


def show_hp_damage_popup(amount_lost):
    """
    Starts a short-lived floating "-<amount> HP" text callout, the same
    way show_hp_heal_popup does for healing.
    """
    global hp_damage_popup_text, hp_damage_popup_start_time

    hp_damage_popup_text = f"-{amount_lost} HP"
    hp_damage_popup_start_time = pygame.time.get_ticks()


def draw_hp_damage_popup():
    """
    Draws the floating "-25 HP" text while it's still within its display
    duration, the same way draw_hp_heal_popup does for healing.
    """
    if hp_damage_popup_text is None:
        return

    elapsed = pygame.time.get_ticks() - hp_damage_popup_start_time
    if elapsed > HP_DAMAGE_POPUP_DURATION_MS:
        return

    popup_surface = render_outlined_text(
        hp_damage_popup_text, hint_font, pygame.Color(HP_DAMAGE_POPUP_COLOR), BLACK
    )
    sprite_screen_x, sprite_screen_y = world_to_screen(sprite_draw_pos[0], sprite_draw_pos[1])
    popup_rect = popup_surface.get_rect(
        center=(int(sprite_screen_x), int(sprite_screen_y) - SPRITE_CHAR_RADIUS - 20)
    )
    screen.blit(popup_surface, popup_rect)


def start_sprite_true_intro_dialogue():
    """
    Plays View 7: Sprite's true introduction and her reluctant-alliance
    pitch. Triggered once, automatically, the first time the ice flower's
    item popup is closed. Ends by chaining into the first dialogue-choice
    moment via dialogue_on_complete.
    """
    global dialogue_lines, current_line_index, revealed_chars, last_reveal_time
    global next_state_after_dialogue, dialogue_backdrop_state, dialogue_on_complete, game_state

    dialogue_lines = SPRITE_TRUE_INTRO_TEXT
    current_line_index = 0
    revealed_chars = 0
    last_reveal_time = pygame.time.get_ticks()
    next_state_after_dialogue = "ROOM"
    dialogue_backdrop_state = "ROOM"
    dialogue_on_complete = "SPRITE_CHOICE_1"
    game_state = "DIALOGUE"


def start_sprite_choice_1():
    """
    Opens the first dialogue-choice moment of View 7 ("Are you in
    properly...?"), feeding sprite_friendship_level.
    """
    start_dialogue_choice(
        options=SPRITE_CHOICE_1_OPTIONS,
        deltas=SPRITE_CHOICE_1_DELTAS,
        reactions=SPRITE_CHOICE_1_REACTIONS,
        target="sprite",
        on_complete="SPRITE_BETWEEN_CHOICES",
    )


def start_sprite_between_choices_dialogue():
    """
    Plays the short connecting lines between View 7's two dialogue-choice
    exchanges, ending on the second exchange's prompt line, then chains
    into the second choice.
    """
    global dialogue_lines, current_line_index, revealed_chars, last_reveal_time
    global next_state_after_dialogue, dialogue_backdrop_state, dialogue_on_complete, game_state

    dialogue_lines = SPRITE_BETWEEN_CHOICES_TEXT
    current_line_index = 0
    revealed_chars = 0
    last_reveal_time = pygame.time.get_ticks()
    next_state_after_dialogue = "ROOM"
    dialogue_backdrop_state = "ROOM"
    dialogue_on_complete = "SPRITE_CHOICE_2"
    game_state = "DIALOGUE"


def start_sprite_choice_2():
    """
    Opens the second dialogue-choice moment of View 7 ("Does any of this
    actually mean something to you?"), feeding sprite_friendship_level.
    Chains straight into View 8 (the potion recipe/checklist intro) once
    the reaction line finishes.
    """
    start_dialogue_choice(
        options=SPRITE_CHOICE_2_OPTIONS,
        deltas=SPRITE_CHOICE_2_DELTAS,
        reactions=SPRITE_CHOICE_2_REACTIONS,
        target="sprite",
        on_complete="START_POTION_RECIPE_INTRO",
    )


def start_potion_recipe_intro_dialogue():
    """
    Plays View 8: Sprite introduces the anti-poison potion recipe and
    the on-screen checklist. The checklist itself pops in mid-dialogue
    (handled in handle_dialogue_input) right as Sprite mentions it, so
    nothing further needs to happen once this dialogue completes.
    """
    global dialogue_lines, current_line_index, revealed_chars, last_reveal_time
    global next_state_after_dialogue, dialogue_backdrop_state, dialogue_on_complete, game_state

    dialogue_lines = POTION_RECIPE_INTRO_TEXT
    current_line_index = 0
    revealed_chars = 0
    last_reveal_time = pygame.time.get_ticks()
    next_state_after_dialogue = "ROOM"
    dialogue_backdrop_state = "ROOM"
    dialogue_on_complete = None
    game_state = "DIALOGUE"


def start_dialogue_choice(options, deltas, reactions, target, on_complete):
    """
    Opens the reusable 3-option dialogue-choice menu, used for every
    Rat/Sprite friendship moment in the game.
    """
    global choice_options, choice_deltas, choice_reactions, choice_friendship_target
    global choice_on_complete, choice_selected_option, game_state

    choice_options = options
    choice_deltas = deltas
    choice_reactions = reactions
    choice_friendship_target = target
    choice_on_complete = on_complete
    choice_selected_option = 0
    game_state = "DIALOGUE_CHOICE"


def trigger_friendship_flash(delta):
    """
    Starts a brief colored flash/sparkle on the friendship counter box:
    green when the total just went up, red when it just went down. Called
    from resolve_dialogue_choice whenever a choice actually changes
    friendship_points_gained.
    """
    global friendship_flash_start_time, friendship_flash_color

    friendship_flash_start_time = pygame.time.get_ticks()
    friendship_flash_color = FRIENDSHIP_FLASH_COLOR_UP if delta > 0 else FRIENDSHIP_FLASH_COLOR_DOWN


def resolve_dialogue_choice(index):
    """
    Applies the friendship point change for the chosen option, then plays
    its reaction line as a normal one-line dialogue, chaining onward via
    choice_on_complete once that line finishes.
    """
    global sprite_friendship_level, rat_friendship_level, friendship_points_gained
    global dialogue_lines, current_line_index, revealed_chars, last_reveal_time
    global next_state_after_dialogue, dialogue_backdrop_state, dialogue_on_complete, game_state

    delta = choice_deltas[index]
    if choice_friendship_target == "sprite":
        sprite_friendship_level = max(0, sprite_friendship_level + delta)
    elif choice_friendship_target == "rat":
        rat_friendship_level = max(0, rat_friendship_level + delta)
    friendship_points_gained += delta
    if delta != 0:
        trigger_friendship_flash(delta)

    dialogue_lines = [choice_reactions[index]]
    current_line_index = 0
    revealed_chars = 0
    last_reveal_time = pygame.time.get_ticks()
    next_state_after_dialogue = "ROOM"
    dialogue_backdrop_state = "ROOM"
    dialogue_on_complete = choice_on_complete
    game_state = "DIALOGUE"


def draw_dialogue_choice():
    """
    Draws the current dialogue backdrop with the 3-option choice menu
    overlaid in a text box near the bottom of the screen. The box's
    height grows to fit however much text each option needs, the same
    way draw_text_box does, so the choices and the "Use UP/DOWN..." hint
    never overlap or spill outside the box.
    """
    global choice_option_rects

    if dialogue_backdrop_state == "ROOM":
        draw_room()
    else:
        screen.fill(BARREN_BG)

    box_width = SCREEN_WIDTH - 100
    max_text_width = box_width - 40
    line_height = dialogue_font.get_linesize()

    wrapped_options = [wrap_text(option_text, dialogue_font, max_text_width) for option_text in choice_options]
    content_height = 15 + sum(len(lines) * line_height + 6 for lines in wrapped_options) + 40
    box_height = max(240, content_height)
    box_bottom = SCREEN_HEIGHT - 30
    box_top = max(140, box_bottom - box_height)
    box_rect = pygame.Rect(50, box_top, box_width, box_bottom - box_top)

    pygame.draw.rect(screen, BLACK, box_rect, border_radius=18)
    pygame.draw.rect(screen, WHITE, box_rect, 3, border_radius=18)

    choice_option_rects = []
    current_y = box_rect.y + 15
    for i, wrapped_lines in enumerate(wrapped_options):
        color = HIGHLIGHT if i == choice_selected_option else WHITE
        option_top = current_y
        for line in wrapped_lines:
            line_surface = dialogue_font.render(line, True, color)
            line_rect = line_surface.get_rect(topleft=(box_rect.x + 20, current_y))
            screen.blit(line_surface, line_rect)
            current_y += line_height
        option_bottom = current_y
        choice_option_rects.append(pygame.Rect(box_rect.x + 20, option_top, max_text_width, option_bottom - option_top))
        current_y += 6

    hint_surface = hint_font.render("Use UP/DOWN and ENTER to choose", True, SOFT_HINT_COLOR)
    hint_rect = hint_surface.get_rect(bottomright=(box_rect.right - 15, box_rect.bottom - 10))
    screen.blit(hint_surface, hint_rect)


def handle_dialogue_choice_input(event):
    """
    Handles input while the dialogue-choice menu is open.
    """
    global choice_selected_option

    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP:
            choice_selected_option = (choice_selected_option - 1) % len(choice_options)
        elif event.key == pygame.K_DOWN:
            choice_selected_option = (choice_selected_option + 1) % len(choice_options)
        elif event.key == pygame.K_RETURN:
            resolve_dialogue_choice(choice_selected_option)

    elif event.type == pygame.MOUSEMOTION:
        for i, rect in enumerate(choice_option_rects):
            if rect.collidepoint(event.pos):
                choice_selected_option = i

    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for i, rect in enumerate(choice_option_rects):
            if rect.collidepoint(event.pos):
                resolve_dialogue_choice(i)


def show_ingredient_checklist():
    """
    Makes the potion checklist visible. Called the instant the
    potion-recipe dialogue reaches the line about the checklist
    appearing (see handle_dialogue_input). The room timer has been
    removed entirely, so this no longer starts any countdown.
    """
    global checklist_visible

    checklist_visible = True


def compute_checklist_box_width(names):
    """
    Works out how wide a checklist box needs to be so every item's name
    fits comfortably next to its checkbox, instead of relying on one
    fixed width that was too narrow for longer names like
    "Vine-Bound Plank". Every checklist below calls this instead of
    using CHECKLIST_WIDTH directly.
    """
    longest_name_width = max(hint_font.size(name)[0] for name in names)
    return CHECKLIST_CHECKBOX_SIZE + 8 + longest_name_width + 30


def draw_checklist():
    """
    Draws the top-right "post-it note" checklist of ingredient flowers
    still needed, each with its own tick-box that fills in with a
    checkmark once that flower has been collected. The box is sized to
    fit its own text and stays anchored to the same top-right corner.
    """
    checklist_items = [
        (INGREDIENT_FLOWER_1_NAME, ingredient_flower_1_collected),
        (INGREDIENT_FLOWER_2_NAME, ingredient_flower_2_collected),
    ]
    box_width = compute_checklist_box_width([name for name, _ in checklist_items])
    checklist_x = SCREEN_WIDTH - CHECKLIST_RIGHT_MARGIN - box_width
    checklist_y = CHECKLIST_POS[1]
    box_rect = pygame.Rect(checklist_x, checklist_y, box_width, 20 + CHECKLIST_LINE_HEIGHT * 2)
    pygame.draw.rect(screen, (245, 235, 200), box_rect, border_radius=10)
    pygame.draw.rect(screen, BLACK, box_rect, 2, border_radius=10)
    for i, (name, collected) in enumerate(checklist_items):
        line_y = box_rect.y + 10 + i * CHECKLIST_LINE_HEIGHT
        checkbox_rect = pygame.Rect(box_rect.x + 10, line_y + 2, CHECKLIST_CHECKBOX_SIZE, CHECKLIST_CHECKBOX_SIZE)
        pygame.draw.rect(screen, BLACK, checkbox_rect, 2, border_radius=4)
        if collected:
            pygame.draw.line(
                screen, BLACK,
                (checkbox_rect.left + 2, checkbox_rect.centery),
                (checkbox_rect.centerx - 1, checkbox_rect.bottom - 3),
                2,
            )
            pygame.draw.line(
                screen, BLACK,
                (checkbox_rect.centerx - 1, checkbox_rect.bottom - 3),
                (checkbox_rect.right - 1, checkbox_rect.top + 2),
                2,
            )

        text_surface = hint_font.render(name, True, BLACK)
        text_rect = text_surface.get_rect(topleft=(checkbox_rect.right + 8, line_y))
        screen.blit(text_surface, text_rect)


def draw_swamp_flowers():
    """
    Draws the swamp's 3 real ingredient flowers (withered until
    collected), the 2 harmful decoys (a flower and a weed that cost HP
    if eaten), and the 1 harmless decoy weed - each only for as long as
    it's still uncollected/uninteracted with.
    """
    ingredient_positions_and_images = [
        (SWAMP_INGREDIENT_FLOWER_1_POS, swamp_ingredient_flower_1_collected, IMAGES["marshglow_lily"]),
        (SWAMP_INGREDIENT_FLOWER_2_POS, swamp_ingredient_flower_2_collected, IMAGES["bogroot_bell"]),
        (SWAMP_INGREDIENT_FLOWER_3_POS, swamp_ingredient_flower_3_collected, IMAGES["mistpetal_reed"]),
    ]
    for position, collected, image in ingredient_positions_and_images:
        if not collected:
            draw_image_or_circle(image, position, SWAMP_INGREDIENT_WITHERED_COLOR, 12)

    if not swamp_harmful_flower_eaten:
        draw_image_or_circle(IMAGES["blistercap_bloom"], SWAMP_HARMFUL_FLOWER_POS, SWAMP_HARMFUL_COLOR, 12)

    if not swamp_harmful_weed_eaten:
        draw_image_or_circle(IMAGES["stingmoss_tangle"], SWAMP_HARMFUL_WEED_POS, SWAMP_HARMFUL_COLOR, 12)

    if not swamp_decoy_weed_eaten:
        draw_image_or_circle(IMAGES["swamp_decoy_weed"], SWAMP_DECOY_WEED_POS, SWAMP_DECOY_WEED_COLOR, 12)


def draw_swamp_checklist():
    """
    Draws the swamp's own 3-item checklist, in the same on-screen slot
    the desert's checklist used (only one of the two is ever visible at
    once, since the desert's is hidden by start_swamp_room before this
    one appears). The box is sized to fit its own text.
    """
    checklist_items = [
        (SWAMP_INGREDIENT_FLOWER_1_NAME, swamp_ingredient_flower_1_collected),
        (SWAMP_INGREDIENT_FLOWER_2_NAME, swamp_ingredient_flower_2_collected),
        (SWAMP_INGREDIENT_FLOWER_3_NAME, swamp_ingredient_flower_3_collected),
    ]
    box_width = compute_checklist_box_width([name for name, _ in checklist_items])
    checklist_x = SCREEN_WIDTH - CHECKLIST_RIGHT_MARGIN - box_width
    checklist_y = SWAMP_CHECKLIST_POS[1]
    box_rect = pygame.Rect(checklist_x, checklist_y, box_width, 20 + CHECKLIST_LINE_HEIGHT * 3)
    pygame.draw.rect(screen, (245, 235, 200), box_rect, border_radius=10)
    pygame.draw.rect(screen, BLACK, box_rect, 2, border_radius=10)
    for i, (name, collected) in enumerate(checklist_items):
        line_y = box_rect.y + 10 + i * CHECKLIST_LINE_HEIGHT
        checkbox_rect = pygame.Rect(box_rect.x + 10, line_y + 2, CHECKLIST_CHECKBOX_SIZE, CHECKLIST_CHECKBOX_SIZE)
        pygame.draw.rect(screen, BLACK, checkbox_rect, 2, border_radius=4)
        if collected:
            pygame.draw.line(
                screen, BLACK,
                (checkbox_rect.left + 2, checkbox_rect.centery),
                (checkbox_rect.centerx - 1, checkbox_rect.bottom - 3),
                2,
            )
            pygame.draw.line(
                screen, BLACK,
                (checkbox_rect.centerx - 1, checkbox_rect.bottom - 3),
                (checkbox_rect.right - 1, checkbox_rect.top + 2),
                2,
            )

        text_surface = hint_font.render(name, True, BLACK)
        text_rect = text_surface.get_rect(topleft=(checkbox_rect.right + 8, line_y))
        screen.blit(text_surface, text_rect)


def draw_bridge():
    """
    Draws the swamp's bridge as a vertical strip at SWAMP_BRIDGE_X. While
    it's still broken, a chunk is left out of the middle so the swamp
    background actually shows through the gap, rather than one solid
    unbroken strip; a couple of jagged splinters poke into the gap so it
    reads as broken wood. Once swamp_bridge_fixed becomes True, it's
    drawn as one solid, continuous plank instead.
    """
    screen_x, _ = world_to_screen(SWAMP_BRIDGE_X, 0)
    bridge_left = int(screen_x - BRIDGE_WIDTH // 2)

    if swamp_bridge_fixed:
        bridge_rect = pygame.Rect(bridge_left, 0, BRIDGE_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(screen, BRIDGE_FIXED_COLOR, bridge_rect)
        return

    gap_top = SCREEN_HEIGHT // 2 - BRIDGE_GAP_HEIGHT // 2
    gap_bottom = gap_top + BRIDGE_GAP_HEIGHT
    top_rect = pygame.Rect(bridge_left, 0, BRIDGE_WIDTH, gap_top)
    bottom_rect = pygame.Rect(bridge_left, gap_bottom, BRIDGE_WIDTH, SCREEN_HEIGHT - gap_bottom)
    pygame.draw.rect(screen, BRIDGE_BROKEN_COLOR, top_rect)
    pygame.draw.rect(screen, BRIDGE_BROKEN_COLOR, bottom_rect)
    pygame.draw.polygon(
        screen, BRIDGE_BROKEN_COLOR,
        [(bridge_left, gap_top), (bridge_left + BRIDGE_WIDTH // 2, gap_top + 18), (bridge_left, gap_top + 34)],
    )
    pygame.draw.polygon(
        screen, BRIDGE_BROKEN_COLOR,
        [(bridge_left + BRIDGE_WIDTH, gap_bottom), (bridge_left + BRIDGE_WIDTH // 2, gap_bottom - 18), (bridge_left + BRIDGE_WIDTH, gap_bottom - 34)],
    )


def draw_tinker_items():
    """
    Draws the swamp's two scavengeable tinkering parts - the rusty cog
    (assets/gear.png) and the vine-bound plank (assets/log_good.png) -
    each only for as long as it's still uncollected. Falls back to the
    original plain circle if either image hasn't loaded.
    """
    if not tinker_item_1_collected:
        draw_image_or_circle(IMAGES["gear"], TINKER_ITEM_1_POS, TINKER_ITEM_COLOR, 12)

    if not tinker_item_2_collected:
        draw_image_or_circle(IMAGES["log_good"], TINKER_ITEM_2_POS, TINKER_ITEM_COLOR, 12)


def draw_swamp_bridge_checklist():
    """
    Draws the bridge-repair checklist (the two tinkering parts), reusing
    the same on-screen slot and post-it styling as the other checklists.
    The box is sized to fit its own text.
    """
    checklist_items = [
        (TINKER_ITEM_1_NAME, tinker_item_1_collected),
        (TINKER_ITEM_2_NAME, tinker_item_2_collected),
    ]
    box_width = compute_checklist_box_width([name for name, _ in checklist_items])
    checklist_x = SCREEN_WIDTH - CHECKLIST_RIGHT_MARGIN - box_width
    checklist_y = SWAMP_CHECKLIST_POS[1]
    box_rect = pygame.Rect(checklist_x, checklist_y, box_width, 20 + CHECKLIST_LINE_HEIGHT * 2)
    pygame.draw.rect(screen, (245, 235, 200), box_rect, border_radius=10)
    pygame.draw.rect(screen, BLACK, box_rect, 2, border_radius=10)
    for i, (name, collected) in enumerate(checklist_items):
        line_y = box_rect.y + 10 + i * CHECKLIST_LINE_HEIGHT
        checkbox_rect = pygame.Rect(box_rect.x + 10, line_y + 2, CHECKLIST_CHECKBOX_SIZE, CHECKLIST_CHECKBOX_SIZE)
        pygame.draw.rect(screen, BLACK, checkbox_rect, 2, border_radius=4)
        if collected:
            pygame.draw.line(
                screen, BLACK,
                (checkbox_rect.left + 2, checkbox_rect.centery),
                (checkbox_rect.centerx - 1, checkbox_rect.bottom - 3),
                2,
            )
            pygame.draw.line(
                screen, BLACK,
                (checkbox_rect.centerx - 1, checkbox_rect.bottom - 3),
                (checkbox_rect.right - 1, checkbox_rect.top + 2),
                2,
            )

        text_surface = hint_font.render(name, True, BLACK)
        text_rect = text_surface.get_rect(topleft=(checkbox_rect.right + 8, line_y))
        screen.blit(text_surface, text_rect)


def start_room_timer():
    """
    The 90-second room timer has been removed entirely (redundant
    alongside the hearts/HP systems). Intentionally left as a no-op so
    any existing call to it elsewhere keeps working safely.
    """
    return


def update_room_timer():
    """
    The room timer has been removed entirely - intentionally a no-op
    now, kept only so any existing call to it elsewhere doesn't break.
    """
    return


def draw_room_timer():
    """
    The room timer has been removed entirely, so this intentionally no
    longer draws anything (no clock icon, no "Time left" text). Left in
    place, rather than deleted outright, purely so any existing call to
    it elsewhere keeps working safely.
    """
    return


def handle_room_timer_expired():
    """
    Runs when the 90-second timer hits zero before the potion's brewed:
    costs 1 heart and, per the confirmed hearts system, respawns the
    player at their last checkpoint. Since only the desert checkpoint
    exists so far, "respawning" currently just means restarting the
    timer rather than losing any already-collected ingredients - once
    more checkpoints exist, this is where that logic will expand.
    Losing the final heart triggers the game-over screen instead. Every
    heart lost also counts toward this session's total_deaths statistic.
    """
    global hearts, room_timer_active, game_state, total_deaths

    room_timer_active = False
    hearts -= 1
    total_deaths += 1

    if hearts <= 0:
        game_state = "GAME_OVER"
    else:
        game_state = checkpoint_state
        start_room_timer()


def draw_ingredient_flowers():
    """
    Draws both ingredient flowers (withered until collected) and the
    decoy weed alongside them, but only for as long as each is still
    uncollected/uninteracted with.
    """
    if not ingredient_flower_1_collected:
        draw_image_or_circle(IMAGES["sunroot_bloom"], INGREDIENT_FLOWER_1_POS, INGREDIENT_FLOWER_WITHERED_COLOR, 12)

    if not ingredient_flower_2_collected:
        draw_image_or_circle(IMAGES["cactus_blossom"], INGREDIENT_FLOWER_2_POS, INGREDIENT_FLOWER_WITHERED_COLOR, 12)

    if not decoy_weed_interacted:
        draw_image_or_circle(IMAGES["decoy_weed_desert"], DECOY_WEED_POS, DECOY_WEED_COLOR, 12)


def consume_ingredient_flower(which):
    """
    Waters and collects one of the two real ingredient flowers: ticks it
    off the checklist and plays Sprite's short "one down!" reaction line.
    If this was the last of the two ingredients needed, chains into the
    swamp-transition dialogue instead of the normal reaction line.

    Args:
        which (str): "ingredient_flower_1" or "ingredient_flower_2".
    """
    global ingredient_flower_1_collected, ingredient_flower_2_collected
    global dialogue_lines, current_line_index, revealed_chars, last_reveal_time
    global next_state_after_dialogue, dialogue_backdrop_state, dialogue_on_complete, game_state

    if which == "ingredient_flower_1":
        ingredient_flower_1_collected = True
    elif which == "ingredient_flower_2":
        ingredient_flower_2_collected = True

    both_collected = ingredient_flower_1_collected and ingredient_flower_2_collected

    dialogue_lines = SWAMP_TRANSITION_TEXT if both_collected else [INGREDIENT_WATERED_REACTION]
    current_line_index = 0
    revealed_chars = 0
    last_reveal_time = pygame.time.get_ticks()
    next_state_after_dialogue = "ROOM"
    dialogue_backdrop_state = "ROOM"
    dialogue_on_complete = "START_LOADING_SCREEN" if both_collected else None
    game_state = "DIALOGUE"


def consume_decoy_weed():
    """
    Reaction to interacting with the checklist puzzle's decoy weed: does
    not affect the checklist, just a short flavour line. Only happens once.
    """
    global decoy_weed_interacted
    global dialogue_lines, current_line_index, revealed_chars, last_reveal_time
    global next_state_after_dialogue, dialogue_backdrop_state, dialogue_on_complete, game_state

    decoy_weed_interacted = True

    dialogue_lines = [DECOY_WEED_REACTION]
    current_line_index = 0
    revealed_chars = 0
    last_reveal_time = pygame.time.get_ticks()
    next_state_after_dialogue = "ROOM"
    dialogue_backdrop_state = "ROOM"
    dialogue_on_complete = None
    game_state = "DIALOGUE"


def consume_swamp_ingredient_flower(which):
    """
    Waters and collects one of the swamp's three real ingredient flowers:
    ticks it off the swamp checklist and plays Sprite's short reaction
    line. If this was the last of the three needed, chains into the
    swamp potion-brewed dialogue, hides the checklist since the potion
    is done, and - once that finishes - chains straight into the bridge
    intro dialogue (Commit 12).

    Args:
        which (str): "swamp_ingredient_flower_1", "_2", or "_3".
    """
    global swamp_ingredient_flower_1_collected, swamp_ingredient_flower_2_collected
    global swamp_ingredient_flower_3_collected, swamp_potion_brewed, swamp_checklist_visible
    global dialogue_lines, current_line_index, revealed_chars, last_reveal_time
    global next_state_after_dialogue, dialogue_backdrop_state, dialogue_on_complete, game_state

    if which == "swamp_ingredient_flower_1":
        swamp_ingredient_flower_1_collected = True
    elif which == "swamp_ingredient_flower_2":
        swamp_ingredient_flower_2_collected = True
    elif which == "swamp_ingredient_flower_3":
        swamp_ingredient_flower_3_collected = True

    all_collected = (
        swamp_ingredient_flower_1_collected
        and swamp_ingredient_flower_2_collected
        and swamp_ingredient_flower_3_collected
    )

    if all_collected:
        swamp_potion_brewed = True
        swamp_checklist_visible = False
        dialogue_lines = SWAMP_POTION_BREWED_TEXT
    else:
        dialogue_lines = [SWAMP_INGREDIENT_WATERED_REACTION]

    current_line_index = 0
    revealed_chars = 0
    last_reveal_time = pygame.time.get_ticks()
    next_state_after_dialogue = "ROOM"
    dialogue_backdrop_state = "ROOM"
    dialogue_on_complete = "START_BRIDGE_INTRO" if all_collected else None
    game_state = "DIALOGUE"


def consume_swamp_harmful_flower():
    """
    Eating the swamp's harmful decoy flower costs HP (floored at 0) and
    opens the item popup warning that it was dangerous to eat raw. Only
    happens once - the flower disappears from the room afterwards.
    """
    global swamp_harmful_flower_eaten, hp

    if swamp_harmful_flower_eaten:
        return

    swamp_harmful_flower_eaten = True
    hp = max(0, hp - SWAMP_HARMFUL_HP_LOSS)
    show_hp_damage_popup(SWAMP_HARMFUL_HP_LOSS)
    show_item_popup(
        title=SWAMP_HARMFUL_FLOWER_NAME,
        description=SWAMP_HARMFUL_FLOWER_REACTION_DESC,
        icon_image=IMAGES["blistercap_bloom"],
    )


def consume_swamp_harmful_weed():
    """
    Eating the swamp's harmful decoy weed costs HP (floored at 0) and
    opens the item popup warning that it was dangerous to eat raw. Only
    happens once - the weed disappears from the room afterwards.
    """
    global swamp_harmful_weed_eaten, hp

    if swamp_harmful_weed_eaten:
        return

    swamp_harmful_weed_eaten = True
    hp = max(0, hp - SWAMP_HARMFUL_HP_LOSS)
    show_hp_damage_popup(SWAMP_HARMFUL_HP_LOSS)
    show_item_popup(
        title=SWAMP_HARMFUL_WEED_NAME,
        description=SWAMP_HARMFUL_WEED_REACTION_DESC,
        icon_image=IMAGES["stingmoss_tangle"],
    )


def consume_swamp_decoy_weed():
    """
    Reaction to interacting with the swamp's harmless decoy weed: no HP
    or checklist effect, just a short flavour line. Only happens once.
    """
    global swamp_decoy_weed_eaten
    global dialogue_lines, current_line_index, revealed_chars, last_reveal_time
    global next_state_after_dialogue, dialogue_backdrop_state, dialogue_on_complete, game_state

    swamp_decoy_weed_eaten = True

    dialogue_lines = [SWAMP_DECOY_WEED_REACTION]
    current_line_index = 0
    revealed_chars = 0
    last_reveal_time = pygame.time.get_ticks()
    next_state_after_dialogue = "ROOM"
    dialogue_backdrop_state = "ROOM"
    dialogue_on_complete = None
    game_state = "DIALOGUE"


def consume_tinker_item(which):
    """
    Collects one of the two scavenged bridge-repair parts: ticks it off
    the bridge checklist and plays a short reaction line. If this was
    the second (final) part, brews the tinkering potion, hides the
    checklist, and chains into that dialogue instead of the normal
    reaction line.

    Args:
        which (str): "tinker_item_1" or "tinker_item_2".
    """
    global tinker_item_1_collected, tinker_item_2_collected
    global swamp_tinker_potion_brewed, swamp_bridge_checklist_visible
    global dialogue_lines, current_line_index, revealed_chars, last_reveal_time
    global next_state_after_dialogue, dialogue_backdrop_state, dialogue_on_complete, game_state

    if which == "tinker_item_1":
        tinker_item_1_collected = True
    elif which == "tinker_item_2":
        tinker_item_2_collected = True

    both_collected = tinker_item_1_collected and tinker_item_2_collected

    if both_collected:
        swamp_tinker_potion_brewed = True
        swamp_bridge_checklist_visible = False
        dialogue_lines = TINKER_POTION_BREWED_TEXT
    else:
        dialogue_lines = [TINKER_ITEM_COLLECTED_REACTION]

    current_line_index = 0
    revealed_chars = 0
    last_reveal_time = pygame.time.get_ticks()
    next_state_after_dialogue = "ROOM"
    dialogue_backdrop_state = "ROOM"
    dialogue_on_complete = None
    game_state = "DIALOGUE"


def repair_bridge():
    """
    Interacting with the bridge once the tinkering potion is brewed
    fixes it for good, clearing the invisible wall enforced in
    handle_room_movement and playing a short reaction dialogue. Only
    happens once.
    """
    global swamp_bridge_fixed
    global dialogue_lines, current_line_index, revealed_chars, last_reveal_time
    global next_state_after_dialogue, dialogue_backdrop_state, dialogue_on_complete, game_state

    if swamp_bridge_fixed:
        return

    swamp_bridge_fixed = True

    dialogue_lines = BRIDGE_FIXED_TEXT
    current_line_index = 0
    revealed_chars = 0
    last_reveal_time = pygame.time.get_ticks()
    next_state_after_dialogue = "ROOM"
    dialogue_backdrop_state = "ROOM"
    dialogue_on_complete = None
    game_state = "DIALOGUE"


def check_rat_trigger():
    """
    Once the protagonist gets within RAT_TRIGGER_RADIUS of the Rat (the
    same distance he should first notice her from), he immediately turns
    to face her and his encounter dialogue starts on its own - no E press
    needed for this first meeting, the same way the desert's decoy/ice
    flowers already announce themselves. Only fires once, before he's
    been encountered.
    """
    global rat_facing

    if rat_encountered or not swamp_bridge_fixed:
        return

    distance = math.hypot(
        protagonist["x"] - RAT_POS[0],
        protagonist["y"] - RAT_POS[1],
    )
    if distance <= RAT_TRIGGER_RADIUS:
        rat_facing = "left" if protagonist["x"] < RAT_POS[0] else "right"
        encounter_rat()


def encounter_rat():
    """
    Triggered the first time the player interacts with the Rat: plays
    his initial grumpy refusal, then chains automatically (via
    dialogue_on_complete) through the prodding intro and all four
    friendship checks without needing another keypress in between.
    """
    global rat_encountered
    global dialogue_lines, current_line_index, revealed_chars, last_reveal_time
    global next_state_after_dialogue, dialogue_backdrop_state, dialogue_on_complete, game_state

    if rat_encountered:
        return

    rat_encountered = True

    dialogue_lines = RAT_ENCOUNTER_TEXT
    current_line_index = 0
    revealed_chars = 0
    last_reveal_time = pygame.time.get_ticks()
    next_state_after_dialogue = "ROOM"
    dialogue_backdrop_state = "ROOM"
    dialogue_on_complete = "RAT_PRODDING_INTRO"
    game_state = "DIALOGUE"


def start_rat_prodding_intro_dialogue():
    """
    Plays the short exchange where the player first asks about the Rat's
    backstory, ending on his suspicious "why do you care" line. Chains
    into the first friendship check.
    """
    global dialogue_lines, current_line_index, revealed_chars, last_reveal_time
    global next_state_after_dialogue, dialogue_backdrop_state, dialogue_on_complete, game_state

    dialogue_lines = RAT_PRODDING_INTRO_TEXT
    current_line_index = 0
    revealed_chars = 0
    last_reveal_time = pygame.time.get_ticks()
    next_state_after_dialogue = "ROOM"
    dialogue_backdrop_state = "ROOM"
    dialogue_on_complete = "RAT_CHOICE_1"
    game_state = "DIALOGUE"


def start_rat_choice_1():
    """Opens the first of the Rat's four friendship-check choices."""
    start_dialogue_choice(
        options=RAT_CHOICE_1_OPTIONS,
        deltas=RAT_CHOICE_1_DELTAS,
        reactions=RAT_CHOICE_1_REACTIONS,
        target="rat",
        on_complete="RAT_BETWEEN_CHOICES_1",
    )


def start_rat_between_choices_1_dialogue():
    """Plays the backstory beat between friendship checks 1 and 2."""
    global dialogue_lines, current_line_index, revealed_chars, last_reveal_time
    global next_state_after_dialogue, dialogue_backdrop_state, dialogue_on_complete, game_state

    dialogue_lines = RAT_BETWEEN_CHOICES_1_TEXT
    current_line_index = 0
    revealed_chars = 0
    last_reveal_time = pygame.time.get_ticks()
    next_state_after_dialogue = "ROOM"
    dialogue_backdrop_state = "ROOM"
    dialogue_on_complete = "RAT_CHOICE_2"
    game_state = "DIALOGUE"


def start_rat_choice_2():
    """Opens the second of the Rat's four friendship-check choices."""
    start_dialogue_choice(
        options=RAT_CHOICE_2_OPTIONS,
        deltas=RAT_CHOICE_2_DELTAS,
        reactions=RAT_CHOICE_2_REACTIONS,
        target="rat",
        on_complete="RAT_BETWEEN_CHOICES_2",
    )


def start_rat_between_choices_2_dialogue():
    """Plays the backstory beat between friendship checks 2 and 3."""
    global dialogue_lines, current_line_index, revealed_chars, last_reveal_time
    global next_state_after_dialogue, dialogue_backdrop_state, dialogue_on_complete, game_state

    dialogue_lines = RAT_BETWEEN_CHOICES_2_TEXT
    current_line_index = 0
    revealed_chars = 0
    last_reveal_time = pygame.time.get_ticks()
    next_state_after_dialogue = "ROOM"
    dialogue_backdrop_state = "ROOM"
    dialogue_on_complete = "RAT_CHOICE_3"
    game_state = "DIALOGUE"


def start_rat_choice_3():
    """Opens the third of the Rat's four friendship-check choices."""
    start_dialogue_choice(
        options=RAT_CHOICE_3_OPTIONS,
        deltas=RAT_CHOICE_3_DELTAS,
        reactions=RAT_CHOICE_3_REACTIONS,
        target="rat",
        on_complete="RAT_BETWEEN_CHOICES_3",
    )


def start_rat_between_choices_3_dialogue():
    """
    Plays the final backstory beat before the fourth friendship check,
    where Sprite reveals the balance potion could be used to heal him.
    """
    global dialogue_lines, current_line_index, revealed_chars, last_reveal_time
    global next_state_after_dialogue, dialogue_backdrop_state, dialogue_on_complete, game_state

    dialogue_lines = RAT_BETWEEN_CHOICES_3_TEXT
    current_line_index = 0
    revealed_chars = 0
    last_reveal_time = pygame.time.get_ticks()
    next_state_after_dialogue = "ROOM"
    dialogue_backdrop_state = "ROOM"
    dialogue_on_complete = "RAT_CHOICE_4"
    game_state = "DIALOGUE"


def start_rat_choice_4():
    """
    Opens the fourth and decisive friendship check, which settles
    whether he'll actually let you heal him. Chains into resolving his
    final outcome once its reaction line finishes.
    """
    start_dialogue_choice(
        options=RAT_CHOICE_4_OPTIONS,
        deltas=RAT_CHOICE_4_DELTAS,
        reactions=RAT_CHOICE_4_REACTIONS,
        target="rat",
        on_complete="RESOLVE_RAT_OUTCOME",
    )


def resolve_rat_outcome():
    """
    Runs once the fourth and final Rat friendship check resolves: checks
    the accumulated rat_friendship_level against the two thresholds and
    plays whichever of the three ending dialogues applies (he dies,
    he's healed but bitter, or he's healed and agrees to help), then
    marks the encounter as fully resolved. If he's agreed to help, this
    also chains into start_rat_following() (Commit 14) once his line
    finishes, so he joins as a following companion from that point on.
    """
    global rat_resolved, rat_outcome
    global dialogue_lines, current_line_index, revealed_chars, last_reveal_time
    global next_state_after_dialogue, dialogue_backdrop_state, dialogue_on_complete, game_state

    rat_resolved = True

    if rat_friendship_level <= RAT_FRIENDSHIP_LOW_THRESHOLD:
        rat_outcome = "died"
        dialogue_lines = RAT_OUTCOME_DIED_TEXT
        dialogue_on_complete = None
    elif rat_friendship_level < RAT_FRIENDSHIP_HIGH_THRESHOLD:
        rat_outcome = "bitter"
        dialogue_lines = RAT_OUTCOME_BITTER_TEXT
        dialogue_on_complete = None
    else:
        rat_outcome = "helped"
        dialogue_lines = RAT_OUTCOME_HELPED_TEXT
        dialogue_on_complete = "START_RAT_FOLLOWING"

    current_line_index = 0
    revealed_chars = 0
    last_reveal_time = pygame.time.get_ticks()
    next_state_after_dialogue = "ROOM"
    dialogue_backdrop_state = "ROOM"
    game_state = "DIALOGUE"


def draw_rat():
    """
    Draws the Rat at his fixed position past the bridge, for as long as
    he hasn't left the scene for good - gone if he ran off ("died") or
    limped away bitter after being healed ("bitter"). Once he's agreed
    to help ("helped"), he becomes a following companion instead, drawn
    by draw_rat_companion() (Commit 14). Uses the pre-flipped image while
    rat_facing is "left", so he visibly turns to face the protagonist the
    moment they first meet.
    """
    if rat_outcome in ("died", "bitter"):
        return
    rat_image = IMAGES["rat_flipped"] if rat_facing == "left" else IMAGES["rat"]
    draw_image_or_circle(rat_image, RAT_POS, RAT_COLOR, 12)


def draw_rat_companion():
    """
    Draws the Rat at his current follow position once he's agreed to
    join as a companion (Commit 14), the same way draw_sprite_character()
    draws Sprite. Uses the pre-flipped image while rat_facing is "left",
    kept in sync with the protagonist's own facing by
    update_rat_companion_animation().
    """
    rat_image = IMAGES["rat_flipped"] if rat_facing == "left" else IMAGES["rat"]
    draw_image_or_circle(rat_image, rat_draw_pos, RAT_COLOR, 12)


def start_rat_following():
    """
    Called once the Rat's healed-and-helped outcome dialogue finishes:
    switches him from his fixed spot into a following companion,
    positioned right at the protagonist's side from that point on,
    and returns play to the room. (Bugfix: this used to skip setting
    game_state, leaving it on "DIALOGUE" with current_line_index
    already past the end of the dialogue that just finished - crashing
    the very next frame's text reveal with an IndexError.)
    """
    global rat_state, rat_draw_pos, game_state
    rat_state = "FOLLOWING"
    rat_draw_pos = [protagonist["x"] + RAT_FOLLOW_OFFSET[0], protagonist["y"] + RAT_FOLLOW_OFFSET[1]]
    game_state = "ROOM"


def update_rat_companion_animation():
    """
    Keeps the Rat's on-screen position locked to his follow offset from
    the protagonist, once he's joined as a companion. Simpler than
    Sprite's own animation, since he walks alongside you rather than
    hovering. Also keeps him always facing the same direction as the
    protagonist while he's following her.
    """
    global rat_draw_pos, rat_facing

    if rat_state != "FOLLOWING":
        return

    rat_draw_pos[0] = protagonist["x"] + RAT_FOLLOW_OFFSET[0]
    rat_draw_pos[1] = protagonist["y"] + RAT_FOLLOW_OFFSET[1]
    rat_facing = protagonist_facing


def start_swamp_room():
    """
    Called once the potion-brewing transition dialogue finishes: switches
    current_room to "swamp", hides the now-irrelevant potion checklist
    and its timer, and repositions the protagonist and camera to the
    start of the new room.
    """
    global current_room, camera_x, checklist_visible, room_timer_active

    current_room = "swamp"
    checklist_visible = False
    room_timer_active = False
    protagonist["x"] = 60
    protagonist["y"] = SCREEN_HEIGHT // 2
    camera_x = 0


def draw_door():
    """
    Draws the swamp's exit door once the Rat's encounter is resolved
    (Commit 14): a huge, mysterious-looking arched door with a slow,
    pulsing red glow behind it so it reads as dangerous, marking the way
    toward the final confrontation.
    """
    screen_x, screen_y = world_to_screen(*DOOR_POS)

    pulse_progress = (pygame.time.get_ticks() % DOOR_GLOW_PERIOD) / DOOR_GLOW_PERIOD
    pulse = math.sin(pulse_progress * 2 * math.pi)
    glow_radius = int(
        DOOR_GLOW_MIN_RADIUS
        + (pulse + 1) / 2 * (DOOR_GLOW_MAX_RADIUS - DOOR_GLOW_MIN_RADIUS)
    )
    glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(glow_surface, (*DOOR_GLOW_COLOR, 90), (glow_radius, glow_radius), glow_radius)
    glow_rect = glow_surface.get_rect(center=(int(screen_x), int(screen_y)))
    screen.blit(glow_surface, glow_rect)

    door_rect = pygame.Rect(0, 0, DOOR_WIDTH, DOOR_HEIGHT)
    door_rect.center = (int(screen_x), int(screen_y))
    pygame.draw.ellipse(screen, DOOR_COLOR, pygame.Rect(door_rect.x, door_rect.y - 22, DOOR_WIDTH, 44))
    pygame.draw.rect(screen, DOOR_COLOR, door_rect, border_radius=16)
    pygame.draw.rect(screen, DOOR_TRIM_COLOR, door_rect, 6, border_radius=16)


def trigger_final_battle():
    """
    Triggered the first time the player interacts with the door past
    the Rat's resolved encounter: plays the door/final-battle intro
    dialogue, then chains straight into resolving the ending based on
    Sprite's and the Rat's willingness to help.
    """
    global door_encountered
    global dialogue_lines, current_line_index, revealed_chars, last_reveal_time
    global next_state_after_dialogue, dialogue_backdrop_state, dialogue_on_complete, game_state

    if door_encountered:
        return

    door_encountered = True

    dialogue_lines = FINAL_BATTLE_INTRO_TEXT
    current_line_index = 0
    revealed_chars = 0
    last_reveal_time = pygame.time.get_ticks()
    next_state_after_dialogue = "ROOM"
    dialogue_backdrop_state = "ROOM"
    dialogue_on_complete = "RESOLVE_FINAL_BATTLE"
    game_state = "DIALOGUE"


def resolve_final_battle():
    """
    Runs once the door's intro dialogue finishes: checks whether Sprite
    (sprite_friendship_level at or above SPRITE_FRIENDSHIP_HELP_THRESHOLD)
    and the Rat (rat_outcome == "helped") are willing to help with the
    final confrontation, and plays whichever of the four ending
    dialogues applies. Chains into either the win screen or a
    narrative-specific game-over once that ending's text finishes.
    """
    global dialogue_lines, current_line_index, revealed_chars, last_reveal_time
    global next_state_after_dialogue, dialogue_backdrop_state, dialogue_on_complete, game_state
    global win_ending_type

    sprite_helps = sprite_friendship_level >= SPRITE_FRIENDSHIP_HELP_THRESHOLD
    rat_helps = rat_outcome == "helped"

    if sprite_helps and rat_helps:
        dialogue_lines = ENDING_BOTH_HELP_TEXT
        win_ending_type = "both"
        dialogue_on_complete = "ACTIVATE_WIN_ENDING"
    elif sprite_helps:
        dialogue_lines = ENDING_SPRITE_ONLY_TEXT
        win_ending_type = "sprite_only"
        dialogue_on_complete = "ACTIVATE_WIN_ENDING"
    elif rat_helps:
        dialogue_lines = ENDING_RAT_ONLY_TEXT
        win_ending_type = "rat_only"
        dialogue_on_complete = "ACTIVATE_WIN_ENDING"
    else:
        dialogue_lines = ENDING_NEITHER_HELP_TEXT
        dialogue_on_complete = "ACTIVATE_SELFISH_LOSS"

    current_line_index = 0
    revealed_chars = 0
    last_reveal_time = pygame.time.get_ticks()
    next_state_after_dialogue = "ROOM"
    dialogue_backdrop_state = "BLACK"  # Stepping through the door leaves the swamp behind - just text on black from here, like the game's opening
    game_state = "DIALOGUE"


def activate_win_ending():
    """
    Moves to the win screen once a successful ending's text finishes,
    updating this session's win statistics the same way the old
    swamp-edge trigger used to.
    """
    global game_state, total_wins, last_run_time_ms, fastest_win_time_ms

    game_state = "WIN"
    total_wins += 1
    last_run_time_ms = pygame.time.get_ticks() - run_start_time
    if fastest_win_time_ms is None or last_run_time_ms < fastest_win_time_ms:
        fastest_win_time_ms = last_run_time_ms


def activate_selfish_loss():
    """
    Moves to the game-over screen for the "neither helped" ending,
    swapping in the narrative-specific message via
    game_over_text_override instead of the usual hearts-based one.
    """
    global game_state, game_over_text_override

    game_over_text_override = SELFISH_LOSS_TEXT
    game_state = "GAME_OVER"


def draw_game_over_screen():
    """
    Draws the full game-over screen shown either once all 3 hearts are
    lost, or after the "neither helped" ending (Commit 14) - using
    game_over_text_override for the latter instead of the usual
    hearts-based message. Either way, offers the option to try again
    from the title screen.
    """
    screen.fill((20, 20, 20))

    title_surface = title_font.render("Game Over", True, WHITE)
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 220))
    screen.blit(title_surface, title_rect)

    wrapped_lines = wrap_text(game_over_text_override or GAME_OVER_TEXT, dialogue_font, SCREEN_WIDTH - 100)
    line_height = dialogue_font.get_linesize()
    for i, line in enumerate(wrapped_lines):
        line_surface = dialogue_font.render(line, True, WHITE)
        line_rect = line_surface.get_rect(center=(SCREEN_WIDTH // 2, 320 + i * line_height))
        screen.blit(line_surface, line_rect)

    stats_text = (
        f"Games played: {games_played}   "
        f"Deaths: {total_deaths}   "
        f"Total wins: {total_wins}"
    )
    stats_surface = hint_font.render(stats_text, True, (200, 200, 200))
    stats_rect = stats_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
    screen.blit(stats_surface, stats_rect)

    stats_surface = hint_font.render(
        f"Friendship points gained this run: {friendship_points_gained}", True, SOFT_HINT_COLOR
    )
    stats_rect = stats_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 70))
    screen.blit(stats_surface, stats_rect)

    hint_surface = hint_font.render("Press ENTER to try again", True, SOFT_HINT_COLOR)
    hint_rect = hint_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
    screen.blit(hint_surface, hint_rect)


def reset_run_state():
    """
    Resets every run-specific counter and flag back to a fresh game's
    starting values, including the swamp's ingredient/decoy flags from
    Commit 11, the bridge/tinkering flags from Commit 12, the Rat's
    encounter flags from Commit 13, and the Rat-companion/door/ending
    flags from Commit 14. Shared by the game-over screen and the win
    screen, since both send the player back to the title screen for a
    new attempt. Session statistics (games_played, total_deaths,
    total_wins, fastest_win_time_ms) are deliberately left untouched here.
    """
    global hearts, hp, sprite_friendship_level, rat_friendship_level
    global decoy_flower_eaten, ice_flower_collected, ice_flower_encountered
    global ingredient_flower_1_collected, ingredient_flower_2_collected, decoy_weed_interacted
    global checklist_visible, room_timer_active, heat_drain_active, heat_immune, hp_bar_visible
    global sprite_true_intro_played, sprite_state, current_room, camera_x
    global swamp_checklist_visible, swamp_potion_brewed
    global swamp_ingredient_flower_1_collected, swamp_ingredient_flower_2_collected, swamp_ingredient_flower_3_collected
    global swamp_harmful_flower_eaten, swamp_harmful_weed_eaten, swamp_decoy_weed_eaten
    global swamp_bridge_checklist_visible, swamp_tinker_potion_brewed, swamp_bridge_fixed
    global tinker_item_1_collected, tinker_item_2_collected
    global hp_heal_popup_text, hp_damage_popup_text
    global rat_encountered, rat_resolved, rat_outcome
    global rat_state, rat_draw_pos, door_encountered, game_over_text_override
    global protagonist_facing, rat_facing

    hearts = MAX_HEARTS
    hp = MAX_HP
    sprite_friendship_level = 0
    rat_friendship_level = 0
    decoy_flower_eaten = False
    ice_flower_collected = False
    ice_flower_encountered = False
    ingredient_flower_1_collected = False
    ingredient_flower_2_collected = False
    decoy_weed_interacted = False
    checklist_visible = False
    room_timer_active = False
    heat_drain_active = False
    heat_immune = False
    hp_bar_visible = False
    sprite_true_intro_played = False
    sprite_state = "HIDDEN"
    current_room = "desert"
    camera_x = 0
    swamp_checklist_visible = False
    swamp_potion_brewed = False
    swamp_ingredient_flower_1_collected = False
    swamp_ingredient_flower_2_collected = False
    swamp_ingredient_flower_3_collected = False
    swamp_harmful_flower_eaten = False
    swamp_harmful_weed_eaten = False
    swamp_decoy_weed_eaten = False
    swamp_bridge_checklist_visible = False
    swamp_tinker_potion_brewed = False
    swamp_bridge_fixed = False
    tinker_item_1_collected = False
    tinker_item_2_collected = False
    hp_heal_popup_text = None
    hp_damage_popup_text = None
    rat_encountered = False
    rat_resolved = False
    rat_outcome = None
    rat_state = "HIDDEN"
    rat_draw_pos = [0, 0]
    door_encountered = False
    game_over_text_override = None
    protagonist["x"] = 1200
    protagonist["y"] = SCREEN_HEIGHT // 2
    protagonist_facing = "right"
    rat_facing = "right"


def handle_game_over_input(event):
    """
    Handles input on the game-over screen: pressing ENTER resets the run
    and returns to the title screen for a fresh attempt.
    """
    global game_state

    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
        reset_run_state()
        game_state = "TITLE"


def handle_win_input(event):
    """
    Handles input on the win screen: pressing ENTER resets the run and
    returns to the title screen, the same as the game-over screen does.
    """
    global game_state

    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
        reset_run_state()
        game_state = "TITLE"


def draw_win_screen():
    """
    Draws the win screen shown once the protagonist crosses the swamp
    safely, with the option to play again from the title screen. Also
    shows this run's time taken alongside the session's fastest win and
    total win count.
    """
    screen.fill((20, 45, 30))

    win_titles = {
        "both": "A New Beginning",
        "sprite_only": "Balance Restored",
        "rat_only": "A Different Path",
    }
    title_surface = title_font.render(win_titles.get(win_ending_type, "You Made It!"), True, WHITE)
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 220))
    screen.blit(title_surface, title_rect)

    win_messages = {
        "both": "Floraborne's balance is restored, and Sprite and the Rat are building a new life together right where it all began.",
        "sprite_only": "Floraborne's balance is restored, and your journey with Sprite continues - though the Rat's story ended without you.",
        "rat_only": "Floraborne's balance is restored - but the same magic that changed the Rat has changed you too. Together, rats in a healing world.",
    }
    wrapped_lines = wrap_text(win_messages.get(win_ending_type, WIN_TEXT), dialogue_font, SCREEN_WIDTH - 100)
    line_height = dialogue_font.get_linesize()
    for i, line in enumerate(wrapped_lines):
        line_surface = dialogue_font.render(line, True, WHITE)
        line_rect = line_surface.get_rect(center=(SCREEN_WIDTH // 2, 320 + i * line_height))
        screen.blit(line_surface, line_rect)

    stats_text = (
        f"Time: {last_run_time_ms // 1000}s   "
        f"Best: {fastest_win_time_ms // 1000}s   "
        f"Total wins: {total_wins}   "
        f"Games played: {games_played}   "
        f"Deaths: {total_deaths}"
    )
    stats_surface = hint_font.render(stats_text, True, (200, 200, 200))
    stats_rect = stats_surface.get_rect(center=(SCREEN_WIDTH // 2, 320 + len(wrapped_lines) * line_height + 20))
    screen.blit(stats_surface, stats_rect)

    stats_surface = hint_font.render(
        f"Friendship points gained this run: {friendship_points_gained}", True, SOFT_HINT_COLOR
    )
    stats_rect = stats_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 70))
    screen.blit(stats_surface, stats_rect)

    hint_surface = hint_font.render("Press ENTER to play again", True, SOFT_HINT_COLOR)
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
        elif game_state == "DIALOGUE_CHOICE":
            handle_dialogue_choice_input(event)
        elif game_state == "ROOM":
            handle_room_input(event)
        elif game_state == "ITEM_POPUP":
            handle_item_popup_input(event)
        elif game_state == "PAUSED":
            handle_pause_input(event)
        elif game_state in ("SETTINGS_PLACEHOLDER", "SAVE_PLACEHOLDER"):
            handle_placeholder_input(event)
        elif game_state == "GAME_OVER":
            handle_game_over_input(event)
        elif game_state == "WIN":
            handle_win_input(event)

    if game_state == "ROOM":
        handle_room_movement()
        update_nearby_interactable()
        if current_room == "desert":
            check_decoy_flower_trigger()
            check_ice_flower_trigger()
        elif current_room == "swamp":
            check_rat_trigger()

    update_camera()

    if game_state not in ("PAUSED", "SETTINGS_PLACEHOLDER", "SAVE_PLACEHOLDER", "ITEM_POPUP", "GAME_OVER", "WIN"):
        update_heat_drain()
        if hp <= 0:
            handle_hp_depleted()
        update_sprite_animation()
        update_rat_companion_animation()
        update_room_timer()

    if game_state == "ROOM" and previous_game_state != "ROOM":
        desert_hint_start_time = pygame.time.get_ticks()
        hp_bar_visible = True
        activate_heat_drain()
    previous_game_state = game_state

    if game_state == "TITLE":
        draw_title_screen()
    elif game_state == "DIALOGUE":
        update_text_reveal()
        if dialogue_backdrop_state == "ROOM":
            draw_room()
        elif dialogue_backdrop_state == "BLACK":
            screen.fill(BLACK)
        else:
            screen.fill(BARREN_BG)
        current_line = dialogue_lines[current_line_index]
        if current_line == "\"Quick - go left! There should be a flower that way that can help you.\"":
            draw_left_arrow_hint()
        draw_text_box(current_line[:revealed_chars])
    elif game_state == "DIALOGUE_CHOICE":
        draw_dialogue_choice()
    elif game_state == "ROOM":
        draw_room()
    elif game_state == "ITEM_POPUP":
        draw_item_popup()
    elif game_state == "PAUSED":
        draw_pause_menu()
    elif game_state in ("SETTINGS_PLACEHOLDER", "SAVE_PLACEHOLDER"):
        draw_placeholder_screen()
    elif game_state == "GAME_OVER":
        draw_game_over_screen()
    elif game_state == "WIN":
        draw_win_screen()

    hud_hidden_for_black_dialogue = game_state == "DIALOGUE" and dialogue_backdrop_state == "BLACK"

    if hp_bar_visible and game_state != "WIN" and not hud_hidden_for_black_dialogue:
        draw_hp_bar()
        draw_hp_heal_popup()
        draw_hp_damage_popup()
        draw_hearts()

    if checklist_visible and game_state != "WIN":
        draw_checklist()
        draw_room_timer()

    if swamp_checklist_visible and game_state != "WIN" and not hud_hidden_for_black_dialogue:
        draw_swamp_checklist()

    if swamp_bridge_checklist_visible and game_state != "WIN" and not hud_hidden_for_black_dialogue:
        draw_swamp_bridge_checklist()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()