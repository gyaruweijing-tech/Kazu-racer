"""assets/ の PNG を減色して軽くする。

どれも表示は最大 150px なので色数は要らない。透過は二値のまま保つこと
（半透明を残すと減色時に縁が濁る）。
"""
import sys, os
from PIL import Image
import numpy as np

def quantize(path, colors):
    im = Image.open(path).convert('RGBA')
    a = np.asarray(im)
    alpha = a[..., 3] >= 128
    # 透明部分は最頻色で埋めてから減色する（縁に黒や白が混ざるのを防ぐ）
    rgb = a[..., :3].copy()
    if alpha.any():
        fill = np.bincount((rgb[alpha][:, 0].astype(int) << 16) +
                           (rgb[alpha][:, 1].astype(int) << 8) +
                            rgb[alpha][:, 2].astype(int)).argmax()
        rgb[~alpha] = (fill >> 16 & 255, fill >> 8 & 255, fill & 255)
    q = Image.fromarray(rgb, 'RGB').quantize(colors=colors, method=Image.MEDIANCUT,
                                             dither=Image.NONE).convert('RGB')
    out = np.dstack([np.asarray(q), np.where(alpha, 255, 0).astype(np.uint8)])
    return Image.fromarray(out, 'RGBA')

def diff(a, b):
    """見た目の変化量：実際の表示サイズ(150px)に落として比べる。"""
    fa = np.asarray(a.resize((150, 150), Image.LANCZOS).convert('RGBA')).astype(int)
    fb = np.asarray(b.resize((150, 150), Image.LANCZOS).convert('RGBA')).astype(int)
    return np.abs(fa - fb).mean()

for path in sys.argv[1:]:
    orig = Image.open(path).convert('RGBA')
    before = os.path.getsize(path)
    best = None
    for n in (32, 48, 64, 96, 128):
        q = quantize(path, n)
        tmp = f'/tmp/q{n}.png'
        q.save(tmp, optimize=True)
        size = os.path.getsize(tmp)
        d = diff(orig, q)
        print(f'  {os.path.basename(path)}  {n:>3}色 → {size/1024:6.1f} KB  '
              f'(元の {100*size/before:4.1f}%)  表示時の差 {d:.2f}')
        if best is None and d < 1.2:          # 150px で見てほぼ差が出ない最小の色数
            best = (n, q, size)
    if best:
        n, q, size = best
        q.save(path, optimize=True)
        print(f'→ {os.path.basename(path)}: {n}色で保存  {before/1024:.0f} KB → {size/1024:.0f} KB'
              f'  ({100*(1-size/before):.0f}% 削減)\n')
