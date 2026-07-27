"""kazu-helmet.png — 生成された画像を assets/ 用に仕上げる。

生成画像はすでに透過済み・ドット絵として完成しているので、触るのは最小限にする。
  1. アルファを二値に正す（224〜254 が大量にあるので 255 に揃える）
  2. タイトルは border-radius:50% で円形に切り抜かれるため、
     全画素が中心からの半径に収まるか測り、はみ出すなら縮めて中央に置き直す

過去に試して**やめたこと**（劣化するので戻さないこと）：
  - 背景抜き … 元から透過済み。灰色に見えたのはビューアの背景だった
  - ドット格子へのスナップ … この生成画像に一定の格子は無く（一致率5割強＝ほぼ偶然）、
    どの幅で丸めても目鼻とバイザーが潰れた。元の解像度のままがいちばんきれい
"""
import sys, os
from PIL import Image
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else f'{HERE}/kazu-helmet.png'
SIZE = 1024
MARGIN = 0.94        # 円の内側にどれだけ余裕を持たせるか

a = np.asarray(Image.open(SRC).convert('RGBA')).copy()
a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
a[a[..., 3] == 0] = (0, 0, 0, 0)          # 透明部分の色を消す（にじみ防止）
im = Image.fromarray(a, 'RGBA').crop(Image.fromarray(a, 'RGBA').getbbox())
print('中身の大きさ', im.size)

def radius_needed(img):
    """中央に置いたとき、円形切り抜きに必要な半径。"""
    m = np.asarray(img)[..., 3] > 0
    ys, xs = np.where(m)
    cx, cy = (img.width - 1) / 2, (img.height - 1) / 2
    return float(np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2).max())

# 円に収まる最大の倍率を選ぶ（NEAREST 拡大でドットの角を保つ）
r0 = radius_needed(im)
scale = (SIZE / 2 * MARGIN) / r0
w, h = max(1, round(im.width * scale)), max(1, round(im.height * scale))
im = im.resize((w, h), Image.NEAREST if scale >= 1 else Image.LANCZOS)
if scale < 1:                              # 縮小したら半透明が戻るので二値化し直す
    b = np.asarray(im).copy()
    b[..., 3] = np.where(b[..., 3] >= 128, 255, 0)
    im = Image.fromarray(b, 'RGBA')

out = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
out.alpha_composite(im, ((SIZE - w) // 2, (SIZE - h) // 2))
out.save(OUT)
r = radius_needed(out)
print('書き出し %s  倍率 x%.2f  必要半径 %.0f / 円の半径 %d  （余裕 %.0f%%）'
      % (OUT, scale, r, SIZE // 2, 100 * (1 - r / (SIZE / 2))))
assert r <= SIZE / 2, '円形切り抜きではみ出す'

# 確認用：実際のタイトル表示と同じ「円形＋白フチ＋墨フチ」で見る
prev = Image.new('RGBA', (SIZE, SIZE), (242, 244, 248, 255))
yy, xx = np.mgrid[0:SIZE, 0:SIZE]
d = np.asarray(prev).copy()
rr = np.sqrt((xx - SIZE / 2) ** 2 + (yy - SIZE / 2) ** 2)
d[rr <= SIZE / 2] = (255, 255, 255, 255)
d[(rr > SIZE / 2 - 34) & (rr <= SIZE / 2 - 14)] = (21, 24, 30, 255)
prev = Image.fromarray(d, 'RGBA')
prev.alpha_composite(out)
prev.resize((300, 300), Image.LANCZOS).save(f'{HERE}/prev-helmet.png')
