"""Deterministic boxing rules, independent of graphics and audio."""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Opponent:
    name: str
    nickname: str
    hud_name: str
    style: str
    sequence: tuple[str, ...]
    hook_windup: float = .78
    upper_windup: float = 1.05
    idle_duration: float = .9
    guard_duration: float = 1.4


OPPONENTS = {
    'brick': Opponent('BRUNO MALONE', 'BRICK', 'BRICK MALONE',
                      'HEAVY HOOKS / OPEN GUARD',
                      ('left', 'right', 'left', 'upper', 'right', 'upper')),
    'voltage': Opponent('NICO REYES', 'VOLTAGE', 'NICO REYES',
                        'FAST HOOKS / LATE UPPERCUT',
                        ('right', 'right', 'upper', 'left', 'upper', 'left'),
                        hook_windup=.64, upper_windup=1.3,
                        idle_duration=.72, guard_duration=.95),
}


@dataclass
class Fight:
    difficulty: str = 'arcade'
    opponent_id: str = field(default='brick', kw_only=True)
    state: str = 'intro'
    state_timer: float = 2.8
    paused: bool = False
    elapsed: float = 0.0
    player_hp: float = 100.0
    opponent_hp: float = 100.0
    power: float = 0.0
    player_downs: int = 0
    opponent_downs: int = 0
    opponent_state: str = 'idle'
    opponent_timer: float = 1.1
    counter_open: bool = False
    attack: str = 'left'
    attack_index: int = 0
    guard: str = 'high'
    guard_timer: float = 1.4
    dodge_timer: float = 0.0
    dodge_cooldown: float = 0.0
    dodge_direction: str = 'left'
    punch_timer: float = 0.0
    punch_cooldown: float = 0.0
    punch_hand: str = 'left'
    punch_high: bool = False
    punch_power: bool = False
    pending_punch: bool = False
    block: bool = False
    player_flash: float = 0.0
    opponent_flash: float = 0.0
    strike_timer: float = 0.0
    stun: float = 0.0
    recovery: float = 0.0
    recovery_hand: str = ''
    down_elapsed: float = 0.0
    score: int = 0
    landed: int = 0
    thrown: int = 0
    counters: int = 0
    dodges: int = 0
    winner: str = ''
    finish: str = ''
    message: str = 'ROUND ONE'
    message_timer: float = 0.0
    events: list = field(default_factory=list)

    @property
    def opponent(self):
        return OPPONENTS[self.opponent_id]

    def emit(self, kind, **data):
        self.events.append({'kind': kind, **data})

    def say(self, message, duration=.65):
        self.message, self.message_timer = message, duration

    def punch(self, hand, high=False, power=False):
        if (self.state != 'fight' or self.paused or self.punch_cooldown > 0
                or self.dodge_timer > 0 or self.stun > 0 or self.block):
            return False
        if power and self.power < 100:
            self.say('BUILD POWER WITH COUNTERS')
            return False
        if power:
            self.power = 0
        self.punch_hand, self.punch_high, self.punch_power = hand, high, power
        self.punch_timer = .32 if power else .23
        self.punch_cooldown = .52 if power else .29
        self.pending_punch = True
        self.thrown += 1
        self.emit('swing')
        return True

    def dodge(self, direction):
        if (self.state != 'fight' or self.paused or self.dodge_cooldown > 0
                or self.punch_timer > .1 or self.stun > 0):
            return False
        self.dodge_direction = direction
        self.dodge_timer = self.dodge_duration
        self.dodge_cooldown = self.dodge_duration + .19
        self.block = False
        self.emit('swoosh')
        return True

    def get_up(self, hand):
        if self.state != 'player_down' or self.paused or hand == self.recovery_hand:
            return
        self.recovery_hand = hand
        self.recovery = min(1.0, self.recovery + .085)

    def step(self, dt, defense=None):
        if self.paused or self.state == 'result':
            return
        # Split slow frames so an attack cannot skip a dodge/impact window.
        remaining = min(.25, max(0, dt))
        while remaining > 1e-9:
            tick = min(1 / 120, remaining)
            self._tick(tick, defense)
            remaining -= tick

    def _tick(self, dt, defense):
        for name in ('message_timer', 'player_flash', 'opponent_flash', 'strike_timer'):
            setattr(self, name, max(0, getattr(self, name) - dt))
        if self.state == 'intro':
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = 'fight'
                self.say('FIGHT!', .8)
                self.emit('bell')
            return
        if self.state in ('opponent_down', 'player_down'):
            self._count(dt)
            return
        if self.state != 'fight':
            return
        self.elapsed += dt
        if self.elapsed >= 180:
            self.end('player' if self.opponent_downs > self.player_downs or
                     (self.opponent_downs == self.player_downs and
                      self.player_hp > self.opponent_hp) else 'opponent', 'DECISION')
            return
        for name in ('dodge_timer', 'dodge_cooldown', 'punch_cooldown', 'stun'):
            setattr(self, name, max(0, getattr(self, name) - dt))
        self.block = defense == 'block' and self.dodge_timer <= 0 and self.punch_timer <= 0
        if self.punch_timer > 0:
            self.punch_timer = max(0, self.punch_timer - dt)
            threshold = .19 if self.punch_power else .13
            if self.pending_punch and self.punch_timer <= threshold:
                self.pending_punch = False
                self._impact()
                if self.state != 'fight':
                    return
        self.opponent_timer -= dt
        if self.opponent_state == 'idle':
            self.guard_timer -= dt
            if self.guard_timer <= 0:
                self.guard = 'low' if self.guard == 'high' else 'high'
                self.guard_timer = self.opponent.guard_duration
            if self.opponent_timer <= 0:
                sequence = self.opponent.sequence
                self.attack = sequence[self.attack_index % len(sequence)]
                self.attack_index += 1
                self.opponent_state = 'windup'
                self.opponent_timer = self.windup_duration
                self.emit('cue', attack=self.attack)
        elif self.opponent_state == 'windup' and self.opponent_timer <= 0:
            self._opponent_impact()
        elif self.opponent_state == 'recover' and self.opponent_timer <= 0:
            self.opponent_state = 'idle'
            self.counter_open = False
            self.opponent_timer = self.opponent.idle_duration - self.opponent_downs * .13

    @property
    def dodge_duration(self):
        return .65 if self.difficulty == 'practice' else .36

    @property
    def dodge_now(self):
        return (self.state == 'fight' and self.opponent_state == 'windup'
                and 0 < self.opponent_timer <= self.dodge_duration - .1)

    @property
    def windup_duration(self):
        base = self.opponent.upper_windup if self.attack == 'upper' else self.opponent.hook_windup
        return base + (.28 if self.difficulty == 'practice' else 0) - self.opponent_downs * .08

    def _impact(self):
        counter = self.opponent_state == 'recover' and self.counter_open
        guarded = not counter and ((self.guard == 'high') == self.punch_high)
        if guarded:
            self.emit('blocked', target='opponent')
            self.say('GUARD UP - GO TO THE BODY' if self.guard == 'high' else 'AIM HIGH: HOLD UP')
            return
        damage = (29 if counter else 15) if self.punch_power else (12 if counter else 3)
        self.opponent_hp = max(0, self.opponent_hp - damage)
        self.opponent_flash = .22
        self.landed += 1
        self.score += damage * (30 if counter else 10)
        if counter:
            self.counters += 1
        self.power = min(100, self.power + (18 if counter else 5))
        self.say('POWER SHOT!' if self.punch_power else 'COUNTER!' if counter else 'CLEAN HIT')
        self.emit('power' if self.punch_power else 'hit', target='opponent', high=self.punch_high)
        if self.opponent_hp <= 0:
            self._down('opponent')

    def _opponent_impact(self):
        self.strike_timer = .18
        safe = (self.dodge_timer > 0 and
                (self.attack == 'upper' or
                 self.dodge_direction == ('right' if self.attack == 'left' else 'left')))
        self.opponent_state = 'recover'
        self.counter_open = safe
        self.opponent_timer = 1.05 if safe else .65
        if safe:
            self.dodges += 1
            self.power = min(100, self.power + 14)
            self.score += 150
            self.say('OPEN! COUNTER NOW', .85)
            self.emit('evade')
            return
        damage = 25 if self.attack == 'upper' else 17
        if self.difficulty == 'practice':
            damage *= .65
        if self.block and self.attack != 'upper':
            damage = 3
            self.emit('blocked', target='player')
            self.say('BLOCKED')
        else:
            self.power = max(0, self.power - 18)
            self.stun = .3
            self.pending_punch = False
            self.punch_timer = 0
            self.player_flash = .3
            self.emit('hurt', target='player')
            self.say('DODGE THE UPPERCUT!' if self.attack == 'upper' else 'WATCH HIS SHOULDERS')
        self.player_hp = max(0, self.player_hp - damage)
        if self.player_hp <= 0:
            self._down('player')

    def _down(self, who):
        if who == 'opponent':
            self.opponent_downs += 1
            self.score += 1000
        else:
            self.player_downs += 1
        self.state = who + '_down'
        self.down_elapsed = 0
        self.recovery = 0
        self.recovery_hand = ''
        self.punch_timer = self.dodge_timer = 0
        self.pending_punch = False
        self.block = False
        self.counter_open = False
        self.emit('knockdown')

    def _count(self, dt):
        self.down_elapsed += dt
        count = self.opponent_downs if self.state == 'opponent_down' else self.player_downs
        if count >= 3 and self.down_elapsed >= 2:
            self.end('player' if self.state == 'opponent_down' else 'opponent', 'TKO')
        elif self.state == 'opponent_down' and self.down_elapsed >= 4:
            self.opponent_hp = 80 - self.opponent_downs * 10
            self._resume()
        elif self.state == 'player_down':
            if self.recovery >= 1 and self.down_elapsed >= 2:
                self.player_hp = 75 - self.player_downs * 15
                self._resume()
            elif self.down_elapsed >= 10:
                self.end('opponent', 'KO')

    def _resume(self):
        self.state = 'intro'
        self.state_timer = 1.5
        self.opponent_state = 'idle'
        self.opponent_timer = 1.0
        self.stun = self.dodge_cooldown = self.punch_cooldown = 0

    def end(self, winner, finish):
        self.winner, self.finish, self.state = winner, finish, 'result'
        self.emit('win' if winner == 'player' else 'bell')
