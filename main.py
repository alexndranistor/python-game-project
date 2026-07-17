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
previous_game_state = None
desert_hint_start_time = 0
HINT_VISIBLE_DURATION = 2000
HINT_FADE_DURATION = 2000

# --- Colours (RGB tuples)
BARREN_BG = (120, 100, 70)
WHITE = (255, 255, 255)
HIGHLIGHT = (255, 215, 0)
BLACK = (0, 0, 0)
DESERT_BG = (194, 178, 128)
SWAMP_BG = (70, 90, 60)

# --- Fonts
title_font = pygame.font.SysFont(None, 64)
menu_font = pygame.font.SysFont(None, 40)
dialogue_font = pygame.font.SysFont(None, 32)
hint_font = pygame.font.SysFont(None, 20)

# --- Core state machine
# Valid values so far: "TITLE", "DIALOGUE", "DIALOGUE_CHOICE", "ROOM", "ITEM_POPUP", "PAUSED", "SETTINGS_PLACEHOLDER", "SAVE_PLACEHOLDER", "GAME_OVER", "WIN"
game_state = "TITLE"

# --- Title screen menu state
selected_option = 0
menu_options = ["New Game", "Quit"]
menu_option_rects = []

# --- Player data
PROTAGONIST_SIZE = 40
PLAYER_SPEED = 4
protagonist = {
    "name": "Protagonist",
    "x": 1200,
    "y": SCREEN_HEIGHT // 2,
}

# --- Pause menu state ---------------------------------------------------
pause_menu_options = ["Settings", "Save", "Quit Game"]
pause_selected_option = 0
pause_option_rects = []
paused_from_state = None

item_popup_title = ""
item_popup_description = ""
item_popup_icon_path = None
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

