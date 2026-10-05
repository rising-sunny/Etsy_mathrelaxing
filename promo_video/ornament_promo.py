"""
Vertical promo video (1080 x 1920, 30 fps, ~21 s) for the fractal ceramic ornaments:
a live-computed Mandelbrot zoom hook, then each two-sided ornament spinning to show its
front and back, the tree photo and a call to action. Music from the digits of pi.

  python ornament_promo.py   -> out/fractal_ornaments_promo.mp4 (+ cover PNG)
"""
import os, sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import calendar_promo as CP
from calendar_promo import font, ctext, ease, Scene, W, H, FPS, NAVY, GOLD, CREAM

OUT = CP.OUT
ORN = os.path.join(REPO, "fractal_ornaments")
DEEP = (16, 24, 48)
ITEMS = [("mandelbrot", "Mandelbrot Set"), ("koch", "Koch Snowflake"), ("julia", "Julia Set"),
         ("pi", "Pi Spiral"), ("golden", "Golden Angle"), ("tree", "Fractal Tree")]
T_ZOOM, T_REVEAL, T_ORN, T_HERO, T_CTA = 4.0, 1.2, 1.5, 4.0, 3.0
TOTAL = T_ZOOM + T_REVEAL + len(ITEMS) * T_ORN + T_HERO + T_CTA


# ------------------------------------------------------------------ Mandelbrot zoom
def _shade():
    a = np.zeros((H, 1)); y = np.arange(H)[:, None]
    a += 175 * np.clip(1 - np.abs(y - 420) / 330, 0, 1) ** 0.8 + 175 * np.clip(1 - np.abs(y - 1530) / 260, 0, 1) ** 0.8
    arr = np.zeros((H, W, 4), np.uint8); arr[..., 3] = np.clip(a, 0, 200).astype(np.uint8) * np.ones((1, W), np.uint8)
    arr[..., :3] = (6, 8, 20); return Image.fromarray(arr, "RGBA")


SHADE = _shade()

def mandel_frame(cx, cy, width, w=720, h=1280, it=700):
    xs = np.linspace(cx - width / 2, cx + width / 2, w); hh = width * h / w
    ys = np.linspace(cy - hh / 2, cy + hh / 2, h)
    C = xs[None, :] + 1j * ys[:, None]; z = np.zeros_like(C); n = np.full(C.shape, -1.0); alive = np.ones(C.shape, bool)
    for k in range(it):
        z[alive] = z[alive] ** 2 + C[alive]
        esc = alive & (np.abs(z) > 8); n[esc] = k + 1 - np.log2(np.log(np.abs(z[esc]))); alive &= ~esc
        if not alive.any():
            break
    t = np.where(n < 0, 0, (np.log1p(np.clip(n, 0, None)) * 0.9) % 1.0)
    stops = [(10, 10, 30), (40, 60, 110), (120, 80, 60), (232, 192, 104), (255, 245, 220), (232, 192, 104), (40, 60, 110)]
    xsn = np.linspace(0, 1, len(stops)); img = np.zeros(t.shape + (3,))
    for c in range(3):
        img[..., c] = np.interp(t, xsn, [s[c] for s in stops])
    img[n < 0] = (6, 8, 18)
    return Image.fromarray(img.astype(np.uint8)).resize((W, H), Image.LANCZOS)


def zoom_frames():
    n = int(T_ZOOM * FPS); cx, cy = -0.743643887037151, 0.131825904205330
    for k in range(n):
        t = k / (n - 1); width = 3.2 * (0.001 / 3.2) ** ease(t)
        f = mandel_frame(cx, cy, width, it=int(250 + 700 * t))
        f = Image.alpha_composite(f.convert("RGBA"), SHADE).convert("RGB"); d = ImageDraw.Draw(f)
        ctext(d, 300, "Zoom into", font("cinzel", 96), CREAM)
        ctext(d, 420, "an equation...", font("cinzel", 96), CREAM)
        ctext(d, 1460, f"x{3.2 / width:,.0f}", font("bold", 70), GOLD)
        ctext(d, 1560, "z² + c", font("semi", 60), CREAM)
        yield f


# ------------------------------------------------------------------ ornament drawing
def disc(key, side, d=820):
    im = Image.open(os.path.join(ORN, "out", f"{key}_{side}.png")).convert("RGB").resize((d, d), Image.LANCZOS)
    m = Image.new("L", (d, d), 0); ImageDraw.Draw(m).ellipse((0, 0, d - 1, d - 1), fill=255)
    out = Image.new("RGBA", (d, d), (0, 0, 0, 0)); out.paste(im, (0, 0), m)
    gl = Image.new("RGBA", (d, d), (0, 0, 0, 0)); g = ImageDraw.Draw(gl)  # glaze highlight
    g.ellipse((d * 0.12, d * 0.06, d * 0.62, d * 0.40), fill=(255, 255, 255, 46))
    gl = gl.filter(ImageFilter.GaussianBlur(d * 0.05)); out = Image.alpha_composite(out, Image.composite(gl, Image.new("RGBA", (d, d)), m))
    ImageDraw.Draw(out).ellipse((d / 2 - 22, d * 0.045, d / 2 + 22, d * 0.045 + 44), fill=(0, 0, 0, 0))  # hanging hole
    return out


