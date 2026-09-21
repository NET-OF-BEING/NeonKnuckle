"""Desktop window, SDL controls and local score storage."""
import json
import math
import os
from pathlib import Path
import pygame as pg
from pygame._sdl2 import controller
from .art import Art, W, H, INK
from .audio import Audio
from .combat import Fight
from .ui import UI


def load_record(path):
    try:
        value = json.loads(Path(path).read_text())
        if not isinstance(value, dict) or type(value.get('best', 0)) is not int:
            return {'best': 0}
        return {'best': max(0, value.get('best', 0))}
    except (OSError, ValueError, TypeError):
        return {'best': 0}


class App:
    def __init__(self, size=None, record_path=None):
        pg.mixer.pre_init(22050, -16, 1, 512)
        pg.init()
        controller.init()
        self.controllers = {}
        for index in range(controller.get_count()):
            self.add_controller(index)
        if size is None:
            info = pg.display.Info()
            scale = max(1, min(3, (info.current_w-100)//W, (info.current_h-100)//H))
            size = (W*scale, H*scale)
        self.window_size = size
        self.fullscreen = False
        self.window = pg.display.set_mode(size, pg.RESIZABLE)
        pg.display.set_caption('Neon Knuckle — Dockside Circuit')
        self.canvas = pg.Surface((W, H))
        self.art = Art()
        pg.display.set_icon(self.art.icon())
        self.ui = UI(self.art)
        self.audio = Audio()
        self.fight = Fight()
        self.screen = 'title'
        self.difficulty = 'practice'
        self.running = True
        self.held = set()
        self.pad_held = set()
        self.stick = (0, 0)
        self.t = 0
        self.freeze = 0
        self.viewport = pg.Rect(0, 0, *size)
        self.record_path = Path(record_path) if record_path else Path(
            os.environ.get('XDG_DATA_HOME', str(Path.home()/'.local/share')))/'neon-knuckle/record.json'
        self.record = load_record(self.record_path)
        self.record_saved = False

    def add_controller(self, index):
        try:
            if controller.is_controller(index):
                pad = controller.Controller(index)
                self.controllers[pad.as_joystick().get_instance_id()] = pad
        except pg.error:
            pass

    def start_fight(self):
        self.fight = Fight(self.difficulty)
        self.screen = 'fight'
        self.held.clear()
        self.pad_held.clear()
        self.stick = (0, 0)
        self.freeze = 0
        self.record_saved = False
        self.ui.sparks.clear()
        self.audio.play('bell')

    def confirm(self):
        self.audio.play('menu')
        if self.screen == 'title':
            self.screen = 'roster'
        elif self.screen == 'roster':
            self.screen = 'instructions'
        elif self.screen in ('instructions', 'result'):
            self.start_fight()
        elif self.screen == 'fight' and self.fight.paused:
            self.fight.paused = False

    def back(self):
        if self.screen == 'title':
            self.running = False
        elif self.screen == 'fight':
            self.fight.paused = not self.fight.paused
        elif self.screen == 'instructions':
            self.screen = 'roster'
        elif self.screen == 'result':
            self.screen = 'roster'
        else:
            self.screen = 'title'

    def change_difficulty(self):
        self.difficulty = 'arcade' if self.difficulty == 'practice' else 'practice'
        self.audio.play('menu')

    def toggle_fullscreen(self):
        if not self.fullscreen:
            self.window_size = self.window.get_size()
        self.fullscreen = not self.fullscreen
        self.window = pg.display.set_mode((0, 0) if self.fullscreen else self.window_size,
                                          pg.FULLSCREEN if self.fullscreen else pg.RESIZABLE)

    def handle_event(self, event):
        if event.type == pg.QUIT:
            self.running = False
        elif event.type == pg.WINDOWFOCUSLOST:
            self.held.clear()
            self.pad_held.clear()
            self.stick = (0, 0)
            if self.screen == 'fight':
                self.fight.paused = True
        elif event.type == pg.KEYUP:
            self.held.discard(event.key)
        elif event.type == pg.KEYDOWN:
            self.held.add(event.key)
            if not getattr(event, 'repeat', False):
                self.key(event.key)
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.viewport.collidepoint(event.pos):
                pos = ((event.pos[0]-self.viewport.x)*W/self.viewport.w,
                       (event.pos[1]-self.viewport.y)*H/self.viewport.h)
                for rect, action in self.ui.buttons:
                    if rect.collidepoint(pos):
                        {'confirm': self.confirm, 'back': self.back, 'difficulty': self.change_difficulty}[action]()
                        break
        elif event.type == pg.CONTROLLERDEVICEADDED:
            self.add_controller(event.device_index)
        elif event.type == pg.CONTROLLERDEVICEREMOVED:
            pad = self.controllers.pop(event.instance_id, None)
            if pad:
                pad.quit()
            self.pad_held.clear()
            self.stick = (0, 0)
            if self.screen == 'fight':
                self.fight.paused = True
        elif event.type in (pg.CONTROLLERBUTTONDOWN, pg.CONTROLLERBUTTONUP):
            mapping = {pg.CONTROLLER_BUTTON_X: pg.K_z, pg.CONTROLLER_BUTTON_B: pg.K_x,
                       pg.CONTROLLER_BUTTON_A: pg.K_SPACE, pg.CONTROLLER_BUTTON_START: pg.K_p,
                       pg.CONTROLLER_BUTTON_BACK: pg.K_ESCAPE,
                       pg.CONTROLLER_BUTTON_DPAD_LEFT: pg.K_LEFT, pg.CONTROLLER_BUTTON_DPAD_RIGHT: pg.K_RIGHT,
                       pg.CONTROLLER_BUTTON_DPAD_UP: pg.K_UP, pg.CONTROLLER_BUTTON_DPAD_DOWN: pg.K_DOWN}
            key = mapping.get(event.button)
            if key is not None:
                if event.type == pg.CONTROLLERBUTTONUP:
                    self.pad_held.discard(key)
                else:
                    self.pad_held.add(key)
                    if self.screen != 'fight' and key in (pg.K_SPACE, pg.K_p):
                        self.confirm()
                    else:
                        self.key(key)
        elif event.type == pg.CONTROLLERAXISMOTION:
            if event.axis in (pg.CONTROLLER_AXIS_LEFTX, pg.CONTROLLER_AXIS_LEFTY):
                axis = 0 if event.axis == pg.CONTROLLER_AXIS_LEFTX else 1
                value = -1 if event.value < -16000 else 1 if event.value > 16000 else 0
                if value != self.stick[axis]:
                    old_keys = ((pg.K_LEFT, pg.K_RIGHT), (pg.K_UP, pg.K_DOWN))[axis]
                    self.pad_held.difference_update(old_keys)
                    self.stick = (value, self.stick[1]) if axis == 0 else (self.stick[0], value)
                    if value:
                        key = old_keys[0 if value < 0 else 1]
                        self.pad_held.add(key)
                        if axis == 0:
                            self.key(key)

    def key(self, key):
        if key == pg.K_F11:
            self.toggle_fullscreen()
        elif key == pg.K_m:
            self.audio.toggle()
        elif key == pg.K_RETURN:
            self.confirm()
        elif key == pg.K_ESCAPE:
            self.back()
        elif self.screen == 'roster' and key in (pg.K_LEFT, pg.K_RIGHT, pg.K_a, pg.K_d):
            self.change_difficulty()
        elif self.screen == 'fight':
            f = self.fight
            if key == pg.K_p:
                f.paused = not f.paused
            elif f.paused:
                if key == pg.K_r:
                    self.start_fight()
                elif key == pg.K_q:
                    self.screen = 'roster'
                    self.held.clear()
            elif key in (pg.K_z, pg.K_x, pg.K_SPACE):
                if f.state == 'player_down' and key != pg.K_SPACE:
                    f.get_up('left' if key == pg.K_z else 'right')
                else:
                    held = self.held | self.pad_held
                    f.block = bool(held & {pg.K_DOWN, pg.K_s}) and f.dodge_timer <= 0
                    f.punch('left' if key == pg.K_z else 'right',
                            high=bool(held & {pg.K_UP, pg.K_w}) or key == pg.K_SPACE,
                            power=key == pg.K_SPACE)
            elif key in (pg.K_LEFT, pg.K_a, pg.K_RIGHT, pg.K_d):
                f.dodge('left' if key in (pg.K_LEFT, pg.K_a) else 'right')

    def update(self, dt):
        dt = min(.1, dt)
        if self.screen == 'fight' and self.fight.paused:
            return
        self.t += dt
        self.ui.update(dt)
        if self.screen != 'fight':
            return
        if self.freeze > 0:
            self.freeze = max(0, self.freeze-dt)
            return
        held = self.held | self.pad_held
        self.fight.step(dt, 'block' if held & {pg.K_DOWN, pg.K_s} else None)
        for event in self.fight.events:
            self.audio.play(event['kind'])
            self.ui.event(event)
            if event['kind'] in ('hit', 'power', 'hurt'):
                self.freeze = .055 if event['kind'] == 'power' else .025
        self.fight.events.clear()
        if self.fight.state == 'result':
            self.screen = 'result'
            self.save_record()

    def save_record(self):
        if self.record_saved:
            return
        self.record_saved = True
        self.record['best'] = max(self.record['best'], self.fight.score)
        try:
            self.record_path.parent.mkdir(parents=True, exist_ok=True)
            temp = self.record_path.with_suffix(f'.{os.getpid()}.tmp')
            temp.write_text(json.dumps(self.record)+'\n')
            temp.replace(self.record_path)
        except OSError:
            # The score still appears for this session on read-only home directories.
            pass

    def render(self):
        s = self.canvas
        if self.screen == 'title':
            self.ui.title(s, self.t, self.record)
        elif self.screen == 'roster':
            self.ui.roster(s, self.t, self.difficulty, self.record)
        elif self.screen == 'instructions':
            self.ui.instructions(s, self.t)
        elif self.screen == 'fight':
            self.ui.fight(s, self.fight, self.t, self.audio.muted)
            if self.fight.paused:
                self.ui.pause(s)
        elif self.screen == 'result':
            self.ui.result(s, self.fight, self.t, self.record)
        s.blit(self.art.scanlines, (0, 0))
        ww, wh = self.window.get_size()
        scale = min(ww/W, wh/H)
        if scale >= 1:
            scale = int(scale)
        width, height = max(1, int(W*scale)), max(1, int(H*scale))
        self.viewport = pg.Rect((ww-width)//2, (wh-height)//2, width, height)
        self.window.fill(INK)
        shake = int(math.sin(self.t*140)*2) if self.ui.shake > 0 and not self.fight.paused else 0
        self.window.blit(pg.transform.scale(s, (width, height)), self.viewport.move(shake, 0))
        pg.display.flip()

    def run(self):
        clock = pg.time.Clock()
        while self.running:
            dt = clock.tick(60)/1000
            for event in pg.event.get():
                self.handle_event(event)
            self.update(dt)
            self.render()
        pg.quit()
