## Floraborne

A narrative-driven 2D exploration game built with Python and Pygame. You wake up after a world-altering catastrophe, guided by a sarcastic, once-herbalist sprite, and have to cross a scorching desert and a poisoned swamp — winning over a bitter, guilt-ridden Rat along the way — to decide how (or whether) the world's balance gets restored.

## How to Play (Quick Start)

1. Run the game (`python Floraborne.py`) and choose **New Game** from the title screen.
2. Read the opening dialogue, then explore the desert with **arrow keys / WASD**. Watch your HP bar because the heat drains it!
3. Press **E** on the ice flower to heal up and get permanently immune to the heat. This also introduces the sprite properly and opens up two dialogue choices. Answer warmly for the best friendship outcome.
4. Once the checklist appears, press **E** on the two named ingredient flowers (avoid the decoy weed) to brew a potion and move into the swamp — there's no time limit, so take your time.
5. In the swamp, repeat the checklist puzzle with 3 ingredients — but watch out, two of the other plants there cost you HP if eaten.
6. Cross the repaired bridge (find and combine 2 scavenged parts first), then talk to the Rat. Be kind and patient across all 4 of his dialogue prompts to win him over.
7. Walk to the door at the far end of the swamp and press **E**. What happens next depends on how much the sprite and the Rat trust you — see **The Four Endings** below.
8. If you run out of hearts along the way, press **Enter** on the Game Over screen to try again.

---
## Full Documentation

### Story

Long ago, this land was full of life and wonder — until a great catastrophe struck. You wake up with no memory of what happened, in a desert that's now baking hot and littered with withered, dying flowers. A tiny sprite of light — once a herbalist, before the same magical surge that broke the world turned her into this — appears to stop you from eating the wrong flower, and ends up sticking around as your reluctant guide. Together, you cross the desert and a poisoned swamp, winning over (or losing) a broken, guilt-ridden Rat who knows exactly what's sustaining the disaster, and ultimately decide together whether to face it — or not.

### Features

- Full state-machine-driven flow: title screen, branching dialogue, dialogue choices, free-roam exploration across two biomes, a pause menu, item popups, an ingredient checklist puzzle, a game-over screen, and a win screen.
- Typewriter-style scrolling dialogue system, reused for every conversation in the game.
- Two connected biomes (desert and swamp), each with their own background, world size, and camera scrolling.
- A heat/HP survival mechanic in the desert, cured permanently by finding the right flower.
- A 3-heart lives system: losing all HP costs a heart and respawns you at a checkpoint; losing your last heart ends the run.
- Two ingredient-checklist potion puzzles (2 ingredients in the desert, 3 in the swamp), plus a third checklist puzzle to scavenge 2 parts to repair a broken bridge — none of them are time-limited, so exploration is at the player's own pace.
- Harmful decoy plants in the swamp that cost HP if eaten, alongside a harmless decoy that just wastes time — not every wrong pick is equally safe.
- A branching friendship system with the sprite companion (two dialogue-choice moments) and a much deeper one with the Rat (four sequential dialogue-choice checks that determine whether he dies, is healed but stays bitter, or is healed and joins you).
- Once won over, the Rat becomes a following companion, just like the sprite.
- An exit door that only appears once the Rat's fate is resolved, leading into the final decision point.
- Four distinct branching endings (one win-condition failure state, three different winning stories) driven entirely by the sprite's and the Rat's accumulated friendship/outcome state — see below.
- Session statistics tracked with global counters: games played, total deaths, total wins, and your fastest win time — shown on the title screen and both end screens.

### Requirements

- Python 3.8 or newer
- The `pygame` package (installed via `pip`, see below)
- Works the same way on **Windows**, **macOS**, and **Linux** — Pygame is cross-platform and the game doesn't use any OS-specific paths or libraries.

### Installation & Running

