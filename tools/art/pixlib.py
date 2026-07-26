"""低解像度キャンバスに描いて NEAREST で拡大＝ドット絵を作るための道具箱。

小さく表示するスプライトはパーツごとに黒縁が入っていないと塊に潰れるので、
Canvas.part() は「奥から順に、各パーツに縁取りを付けながら」重ねていく。
"""
from PIL import Image, ImageDraw
import numpy as np

# --- ゲーム側のパレットに合わせる（index.html の :root と同じ） ---
INK     = (21, 24, 30, 255)
RED     = (225, 29, 72, 255)
RED_D   = (152, 16, 48, 255)
RED_L   = (245, 110, 140, 255)
WHITE   = (255, 255, 255, 255)
WHITE_D = (206, 214, 226, 255)
SKIN    = (253, 182, 112, 255)
SKIN_D  = (198, 102, 35, 255)
BLACK   = (36, 40, 50, 255)
CLEAR   = (0, 0, 0, 0)


def _bin(mask):
    return np.asarray(mask) > 127


def _dilate(a, px=1):
    for _ in range(px):
        a = (a | np.roll(a, 1, 0) | np.roll(a, -1, 0) |
             np.roll(a, 1, 1) | np.roll(a, -1, 1))
    return a


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.arr = np.zeros((h, w, 4), np.uint8)

    def layer(self):
        return Image.new('L', (self.w, self.h), 0)

    def part(self, mask, fill, shade=None, sd=(2, -2), ink=INK):
        """1パーツを縁取り付きで重ねる。奥のパーツから順に呼ぶこと。"""
        m = _bin(mask)
        ring = _dilate(m) & ~m
        if ink is not None:
            self.arr[ring] = ink
        self.arr[m] = fill
        if shade is not None:
            s = m & ~np.roll(np.roll(m, sd[1], 0), sd[0], 1)
            self.arr[s] = shade

    def detail(self, mask, color):
        """縁取りなしで色を置く（ライン・模様など）。"""
        self.arr[_bin(mask)] = color

    def clip(self, mask, keep):
        """mask を keep の内側だけに切り詰める。"""
        out = (_bin(mask) & _bin(keep)) * 255
        return Image.fromarray(out.astype(np.uint8), 'L')

    @property
    def img(self):
        return Image.fromarray(self.arr, 'RGBA')

    def paste_sprite(self, sprite, x, y):
        im = self.img
        im.alpha_composite(sprite, (x, y))
        self.arr = np.asarray(im).copy()

    def center(self):
        """描いた内容をキャンバス中央に寄せる（端の切れ・偏りを防ぐ）。"""
        bb = self.img.getbbox()
        if not bb:
            return
        dx = (self.w - (bb[2] - bb[0])) // 2 - bb[0]
        dy = (self.h - (bb[3] - bb[1])) // 2 - bb[1]
        self.arr = np.roll(np.roll(self.arr, dy, 0), dx, 1)

    def export(self, path, scale):
        self.img.resize((self.w * scale, self.h * scale), Image.NEAREST).save(path)

    def preview(self, path, scale):
        bg = Image.new('RGBA', (self.w, self.h), (242, 244, 248, 255))
        px = bg.load()
        for y in range(self.h):
            for x in range(self.w):
                if ((x // 4) + (y // 4)) % 2:
                    px[x, y] = (225, 229, 238, 255)
        bg.alpha_composite(self.img)
        bg.resize((self.w * scale, self.h * scale), Image.NEAREST).save(path)


def capsule(mask, p0, p1, r):
    d = ImageDraw.Draw(mask)
    d.line([p0, p1], fill=255, width=2 * r + 1)
    for p in (p0, p1):
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=255)


def blob(mask, cx, cy, rx, ry):
    ImageDraw.Draw(mask).ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=255)


def poly(mask, pts):
    ImageDraw.Draw(mask).polygon(pts, fill=255)


def rect(mask, x0, y0, x1, y1):
    ImageDraw.Draw(mask).rectangle([x0, y0, x1, y1], fill=255)


def load_face(path):
    return Image.open(path).convert('RGBA')
