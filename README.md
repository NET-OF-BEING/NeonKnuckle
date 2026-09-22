# Neon Knuckle

An original retro boxing game for Linux, inspired by the rhythm, perspective and
pixel presentation of 1990s arcade boxing. **Two-opponent prototype:** Jax “Switch”
Vega faces Bruno “Brick” Malone or Nico “Voltage” Reyes in the Dockside Circuit. All game art and sound
effects are original; no ROM, Nintendo sprites or other downloaded artwork is used.

## Play

Open **Neon Knuckle** from the application menu/Desktop, or run:

```bash
./launch.sh
```

Enter advances through the title, matchup and controls screens. On the matchup
screen, Up/Down selects the opponent and Left/Right switches between Practice
(default) and Arcade. Click the opponent portrait or use controller D-pad Up/Down
to switch opponents. Restart and rematch keep your current selection.

- **Bruno “Brick” Malone:** the original gatekeeper, with heavy hooks and a steady rhythm.
- **Nico “Voltage” Reyes:** quicker hooks, faster guard changes, and a delayed uppercut.
  Wait for the teal cue instead of guessing the timing from the previous punch.

Both opponents are available immediately. Circuit progression is not implemented yet.

| Action | Keyboard | SDL game controller |
|---|---|---|
| Left / right body punch | Z / X | X / B |
| Head punch | Hold Up + Z / X | Hold D-pad Up + X / B |
| Dodge left / right | Left / Right | D-pad or left stick |
| Block hooks | Hold Down | Hold D-pad Down |
| Power uppercut | Space, when meter is full | A |
| Get up after knockdown | Alternate Z and X | Alternate X and B |
| Confirm menus | Enter | A / Start |
| Pause / resume | P or Escape | Start |
| Restart while paused | R | Keyboard |
| Return to circuit while paused | Q | Keyboard |
| Toggle fullscreen | F11 | Keyboard |
| Toggle sound | M | Keyboard |

W/A/S/D also work for head aim / left dodge / block / right dodge.
Close the window or press Escape on the title screen to exit. Menu buttons also
accept mouse clicks. A controller uses SDL's standard mappings; unusual unmapped
controllers may require an SDL mapping. Physical controller play has not been tested.

## Graphics and sound

The ring now has neon signage, moving arena lights, canvas wear and camera flashes.
Fighters have reflected edge lighting, extra skin/cloth/glove detail, and clearer
hit bursts, spark trails and knockdown dust. The native pixel resolution remains
480×360 with crisp integer scaling.

Original synthesized effects distinguish body punches from head hits, with three
variations for impacts and movement, layered power thumps, a resonant bell and a
short victory flourish. Quiet crowd ambience plays during bouts and stops while
paused or in menus. **M** mutes all audio; `./launch.sh --mute` starts silent.
Combat timing and difficulty are unchanged by this presentation update.

## Winning the fight

- Watch the wind-up cue: dodge right against a left hook, left against a right hook.
- Uppercuts beat your block. Dodge either direction shortly before impact.
- Wait for the teal **DODGE NOW!** cue, then tap the indicated direction.
  The earlier gold/red warning announces the attack; do not dodge immediately.
- Dodges last 0.65 seconds in Practice and 0.36 seconds in Arcade. The cue appears
  0.55 / 0.26 seconds before impact respectively. Holding a direction does not
  repeat the dodge; release and tap again for the next attack.
- Counter during **OPEN!** for extra damage and power. A full meter unlocks Space.
- Only a successful dodge opens the counter window; taking or blocking a punch
  does not. Ordinary clean punches deal 3 damage, dodge counters deal 12, and
  power counters deal 29. Repeated body punches alone are a losing strategy.
- When your opponent guards his head, punch his body. When he guards low, hold Up to aim high.
- Three knockdowns produce a TKO. Alternate punches before the ten-count to get up.
- After three minutes, knockdowns decide the winner, then remaining health. A tie
  goes to the opponent. Practice increases wind-up time and reduces incoming damage.

## Installation on another Linux machine

Requires Python 3.13 and an SDL-compatible desktop/audio environment. This checkout
already has its own `.venv` with pygame-ce 2.5.7 installed.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
chmod +x launch.sh
./launch.sh
```

The checked-in `.desktop` entry contains this machine's absolute project path;
adjust it if relocating. No network or server is required after setup.

## Local data and troubleshooting

- Best score: `$XDG_DATA_HOME/neon-knuckle/record.json`, default
  `~/.local/share/neon-knuckle/record.json`. Both opponents and difficulties share the prototype best score.
- Launcher log: `$XDG_STATE_HOME/neon-knuckle/launch.log`, default
  `~/.local/state/neon-knuckle/launch.log`.
- Audio failure falls back to silent play. `./launch.sh --mute` starts muted.
- Switching away from the window or disconnecting a controller pauses the fight.
- The launcher selects native Wayland when a Wayland session is present. You can
  override this explicitly with `SDL_VIDEODRIVER=x11 ./launch.sh` on an X11 display.
- Rendering uses a 480×360 canvas and crisp integer scaling, with letterboxing.
- This prototype uses original procedural pixel sprites and sound effects; it has
  no music track, full tournament, configurable key bindings, or packaged AppImage yet.

## Development and checks

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python tests/playthrough.py
bash -n launch.sh
desktop-file-validate neon-knuckle.desktop
```

The playthrough drives SDL keyboard events through the normal application. It wins
a complete Arcade fight against each opponent, verifies score persistence, rematches
and loses by count-out. It saves ten screenshots plus a JSON report per opponent
under `artifacts/brick/` and `artifacts/voltage/`. It uses temporary
records so tests do not overwrite your best score.

`combat.py` contains the independent rules; `art.py`, `ui.py`, and `audio.py` handle
presentation; `app.py` handles the window, input and records. See
`docs/verification.md` for the verified delivery state.
