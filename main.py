#!/usr/bin/env python3
"""Launch Neon Knuckle, an original offline Linux arcade boxing game."""
import argparse
import os
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
from neon_knuckle.app import App


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mute', action='store_true', help='Start with sound disabled')
    args = parser.parse_args()
    app = App()
    if args.mute:
        app.audio.muted = True
    app.run()


if __name__ == '__main__':
    main()
