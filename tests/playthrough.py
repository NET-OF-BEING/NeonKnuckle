"""Scripted SDL keyboard playthrough, screenshots and score persistence check."""
import json
import os
import sys
import tempfile
from pathlib import Path
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pygame as pg
from neon_knuckle.app import App


def main():
    destination = Path('artifacts')
    destination.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as temp:
        app = App(size=(960,720), record_path=Path(temp)/'record.json')

        def press(key):
            for kind in (pg.KEYDOWN, pg.KEYUP):
                pg.event.post(pg.event.Event(kind, key=key, repeat=False))
            for event in pg.event.get():
                app.handle_event(event)

        def capture(name):
            app.render()
            pg.image.save(pg.transform.scale(app.canvas, (1440,1080)), destination/f'{name}.png')

        capture('01-title')
        press(pg.K_RETURN)
        # Verify both difficulty choices before using Arcade for the full win.
        press(pg.K_RIGHT)
        assert app.difficulty == 'arcade'
        capture('02-matchup')
        press(pg.K_RETURN)
        capture('03-controls')
        press(pg.K_RETURN)
        capture('04-intro')
        captures = set()
        for tick in range(60*220):
            f = app.fight
            if f.state == 'fight' and app.freeze <= 0:
                if 'fight' not in captures:
                    capture('05-fight')
                    captures.add('fight')
                    press(pg.K_p)
                    capture('06-pause')
                    press(pg.K_p)
                if f.opponent_state == 'windup':
                    if 'cue' not in captures:
                        capture('07-attack-cue')
                        captures.add('cue')
                    if f.opponent_timer < .18:
                        press(pg.K_LEFT if f.attack == 'right' else pg.K_RIGHT)
                elif f.opponent_state == 'recover' and f.dodge_timer <= 0:
                    if f.power >= 100:
                        press(pg.K_SPACE)
                    else:
                        press(pg.K_x)
                elif f.opponent_state == 'idle':
                    if f.guard == 'low':
                        app.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_UP, repeat=False))
                    press(pg.K_z)
                    app.handle_event(pg.event.Event(pg.KEYUP, key=pg.K_UP))
            app.update(1/60)
            if tick % 30 == 0:
                app.render()
            if f.state == 'opponent_down' and 'down' not in captures:
                capture('08-knockdown')
                captures.add('down')
            if app.screen == 'result':
                break
        assert app.fight.winner == 'player', (app.fight.state, app.fight.player_hp)
        assert app.fight.player_hp == 100
        assert app.fight.opponent_downs == 3
        assert json.loads(app.record_path.read_text())['best'] == app.fight.score
        capture('09-victory')
        victory = {'score': app.fight.score, 'time': round(app.fight.elapsed, 2),
                   'hp': app.fight.player_hp, 'counters': app.fight.counters,
                   'dodges': app.fight.dodges, 'finish': app.fight.finish}
        press(pg.K_RETURN)
        for tick in range(60*130):
            app.update(1/60)
            if tick % 60 == 0:
                app.render()
            if app.screen == 'result':
                break
        assert app.fight.winner == 'opponent'
        assert app.fight.finish == 'KO'
        capture('10-defeat')
        pg.image.save(app.art.icon(), 'assets/icon.png')
        result = {'victory': victory, 'idle_loss': app.fight.finish, 'screenshots': 10}
        (destination/'playthrough.json').write_text(json.dumps(result, indent=2)+'\n')
        print(json.dumps(result, indent=2))
        pg.quit()


if __name__ == '__main__':
    main()
