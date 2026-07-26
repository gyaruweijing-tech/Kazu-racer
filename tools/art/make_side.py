"""kazu-side.png — コース上を右向きに走るカズ。128x96 ドット → x8 = 1024x768。

コース上では 74px 幅までしか表示されないので細かい描き込みは効かない。
「頭が主役・胴と手足はシルエットで読ませる」方針。
腕は細く（r=3）脚は太く（r=5）、奥側の手足は暗い赤にして前後を分ける。
図は右寄せにして、空いた左側にスピードラインを流す。
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pixlib import *

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, SCALE = 128, 96, 8
DX = 17                                          # 図全体を進行方向へ寄せる
c = Canvas(W, H)
face = load_face(f'{HERE}/kazu44.png')           # 44x53
FX, FY = 38 + DX, 0

P = lambda x, y: (x + DX, y)
SHO, HIP = P(65, 59), P(59, 70)

def limb(a, b, d, r1, r2):
    m = c.layer(); capsule(m, a, b, r1); capsule(m, b, d, r2); return m

def shoe(ank, tip):
    body, sole = c.layer(), c.layer()
    capsule(body, ank, tip, 3)
    x0, x1 = min(ank[0], tip[0]) - 3, max(ank[0], tip[0]) + 3
    rect(sole, x0, tip[1] + 1, x1, tip[1] + 3)
    body.paste(sole, (0, 0), sole)
    return body, sole

torso = c.layer()
capsule(torso, SHO, HIP, 7)
capsule(torso, (SHO[0] - 7, SHO[1]), (SHO[0] + 6, SHO[1] + 1), 6)

# 前脚は膝を上げて宙に浮かせ、後脚だけを接地させる＝ストライド中に見せる
ANK_F, ANK_B = P(78, 80), P(37, 88)
legF = limb(P(63, 70), P(74, 76), ANK_F, 5, 4)
legB = limb(P(56, 71), P(46, 81), ANK_B, 5, 4)
shoeF, soleF = shoe(ANK_F, P(85, 81))
shoeB, soleB = shoe(ANK_B, P(30, 89))

# 腕は脚より細い。前腕を振り上げ、後腕は後ろ下へ振り抜く
armF = limb(P(70, 59), P(80, 63), P(85, 54), 3, 3)
armB = limb(P(58, 60), P(47, 66), P(39, 72), 3, 3)
fistF, fistB = c.layer(), c.layer()
blob(fistF, *P(85, 53), 4, 4); blob(fistB, *P(39, 72), 4, 4)

# ---- 奥から順に ----
lines = c.layer()
for (x0, y, ln) in [(2, 30, 20), (0, 46, 30), (6, 61, 16), (1, 76, 24)]:
    capsule(lines, (x0, y), (x0 + ln, y), 0)
c.detail(lines, INK)

c.part(armB, RED_D);  c.part(fistB, SKIN_D)
c.part(legB, RED_D)
c.part(shoeB, WHITE_D); c.detail(c.clip(soleB, shoeB), RED_D)
c.part(torso, RED, shade=RED_D, sd=(3, -2))
c.part(legF, RED, shade=RED_D, sd=(2, -2))
c.part(shoeF, WHITE); c.detail(c.clip(soleF, shoeF), RED)
c.part(armF, RED); c.part(fistF, SKIN, shade=SKIN_D)

# 蹴り出した後ろ足の砂煙
dust = c.layer()
blob(dust, *P(24, 90), 5, 3); blob(dust, *P(15, 88), 3, 2)
c.part(dust, WHITE_D)

c.paste_sprite(face, FX, FY)
c.center()
c.export(f'{HERE}/kazu-side.png', SCALE)
c.preview(f'{HERE}/prev-side.png', 6)
c.img.resize((74, 56), Image.LANCZOS).resize((74 * 5, 56 * 5), Image.NEAREST) \
     .save(f'{HERE}/prev-side-small.png')
print('side ok', c.img.getbbox())
