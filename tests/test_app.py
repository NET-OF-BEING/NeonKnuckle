"""SDL event routing and application lifecycle, using a dummy display."""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import tempfile
import unittest
from pathlib import Path
import pygame as pg
from neon_knuckle.app import App, load_record


class AppTests(unittest.TestCase):
    def test_crowd_follows_fight_pause_and_menu_transitions(self):
        self.fight()
        self.assertTrue(self.app.audio.crowd_channel.get_busy())
        self.key(pg.K_p)
        self.app.update(.02)
        self.assertFalse(self.app.audio.crowd_channel.get_busy())
        self.key(pg.K_p)
        self.app.update(.02)
        self.assertTrue(self.app.audio.crowd_channel.get_busy())
        self.key(pg.K_p)
        self.key(pg.K_q)
        self.app.update(.02)
        self.assertFalse(self.app.audio.crowd_channel.get_busy())

    def test_opponent_selection_survives_restart_and_rematch(self):
        self.key(pg.K_RETURN)
        self.key(pg.K_DOWN)
        self.key(pg.K_RIGHT)
        self.key(pg.K_RETURN)
        self.key(pg.K_RETURN)
        self.assertEqual(self.app.fight.opponent_id, 'voltage')
        self.assertEqual(self.app.fight.difficulty, 'arcade')
        self.key(pg.K_p)
        self.key(pg.K_r)
        self.assertEqual(self.app.fight.opponent_id, 'voltage')
        self.app.fight.end('opponent', 'KO')
        self.app.update(.02)
        self.app.render()
        self.key(pg.K_RETURN)
        self.assertEqual(self.app.fight.opponent_id, 'voltage')
        self.key(pg.K_p)
        self.key(pg.K_q)
        self.key(pg.K_UP)
        self.key(pg.K_RETURN)
        self.key(pg.K_RETURN)
        self.assertEqual(self.app.fight.opponent_id, 'brick')

    def test_mouse_and_controller_can_select_opponent(self):
        self.key(pg.K_RETURN)
        self.app.render()
        rect = next(rect for rect, action in self.app.ui.buttons if action == 'opponent')
        self.app.handle_event(pg.event.Event(pg.MOUSEBUTTONDOWN, button=1,
                                            pos=(rect.centerx*2, rect.centery*2)))
        self.assertEqual(self.app.opponent_id, 'voltage')
        self.app.handle_event(pg.event.Event(pg.CONTROLLERBUTTONDOWN,
                                            button=pg.CONTROLLER_BUTTON_DPAD_UP))
        self.assertEqual(self.app.opponent_id, 'brick')

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.app = App(size=(960,720), record_path=Path(self.temp.name)/'record.json')

    def tearDown(self):
        pg.quit()
        self.temp.cleanup()

    def key(self, key, down=True):
        self.app.handle_event(pg.event.Event(pg.KEYDOWN if down else pg.KEYUP, key=key, repeat=False))

    def fight(self):
        for _ in range(3):
            self.key(pg.K_RETURN)
        for _ in range(190):
            self.app.update(1/60)

    def test_enter_reaches_fight_and_punch_key_lands(self):
        self.fight()
        self.assertEqual(self.app.screen, 'fight')
        self.assertEqual(self.app.fight.state, 'fight')
        self.key(pg.K_z)
        for _ in range(12):
            self.app.update(1/60)
        self.assertLess(self.app.fight.opponent_hp, 100)

    def test_focus_loss_pauses_and_clears_held_keys(self):
        self.fight()
        self.key(pg.K_DOWN)
        self.app.handle_event(pg.event.Event(pg.WINDOWFOCUSLOST))
        self.assertTrue(self.app.fight.paused)
        self.assertFalse(self.app.held)
        elapsed = self.app.fight.elapsed
        self.app.update(.1)
        self.assertEqual(self.app.fight.elapsed, elapsed)

    def test_escape_pauses_then_resumes_without_quitting(self):
        self.fight()
        self.key(pg.K_ESCAPE)
        self.assertTrue(self.app.fight.paused)
        self.key(pg.K_ESCAPE)
        self.assertFalse(self.app.fight.paused)
        self.assertTrue(self.app.running)

    def test_all_menu_screens_render(self):
        for screen in ('title', 'roster', 'instructions'):
            self.app.screen = screen
            self.app.render()
            self.assertNotEqual(self.app.canvas.get_at((0,0))[:3], (0,0,0))

    def test_corrupt_or_wrong_type_record_does_not_prevent_start(self):
        path = Path(self.temp.name)/'corrupt.json'
        for content in ('broken', '[]', '{"best":"oops"}'):
            path.write_text(content)
            self.assertEqual(load_record(path)['best'], 0)

    def test_restart_recreates_fight(self):
        self.fight()
        self.key(pg.K_ESCAPE)
        self.key(pg.K_r)
        self.assertEqual(self.app.fight.elapsed, 0)
        self.assertEqual(self.app.fight.state, 'intro')
        self.assertFalse(self.app.fight.paused)


if __name__ == '__main__':
    unittest.main()
