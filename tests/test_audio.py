"""Real PCM generation and SDL mixer lifecycle checks (silent test device)."""
import os
os.environ['SDL_AUDIODRIVER'] = 'dummy'
from array import array
import unittest
from unittest.mock import patch
import pygame as pg
from neon_knuckle.audio import Audio


class AudioTests(unittest.TestCase):
    def setUp(self):
        pg.mixer.init(44100, -16, 1, 512)
        self.audio = Audio()

    def tearDown(self):
        pg.mixer.quit()

    def test_head_and_body_impacts_have_distinct_pcm_with_headroom(self):
        self.assertIn('head', self.audio.sounds)
        self.assertIn('body', self.audio.sounds)
        self.assertNotEqual(self.audio.sounds['head'][0].get_raw(),
                            self.audio.sounds['body'][0].get_raw())
        for variants in self.audio.sounds.values():
            for sound in variants:
                samples = array('h', sound.get_raw())
                self.assertGreater(max(map(abs, samples)), 100)
                self.assertLess(max(map(abs, samples)), 28000)
                self.assertLess(abs(samples[0]), 100)
                self.assertLess(abs(samples[-1]), 100)

    def test_crowd_stops_on_mute_and_resumes_only_when_active(self):
        self.audio.set_crowd(True)
        self.assertTrue(self.audio.crowd_channel.get_busy())
        self.audio.toggle()
        self.assertFalse(pg.mixer.get_busy())
        self.audio.set_crowd(True)
        self.assertFalse(pg.mixer.get_busy())
        self.audio.toggle()
        self.audio.set_crowd(True)
        self.assertTrue(self.audio.crowd_channel.get_busy())
        self.audio.set_crowd(False)
        self.assertFalse(self.audio.crowd_channel.get_busy())

    def test_hit_metadata_selects_head_or_body_sound(self):
        head = self.audio.play('hit', high=True)
        self.assertIn(head.get_sound(), self.audio.sounds['head'])
        body = self.audio.play('hit', high=False)
        self.assertIn(body.get_sound(), self.audio.sounds['body'])

    def test_bell_remains_available_when_effect_channels_are_full(self):
        for _ in range(30):
            self.audio.play('power')
        bell = self.audio.play('bell')
        self.assertIsNotNone(bell)
        self.assertIn(bell.get_sound(), self.audio.sounds['bell'])

    def test_combat_sounds_do_not_occupy_reserved_channels(self):
        self.audio.set_crowd(True)
        self.audio.play('bell')
        for _ in range(30):
            self.audio.play('power')
        self.assertIn(self.audio.crowd_channel.get_sound(), self.audio.sounds['crowd'])
        self.assertIn(self.audio.signal_channel.get_sound(), self.audio.sounds['bell'])
        self.audio.set_crowd(False)
        self.audio.signal_channel.stop()
        self.audio.play('body')
        self.assertIsNone(self.audio.crowd_channel.get_sound())
        self.assertIsNone(self.audio.signal_channel.get_sound())

    def test_missing_audio_device_stays_safe_after_toggle(self):
        pg.mixer.quit()
        with patch.object(pg.mixer, 'init', side_effect=pg.error('No audio device')):
            audio = Audio()
        self.assertTrue(audio.muted)
        audio.toggle()
        audio.set_crowd(True)
        self.assertIsNone(audio.play('bell'))