def ornament_frame(bg, key, angle, cy=1000, d=820):
    """angle in degrees: 0 = front facing, 180 = back facing."""
    f = bg.copy(); c = math.cos(math.radians(angle)); side = "front" if c >= 0 else "back"
    face = disc(key, side, d); wv = max(6, int(d * abs(c)))
    face = face.resize((wv, d), Image.LANCZOS)
    x, y = (W - wv) // 2, int(cy - d / 2)
    sh = Image.new("L", (W, H), 0); ImageDraw.Draw(sh).ellipse((x + 24, y + 40, x + wv + 24, y + d + 40), fill=150)
    f.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(30)))
    dr = ImageDraw.Draw(f); dr.line((W / 2, 470, W / 2, y + d * 0.07), fill=(214, 176, 92), width=6)
    dr.ellipse((W / 2 - 14, 456, W / 2 + 14, 484), outline=(214, 176, 92), width=6)
    f.paste(face, (x, y), face)
    edge = ImageDraw.Draw(f); edge.ellipse((x, y, x + wv, y + d), outline=(235, 230, 220), width=4)
    return f


def soft_bg(col_top, col_bot):
    g = np.linspace(0, 1, H)[:, None, None]
    arr = (np.array(col_top) * (1 - g) + np.array(col_bot) * g) * np.ones((1, W, 1))
    return Image.fromarray(arr.astype(np.uint8))


def reveal_frames():
    """The zoom pulls back out and lands on the Mandelbrot ornament."""
    bg = soft_bg((24, 34, 66), (8, 12, 26)); n = int(T_REVEAL * FPS)
    last = mandel_frame(-0.743643887037151, 0.131825904205330, 0.001, it=950)
    for k in range(n):
        t = ease(k / (n - 1)); f = ornament_frame(bg, "mandelbrot", 0)
        f = Image.blend(last, f, t); d = ImageDraw.Draw(f)
        ctext(d, 300, "...and hang it", font("cinzel", 96), CREAM)
        ctext(d, 420, "on your tree", font("cinzel", 96), GOLD)
        yield f


def orn_frames():
    bg = soft_bg((24, 34, 66), (8, 12, 26)); n = int(T_ORN * FPS)
    for i, (key, name) in enumerate(ITEMS):
        for k in range(n):
            t = k / (n - 1)
            # hold front, spin 360 degrees through the back, settle on front
            ang = 0 if t < 0.2 else 360 if t > 0.85 else 360 * ease((t - 0.2) / 0.65)
            f = ornament_frame(bg, key, ang); d = ImageDraw.Draw(f)
            ctext(d, 250, name, font("cinzel", 92), CREAM)
            ctext(d, 370, "printed on both sides", font("semi", 52), GOLD)
            ctext(d, 1520, f"{i + 1} of 6  ·  ceramic  ·  gold cord", font("light", 46), (220, 222, 232))
            yield f


def hero_frames():
    s = Scene(Image.open(os.path.join(ORN, "ai_mockups", "fractal_ornaments_tree.jpg")).convert("RGB"))
    n = int(T_HERO * FPS)
    for k in range(n):
        f = s.frame(k / n, (1.0, 1.08), aw=1040, cy=1000); d = ImageDraw.Draw(f)
        ctext(d, 215, "6 FRACTAL", font("cinzel", 88), GOLD)
        ctext(d, 320, "CERAMIC ORNAMENTS", font("cinzel", 70), CREAM)
        ctext(d, 1560, "a gift for every math lover", font("semi", 56), CREAM)
        ctext(d, 1645, "computed from real equations", font("light", 46), (225, 225, 235))
        yield f


def main():
    wav = os.path.join(OUT, "pi_music_orn.wav"); CP.music(wav, dur=TOTAL)
    mp4 = os.path.join(OUT, "fractal_ornaments_promo.mp4")
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
           "-c:a", "aac", "-b:a", "160k", "-shortest", mp4]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE); count = 0
    for gen in (zoom_frames(), reveal_frames(), orn_frames(), hero_frames(), CP.cta_frames()):
        for fr in gen:
            if count == int(2.5 * FPS):
                fr.save(os.path.join(OUT, "fractal_ornaments_promo_cover.png"))
            p.stdin.write(fr.tobytes()); count += 1
            if count % 60 == 0:
                print("frames", count, flush=True)
    p.stdin.close(); p.wait()
    print(f"{mp4}: {count} frames ({count / FPS:.1f} s), {os.path.getsize(mp4) // 1024} KB")


if __name__ == "__main__":
    main()
