"""Arcade screens and fight presentation."""
import math
import random
import pygame as pg
from .combat import OPPONENTS
from .art import (W, H, INK, NAVY, PANEL, LINE, WHITE, MUTED, GOLD, TEAL, RED,
                  text, text_width, star, ellipse, poly)


def panel(s, rect, color=LINE, fill=PANEL):
    pg.draw.rect(s, fill, rect)
    pg.draw.rect(s, color, rect, 1)


def button(s, label, rect, selected=True):
    panel(s, rect, GOLD if selected else LINE, '#544538' if selected else NAVY)
    text(s, label, (rect[0] + rect[2]//2, rect[1] + (rect[3]-7)//2), GOLD if selected else WHITE, center=True)


class UI:
    def __init__(self, art):
        self.art = art
        self.portraits = {who: art.portrait(who) for who in ('player', *OPPONENTS)}
        self.small = {who: pg.transform.scale(p, (28, 28)) for who, p in self.portraits.items()}
        self.sparks = []
        self.shake = 0
        self.buttons = []

    def event(self, event):
        kind = event['kind']
        if kind in ('hit', 'power', 'hurt'):
            self.shake = .16 if kind == 'power' else .07
            x, y = (240, 148 if event.get('high') else 195) if kind != 'hurt' else (240, 262)
            for _ in range(15 if kind == 'power' else 8):
                self.sparks.append([x, y, random.uniform(-100, 100), random.uniform(-95, 25), .4, GOLD if kind != 'hurt' else RED])

    def update(self, dt):
        self.shake = max(0, self.shake - dt)
        for spark in self.sparks:
            spark[0] += spark[2] * dt
            spark[1] += spark[3] * dt
            spark[3] += dt * 250
            spark[4] -= dt
        self.sparks = [spark for spark in self.sparks if spark[4] > 0]

    def base(self, s, t):
        s.fill(INK)
        for y in range(0, H, 8):
            pg.draw.line(s, '#191d32', (0, y), (W, y))
        for x in range(-H, W, 24):
            pg.draw.line(s, '#1d2239', (x, H), (x+H, 0))
        pg.draw.rect(s, GOLD, (0, 0, W, 3))
        text(s, 'NK / DOCKSIDE CIRCUIT', (14, 13), MUTED)
        text(s, 'EST. 1994', (405, 13), GOLD)

    def title(self, s, t, record):
        self.base(s, t)
        # Fighter silhouettes frame the title like cabinet side art.
        rival = self.art.opponent(t, 'idle')
        rival.set_alpha(65)
        s.blit(pg.transform.scale(rival, (268, 316)), (286, 42))
        player = self.art.player(t)
        player.set_alpha(65)
        s.blit(pg.transform.scale(player, (238, 272)), (-58, 90))
        for x in (127, 353):
            star(s, (x, 61), 7, GOLD)
        text(s, 'AFTER HOURS. ALL HEART.', (240, 58), GOLD, center=True)
        text(s, 'NEON', (240, 84), TEAL, 7, center=True)
        text(s, 'KNUCKLE', (240, 139), WHITE, 5, center=True)
        pg.draw.line(s, GOLD, (143, 185), (337, 185), 2)
        text(s, 'READ THE MOVE. MAKE YOUR MOMENT.', (240, 202), MUTED, center=True)
        button(s, 'ENTER THE CIRCUIT  >', (139, 233, 202, 29))
        text(s, 'PRESS ENTER / CONTROLLER A', (240, 274), WHITE if int(t*2)%2 else MUTED, center=True)
        text(s, f"BEST SCORE  {record.get('best', 0):06d}", (240, 302), GOLD, center=True)
        text(s, 'ORIGINAL ARCADE BOXING / TWO CHALLENGERS', (240, 335), MUTED, center=True)
        self.buttons = [(pg.Rect(139, 233, 202, 29), 'confirm')]

    def roster(self, s, t, difficulty, record, opponent_id='brick'):
        opponent = OPPONENTS[opponent_id]
        self.base(s, t)
        text(s, 'DOCKSIDE CIRCUIT', (240, 40), GOLD, 2, center=True)
        text(s, 'CHOOSE YOUR OPPONENT / UP + DOWN', (240, 65), MUTED, center=True)
        # Portrait frames and patterns echo the supplied circuit roster reference.
        for who, x, color in (('player', 54, TEAL), (opponent_id, 322, GOLD)):
            panel(s, (x-3, 88, 110, 114), color, INK)
            s.blit(self.portraits[who], (x, 91))
            pg.draw.rect(s, color, (x-3, 205, 110, 15))
            text(s, 'CHALLENGER' if who == 'player' else ('#1 / GATEKEEPER' if opponent_id == 'brick' else '#2 / LIVE WIRE'), (x+52, 209), INK, center=True, shadow=False)
        text(s, 'VS', (240, 130), WHITE, 4, center=True)
        text(s, 'JAX VEGA', (106, 230), WHITE, 2, center=True)
        text(s, opponent.name, (374, 230), WHITE, 1, center=True)
        text(s, '"SWITCH"'.replace('"', ''), (106, 252), TEAL, center=True)
        text(s, opponent.nickname, (374, 248), GOLD, 2, center=True)
        text(s, 'FAST HANDS / BIG HEART', (106, 270), MUTED, center=True)
        text(s, opponent.style, (374, 270), MUTED, center=True)
        text(s, '<', (161, 294), GOLD)
        text(s, f'{difficulty.upper()} MODE', (240, 294), GOLD, center=True)
        text(s, '>', (314, 294), GOLD)
        button(s, 'ENTER / STEP INTO THE RING', (134, 310, 212, 25))
        text(s, 'UP DOWN: RIVAL / LEFT RIGHT: MODE / ESC: BACK', (240, 345), MUTED, center=True)
        self.buttons = [(pg.Rect(305, 85, 139, 195), 'opponent'), (pg.Rect(145, 285, 190, 21), 'difficulty'), (pg.Rect(134, 310, 212, 25), 'confirm')]

    def instructions(self, s, t):
        self.base(s, t)
        text(s, 'LEARN THE RHYTHM', (240, 40), GOLD, 2, center=True)
        text(s, 'DEFEND. COUNTER. FINISH.', (240, 66), TEAL, center=True)
        rows = [
            ('Z / X', 'LEFT / RIGHT BODY PUNCH'),
            ('UP + Z / X', 'HEAD PUNCH'),
            ('LEFT / RIGHT', 'TIMED DODGE'),
            ('DOWN', 'HOLD TO BLOCK HOOKS'),
            ('SPACE', 'POWER UPPERCUT AT FULL METER'),
        ]
        for n, (key, desc) in enumerate(rows):
            y = 91 + n * 25
            panel(s, (33, y-4, 104, 19), LINE, NAVY)
            text(s, key, (85, y+2), GOLD, center=True)
            text(s, desc, (150, y+2))
        pg.draw.line(s, LINE, (33, 219), (447, 219))
        text(s, 'LEFT HOOK: DODGE RIGHT / RIGHT HOOK: DODGE LEFT', (240, 230), WHITE, center=True)
        text(s, 'UPPERCUT: DODGE EITHER WAY. BLOCK WILL NOT STOP IT.', (240, 245), RED, center=True)
        text(s, 'WAIT FOR DODGE NOW! THEN TAP THE DIRECTION.', (240, 260), GOLD, center=True)
        text(s, 'HIT DURING OPEN! TO BUILD YOUR POWER.', (240, 272), TEAL, center=True)
        text(s, 'KNOCKED DOWN? ALTERNATE Z AND X TO GET UP.', (240, 286), MUTED, center=True)
        button(s, 'ENTER / RING THE BELL', (138, 302, 204, 26))
        text(s, 'PAD: X/B PUNCH  A POWER  D-PAD MOVE  START PAUSE', (240, 340), MUTED, center=True)
        self.buttons = [(pg.Rect(138, 302, 204, 26), 'confirm')]

    def fight(self, s, f, t, muted=False):
        s.blit(self.art.arena, (0, 0))
        if int(t * 4) % 11 == 0:
            star(s, (81, 102), 3, WHITE)
        ellipse(s, '#344158', (180, 272, 121, 18), None)
        pose = f.guard if f.opponent_state == 'idle' else 'windup' if f.opponent_state == 'windup' else 'idle'
        if f.strike_timer > 0:
            pose = 'strike'
        if f.opponent_flash > 0 and f.opponent_state != 'windup' and f.strike_timer <= 0:
            pose = 'hit'
        progress = (1-f.opponent_timer/f.windup_duration if pose == 'windup' else
                    1-f.strike_timer/.18 if pose == 'strike' else 0)
        enemy = self.art.opponent(t, pose, f.attack, progress=progress, flash=f.opponent_flash > .12, opponent_id=f.opponent_id)
        ex, ey = 144, 69 + int(math.sin(t * 3) * 1)
        if f.state == 'opponent_down':
            fall = min(1, f.down_elapsed/.65)
            enemy = enemy.subsurface(enemy.get_bounding_rect()).copy()
            enemy = pg.transform.rotate(enemy, -90*fall*fall)
            enemy = pg.transform.scale(enemy, (int(enemy.get_width()*.8), int(enemy.get_height()*.8)))
            ex, ey = 240-enemy.get_width()//2, 287-enemy.get_height()
        s.blit(enemy, (ex, ey))
        px, py = 171, 201
        if f.dodge_timer > 0:
            shift = math.sin(min(1, f.dodge_timer / f.dodge_duration)*math.pi) * 45
            px += int(shift) * (1 if f.dodge_direction == 'right' else -1)
            py += int(shift*.18)
        if f.player_flash:
            px += int(math.sin(t*80)*4)
        player = self.art.player(t, f.punch_hand, f.punch_high, f.punch_timer, f.block,
                                 hurt=f.player_flash > 0, power=f.punch_power)
        if f.player_flash and f.state != 'player_down':
            py += int(9*f.player_flash/.3)
        player.set_alpha(165 if f.state != 'player_down' else 230)
        if f.state == 'player_down':
            fall = min(1, f.down_elapsed/.65)
            player = player.subsurface(player.get_bounding_rect()).copy()
            player = pg.transform.rotate(player, 90*fall*fall)
            px = 241-player.get_width()//2
            py = 317-player.get_height()
        s.blit(player, (px, py))
        for x, y, vx, vy, life, color in self.sparks:
            star(s, (int(x), int(y)), 3 if life > .2 else 1, color, 4)
        # The top HUD is always outside the fighting area.
        pg.draw.rect(s, INK, (0, 0, W, 44))
        s.blit(self.small['player'], (7, 8))
        s.blit(self.small[f.opponent_id], (445, 8))
        text(s, 'JAX VEGA', (42, 6), TEAL)
        text(s, f.opponent.hud_name, (325, 6), GOLD)
        self.bar(s, (42, 19, 143, 9), f.player_hp, TEAL)
        self.bar(s, (295, 19, 143, 9), f.opponent_hp, GOLD, reverse=True)
        text(s, f'{int(f.player_hp):03d}', (42, 32), MUTED)
        text(s, f'{int(f.opponent_hp):03d}', (419, 32), MUTED)
        for n in range(3):
            pg.draw.rect(s, RED if n < f.player_downs else LINE, (157+n*10, 33, 6, 4))
            pg.draw.rect(s, RED if n < f.opponent_downs else LINE, (296+n*10, 33, 6, 4))
        remaining = max(0, 180-int(f.elapsed))
        text(s, f'{remaining//60}:{remaining%60:02d}', (240, 13), WHITE, 2, center=True)
        text(s, 'ROUND 01', (240, 33), MUTED, center=True)
        # Instruction cue is legible, and placed away from heads.
        if f.state == 'fight' and f.opponent_state == 'windup':
            cue = {'left': 'LEFT HOOK - DODGE RIGHT >', 'right': '< DODGE LEFT - RIGHT HOOK', 'upper': 'UPPERCUT! DODGE LEFT OR RIGHT'}[f.attack]
            if f.dodge_now:
                cue = {'left': 'DODGE NOW! RIGHT >', 'right': '< LEFT! DODGE NOW!',
                       'upper': 'DODGE NOW! LEFT OR RIGHT'}[f.attack]
            panel(s, (122, 57, 236, 23), TEAL if f.dodge_now else '#875653', INK)
            text(s, cue, (240, 64), TEAL if f.dodge_now else RED if f.attack == 'upper' else GOLD, center=True)
            width = int(232 * max(0, f.opponent_timer / f.windup_duration))
            pg.draw.rect(s, GOLD, (124, 76, width, 2))
        elif f.state == 'fight' and f.message_timer > 0:
            panel(s, (122, 57, 236, 23), LINE, INK)
            text(s, f.message, (240, 65), TEAL, center=True)
        elif f.state == 'fight':
            panel(s, (122, 57, 236, 23), LINE, INK)
            text(s, 'GUARD HIGH / BODY OPEN' if f.guard == 'high' else 'GUARD LOW / HEAD OPEN', (240, 65), MUTED, center=True)
        # Meter, score and control hints.
        pg.draw.rect(s, INK, (0, 319, W, 41))
        text(s, 'POWER', (12, 326), GOLD if f.power >= 100 else MUTED)
        self.bar(s, (49, 325, 145, 10), f.power, GOLD if f.power >= 100 else TEAL)
        text(s, 'SPACE!' if f.power >= 100 else f'{int(f.power):02d}%', (204, 326), GOLD if f.power >= 100 else MUTED)
        text(s, f'SCORE {f.score:06d}', (354, 326), WHITE)
        text(s, 'Z X PUNCH / ARROWS DEFEND / P PAUSE / F11 FULL', (12, 347), MUTED)
        text(s, 'M:OFF' if muted else 'M:ON', (442, 347), MUTED)
        if f.state == 'intro':
            count = max(1, math.ceil(f.state_timer))
            panel(s, (166, 128, 148, 90), GOLD, INK)
            text(s, 'GET READY', (240, 140), WHITE, center=True)
            text(s, str(count), (240, 158), GOLD, 6, center=True)
        elif f.state in ('opponent_down', 'player_down'):
            label = f'{f.opponent.nickname} IS DOWN!' if f.state == 'opponent_down' else 'GET BACK UP!'
            panel(s, (109, 49, 262, 61), GOLD, INK)
            text(s, label, (240, 56), GOLD, 2, center=True)
            downs = f.opponent_downs if f.state == 'opponent_down' else f.player_downs
            text(s, 'TKO' if downs >= 3 else str(min(10, int(f.down_elapsed)+1)), (240, 78), WHITE, 3, center=True)
            if f.state == 'player_down' and downs < 3:
                text(s, 'ALTERNATE Z / X TO STAND', (240, 119), WHITE, center=True)
                self.bar(s, (163, 134, 154, 12), f.recovery*100, TEAL)
        self.buttons = []

    @staticmethod
    def bar(s, rect, value, color, reverse=False):
        x, y, w, h = rect
        pg.draw.rect(s, LINE, rect)
        pg.draw.rect(s, '#1d243a', (x+1, y+1, w-2, h-2))
        amount = int((w-2)*max(0, min(100, value))/100)
        if amount:
            bx = x+w-1-amount if reverse else x+1
            pg.draw.rect(s, color, (bx, y+1, amount, h-2))
            pg.draw.rect(s, WHITE, (bx, y+1, amount, 1))

    def pause(self, s):
        veil = pg.Surface((W, H), pg.SRCALPHA)
        veil.fill((10, 13, 26, 200))
        s.blit(veil, (0, 0))
        panel(s, (101, 91, 278, 166), GOLD, INK)
        text(s, 'TIME OUT', (240, 109), GOLD, 3, center=True)
        text(s, 'P / ESC / ENTER: RESUME', (240, 149), WHITE, center=True)
        text(s, 'R: RESTART FIGHT', (240, 170), WHITE, center=True)
        text(s, 'Q: RETURN TO CIRCUIT', (240, 191), WHITE, center=True)
        text(s, 'M: SOUND / F11: FULLSCREEN', (240, 230), MUTED, center=True)
        self.buttons = [(pg.Rect(130, 141, 220, 21), 'confirm')]

    def result(self, s, f, t, record):
        self.base(s, t)
        won = f.winner == 'player'
        text(s, 'VICTORY' if won else 'KEEP FIGHTING', (240, 42), GOLD if won else RED, 3, center=True)
        text(s, f.finish, (240, 77), TEAL, 2, center=True)
        who = 'player' if won else f.opponent_id
        panel(s, (51, 110, 116, 120), GOLD)
        s.blit(pg.transform.scale(self.portraits[who], (110, 114)), (54, 113))
        text(s, 'JAX VEGA' if won else f.opponent.hud_name, (109, 244), WHITE, center=True)
        stats = [('SCORE', f'{f.score:06d}'), ('TIME', f'{int(f.elapsed)//60}:{int(f.elapsed)%60:02d}'),
                 ('ACCURACY', f'{round(f.landed/max(1,f.thrown)*100)}%'), ('COUNTERS', str(f.counters)),
                 ('CLEAN DODGES', str(f.dodges)), ('BEST SCORE', f"{record.get('best',0):06d}")]
        for n, (label, value) in enumerate(stats):
            text(s, label, (205, 117+n*23), MUTED)
            text(s, value, (366, 117+n*23), GOLD if n in (0,5) else WHITE)
        text(s, 'GOOD HANDS. BETTER TIMING.' if won else 'WAIT FOR THE WIND-UP. DODGE. THEN COUNTER.', (240, 282), TEAL, center=True)
        button(s, 'ENTER / REMATCH', (65, 308, 162, 26))
        button(s, 'ESC / CIRCUIT', (253, 308, 162, 26), False)
        self.buttons = [(pg.Rect(65,308,162,26),'confirm'), (pg.Rect(253,308,162,26),'back')]
