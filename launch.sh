#!/usr/bin/env bash
# Launch Neon Knuckle using the project's Python environment on Linux.
set -euo pipefail
PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"
if [[ ! -x .venv/bin/python ]]; then
    printf 'Neon Knuckle needs its virtual environment. See %s/README.md\n' "$PROJECT_DIR" >&2
    exit 1
fi
export PYGAME_HIDE_SUPPORT_PROMPT=1
export SDL_VIDEO_X11_WMCLASS=neon-knuckle
if [[ -n "${WAYLAND_DISPLAY:-}" && -z "${SDL_VIDEODRIVER:-}" ]]; then
    export SDL_VIDEODRIVER=wayland
fi
LOG_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/neon-knuckle"
mkdir -p "$LOG_DIR"
exec .venv/bin/python main.py "$@" >> "$LOG_DIR/launch.log" 2>&1
