"""Original pixel artwork, built from a small palette at native resolution."""
import math
import random
import pygame as pg

W, H = 480, 360
INK = '#101323'
NAVY = '#161a32'
PANEL = '#222840'
LINE = '#3b4664'
WHITE = '#f8ecd5'
MUTED = '#98a6bd'
GOLD = '#ffc857'
TEAL = '#4ee0cd'
RED = '#ff686e'
BLUE = '#6594ef'

# A deliberately compact 5×7 arcade alphabet; no platform font dependency.
GLYPHS = dict(zip(
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
    [
        '01110/10001/10001/11111/10001/10001/10001',
        '11110/10001/10001/11110/10001/10001/11110',
        '01111/10000/10000/10000/10000/10000/01111',
        '11110/10001/10001/10001/10001/10001/11110',
        '11111/10000/10000/11110/10000/10000/11111',
        '11111/10000/10000/11110/10000/10000/10000',
        '01111/10000/10000/10111/10001/10001/01111',
        '10001/10001/10001/11111/10001/10001/10001',
        '11111/00100/00100/00100/00100/00100/11111',
        '00111/00010/00010/00010/10010/10010/01100',
        '10001/10010/10100/11000/10100/10010/10001',
        '10000/10000/10000/10000/10000/10000/11111',
        '10001/11011/10101/10101/10001/10001/10001',
        '10001/11001/11001/10101/10011/10011/10001',
        '01110/10001/10001/10001/10001/10001/01110',
        '11110/10001/10001/11110/10000/10000/10000',
        '01110/10001/10001/10001/10101/10010/01101',
        '11110/10001/10001/11110/10100/10010/10001',
        '01111/10000/10000/01110/00001/00001/11110',
        '11111/00100/00100/00100/00100/00100/00100',
        '10001/10001/10001/10001/10001/10001/01110',
        '10001/10001/10001/10001/10001/01010/00100',
        '10001/10001/10001/10101/10101/10101/01010',
        '10001/10001/01010/00100/01010/10001/10001',
        '10001/10001/01010/00100/00100/00100/00100',
        '11111/00001/00010/00100/01000/10000/11111',
        '01110/10001/10011/10101/11001/10001/01110',
        '00100/01100/00100/00100/00100/00100/01110',
        '01110/10001/00001/00010/00100/01000/11111',
        '11110/00001/00001/01110/00001/00001/11110',
        '00010/00110/01010/10010/11111/00010/00010',
        '11111/10000/10000/11110/00001/00001/11110',
        '01110/10000/10000/11110/10001/10001/01110',
        '11111/00001/00010/00100/01000/01000/01000',
        '01110/10001/10001/01110/10001/10001/01110',
        '01110/10001/10001/01111/00001/00001/01110',
    ]))
GLYPHS.update({
    ' ': '000/000/000/000/000/000/000',
    '.': '0/0/0/0/0/1/1', ':': '0/1/1/0/1/1/0',
    '-': '000/000/000/111/000/000/000',
    '/': '00001/00001/00010/00100/01000/10000/10000',
    '!': '1/1/1/1/1/0/1', "'": '1/1/0/0/0/0/0',
    '+': '00000/00100/00100/11111/00100/00100/00000',
    '>': '100/010/001/001/001/010/100',
    '<': '001/010/100/100/100/010/001',
    '?': '01110/10001/00001/00010/00100/00000/00100',
    '%': '11001/11010/00010/00100/01000/01011/10011',
    '#': '01010/11111/01010/01010/11111/01010/01010',
})


def text_width(value, scale=1):
    return sum(len(GLYPHS.get(c, GLYPHS['?']).split('/')[0]) + 1
               for c in str(value).upper()) * scale - scale


def text(surface, value, xy, color=WHITE, scale=1, center=False, shadow=True):
    value = str(value).upper()
    x, y = map(int, xy)
    if center:
        x -= text_width(value, scale) // 2
    if shadow:
        text(surface, value, (x + scale, y + scale), INK, scale, shadow=False)
    for char in value:
        rows = GLYPHS.get(char, GLYPHS['?']).split('/')
        for j, row in enumerate(rows):
            for i, bit in enumerate(row):
                if bit == '1':
                    pg.draw.rect(surface, color, (x + i * scale, y + j * scale, scale, scale))
        x += (len(rows[0]) + 1) * scale


