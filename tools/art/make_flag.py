"""kazu-flag.png — 1位のときだけ出る、チェッカーフラッグを掲げたカズ。
128x128 ドット → x8 = 1024x1024。リザルト画面では最大150px表示。
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pixlib import *

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, SCALE = 128, 128, 8
c = Canvas(W, H)
face = load_face(f'{HERE}/kazu44.png')           # 44x53
FX, FY = 30, 10
HEAD_CX, HEAD_BOT = FX + 22, FY + 53             # (52, 63)

SHO, HIP = (52, 71), (52, 92)

def limb(a, b, d, r1, r2):
    m = c.layer(); capsule(m, a, b, r1); capsule(m, b, d, r2); return m

def shoe(ank, tip):
    body, sole = c.layer(), c.layer()
    capsule(body, ank, tip, 4)
    x0, x1 = min(ank[0], tip[0]) - 4, max(ank[0], tip[0]) + 4
    rect(sole, x0, tip[1] + 2, x1, tip[1] + 4)
    body.paste(sole, (0, 0), sole)
    return body, sole

torso = c.layer()
capsule(torso, SHO, HIP, 9)
capsule(torso, (SHO[0] - 9, SHO[1]), (SHO[0] + 9, SHO[1]), 7)

ANK_L, ANK_R = (44, 112), (61, 112)
legL = limb((46, 92), (43, 102), ANK_L, 6, 5)
legR = limb((59, 92), (62, 102), ANK_R, 6, 5)
shoeL, soleL = shoe(ANK_L, (38, 114))
shoeR, soleR = shoe(ANK_R, (67, 114))

# 右腕：旗竿を高く掲げる。左腕：腰に当ててドヤる
HAND = (76, 52)
armR = limb((61, 71), (71, 63), HAND, 5, 4)
armL = limb((43, 72), (34, 82), (33, 93), 5, 4)
handR, handL = c.layer(), c.layer()
blob(handR, *HAND, 5, 5); blob(handL, 33, 93, 5, 5)

# ---- チェッカーフラッグ ----
# 竿は手からほぼ真上へ。旗はその右側に波打たせて掛ける（竿は旗の奥に置く）。
POLE_TOP = (84, 11)
pole = c.layer(); capsule(pole, (HAND[0] - 1, HAND[1] + 5), POLE_TOP, 1)

def wave_flag(x0, y0, length, height, amp, phase):
    """竿から右へ伸びる、波打つ旗のマスク。"""
    top, bot = [], []
    for i in range(length + 1):
        t = i / length
        x = x0 + i
        sag = 3 * t                                    # 先端ほど少し垂れる
        w = amp * math.sin(t * 5.0 + phase) * t        # 根元は動かず先端がうねる
        top.append((x, y0 + sag + w))
        bot.append((x, y0 + sag + w + height * (1 - 0.12 * t)))
    m = c.layer(); poly(m, top + bot[::-1]); return m

flag = wave_flag(85, 16, 38, 25, 4.5, 0.4)

# ---- 奥から順に ----
c.part(armL, RED_D); c.part(handL, SKIN_D)
c.part(legL, RED_D); c.part(shoeL, WHITE_D); c.detail(c.clip(soleL, shoeL), RED_D)
c.part(torso, RED, shade=RED_D, sd=(4, -3))
c.part(legR, RED, shade=RED_D, sd=(2, -2))
c.part(shoeR, WHITE); c.detail(c.clip(soleR, shoeR), RED)

# 胸の白パネル＋赤ライン（レーシングスーツ感）
panel = c.layer(); capsule(panel, (SHO[0] - 6, SHO[1] + 6), (SHO[0] + 6, SHO[1] + 6), 3)
c.detail(c.clip(panel, torso), WHITE)

c.part(pole, WHITE_D, shade=INK, sd=(1, 0))
c.part(flag, WHITE)
checker = c.layer()
for y in range(H):
    for x in range(W):
        if ((x // 5) + (y // 5)) % 2 == 0:
            checker.putpixel((x, y), 255)
c.detail(c.clip(checker, flag), INK)

c.part(armR, RED, shade=RED_D, sd=(2, -2))
c.part(handR, SKIN, shade=SKIN_D)

c.paste_sprite(face, FX, FY)
c.center()
c.export(f'{HERE}/kazu-flag.png', SCALE)
c.preview(f'{HERE}/prev-flag.png', 5)
c.img.resize((150, 150), Image.LANCZOS).resize((150 * 3, 150 * 3), Image.NEAREST) \
     .save(f'{HERE}/prev-flag-small.png')
print('flag ok', c.img.getbbox())
