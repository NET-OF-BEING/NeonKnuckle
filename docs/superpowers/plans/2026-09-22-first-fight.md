# Neon Knuckle Implementation Plan

> Execute inline using the executing-plans workflow; this is a new isolated repo.

**Goal:** Deliver a playable original Linux boxing fight with retro presentation.

**Architecture:** Deterministic combat model separate from pygame rendering/input.
Procedural original pixel art and synthesised audio require no external assets.

**Tech Stack:** Python 3.13, pygame-ce 2.5.7, unittest, Linux desktop entry.

**Spec:** `docs/superpowers/specs/2026-09-22-first-fight-design.md`

## Global constraints

- Linux desktop, original characters and assets, offline play.
- One matchup; truthful prototype scope; keep source reference files unchanged.
- Own virtualenv, executable LF shell launcher, local incremental commits.

## Task 1: Deterministic fight

Files: `neon_knuckle/combat.py`, `tests/test_combat.py`.
Interface: `Fight(difficulty='arcade')`, `step(dt, defense=None)`,
`punch(hand, high=False, power=False)`, `dodge(direction)`, `get_up(hand)`.

- [x] Write behavior tests before implementation; run `python3 -m unittest discover -s tests -v`.
- [x] Implement 120 Hz model stepping, guard, timed attacks/defense, health, meter,
      knockdown/get-up/TKO, intro, timer and event queue.
- [x] Prove correct dodge protects and wrong dodge hits; counter does extra damage;
      power cannot be spent twice; finite dodge expires; fight can finish both ways.
- [x] Commit with `git commit -m 'feat: add deterministic boxing combat'`.

## Task 2: Playable presentation

Files: `neon_knuckle/art.py`, `ui.py`, `audio.py`, `app.py`, `main.py`.
Inputs: combat model state and events. Output: live 60 fps desktop game.

- [x] Draw native 480×360 arena and original layered sprites; animate from states.
- [x] Add title, portrait matchup, controls overlay, fight HUD, pause and result.
- [x] Add keyboard/gamepad actions, resize/fullscreen, focus pause, local records.
- [x] Add original synthesised punch, bell, block, dodge and menu sounds.
- [x] Render representative screens into `artifacts/` using SDL dummy driver;
      inspect images and run scripted full-fight input through the application.
- [x] Commit with `git commit -m 'feat: add original arcade presentation and controls'`.

## Task 3: Delivery

Files: `launch.sh`, `README.md`, `assets/icon.png`, `neon-knuckle.desktop`.

- [x] Install executable launcher and Desktop/application entries.
- [x] Run combat tests, headless integration checks, bash syntax, desktop validation.
- [x] Launch desktop game and inspect an actual screenshot; report any unavailable checks.
- [x] Record verification in `docs/verification.md`; commit delivery files.
- [x] Update shared Codex summary/history and script index entry.