def poly(s, color, points, outline=INK, width=2):
    pg.draw.polygon(s, color, points)
    if outline:
        pg.draw.lines(s, outline, True, points, width)


def ellipse(s, color, rect, outline=INK, width=2):
    pg.draw.ellipse(s, color, rect)
    if outline:
        pg.draw.ellipse(s, outline, rect, width)


def star(s, xy, radius, color, points=5):
    x, y = xy
    vertices = []
    for i in range(points * 2):
        a = i * math.pi / points - math.pi / 2
        r = radius if i % 2 == 0 else radius * .43
        vertices.append((x + math.cos(a) * r, y + math.sin(a) * r))
    pg.draw.polygon(s, color, vertices)


def glove(s, xy, color, light, size=1):
    x, y = xy
    r = int(16 * size)
    ellipse(s, color, (x - r, y - r, r * 2, r * 2))
    ellipse(s, light, (x - r + 4, y - r + 3, r, max(4, r // 2)), None)
    pg.draw.line(s, '#ffe4be', (x - r + 6, y - r + 4), (x - 1, y - r + 4), 2)
    ellipse(s, color, (x - r - 3, y + 1, max(7, r // 2), r), INK, 1)
    pg.draw.rect(s, INK, (x - r + 3, y + r - 4, r * 2 - 6, 8))
    pg.draw.rect(s, WHITE, (x - r + 5, y + r - 3, r * 2 - 10, 4))


class Art:
    def __init__(self):
        self.arena = self._arena()
        self.scanlines = pg.Surface((W, H), pg.SRCALPHA)
        for y in range(0, H, 3):
            pg.draw.line(self.scanlines, (0, 0, 0, 17), (0, y), (W, y))

    def _arena(self):
        s = pg.Surface((W, H))
        s.fill(INK)
        for y in range(42, 181):
            pg.draw.line(s, (20 + y // 15, 22 + y // 20, 40 + y // 13), (0, y), (W, y))
        # Ceiling trusses and pools of light.
        for x in (42, 138, 342, 438):
            poly(s, '#272b42', [(x-5, 48), (x+5, 48), (x+58, 165), (x-58, 165)], None)
            pg.draw.rect(s, '#76859b', (x-13, 47, 26, 4))
            pg.draw.rect(s, WHITE, (x-9, 51, 18, 3))
        pg.draw.rect(s, '#121528', (158, 57, 164, 23))
        pg.draw.rect(s, '#56506c', (158, 57, 164, 23), 1)
        text(s, 'DOCKSIDE FIGHT CLUB', (240, 65), GOLD, center=True)
        rng = random.Random(17)
        for row in range(4):
            y = 94 + row * 19
            pg.draw.rect(s, '#101526', (0, y+14, W, 4))
            for col in range(40):
                x = col * 13 + (row % 2) * 6 - 8
                skin = rng.choice(('#bf876f', '#95645c', '#d1a182', '#705b65'))
                shirt = rng.choice(('#41486c', '#725460', '#3e6677', '#75643f', '#4d3e61'))
                pg.draw.rect(s, shirt, (x-3, y+5, 10, 10))
                pg.draw.rect(s, skin, (x, y, 5, 6))
                pg.draw.rect(s, '#202035', (x, y, 5, 2))
                if rng.random() > .65:
                    pg.draw.line(s, skin, (x-3, y+7), (x-5, y+1), 2)
        poly(s, '#414a70', [(32, 169), (448, 169), (493, 329), (-13, 329)], None)
        poly(s, '#5c7590', [(39, 174), (441, 174), (479, 325), (0, 325)], None)
        for y in range(179, 325, 4):
            shade = (89 + (y-179)//12, 114 + (y-179)//14, 142 + (y-179)//14)
            pg.draw.line(s, shade, (0, y), (W, y))
        for x in (-100, 30, 145, 335, 450, 580):
            pg.draw.line(s, '#71849b', (240 + (x-240)*.65, 175), (x, 326), 1)
        ellipse(s, '#435775', (139, 224, 202, 74), '#a5b9bd', 2)
        ellipse(s, '#3c4b66', (150, 231, 180, 59), '#6f91a0', 1)
        text(s, 'NK', (240, 245), '#8ca7af', 4, center=True)
        for y, color in ((127, '#be5c6d'), (148, '#ddd5c7'), (169, '#648cba')):
            pg.draw.line(s, INK, (21, y+3), (459, y+3), 5)
            pg.draw.line(s, color, (21, y), (459, y), 3)
            pg.draw.line(s, color, (21, y), (-12, y+98), 3)
            pg.draw.line(s, color, (459, y), (492, y+98), 3)
        for x in (14, 457):
            pg.draw.rect(s, '#181c31', (x, 110, 9, 94))
            pg.draw.rect(s, '#79879b', (x+2, 110, 3, 94))
            for y in (125, 146, 167):
                pg.draw.rect(s, '#df705e' if x < 30 else '#559cac', (x-4, y-5, 15, 11))
                pg.draw.rect(s, '#ffb18b' if x < 30 else '#95c4cf', (x-3, y-5, 13, 2))
        return s

    def opponent(self, t=0, pose='idle', attack='left', progress=0, flash=False, opponent_id='brick'):
        s = pg.Surface((192, 226), pg.SRCALPHA)
        voltage = opponent_id == 'voltage'
        skin, light, shade, deep = (('#a96d50', '#db9f70', '#794b43', '#503641') if voltage
                                    else ('#d69a74', '#f6c294', '#aa6657', '#794c4c'))
        trunks, trunks_light, trunks_dark = (('#663c99', '#a269ce', '#40285e') if voltage
                                             else ('#206577', '#2c8d98', '#154456'))
        bob = int(math.sin(t * 4) * 2) if pose == 'idle' else 0
        progress = max(0, min(1, progress))
        lean = 0
        if pose == 'windup':
            lean = int((-1 if attack == 'left' else 1) * (4 + 10*progress))
            if attack == 'upper':
                lean = 0
                bob = int(5 + 10*progress)
        elif pose == 'strike':
            lean = int((1 if attack == 'left' else -1) * 9 * math.sin(progress*math.pi))
        if pose == 'hit':
            lean = 5
        # Boots and calves.
        for x, flip in ((70, -1), (110, 1)):
            poly(s, skin, [(x-8, 161), (x+13, 160), (x+11, 193), (x-5, 196)])
            poly(s, shade, [(x+5, 163), (x+13, 160), (x+11, 192), (x+3, 194)], None)
            poly(s, '#3f355c', [(x-9, 185), (x+13, 183), (x+15, 204), (x+21, 210), (x-12, 211)])
            pg.draw.line(s, '#b6b1ce', (x-10, 209), (x+20, 208), 3)
            pg.draw.line(s, '#ecbf70', (x-6, 187), (x-6, 204), 3)
            for y in range(189, 203, 4):
                pg.draw.line(s, '#9386a5', (x-1, y), (x+8, y-1), 1)
        body = pg.Surface((192, 180), pg.SRCALPHA)
        # Trapezius, torso and shaded abdominal planes.
        poly(body, skin, [(78, 63), (111, 63), (120, 72), (139, 74), (149, 94),
                          (131, 121), (127, 142), (66, 142), (60, 117), (45, 94), (55, 76), (73, 72)])
        poly(body, shade, [(55, 79), (68, 87), (71, 116), (80, 139), (66, 142), (60, 117), (46, 95)], None)
        poly(body, shade, [(115, 78), (136, 78), (146, 95), (129, 120), (127, 140), (110, 140), (117, 112)], None)
        poly(body, light, [(77, 77), (91, 82), (92, 102), (74, 101), (65, 90)], None)
        poly(body, light if voltage else '#e9ad81', [(98, 82), (117, 77), (128, 89), (117, 103), (98, 101)], None)
        pg.draw.lines(body, deep, False, [(68, 103), (82, 107), (94, 104), (109, 107), (125, 102)], 2)
        pg.draw.line(body, shade, (95, 86), (95, 133), 2)
        for y in (116, 128):
            pg.draw.line(body, shade, (82, y), (109, y), 2)
        # Original lightning tattoo.
        poly(body, '#505776', [(60, 84), (54, 95), (60, 94), (55, 106), (67, 90), (61, 92)], None)
        # High-waisted trunks and gold piping.
        poly(body, trunks, [(65, 137), (128, 137), (137, 168), (106, 176), (97, 158), (85, 176), (57, 168)])
        poly(body, trunks_light, [(69, 147), (86, 146), (89, 159), (82, 169), (63, 165)], None)
        poly(body, trunks_dark, [(117, 146), (127, 145), (134, 166), (111, 172), (103, 158)], None)
        pg.draw.rect(body, GOLD, (64, 137, 65, 9))
        pg.draw.rect(body, WHITE, (90, 138, 12, 7))
        pg.draw.line(body, GOLD, (58, 166), (83, 173), 3)
        pg.draw.line(body, GOLD, (109, 173), (135, 166), 3)
        # Neck and ears.
        poly(body, shade, [(79, 54), (110, 54), (113, 73), (98, 85), (77, 73)])
        ellipse(body, shade, (69, 35, 13, 24))
        ellipse(body, shade, (111, 35, 13, 24))
        poly(body, skin, [(79, 19), (107, 18), (116, 32), (115, 56), (106, 69),
                         (86, 72), (75, 60), (73, 37)])
        poly(body, light, [(81, 27), (99, 25), (108, 34), (103, 46), (94, 43), (82, 47)], None)
        poly(body, shade, [(108, 27), (115, 33), (114, 55), (105, 65), (102, 53)], None)
        # Swept-back dark hair with a copper streak.
        poly(body, '#292435', [(72, 39), (70, 24), (77, 14), (90, 9), (105, 13), (117, 24), (116, 39), (109, 30), (104, 25), (89, 31), (79, 28)])
        poly(body, '#535063', [(77, 24), (85, 16), (97, 15), (108, 21), (97, 20), (86, 25)], None)
        pg.draw.line(body, '#d99968', (85, 16), (77, 23), 2)
        # Brows, eyes and nose.
        pg.draw.line(body, INK, (80, 38), (91, 41), 3)
        pg.draw.line(body, INK, (101, 41), (111, 37), 3)
        pg.draw.rect(body, WHITE, (80, 43, 10, 3))
        pg.draw.rect(body, WHITE, (102, 43, 9, 3))
        pg.draw.rect(body, INK, (86, 43, 3, 3))
        pg.draw.rect(body, INK, (103, 43, 3, 3))
        poly(body, light, [(94, 40), (91, 52), (99, 54), (102, 50)], shade, 1)
        # Angular auburn beard and asymmetric grin.
        poly(body, '#713e36', [(77, 51), (85, 56), (94, 57), (106, 53), (114, 49),
                            (111, 62), (104, 71), (88, 75), (79, 67)], None)
        poly(body, '#a56846', [(80, 57), (86, 60), (88, 69), (96, 71), (89, 73), (81, 65)], None)
        poly(body, INK, [(88, 57), (107, 55), (105, 64), (93, 65)])
        pg.draw.line(body, WHITE, (91, 59), (104, 58), 3)
        pg.draw.line(body, '#dba77e', (94, 69), (102, 68), 2)
        if voltage:
            # Close-cropped sides, tall crest, clean-shaven angular jaw.
            poly(body, skin, [(75, 39), (73, 25), (82, 14), (103, 13),
                              (115, 26), (116, 38), (106, 29), (83, 29)])
            poly(body, '#24263e', [(83, 29), (85, 11), (91, 2), (96, 9),
                                  (102, 4), (107, 17), (106, 30)])
            pg.draw.line(body, '#c996ef', (94, 9), (94, 25), 3)
            poly(body, skin, [(77, 51), (88, 56), (102, 54), (114, 49),
                              (110, 63), (102, 70), (88, 69), (79, 62)], None)
            poly(body, shade, [(108, 55), (114, 49), (110, 63), (102, 70),
                               (97, 67)], None)
            pg.draw.line(body, INK, (88, 60), (104, 58), 2)
            pg.draw.line(body, WHITE, (90, 60), (102, 59), 1)
            pg.draw.line(body, TEAL, (74, 31), (115, 31), 4)
            # A bright chevron identifies the trunks even at native scale.
            poly(body, TEAL, [(71, 148), (82, 154), (74, 166), (86, 154), (75, 146)], None)
        if pose == 'hit':
            pg.draw.line(body, INK, (80, 44), (89, 44), 2)
            pg.draw.line(body, INK, (102, 44), (110, 44), 2)
        # Arms articulate toward the player for punches.
        left, right = (47, 91), (145, 91)
        if pose == 'high':
            left, right = (72, 61), (121, 61)
        elif pose == 'low':
            left, right = (64, 115), (129, 115)
        elif pose == 'windup':
            if attack == 'left':
                left = (int(43-17*progress), int(85-22*progress))
                right = (121, 61)
            elif attack == 'right':
                right = (int(149+17*progress), int(85-22*progress))
                left = (72, 61)
            else:
                right = (132, int(105+29*progress))
                left = (64, 94)
        elif pose == 'strike':
            # Full extension at impact, followed by a quick return to guard.
            reach = 1-progress*progress
            if attack == 'left':
                left = (int(26+60*reach), int(63+67*reach))
                right = (121, 61)
            elif attack == 'right':
                right = (int(166-60*reach), int(63+67*reach))
                left = (72, 61)
            else:
                right = (int(132-33*reach), int(134-64*reach))
        elif pose == 'hit':
            left, right = (36, 106), (156, 105)
        for shoulder, elbow, hand in (((59, 85), (39, 114), left), ((133, 85), (153, 114), right)):
            pg.draw.lines(body, INK, False, [shoulder, elbow, hand], 22)
            pg.draw.lines(body, shade, False, [shoulder, elbow, hand], 18)
            pg.draw.line(body, skin, shoulder, elbow, 13)
            pg.draw.line(body, light, (shoulder[0]-2, shoulder[1]-2), (elbow[0]-2, elbow[1]-2), 5)
            pg.draw.line(body, skin, elbow, hand, 13)
            glove(body, hand, '#2768bb' if voltage else '#d35b40', '#70dcff' if voltage else '#ff9b53', 1.2 if pose == 'strike' else 1)
        s.blit(body, (lean, bob))
        if voltage:
            slim = pg.transform.scale(s, (170, 226))
            s.fill((0, 0, 0, 0))
            s.blit(slim, (11, 0))
        if flash:
            tint = pg.Surface(s.get_size(), pg.SRCALPHA)
            tint.fill((80, 30, 20, 0))
            s.blit(tint, (0, 0), special_flags=pg.BLEND_RGBA_ADD)
        return s

    def player(self, t=0, hand='left', high=False, punch=0, block=False, hurt=False, power=False):
        s = pg.Surface((140, 160), pg.SRCALPHA)
        skin, light, shade = '#be8b76', '#ecc2a0', '#805568'
        # Back-facing athletic silhouette, gloves kept outside the central sightline.
        poly(s, skin, [(48, 49), (85, 49), (99, 57), (104, 79), (94, 100), (95, 124),
                       (44, 124), (42, 102), (30, 78), (35, 60)])
        poly(s, shade, [(35, 60), (47, 68), (52, 101), (50, 120), (43, 120), (42, 101), (31, 78)], None)
        poly(s, shade, [(84, 60), (98, 62), (102, 79), (94, 101), (94, 122), (80, 122), (85, 92)], None)
        poly(s, light, [(50, 57), (68, 63), (64, 91), (54, 83)], None)
        poly(s, '#dca78b', [(73, 63), (86, 55), (88, 80), (77, 91)], None)
        pg.draw.line(s, shade, (70, 65), (69, 113), 2)
        pg.draw.line(s, shade, (49, 94), (62, 101), 2)
        pg.draw.line(s, shade, (77, 101), (88, 92), 2)
        poly(s, '#7d456b', [(43, 115), (96, 115), (103, 151), (72, 154), (68, 137), (62, 155), (37, 151)])
        poly(s, '#b76482', [(44, 126), (58, 125), (56, 150), (40, 148)], None)
        pg.draw.rect(s, WHITE, (42, 115, 55, 8))
        pg.draw.rect(s, TEAL, (64, 116, 11, 6))
        poly(s, skin, [(52, 36), (82, 36), (86, 53), (72, 66), (50, 53)])
        ellipse(s, skin, (45, 17, 44, 37))
        poly(s, '#20263b', [(43, 34), (43, 18), (49, 9), (45, 3), (59, 8), (66, 0),
                           (73, 7), (85, 3), (84, 13), (94, 18), (88, 30), (81, 39), (55, 37)])
        poly(s, '#434661', [(49, 18), (62, 10), (70, 13), (83, 11), (77, 22), (57, 26)], None)
        pg.draw.line(s, '#76849b', (55, 18), (64, 15), 2)
        pg.draw.rect(s, TEAL, (46, 30, 40, 5))
        poly(s, TEAL, [(46, 31), (33, 35), (30, 46), (43, 40)], None)
        left, right = (23, 76), (116, 77)
        if block:
            left, right = (43, 38), (95, 38)
        elif hurt:
            left, right = (17, 92), (122, 94)
        extension = 0
        if punch > 0:
            duration, impact = (.32, .13) if power else (.23, .10)
            elapsed = max(0, duration-punch)
            extension = (elapsed/impact if elapsed <= impact else
                         max(0, (duration-elapsed)/(duration-impact)))
            extension = math.sin(extension*math.pi/2)
            rest = left if hand == 'left' else right
            target = (int(rest[0]+((57 if hand == 'left' else 82)-rest[0])*extension),
                      int(rest[1]+((16 if high else 48)-rest[1])*extension))
            if hand == 'left':
                left = target
            else:
                right = target
        for shoulder, elbow, glove_pos in (((39, 65), (22, 100), left), ((96, 66), (116, 100), right)):
            pg.draw.lines(s, INK, False, [shoulder, elbow, glove_pos], 15)
            pg.draw.lines(s, shade, False, [shoulder, elbow, glove_pos], 12)
            pg.draw.lines(s, skin, False, [shoulder, elbow, glove_pos], 8)
            active = punch > 0 and glove_pos == (left if hand == 'left' else right)
            glove(s, glove_pos, '#2488a3', '#78e8dc',
                  .82 + (.3 if power else .13)*extension if active else .82)
        return s

    def portrait(self, who, size=(104, 108)):
        s = pg.Surface((88, 88))
        s.fill('#30455c' if who == 'player' else '#614957')
        for y in range(8, 96, 16):
            for x in range(8, 96, 16):
                star(s, (x, y), 6, '#426277' if who == 'player' else '#80616a')
        if who != 'player':
            sprite = self.opponent(pose='idle', opponent_id=who)
            crop = sprite.subsurface((53, 6, 84, 93))
            s.blit(pg.transform.scale(crop, (88, 98)), (0, -1))
        else:
            # A separate front-facing portrait for Jax.
            poly(s, '#bc8878', [(18, 88), (20, 65), (34, 56), (58, 55), (73, 67), (79, 88)])
            poly(s, '#e4b495', [(33, 31), (58, 27), (66, 42), (60, 61), (49, 70), (33, 61), (26, 43)])
            poly(s, '#a56866', [(57, 29), (65, 41), (60, 60), (50, 69), (49, 57)], None)
            poly(s, '#22283f', [(24, 44), (20, 26), (30, 18), (26, 8), (41, 15), (49, 7), (55, 17), (69, 15), (65, 29), (70, 34), (62, 41), (57, 31), (34, 35)])
            poly(s, '#4e5876', [(29, 27), (40, 20), (49, 22), (61, 20), (53, 29), (35, 31)], None)
            pg.draw.rect(s, TEAL, (26, 32, 38, 5))
            pg.draw.line(s, INK, (32, 42), (41, 44), 2)
            pg.draw.line(s, INK, (50, 43), (59, 40), 2)
            pg.draw.rect(s, WHITE, (32, 46, 9, 3))
            pg.draw.rect(s, WHITE, (51, 45, 8, 3))
            pg.draw.rect(s, INK, (38, 46, 2, 3))
            pg.draw.rect(s, INK, (52, 45, 2, 3))
            pg.draw.lines(s, '#885b60', False, [(47, 43), (43, 53), (49, 54)], 1)
            pg.draw.line(s, INK, (39, 59), (54, 57), 2)
            pg.draw.line(s, WHITE, (41, 59), (52, 58), 1)
            glove(s, (17, 76), '#2488a3', '#78e8dc', .9)
            glove(s, (76, 73), '#2488a3', '#78e8dc', .9)
        return pg.transform.scale(s, size)

    def icon(self):
        s = pg.Surface((64, 64))
        s.fill(INK)
        pg.draw.rect(s, LINE, (2, 2, 60, 60), 2)
        star(s, (33, 28), 25, GOLD)
        glove(s, (31, 28), '#d35b40', '#ff9b53', 1.2)
        text(s, 'NK', (32, 51), WHITE, center=True)
        return pg.transform.scale(s, (256, 256))