# --- Desert biome opening dialogue -------------------------------------------------
DESERT_INTRO_TEXT = [
    "The heat is immediate and overwhelming.",
    "Sand stretches in every direction, and a long stretch of withered flowers in the distance creates a sad, pensive atmosphere.",
    "This place is dangerous - keep an eye on your health, the heat is already starting to get to you.",
    "Look around... there might be something nearby that can help.",
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
HP_DRAIN_INTERVAL = 1000
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
SWAMP_WORLD_WIDTH = 1600
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
    "\"Next thing I know - poof. This.\" She gestures at her tiny glowing self, thoroughly unimpressed. \"A sprite of light. No hands, no proper body, and somehow still expected to fix everything.\"",
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
    "\"Oh - and if you spot any flowers out there looking half-dead, just walk up and interact with them. I've still got just enough magic left in me to water them myself. You don't have to do a thing, for once.\"",
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
CHECKLIST_POS = (SCREEN_WIDTH - 210, 20)
CHECKLIST_WIDTH = 190
CHECKLIST_LINE_HEIGHT = 26
CHECKLIST_CHECKBOX_SIZE = 14

# --- Room timer (90-second countdown, starts once View 8 finishes) -------
ROOM_TIMER_DURATION_MS = 90000
room_timer_active = False
room_timer_start_time = 0

# --- Ingredient flowers (View 8's checklist puzzle) ----------------------
INGREDIENT_FLOWER_1_NAME = "Sunroot Bloom"
INGREDIENT_FLOWER_2_NAME = "Cactus Blossom"
INGREDIENT_FLOWER_1_POS = (700, 150)
INGREDIENT_FLOWER_2_POS = (1020, 480)
INGREDIENT_FLOWER_TRIGGER_RADIUS = 50
INGREDIENT_FLOWER_WITHERED_COLOR = (150, 130, 90)
INGREDIENT_FLOWER_BLOOMED_COLOR = (255, 140, 180)
ingredient_flower_1_collected = False
ingredient_flower_2_collected = False
DECOY_WEED_POS = (860, 540)
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

# --- Hearts / lives system (confirmed core system) ------------------------
MAX_HEARTS = 3
hearts = MAX_HEARTS
checkpoint_state = "ROOM"  # Only one checkpoint exists so far (desert)
GAME_OVER_TEXT = "You've run out of hearts. Take a breath, then try again."
WIN_TEXT = "You've crossed the swamp safely, potion in hand. Floraborne's balance is one step closer to being restored."

# --- Session statistics (global counters, per the project's code requirements) ---
# Deliberately not reset by reset_run_state - these track the whole session,
# not just the current attempt.
games_played = 0
total_deaths = 0
total_wins = 0
fastest_win_time_ms = None
last_run_time_ms = 0
run_start_time = 0

# --- Swamp ingredient puzzle (Commit 11) ---------------------------------
SWAMP_CHECKLIST_POS = CHECKLIST_POS  # Reuses the same on-screen slot as the desert checklist, since only one is ever visible at a time
SWAMP_INGREDIENT_FLOWER_1_NAME = "Marshglow Lily"
SWAMP_INGREDIENT_FLOWER_2_NAME = "Bogroot Bell"
SWAMP_INGREDIENT_FLOWER_3_NAME = "Mistpetal Reed"
SWAMP_INGREDIENT_FLOWER_1_POS = (250, 180)
SWAMP_INGREDIENT_FLOWER_2_POS = (600, 480)
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
SWAMP_DECOY_WEED_POS = (150, 450)
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
BRIDGE_TRIGGER_RADIUS = 60
BRIDGE_BROKEN_COLOR = (60, 50, 45)
BRIDGE_FIXED_COLOR = (150, 110, 70)
swamp_bridge_fixed = False
TINKER_ITEM_1_NAME = "Rusty Cog"
TINKER_ITEM_2_NAME = "Vine-Bound Plank"
TINKER_ITEM_1_POS = (1000, 200)
TINKER_ITEM_2_POS = (1050, 480)
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
RAT_TRIGGER_RADIUS = 60
rat_encountered = False
rat_resolved = False
rat_outcome = None  # None, "died", "bitter", or "helped"
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
DOOR_POS = (1550, 300)
DOOR_TRIGGER_RADIUS = 60
DOOR_COLOR = (40, 35, 30)
door_encountered = False
SPRITE_FRIENDSHIP_HELP_THRESHOLD = 4  # sprite_friendship_level at or above this -> she helps in the final battle
game_over_text_override = None
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

def draw_title_screen():
    """
    Draw the game's title text and the New Game / Quit
    menu, highlighting whichever option is currently selected. Also
    shows this session's running statistics (games played and wins)
    underneath the menu once at least one game has been played.
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

    if games_played > 0:
        stats_surface = hint_font.render(
            f"Games played: {games_played}   Wins: {total_wins}", True, (180, 180, 180)
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
    global games_played, run_start_time

    if option_name == "New Game":
        games_played += 1
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
    Draw the scrolling dialogue box at the bottom of the screen.
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
    in handle_dialogue_input, the same way the desert's did.
    """
    global dialogue_lines, current_line_index, revealed_chars, last_reveal_time
    global next_state_after_dialogue, dialogue_backdrop_state, dialogue_on_complete, game_state

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

def handle_room_movement():
    """
    Update the protagonist's position based on which movement keys are
    currently held down (arrow keys or WASD), bounded by the current
    room's world width, and further clamped at the swamp's bridge until
    it's been repaired (Commit 12) so the player can't just walk across
    the broken gap.
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

    room_width = ROOM_CONFIG[current_room]["world_width"]
    half_size = PROTAGONIST_SIZE // 2
    protagonist["x"] = max(half_size, min(room_width - half_size, protagonist["x"]))
    protagonist["y"] = max(half_size, min(SCREEN_HEIGHT - half_size, protagonist["y"]))

    if current_room == "swamp" and not swamp_bridge_fixed:
        protagonist["x"] = min(protagonist["x"], SWAMP_BRIDGE_X - half_size)


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
    screen.fill(ROOM_CONFIG[current_room]["bg_color"])

    if current_room == "desert":
        if not decoy_flower_eaten:
            draw_decoy_flower_glow()
            draw_decoy_flower()
        if not ice_flower_collected:
            if ice_flower_encountered:
                draw_ice_flower_glow()
                draw_ice_flower()
        if checklist_visible:
            draw_ingredient_flowers()
    elif current_room == "swamp":
        if swamp_checklist_visible:
            draw_swamp_flowers()
        if swamp_bridge_checklist_visible:
            draw_tinker_items()
        draw_bridge()
        if swamp_bridge_fixed and rat_state != "FOLLOWING":
            draw_rat()
        if rat_resolved:
            draw_door()

    draw_interaction_hint()

    protagonist_screen_x, protagonist_screen_y = world_to_screen(protagonist["x"], protagonist["y"])
    protagonist_rect = pygame.Rect(0, 0, PROTAGONIST_SIZE, PROTAGONIST_SIZE)
    protagonist_rect.center = (int(protagonist_screen_x), int(protagonist_screen_y))
    pygame.draw.rect(screen, WHITE, protagonist_rect)

    draw_sprite_character()
    if rat_state == "FOLLOWING":
        draw_rat_companion()
    draw_control_hint()

def draw_control_hint():
    """
    Draw a temporary "Use ARROW KEYS or WASD to move" prompt.
    """
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

    hint_surface = hint_font.render("Press ESC to resume", True, (180, 180, 180))
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

    hint_surface = hint_font.render("Press ESC to go back", True, (180, 180, 180))
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
    screen_x, screen_y = world_to_screen(*DECOY_FLOWER_POS)
    pygame.draw.circle(screen, DECOY_FLOWER_COLOR, (int(screen_x), int(screen_y)), 12)

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
    screen_x, screen_y = world_to_screen(sprite_draw_pos[0], sprite_draw_pos[1])
    pygame.draw.circle(screen, SPRITE_CHAR_COLOR, (int(screen_x), int(screen_y)), SPRITE_CHAR_RADIUS)

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
    Drain the protagonist's HP by 1 point per second while heat_drain_active
    is True.
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
    Draw a placeholder for the ice flower.
    """
    screen_x, screen_y = world_to_screen(*ICE_FLOWER_POS)
    pygame.draw.circle(screen, ICE_FLOWER_COLOR, (int(screen_x), int(screen_y)), 12)

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
        rat_distance = math.hypot(
            protagonist["x"] - RAT_POS[0],
            protagonist["y"] - RAT_POS[1],
        )
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
        elif swamp_bridge_fixed and not rat_encountered and rat_distance <= RAT_TRIGGER_RADIUS:
            nearby_interactable = "rat"
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
    elif nearby_interactable == "rat":
        encounter_rat()
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
        icon_path=None,
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
    Opens the small item-info popup window.
    """
    global item_popup_title, item_popup_description, item_popup_icon_path
    global previous_state_before_popup, game_state

    item_popup_title = title
    item_popup_description = description
    item_popup_icon_path = icon_path
    previous_state_before_popup = "ROOM"
    game_state = "ITEM_POPUP"

def draw_item_popup():
    """
    Draws the desert scene behind a centered popup box.
    """
    draw_room()

    box_rect = pygame.Rect(0, 0, 400, 220)
    box_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    pygame.draw.rect(screen, BLACK, box_rect)
    pygame.draw.rect(screen, WHITE, box_rect, 3)

    icon_rect = pygame.Rect(box_rect.x + 20, box_rect.y + 20, ITEM_POPUP_ICON_SIZE, ITEM_POPUP_ICON_SIZE)
    if item_popup_icon_path is None:
        pygame.draw.rect(screen, (150, 150, 150), icon_rect)
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
    pygame.draw.rect(screen, WHITE, outline_rect, 2)

    fill_width = int(HP_BAR_WIDTH * (hp / MAX_HP))
    fill_rect = pygame.Rect(bar_x, bar_y, fill_width, HP_BAR_HEIGHT)
    pygame.draw.rect(screen, pygame.Color(get_hp_bar_color(hp)), fill_rect)

    hp_text_surface = hint_font.render(f"HP: {hp}/{MAX_HP}", True, WHITE)
    hp_text_rect = hp_text_surface.get_rect(topleft=(bar_x, bar_y + HP_BAR_HEIGHT + 4))
    screen.blit(hp_text_surface, hp_text_rect)

def draw_hearts():
    """
    Draws the player's remaining hearts (simple filled/outline circles)
    just under the HP bar, since both are always-visible survival stats.
    """
    heart_radius = 8
    start_x = HP_BAR_POS[0] + heart_radius
    start_y = HP_BAR_POS[1] + HP_BAR_HEIGHT + 26

    for i in range(MAX_HEARTS):
        center = (start_x + i * (heart_radius * 2 + 6), start_y)
        if i < hearts:
            pygame.draw.circle(screen, (231, 76, 60), center, heart_radius)
        else:
            pygame.draw.circle(screen, (231, 76, 60), center, heart_radius, 2)

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


def resolve_dialogue_choice(index):
    """
    Applies the friendship point change for the chosen option, then plays
    its reaction line as a normal one-line dialogue, chaining onward via
    choice_on_complete once that line finishes.
    """
    global sprite_friendship_level, rat_friendship_level
    global dialogue_lines, current_line_index, revealed_chars, last_reveal_time
    global next_state_after_dialogue, dialogue_backdrop_state, dialogue_on_complete, game_state

    delta = choice_deltas[index]
    if choice_friendship_target == "sprite":
        sprite_friendship_level = max(0, sprite_friendship_level + delta)
    elif choice_friendship_target == "rat":
        rat_friendship_level = max(0, rat_friendship_level + delta)

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
    overlaid in a tall text box near the bottom of the screen.
    """
    global choice_option_rects

    if dialogue_backdrop_state == "ROOM":
        draw_room()
    else:
        screen.fill(BARREN_BG)

    box_rect = pygame.Rect(50, 330, SCREEN_WIDTH - 100, 240)
    pygame.draw.rect(screen, BLACK, box_rect)
    pygame.draw.rect(screen, WHITE, box_rect, 3)

    max_text_width = box_rect.width - 40
    line_height = dialogue_font.get_linesize()

    choice_option_rects = []
    current_y = box_rect.y + 15
    for i, option_text in enumerate(choice_options):
        color = HIGHLIGHT if i == choice_selected_option else WHITE
        wrapped_lines = wrap_text(option_text, dialogue_font, max_text_width)
        option_top = current_y
        for line in wrapped_lines:
            line_surface = dialogue_font.render(line, True, color)
            line_rect = line_surface.get_rect(topleft=(box_rect.x + 20, current_y))
            screen.blit(line_surface, line_rect)
            current_y += line_height
        option_bottom = current_y
        choice_option_rects.append(pygame.Rect(box_rect.x + 20, option_top, max_text_width, option_bottom - option_top))
        current_y += 6

    hint_surface = hint_font.render("Use UP/DOWN and ENTER to choose", True, (180, 180, 180))
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
    Makes the potion checklist visible and starts the 90-second room
    timer. Called the instant the potion-recipe dialogue reaches the
    line about the checklist appearing (see handle_dialogue_input).
    """
    global checklist_visible

    checklist_visible = True
    start_room_timer()


def draw_checklist():
    """
    Draws the top-right "post-it note" checklist of ingredient flowers
    still needed, each with its own tick-box that fills in with a
    checkmark once that flower has been collected.
    """
    checklist_x, checklist_y = CHECKLIST_POS
    box_rect = pygame.Rect(checklist_x, checklist_y, CHECKLIST_WIDTH, 20 + CHECKLIST_LINE_HEIGHT * 2)
    pygame.draw.rect(screen, (245, 235, 200), box_rect)
    pygame.draw.rect(screen, BLACK, box_rect, 2)

    checklist_items = [
        (INGREDIENT_FLOWER_1_NAME, ingredient_flower_1_collected),
        (INGREDIENT_FLOWER_2_NAME, ingredient_flower_2_collected),
    ]
    for i, (name, collected) in enumerate(checklist_items):
        line_y = box_rect.y + 10 + i * CHECKLIST_LINE_HEIGHT
        checkbox_rect = pygame.Rect(box_rect.x + 10, line_y + 2, CHECKLIST_CHECKBOX_SIZE, CHECKLIST_CHECKBOX_SIZE)
        pygame.draw.rect(screen, BLACK, checkbox_rect, 2)
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
    ingredient_positions_and_flags = [
        (SWAMP_INGREDIENT_FLOWER_1_POS, swamp_ingredient_flower_1_collected),
        (SWAMP_INGREDIENT_FLOWER_2_POS, swamp_ingredient_flower_2_collected),
        (SWAMP_INGREDIENT_FLOWER_3_POS, swamp_ingredient_flower_3_collected),
    ]
    for position, collected in ingredient_positions_and_flags:
        if not collected:
            screen_x, screen_y = world_to_screen(*position)
            pygame.draw.circle(screen, SWAMP_INGREDIENT_WITHERED_COLOR, (int(screen_x), int(screen_y)), 12)

    if not swamp_harmful_flower_eaten:
        screen_x, screen_y = world_to_screen(*SWAMP_HARMFUL_FLOWER_POS)
        pygame.draw.circle(screen, SWAMP_HARMFUL_COLOR, (int(screen_x), int(screen_y)), 12)

    if not swamp_harmful_weed_eaten:
        screen_x, screen_y = world_to_screen(*SWAMP_HARMFUL_WEED_POS)
        pygame.draw.circle(screen, SWAMP_HARMFUL_COLOR, (int(screen_x), int(screen_y)), 12)

    if not swamp_decoy_weed_eaten:
        screen_x, screen_y = world_to_screen(*SWAMP_DECOY_WEED_POS)
        pygame.draw.circle(screen, SWAMP_DECOY_WEED_COLOR, (int(screen_x), int(screen_y)), 12)


def draw_swamp_checklist():
    """
    Draws the swamp's own 3-item checklist, in the same on-screen slot
    the desert's checklist used (only one of the two is ever visible at
    once, since the desert's is hidden by start_swamp_room before this
    one appears).
    """
    checklist_x, checklist_y = SWAMP_CHECKLIST_POS
    box_rect = pygame.Rect(checklist_x, checklist_y, CHECKLIST_WIDTH, 20 + CHECKLIST_LINE_HEIGHT * 3)
    pygame.draw.rect(screen, (245, 235, 200), box_rect)
    pygame.draw.rect(screen, BLACK, box_rect, 2)

    checklist_items = [
        (SWAMP_INGREDIENT_FLOWER_1_NAME, swamp_ingredient_flower_1_collected),
        (SWAMP_INGREDIENT_FLOWER_2_NAME, swamp_ingredient_flower_2_collected),
        (SWAMP_INGREDIENT_FLOWER_3_NAME, swamp_ingredient_flower_3_collected),
    ]
    for i, (name, collected) in enumerate(checklist_items):
        line_y = box_rect.y + 10 + i * CHECKLIST_LINE_HEIGHT
        checkbox_rect = pygame.Rect(box_rect.x + 10, line_y + 2, CHECKLIST_CHECKBOX_SIZE, CHECKLIST_CHECKBOX_SIZE)
        pygame.draw.rect(screen, BLACK, checkbox_rect, 2)
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
    Draws the swamp's bridge as a vertical strip at SWAMP_BRIDGE_X,
    coloured broken (dark, splintered-looking) until swamp_bridge_fixed
    becomes True, at which point it switches to a solid fixed colour.
    """
    screen_x, _ = world_to_screen(SWAMP_BRIDGE_X, 0)
    bridge_rect = pygame.Rect(int(screen_x - BRIDGE_WIDTH // 2), 0, BRIDGE_WIDTH, SCREEN_HEIGHT)
    color = BRIDGE_FIXED_COLOR if swamp_bridge_fixed else BRIDGE_BROKEN_COLOR
    pygame.draw.rect(screen, color, bridge_rect)


def draw_tinker_items():
    """
    Draws the swamp's two scavengeable tinkering parts (the rusty cog and
    the vine-bound plank), each only for as long as it's still
    uncollected.
    """
    if not tinker_item_1_collected:
        screen_x, screen_y = world_to_screen(*TINKER_ITEM_1_POS)
        pygame.draw.circle(screen, TINKER_ITEM_COLOR, (int(screen_x), int(screen_y)), 12)

    if not tinker_item_2_collected:
        screen_x, screen_y = world_to_screen(*TINKER_ITEM_2_POS)
        pygame.draw.circle(screen, TINKER_ITEM_COLOR, (int(screen_x), int(screen_y)), 12)


def draw_swamp_bridge_checklist():
    """
    Draws the bridge-repair checklist (the two tinkering parts), reusing
    the same on-screen slot and post-it styling as the other checklists.
    """
    checklist_x, checklist_y = SWAMP_CHECKLIST_POS
    box_rect = pygame.Rect(checklist_x, checklist_y, CHECKLIST_WIDTH, 20 + CHECKLIST_LINE_HEIGHT * 2)
    pygame.draw.rect(screen, (245, 235, 200), box_rect)
    pygame.draw.rect(screen, BLACK, box_rect, 2)

    checklist_items = [
        (TINKER_ITEM_1_NAME, tinker_item_1_collected),
        (TINKER_ITEM_2_NAME, tinker_item_2_collected),
    ]
    for i, (name, collected) in enumerate(checklist_items):
        line_y = box_rect.y + 10 + i * CHECKLIST_LINE_HEIGHT
        checkbox_rect = pygame.Rect(box_rect.x + 10, line_y + 2, CHECKLIST_CHECKBOX_SIZE, CHECKLIST_CHECKBOX_SIZE)
        pygame.draw.rect(screen, BLACK, checkbox_rect, 2)
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
    Starts (or restarts) the 90-second room timer, used for the desert's
    ingredient-gathering countdown.
    """
    global room_timer_active, room_timer_start_time

    room_timer_active = True
    room_timer_start_time = pygame.time.get_ticks()


def update_room_timer():
    """
    Counts the room timer down, triggering handle_room_timer_expired()
    the moment it runs out. Does nothing once the timer isn't active.
    """
    if not room_timer_active:
        return

    elapsed = pygame.time.get_ticks() - room_timer_start_time
    if elapsed >= ROOM_TIMER_DURATION_MS:
        handle_room_timer_expired()


def draw_room_timer():
    """
    Draws the remaining seconds on the room timer just above the
    ingredient checklist, turning red once time is running low (10
    seconds or less) as an urgency cue.
    """
    elapsed = pygame.time.get_ticks() - room_timer_start_time
    seconds_left = max(0, (ROOM_TIMER_DURATION_MS - elapsed) // 1000 + 1)

    color = HP_BAR_COLOR_LOW if seconds_left <= 10 else WHITE
    timer_surface = hint_font.render(f"Time left: {int(seconds_left)}s", True, color)
    timer_rect = timer_surface.get_rect(topright=(SCREEN_WIDTH - 20, CHECKLIST_POS[1] - 22))
    screen.blit(timer_surface, timer_rect)


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
        screen_x, screen_y = world_to_screen(*INGREDIENT_FLOWER_1_POS)
        pygame.draw.circle(screen, INGREDIENT_FLOWER_WITHERED_COLOR, (int(screen_x), int(screen_y)), 12)

    if not ingredient_flower_2_collected:
        screen_x, screen_y = world_to_screen(*INGREDIENT_FLOWER_2_POS)
        pygame.draw.circle(screen, INGREDIENT_FLOWER_WITHERED_COLOR, (int(screen_x), int(screen_y)), 12)

    if not decoy_weed_interacted:
        screen_x, screen_y = world_to_screen(*DECOY_WEED_POS)
        pygame.draw.circle(screen, DECOY_WEED_COLOR, (int(screen_x), int(screen_y)), 12)


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
    dialogue_on_complete = "START_SWAMP_ROOM" if both_collected else None
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
        icon_path=None,
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
        icon_path=None,
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
    by draw_rat_companion() (Commit 14).
    """
    if rat_outcome in ("died", "bitter"):
        return
    screen_x, screen_y = world_to_screen(*RAT_POS)
    pygame.draw.circle(screen, RAT_COLOR, (int(screen_x), int(screen_y)), 12)


def draw_rat_companion():
    """
    Draws the Rat at his current follow position once he's agreed to
    join as a companion (Commit 14), the same way draw_sprite_character()
    draws Sprite.
    """
    screen_x, screen_y = world_to_screen(rat_draw_pos[0], rat_draw_pos[1])
    pygame.draw.circle(screen, RAT_COLOR, (int(screen_x), int(screen_y)), 12)


def start_rat_following():
    """
    Called once the Rat's healed-and-helped outcome dialogue finishes:
    switches him from his fixed spot into a following companion,
    positioned right at the protagonist's side from that point on.
    """
    global rat_state, rat_draw_pos
    rat_state = "FOLLOWING"
    rat_draw_pos = [protagonist["x"] + RAT_FOLLOW_OFFSET[0], protagonist["y"] + RAT_FOLLOW_OFFSET[1]]


def update_rat_companion_animation():
    """
    Keeps the Rat's on-screen position locked to his follow offset from
    the protagonist, once he's joined as a companion. Simpler than
    Sprite's own animation, since he walks alongside you rather than
    hovering.
    """
    global rat_draw_pos
    if rat_state != "FOLLOWING":
        return
    rat_draw_pos[0] = protagonist["x"] + RAT_FOLLOW_OFFSET[0]
    rat_draw_pos[1] = protagonist["y"] + RAT_FOLLOW_OFFSET[1]


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
    (Commit 14), marking the way toward the final confrontation.
    """
    screen_x, screen_y = world_to_screen(*DOOR_POS)
    door_rect = pygame.Rect(0, 0, 30, 70)
    door_rect.center = (int(screen_x), int(screen_y))
    pygame.draw.rect(screen, DOOR_COLOR, door_rect)


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

    sprite_helps = sprite_friendship_level >= SPRITE_FRIENDSHIP_HELP_THRESHOLD
    rat_helps = rat_outcome == "helped"

    if sprite_helps and rat_helps:
        dialogue_lines = ENDING_BOTH_HELP_TEXT
        dialogue_on_complete = "ACTIVATE_WIN_ENDING"
    elif sprite_helps:
        dialogue_lines = ENDING_SPRITE_ONLY_TEXT
        dialogue_on_complete = "ACTIVATE_WIN_ENDING"
    elif rat_helps:
        dialogue_lines = ENDING_RAT_ONLY_TEXT
        dialogue_on_complete = "ACTIVATE_WIN_ENDING"
    else:
        dialogue_lines = ENDING_NEITHER_HELP_TEXT
        dialogue_on_complete = "ACTIVATE_SELFISH_LOSS"

    current_line_index = 0
    revealed_chars = 0
    last_reveal_time = pygame.time.get_ticks()
    next_state_after_dialogue = "ROOM"
    dialogue_backdrop_state = "ROOM"
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

    hint_surface = hint_font.render("Press ENTER to try again", True, (180, 180, 180))
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

    title_surface = title_font.render("You Made It!", True, WHITE)
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 220))
    screen.blit(title_surface, title_rect)

    wrapped_lines = wrap_text(WIN_TEXT, dialogue_font, SCREEN_WIDTH - 100)
    line_height = dialogue_font.get_linesize()
    for i, line in enumerate(wrapped_lines):
        line_surface = dialogue_font.render(line, True, WHITE)
        line_rect = line_surface.get_rect(center=(SCREEN_WIDTH // 2, 320 + i * line_height))
        screen.blit(line_surface, line_rect)

    stats_text = (
        f"Time: {last_run_time_ms // 1000}s   "
        f"Best: {fastest_win_time_ms // 1000}s   "
        f"Total wins: {total_wins}"
    )
    stats_surface = hint_font.render(stats_text, True, (200, 200, 200))
    stats_rect = stats_surface.get_rect(center=(SCREEN_WIDTH // 2, 320 + len(wrapped_lines) * line_height + 20))
    screen.blit(stats_surface, stats_rect)

    hint_surface = hint_font.render("Press ENTER to play again", True, (180, 180, 180))
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

    if hp_bar_visible and game_state != "WIN":
        draw_hp_bar()
        draw_hp_heal_popup()
        draw_hp_damage_popup()
        draw_hearts()

    if checklist_visible and game_state != "WIN":
        draw_checklist()
        draw_room_timer()

    if swamp_checklist_visible and game_state != "WIN":
        draw_swamp_checklist()

    if swamp_bridge_checklist_visible and game_state != "WIN":
        draw_swamp_bridge_checklist()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()