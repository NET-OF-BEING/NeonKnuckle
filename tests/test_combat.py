"""Rules that distinguish a fair fight from an unwinnable or exploitable one."""
import unittest

from neon_knuckle.combat import Fight


def advance(fight, seconds, defense=None):
    for _ in range(round(seconds * 120)):
        fight.step(1 / 120, defense)


def active():
    fight = Fight()
    advance(fight, 3)
    return fight


def telegraph(fight):
    for _ in range(1200):
        if fight.opponent_state == 'windup':
            return
        fight.step(1 / 120)
    raise AssertionError('Opponent never attacks')


class FightTests(unittest.TestCase):
    def test_intro_protects_both_boxers(self):
        f = Fight()
        self.assertFalse(f.punch('left'))
        advance(f, 2)
        self.assertEqual((f.player_hp, f.opponent_hp), (100, 100))
        self.assertEqual(f.elapsed, 0)

    def test_correct_dodge_opens_counter(self):
        f = active()
        telegraph(f)
        advance(f, f.opponent_timer - .15)
        self.assertTrue(f.dodge('right'))
        advance(f, .2)
        self.assertEqual(f.player_hp, 100)
        self.assertGreater(f.power, 0)
        self.assertEqual(f.opponent_state, 'recover')

    def test_wrong_dodge_takes_damage(self):
        f = active()
        telegraph(f)
        advance(f, f.opponent_timer - .15)
        f.dodge('left')
        advance(f, .2)
        self.assertLess(f.player_hp, 100)

    def test_early_dodge_expires(self):
        f = active()
        telegraph(f)
        f.dodge('right')
        advance(f, 1)
        self.assertLess(f.player_hp, 100)

    def test_block_reduces_hook_damage(self):
        f = active()
        telegraph(f)
        advance(f, 1, 'block')
        self.assertGreater(f.player_hp, 90)
        self.assertLess(f.player_hp, 100)

    def test_landed_opponent_attack_has_visible_strike_phase(self):
        f = active()
        telegraph(f)
        advance(f, f.opponent_timer + .04)
        self.assertGreater(f.strike_timer, 0)
        advance(f, .3)
        self.assertEqual(f.strike_timer, 0)

    def test_uppercut_breaks_block(self):
        f = active()
        for _ in range(6000):
            if f.opponent_state == 'windup' and f.attack == 'upper':
                hp = f.player_hp
                advance(f, f.opponent_timer + .05, 'block')
                self.assertGreater(hp - f.player_hp, 20)
                return
            f.step(1 / 120, 'block')
        self.fail('No uppercut')

    def test_guard_blocks_matching_height(self):
        f = active()
        f.guard = 'high'
        f.punch('left', high=True)
        advance(f, .2)
        self.assertEqual(f.opponent_hp, 100)

    def test_unguarded_body_shot_lands(self):
        f = active()
        f.guard = 'high'
        f.punch('left')
        advance(f, .2)
        self.assertLess(f.opponent_hp, 100)

    def test_punch_cooldown_prevents_spam(self):
        f = active()
        self.assertTrue(f.punch('left'))
        self.assertFalse(f.punch('right'))

    def test_power_requires_and_consumes_full_meter(self):
        f = active()
        self.assertFalse(f.punch('right', power=True))
        f.power = 100
        self.assertTrue(f.punch('right', power=True))
        self.assertEqual(f.power, 0)
        advance(f, .6)
        self.assertFalse(f.punch('right', power=True))

    def test_pause_freezes_fight(self):
        f = active()
        f.paused = True
        before = (f.elapsed, f.opponent_timer, f.player_hp)
        advance(f, 3)
        self.assertEqual(before, (f.elapsed, f.opponent_timer, f.player_hp))

    def test_idle_player_loses_by_count_out(self):
        f = active()
        advance(f, 100)
        self.assertEqual(f.state, 'result')
        self.assertEqual(f.winner, 'opponent')
        self.assertEqual(f.finish, 'KO')

    def test_get_up_requires_alternating_buttons(self):
        f = active()
        while f.state == 'fight':
            f.step(1 / 120)
        self.assertEqual(f.state, 'player_down')
        for _ in range(50):
            f.get_up('left')
        self.assertLess(f.recovery, 1)
        for n in range(30):
            f.get_up('right' if n % 2 == 0 else 'left')
        advance(f, 4)
        self.assertEqual(f.state, 'fight')
        self.assertGreater(f.player_hp, 0)

    def test_timed_defense_and_counters_can_win(self):
        f = active()
        for _ in range(120 * 180):
            if f.state == 'fight':
                if f.opponent_state == 'windup' and f.opponent_timer < .18:
                    f.dodge('left' if f.attack == 'right' else 'right')
                elif f.opponent_state == 'recover' and f.dodge_timer <= 0:
                    f.punch('left', high=True, power=f.power >= 100)
                elif f.opponent_state == 'idle':
                    f.punch('right', high=f.guard == 'low')
            f.step(1 / 120)
            if f.state == 'result':
                break
        self.assertEqual(f.winner, 'player')
        self.assertEqual(f.finish, 'TKO')
        self.assertEqual(f.opponent_downs, 3)
        self.assertEqual(f.player_hp, 100)


if __name__ == '__main__':
    unittest.main()
