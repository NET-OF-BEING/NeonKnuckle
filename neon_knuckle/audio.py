"""Original layered Foley and arcade accents, synthesized once into cached PCM."""
from array import array
from functools import lru_cache
import math
import random
import pygame as pg


DURATIONS = {'body': .22, 'head': .16, 'power': .42, 'hurt': .28,
             'blocked': .15, 'swing': .14, 'swoosh': .23, 'evade': .19,
             'cue': .09, 'menu': .12, 'bell': 1.4, 'win': 1.8,
             'knockdown': .75, 'crowd': 3.0}
VARIED = {'body', 'head', 'power', 'hurt', 'blocked', 'swing', 'swoosh'}


@lru_cache(maxsize=128)
def synthesize(name, rate, variant=0):
    """Return mono signed-16 PCM with smooth edges and ample mixing headroom."""
    duration = DURATIONS[name]
    rng = random.Random(71 + variant*997 + sum(map(ord, name)))
    samples = array('h')
    low = previous = phase = 0.0
    pitch = 1 + (variant-1)*.045
    for i in range(int(rate*duration)):
        t = i/rate
        u = t/duration
        noise = rng.uniform(-1, 1)
        low += .075 * (noise-low)
        high = noise-previous
        previous = noise
        if name in ('body', 'head', 'power', 'hurt', 'knockdown', 'blocked'):
            bass = {'body': 115, 'head': 185, 'power': 77, 'hurt': 95,
                    'knockdown': 53, 'blocked': 230}[name]
            phase += 2*math.pi*pitch*(bass + bass*1.8*math.exp(-t*65))/rate
            thud = math.sin(phase)*math.exp(-t*(19 if name == 'head' else 13))
            snap = high*math.exp(-t*(75 if name == 'head' else 110))
            leather = low*4*math.exp(-t*23)
            value = .48*thud + (.38 if name == 'head' else .22)*snap + .3*leather
            if name in ('power', 'knockdown'):
                value += .25*math.sin(2*math.pi*46*t)*math.exp(-t*8)
                value += .2*low*math.exp(-t*5)
            if name == 'blocked':
                value = .35*thud + .7*leather
        elif name in ('swing', 'swoosh', 'evade'):
            envelope = math.sin(math.pi*u)**2
            value = (1.4*low + .09*high)*envelope
            if name == 'evade':
                value += .13*math.sin(2*math.pi*(650*t+900*t*t))*envelope
        elif name == 'bell':
            value = sum(gain*math.sin(2*math.pi*freq*t)*math.exp(-t*decay)
                        for freq, gain, decay in ((740,.35,3), (1187,.2,4),
                                                 (1993,.12,5), (3021,.07,7)))
            value += high*.12*math.exp(-t*130)
        elif name == 'win':
            value = 0
            for start, freq in ((0,392), (.18,494), (.36,587), (.58,784)):
                age = t-start
                if age >= 0:
                    env = min(1, age*180)*math.exp(-age*3.8)
                    value += .22*env*(math.sin(2*math.pi*freq*age)
                                      + .22*math.sin(4*math.pi*freq*age))
        elif name == 'crowd':
            # A low, diffuse bed of filtered noise and distant vowel-like tones.
            swell = .65 + .25*math.sin(2*math.pi*t/duration)
            murmur = sum(math.sin(2*math.pi*f*t + .3*math.sin(t*5+j))
                         for j, f in enumerate((137, 181, 233, 307)))
            value = (.9*low + .035*murmur)*swell
        else:
            freq = 660 if name == 'cue' else 880
            value = .27*math.sin(2*math.pi*freq*t)*math.exp(-t*32)
        # Short attack, longer release prevent clicks, including crowd loop seam.
        edge = min(1, t/.003, (duration-t)/(.16 if name == 'crowd' else .025))
        samples.append(round(18000*math.tanh(value)*max(0, edge)))
    return samples.tobytes()


class Audio:
    def __init__(self):
        self.muted = False
        self.sounds = {}
        self.next_variant = {}
        self.crowd_channel = self.signal_channel = None
        try:
            if not pg.mixer.get_init():
                pg.mixer.init(44100, -16, 2, 512)
            rate, sample_format, channels = pg.mixer.get_init()
            if sample_format != -16:
                self.muted = True
                return
            pg.mixer.set_num_channels(16)
            pg.mixer.set_reserved(2)
            self.crowd_channel = pg.mixer.Channel(0)
            self.signal_channel = pg.mixer.Channel(1)
            for name in DURATIONS:
                variants = []
                for variant in range(3 if name in VARIED else 1):
                    pcm = synthesize(name, rate, variant)
                    if channels > 1:
                        mono = array('h', pcm)
                        pcm = array('h', (sample for sample in mono for _ in range(channels))).tobytes()
                    sound = pg.mixer.Sound(buffer=pcm)
                    sound.set_volume(.24 if name == 'crowd' else .65)
                    variants.append(sound)
                self.sounds[name] = variants
        except (pg.error, OSError):
            self.muted = True
            self.sounds.clear()

    def play(self, name, **details):
        if name == 'hit':
            name = 'head' if details.get('high') else 'body'
        if self.muted or name not in self.sounds or not pg.mixer.get_init():
            return None
        variants = self.sounds[name]
        index = self.next_variant.get(name, 0)
        self.next_variant[name] = (index+1) % len(variants)
        # find_channel() can return reserved channels; allocate effects explicitly.
        channel = (self.signal_channel if name in ('bell', 'win', 'cue') else
                   next((pg.mixer.Channel(i) for i in range(2, 16)
                         if not pg.mixer.Channel(i).get_busy()), None))
        if channel is not None:
            channel.play(variants[index])
        return channel

    def set_crowd(self, active):
        if self.crowd_channel is None or not pg.mixer.get_init() or 'crowd' not in self.sounds:
            return
        if active and not self.muted:
            if not self.crowd_channel.get_busy():
                self.crowd_channel.play(self.sounds['crowd'][0], loops=-1)
        else:
            self.crowd_channel.stop()

    def toggle(self):
        self.muted = not self.muted
        if self.muted and pg.mixer.get_init():
            pg.mixer.stop()