**macOS / Linux**
git clone <this-repo-url>
cd <repo-folder>
python3 -m venv venv
source venv/bin/activate
pip install pygame
python3 Floraborne.py

**Windows (Command Prompt / PowerShell)**
git clone <this-repo-url>
cd <repo-folder>
python -m venv venv
venv\Scripts\activate
pip install pygame
python Floraborne.py

> If `python` isn't recognized on Windows, try `py` instead (e.g. `py -m venv venv`, `py Floraborne.py`) — this depends on how Python was installed. On macOS, plain `python` may point to an old Python 2 install, so `python3` is used above to be safe.
> The virtual environment (`venv`) step is optional but recommended so `pygame` doesn't install system-wide. You can skip it and just run `pip install pygame` directly if you'd rather not bother with it.
> Keep the `assets/` folder (the game's PNG images) in the same folder as `Floraborne.py` — the game still runs without it (falling back to plain shapes), but graphics won't display correctly if it's missing or moved.

### Controls

| Input | Action |
|---|---|
| Arrow keys / WASD | Move around the current room |
| E | Interact with a nearby flower, weed, object, the bridge, the Rat, or the door |
| Space / Enter / Left-click | Advance dialogue |
| Up / Down | Navigate menus and dialogue choices |
| Enter | Confirm a menu option or dialogue choice |
| Esc | Open/close the pause menu |

### Detailed Walkthrough & Game Logic

This section documents every mechanic in enough detail to reproduce the game's logic from scratch.

**Title & intro:** The title screen offers New Game / Quit, plus running session stats once at least one game has been played. New Game plays a 3-line catastrophe intro, then a 4-line desert intro, then drops the player into free movement in the desert.

**Desert biome:**
- A decoy flower and an (initially hidden) ice flower sit in the world. Walking near the decoy triggers the sprite's warning dialogue (her first appearance). Eating it anyway (press E) costs 1 friendship point (floored at 0) and a disappointed reaction.
- Walking near the ice flower triggers a hint dialogue; eating it restores 80 HP (capped at 100) and grants permanent heat immunity, via an item popup. The *first* time this popup is closed, it chains automatically into the sprite's full backstory dialogue and two 3-option dialogue-choice moments (each worth +3/+1/+0 friendship depending on the answer chosen), ending with the potion-recipe intro.
- The potion-recipe intro reveals a 2-item checklist ("Sunroot Bloom", "Cactus Blossom"). Pressing E on each real flower ticks it off; a decoy weed does nothing but waste time. Collecting both brews the potion automatically and, after a short loading-screen dialogue, transitions into the swamp.
- The heat continuously drains HP roughly once a second until the ice flower is eaten. If HP hits 0, the player loses 1 heart and respawns at the desert entrance (with HP restored); losing the 3rd heart ends the run on the Game Over screen.

**Swamp biome:**
- On first entry, a dialogue explains a stronger 3-ingredient potion is needed, and reveals a 3-item checklist. Three real ingredient flowers, two harmful decoys (a flower and a weed that each cost 25 HP if eaten), and one harmless decoy weed are scattered around. Collecting all 3 real ingredients brews the balance potion.
- Next, a broken bridge blocks the path. A bridge-intro dialogue reveals a 2-item checklist for two scavenged parts (a rusty cog and a vine-bound plank). Collecting both brews a tinkering potion; pressing E on the bridge then repairs it, letting the player cross.
- Past the bridge, the Rat is found injured and refuses help. Talking to him (E) plays his grumpy refusal, then chains automatically through a "why do you care" prompt and 4 sequential 3-option dialogue-choice checks (each affecting `rat_friendship_level`, floored at 0). Once all 4 resolve, his total is compared against two thresholds:
  - At or below the low threshold → he panics and runs off (`rat_outcome = "died"`); he's gone for the rest of the game.
  - Between the two thresholds → he's healed by the balance potion but stays bitter and limps away alone (`rat_outcome = "bitter"`).
  - At or above the high threshold → he's healed, grateful, and asks to join (`rat_outcome = "helped"`) — from this point on he follows the player around the same way the sprite does.
- Once the Rat's encounter is resolved (whichever way it went), a door appears further into the swamp. Interacting with it (E) plays a final-battle intro dialogue about the ancient evil sustaining the disaster, then immediately resolves the ending (see below) — no further input needed once that dialogue finishes.

**Hearts, checkpoints & game over:** The player starts with 3 hearts. Losing a heart (currently triggered only by heat depletion in the desert) respawns the player at their last checkpoint with HP restored; losing the 3rd heart ends the run on the Game Over screen, which normally shows a hearts-based message but shows a different narrative message for the "neither helps" ending (see below). Either way, pressing Enter returns to the title screen.

### The Four Endings

The instant the door dialogue finishes, the game checks two independent conditions:
- **Does the sprite help?** — Yes if `sprite_friendship_level` is 4 or higher (out of a possible 6 from her two dialogue choices).
- **Does the Rat help?** — Yes only if his outcome was `"helped"` (his top tier); if he died or stayed bitter, he will not join the fight even if the player was otherwise kind to him elsewhere.

| Sprite helps? | Rat helps? | Result |
|---|---|---|
| Yes | Yes | **Best ending.** Balance is restored; Sprite and the Rat build a new apothecary together, fall in love once human again, and teach the player everything they know. |
| Yes | No | **Win.** The player succeeds and continues their journey with Sprite, but later hears sad whispers about the Rat's fate. |
| No | Yes | **Win, with a twist.** The player succeeds, but without Sprite's expertise the same magic that twisted the Rat catches up to the player too — they become a rat as well, and the two live out their rat lives together as friends. |
| No | No | **Loss.** Neither companion trusted the player enough to help; potions alone weren't enough, ending on the Game Over screen with a narrative-specific message instead of the usual hearts-based one. |

The three winning combinations all route into the same Win screen (updating `total_wins`, `last_run_time_ms`, and `fastest_win_time_ms`) after their own ending text plays; the losing combination routes into the Game Over screen with `game_over_text_override` set instead of the default hearts-based message.

### Project structure

- `Floraborne.py` — the entire game. It's a single file by design, built incrementally commit-by-commit.

### Key Functions Reference

Every system below is broken into several small, single-purpose functions rather than one large block, demonstrating the code's modularity.

**Setup & shared helpers**
- `load_image_safe()` / `load_sheet_frame()` — load a PNG (or one frame out of a spritesheet), returning `None` on any failure so callers fall back to a plain shape instead of crashing. This is the project's error handling around unexpected/bad input.
- `draw_image_or_circle()` — shared helper that draws an image if it loaded, otherwise a fallback circle.
- `world_to_screen()` / `update_camera()` — world-to-screen coordinate conversion and camera following.
- `wrap_text()` / `render_outlined_text()` — text-wrapping and outlined-text helpers reused by every dialogue box, popup, and label.

**Title & pause menus**
- `draw_title_screen()`, `activate_menu_option()`, `handle_title_input()`
- `draw_pause_menu()`, `activate_pause_option()`, `handle_pause_input()`
- `draw_placeholder_screen()`, `handle_placeholder_input()` — the Settings/Save "coming soon" screens

**Dialogue system (reused for every conversation in the game)**
- `draw_text_box()`, `update_text_reveal()`, `handle_dialogue_input()` — the typewriter-style dialogue box
- `start_dialogue_choice()`, `resolve_dialogue_choice()`, `draw_dialogue_choice()`, `handle_dialogue_choice_input()`, `trigger_friendship_flash()` — the reusable 3-option choice component powering every Sprite and Rat friendship moment

**Desert biome**
- `check_decoy_flower_trigger()`, `consume_decoy_flower()`, `check_ice_flower_trigger()`, `consume_ice_flower()`
- `draw_ingredient_flowers()`, `consume_ingredient_flower()`, `consume_decoy_weed()`, `show_ingredient_checklist()`, `draw_checklist()`

**HP, hearts & checkpoints**
- `activate_heat_drain()`, `update_heat_drain()`, `handle_hp_depleted()`
- `draw_hp_bar()`, `draw_hearts()`, `show_hp_heal_popup()` / `draw_hp_heal_popup()`, `show_hp_damage_popup()` / `draw_hp_damage_popup()`

**Swamp biome**
- `draw_swamp_flowers()`, `draw_swamp_checklist()`, `consume_swamp_ingredient_flower()`, `consume_swamp_harmful_flower()`, `consume_swamp_harmful_weed()`, `consume_swamp_decoy_weed()`
- `draw_bridge()`, `draw_tinker_items()`, `draw_swamp_bridge_checklist()`, `consume_tinker_item()`, `repair_bridge()`

**The Rat**
- `check_rat_trigger()`, `encounter_rat()`, `start_rat_prodding_intro_dialogue()`, `start_rat_choice_1()` through `start_rat_choice_4()`, `resolve_rat_outcome()`
- `draw_rat()`, `draw_rat_companion()`, `start_rat_following()`

**Door, final battle & endings**
- `start_swamp_room()`, `draw_door()`, `trigger_final_battle()`, `resolve_final_battle()`
- `activate_win_ending()`, `activate_selfish_loss()`

**End screens & session stats**
- `draw_game_over_screen()`, `draw_win_screen()`, `handle_game_over_input()`, `handle_win_input()`, `reset_run_state()`

### Session Statistics

The game tracks session-wide statistics using global counter variables (`games_played`, `total_deaths`, `total_wins`, `fastest_win_time_ms`, `friendship_points_gained`), which persist across every attempt in a single session (intentionally not reset when starting a new run — see `reset_run_state()`). These display on the title screen (games played / wins) and on both end screens: the Win screen (this run's time, best time, total wins, games played, and total deaths) and the Game Over screen (games played, total deaths, total wins, and friendship points gained this run).

### Use of AI

This project was developed independently, with AI used only in a supporting, efficiency-focused capacity rather than for core design or implementation work.

Before writing any code, I spent the first part of the week researching and planning across two separate working files: reading discussions on the internet and Reddit, and studying other developers' open-source Pygame projects on GitHub and YouTube, to understand good function structure and think through what systems this game would need. I also spent time exploring Pygame's own features directly to understand what was feasible. Development itself began later on, at which point I built the game function-by-function, following the structure I'd planned out, and iterated commit-by-commit, adding bits of code from my exploration where they fit and worked — the repository's 56 commits document every step and edit made throughout the process.

AI was used for three specific purposes: troubleshooting issues encountered while building,teaching me new functions step by step so that I can better understand them, and helping format parts of the documentation more efficiently. It was not used to plan the game's logic, design its functions, write the dialogue and story or write thefull code itself — that work came from my own planning, research, and iteration, supported throughout by detailed personal notes on what each new function and Pygame feature taught me along the way.

### Credits

Pixel art assets used in this project are free/open-source resources sourced from itch.io:
- [Free Pixel Art Flower Pack](https://karsiori.itch.io/free-pixel-art-flower-pack) — karsiori
- [Assorted Pixel Art Game Assets (16x16)](https://joyofgaming.itch.io/assorted-pixel-art-game-assets-16x16) — joyofgaming
- [Rats](https://micaxx.itch.io/rats) — micaxx
- [All-in-One Pixel Game Assets Bundle](https://retrocodedev.itch.io/all-in-one-pixel-game-assets-bundle) — retrocodedev
- [Butterfly](https://papoycore.itch.io/butterfly) — papoycore
- [Clock Pixel Art](https://bontt.itch.io/clock-pixel-art) — bontt

### Author

- Andreea Alexandra Nistor 


