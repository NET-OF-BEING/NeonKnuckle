# Neon Knuckle — Linux first fight

User-approved direction: standalone Linux, new characters, one complete fight,
retro pixel graphics, keyboard controls, punches, dodging, blocking and knockouts.
The supplied video and screenshots inform presentation; the Reddit roster image
informs framed character portraits and circuit labels. No Nintendo assets ship.

## Experience

Title → Dockside circuit matchup → three-second introduction → fight → result.
Jax “Switch” Vega is the player, facing Bruno “Brick” Malone. This build contains
one matchup, not a full tournament. Matchup portraits show the two original boxers.
Practice and Arcade offer different reaction windows and damage.

480×360 logical canvas, nearest-neighbour scaling, resizable 1440×1080 default
bounded to the screen; fullscreen available. Detailed pixel silhouettes, shaded
skin, expressive faces, perspective ring, crowd, impact sparks and brief hit-stop.
Player viewed from behind with partial transparency. Original synthesised effects.

## Play

Z/X: left/right punch; hold Up for head punches, otherwise body shots.
Left/Right: short timed dodge; Down: block; Space: power uppercut with full meter.
P/Escape pauses; F11 toggles fullscreen; M toggles sound. Enter confirms screens.
Gamepad buttons and directional inputs are supported if SDL detects a controller.
An on-screen help overlay explains controls and opponent cues before the fight.

Opponent guard alternates; hit the unguarded level for small damage. A successful
dodge opens a larger counter window and charges power. Punching and dodging have
finite durations and cooldowns, preventing permanent invulnerability and spam.
Three readable attacks: left hook (dodge right), right hook (dodge left), uppercut
(dodge either direction; cannot block). Opponent speeds up after knockdowns.
Three knockdowns end the fight as a TKO; player can get up twice by alternating
Z/X before the ten-count. The fight ends at three minutes if unfinished.

## Architecture and checks

Python 3.13 project virtualenv; pygame-ce 2.5.7. No server or network needed to play.
`combat.py` owns deterministic simulation and events; `art.py` draws characters
and arena; `ui.py` draws screens; `audio.py` synthesises sound; `app.py` owns SDL,
input and persistence. Records use XDG data storage and tolerate unwritable files.
Missing audio is non-fatal. Tests cover defense direction, finite dodge duration,
guard selection, meter consumption, recovery, pause, countdown and end-to-end wins
and losses. Headless rendered captures and a real desktop launch verify visuals.

Linux shell launcher is executable, uses its own cwd and venv. Menu and Desktop
entries use a project-local icon. Local git commits and shared state are updated.
