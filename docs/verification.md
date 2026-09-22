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
