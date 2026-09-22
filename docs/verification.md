# Verification — 2026-09-22

## Automated checks

- `.venv/bin/python -m unittest discover -s tests -v`: 21 passing tests.
- `.venv/bin/python tests/playthrough.py`: passes SDL keyboard-driven title →
  matchup → instructions → Arcade fight → victory → rematch → count-out defeat.
- Scripted victory: 9,300 points, 12.03 seconds of fight time, 100 remaining HP,
  11 counters, four clean dodges, three opponent knockdowns, TKO. The automation
  knows the attack state; this demonstrates reachability, not human difficulty balance.
- Temporary best-score file persisted the result. Real player records untouched.
- Ten screenshots generated under `artifacts/`; title, matchup, controls, fight,
  attack cue and victory were visually inspected. Rank glyph and cue placement
  were corrected. Native canvas 480×360; captures scaled to 1440×1080.
- `bash -n launch.sh`, `desktop-file-validate neon-knuckle.desktop` and
  `git diff --check` pass. Installed Desktop entry also passes validation.

## Desktop check

- Application and Desktop entries installed as `neon-knuckle.desktop`.
- `gtk-launch neon-knuckle` initially returned success, but this alone did not
  establish a visible window. The default SDL backend selected X11 while the
  user's desktop is Wayland. X11 screenshot capture was blank.
- Native Wayland startup and rendering diagnostic passed. Launcher now selects
  `SDL_VIDEODRIVER=wayland` when `WAYLAND_DISPLAY` is present and the driver has
  not already been explicitly set.
- Launched the final `./launch.sh` in a live session. Log reports
  `Neon Knuckle ready: wayland, (1440, 1080)`.
- KDE Spectacle desktop capture `/tmp/neon-knuckle-wayland.png` showed the actual
  title screen, partly behind other windows. The desktop capture includes unrelated
  applications and is intentionally not copied into the repository.
- An earlier X11 test session was interrupted intentionally; its KeyboardInterrupt
  in the append-only launch log is from that shutdown, before the successful Wayland line.

## Limits

- Physical controller hardware and audible playback have not been manually tested.
  SDL input mappings and synthesis code exist; silent fallback is supported.
- One matchup is complete. Full tournament/character-selection roster, music,
  controller remapping and an AppImage are not part of this first prototype.
- Visuals are original procedural pixel artwork, not a recreation of Nintendo's
  sprite animation. Human playtesting is still needed to tune feel and difficulty.

## Reference inputs

- User video: `/home/panda/Videos/[SNES] Super Punch-Out - No Damage HD.mp4`,
  17.621 seconds, 720×900, 30 fps; original remains unchanged.
- User-supplied screenshots from Unseen64 and Wizard Dojo were inspected.
- Portrait/circuit layout reference:
  https://www.reddit.com/r/punchout/comments/vuegsd/i_have_finally_finished_my_ultimate_punch_out/
  by Foxaias_Rythm. Its art was inspected as a reference, not included in the game.

## 2026-09-22 dodge accessibility

Practice dodge duration is now 0.65 seconds, with a 0.19-second recovery gap.
Directional DODGE NOW cue begins 0.55 seconds before impact in Practice and
0.26 seconds in Arcade. Animation and instructions were updated.
All 23 unit tests and the Arcade win/loss playthrough passed. Nine additional
SDL Practice scenarios covered hooks/uppercuts with immediate, 0.2-second and
0.4-second reactions. Rendered cue/help inspected; no desktop restart performed.

## 2026-09-22 combat balance

Only successfully evaded attacks open bonus counter damage/power and bypass
guard. The opening closes after recovery or knockdown. Ordinary punches now
deal 3 damage (previously 4); dodge counters remain 12 and power counters 29.
All 26 tests passed, including blind body-punch spam losing in both modes even
with get-ups, and counter-only wins at 0.2/0.4-second Practice and 0.12-second
Arcade cue reaction delays. The SDL playthrough passed: 10,230-point TKO at
14.07 fight seconds, 100 HP, 12 counters and five dodges; rematch count-out passed.
No human playtest or live desktop restart performed.

## 2026-09-22 animation readability

Animation update: progressive hook wind-ups and uppercut crouch, strike retraction, smoother player punches synchronized to impact (including power shots), larger striking gloves and player recoil. Attack poses stay visible during hit flashes. Knockdowns accelerate onto the canvas; count/recovery UI moved above the action.

26 tests and SDL win/loss playthrough passed with unchanged combat results.
Rendered attack/fall phase sheets and revised knockdown overlay inspected.
No live desktop restart or human playtest.

## 2026-09-22 second opponent

Added Nico “Voltage” Reyes with original portrait/ring variations, faster hooks,
a delayed uppercut, a distinct attack sequence and faster guard changes. Matchup
selection supports keyboard Up/Down, mouse portrait clicks and controller D-pad.
Difficulty selection, restart and rematch retain the chosen opponent. Fighter
identity follows selection through HUD, knockdown and defeat screens.

- 30 unit tests pass, including both opponents' delayed-reaction counter wins
  and blind-punch losses in Practice/Arcade, and selection/restart/rematch input tests.
- SDL keyboard playthrough passes for both opponents: Brick 10,230-point TKO
  at 14.07 fight seconds; Voltage 10,170-point TKO at 14.06 seconds. Both retain
  100 HP, land 12 counters, evade five attacks, then lose rematches by count-out.
- Twenty captures and two JSON reports are saved separately under
  `artifacts/brick/` and `artifacts/voltage/`; temporary records protect real scores.
- Inspected Voltage matchup, attack cue and knockdown captures.
- Python compilation, launcher/desktop syntax and `git diff --check` passed.
- No live desktop restart, physical controller test or human balance playtest.
  This is two selectable fights; tournament progression remains future work.

## 2026-09-22 graphics and SFX polish

User confirmed beating Nico in actual play and that his rhythm felt noticeably
different from Bruno. This update keeps combat rules and hit-stop timing intact.

- Added reflected fighter edges, torso/glove/trunk detail, less transparent player,
  lighter scanlines, rafters/neon signage, canvas scuffs, moving light beams,
  camera flashes, expanding impact bursts, particle trails and knockdown dust.
- Replaced single-tone audio with original layered 44.1 kHz synthesis: distinct
  head/body hits, three impact/movement variants, power/knockdown bass, leather
  blocks, noise swooshes, resonant bell, victory notes and quiet crowd ambience.
- Crowd pauses/stops on pause, menus, result and mute; silent-device fallback
  survives mute toggles. Dedicated crowd/cue channels cannot be stolen by effects.
- 37 unit tests pass, including PCM boundaries/headroom, head/body routing,
  audio saturation/channel isolation, missing audio device and crowd lifecycle.
- Both complete SDL win/rematch/loss playthroughs still pass with exactly the
  previous scores/times/HP: Brick 10,230 / 14.07 / 100; Nico 10,170 / 14.06 / 100.
- Python compilation and `git diff --check` pass. Headless 960×720 window render
  probe averaged 9.44 ms over 360 frames;
  this is not a live desktop frame-rate guarantee.
- Visual review: `artifacts/presentation/graphics-preview.png`, plus fight captures.
  Audio review artifact: `artifacts/presentation/sfx-preview.wav` (12.6 s, mono PCM
  44.1 kHz); accompanying JSON lists effect timestamps. Full FFmpeg decode passed,
  preview peak 8,848/32,767. Numeric checks do not establish subjective sound quality.
- No live desktop restart, speaker audition or physical controller test performed.
