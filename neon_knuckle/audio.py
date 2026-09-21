"""Small original arcade sound effects; unavailable audio never blocks play."""
from array import array
import math
import random
import pygame as pg


class Audio:
    def __init__(self):
        self.muted = False
        self.sounds = {}
        try:
            if not pg.mixer.get_init():
                pg.mixer.init(22050, -16, 1, 512)
            rate, _, channels = pg.mixer.get_init()
            specs = {'hit': (.12, 130, .5), 'power': (.25, 85, .6), 'hurt': (.2, 90, .55),
                     'blocked': (.08, 280, .6), 'swing': (.065, 90, .3), 'swoosh': (.10, 180, .15),
                     'evade': (.12, 620, .02), 'cue': (.045, 330, .05), 'menu': (.09, 520, .01),
                     'bell': (.65, 830, .015), 'win': (.85, 660, .02), 'knockdown': (.32, 65, .4)}
            rng = random.Random(34)
            for name, (duration, freq, noise) in specs.items():
                samples = array('h')
                for i in range(int(rate*duration)):
                    t = i / rate
                    envelope = (1-t/duration)**2 * min(1, t*500)
                    tone = math.sin(2*math.pi*freq*t*(1-.3*t/duration))
                    if name in ('bell', 'win'):
                        tone += .3*math.sin(2*math.pi*freq*2.76*t)
                    value = int(10000*envelope*((1-noise)*tone+noise*rng.uniform(-1, 1)))
                    samples.extend([value]*channels)
                self.sounds[name] = pg.mixer.Sound(buffer=samples)
        except (pg.error, OSError):
            self.muted = True

    def play(self, name):
        if not self.muted and name in self.sounds:
            self.sounds[name].play()

    def toggle(self):
        self.muted = not self.muted
        if self.muted and pg.mixer.get_init():
            pg.mixer.stop()
