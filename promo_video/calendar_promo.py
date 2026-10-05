"""
Vertical promo video (1080 x 1920, 30 fps, ~22 s) for the 2027 Mathematical Art
Calendar, for TikTok / Instagram Reels / Facebook. Music is synthesised from the digits
of pi (royalty-free). Text stays inside the platforms' safe zone.

  python calendar_promo.py   -> out/calendar_2027_promo.mp4 (+ cover frame PNG)
"""
import os, sys, math, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(REPO, "advent_stem")); sys.path.insert(0, os.path.join(REPO, "math_cards_xmas"))
from generate_advent import font
import generate_cards as GC  # pi_digits

OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
CAL = os.path.join(REPO, "calendar_2027")
W, H, FPS = 1080, 1920, 30
NAVY = (18, 26, 52); GOLD = (222, 182, 96); CREAM = (250, 246, 238)
MONTHS = [("JANUARY", "jan", "Julia Set"), ("FEBRUARY", "feb", "Cardioid"), ("MARCH", "mar", "Barnsley Fern"),
          ("APRIL", "apr", "Phyllotaxis"), ("MAY", "may", "Lorenz Attractor"), ("JUNE", "jun", "Harmonograph"),
          ("JULY", "jul", "Mandelbrot Set"), ("AUGUST", "aug", "Newton Fractal"), ("SEPTEMBER", "sep", "Dragon Curve"),
          ("OCTOBER", "oct", "Clifford Attractor"), ("NOVEMBER", "nov", "Fractal Tree"), ("DECEMBER", "dec", "Apollonian Gasket")]
T_HOOK, T_MONTH, T_HERO, T_CTA = 3.0, 1.0, 4.0, 3.0
TOTAL = T_HOOK + 12 * T_MONTH + T_HERO + T_CTA


def art(i):
    return Image.open(os.path.join(CAL, "out", f"{i + 1:02d}_{MONTHS[i][1]}_raw.jpg")).convert("RGB")


def ease(t):
    return t * t * (3 - 2 * t)


def ctext(d, y, s, f, fill, shadow=True):
    x = (W - d.textlength(s, font=f)) / 2
    if shadow:
        d.text((x + 3, y + 4), s, font=f, fill=(0, 0, 0, fill[3]) if len(fill) == 4 else (0, 0, 0))
    d.text((x, y), s, font=f, fill=fill)


class Scene:
    """Landscape artwork centred on a blurred, darkened copy of itself (vertical frame)."""
    def __init__(self, im):
        self.im = im
        bg = im.resize((int(H * im.width / im.height), H), Image.LANCZOS)
        x0 = (bg.width - W) // 2
        bg = bg.crop((x0, 0, x0 + W, H)).filter(ImageFilter.GaussianBlur(40))
        self.bg = Image.blend(bg, Image.new("RGB", (W, H), (0, 0, 0)), 0.45)

    def frame(self, t, zoom=(1.0, 1.08), aw=1000, cy=960):
        z = zoom[0] + (zoom[1] - zoom[0]) * t
        im = self.im; cw, ch = im.width / z, im.height / z
        crop = im.crop(((im.width - cw) / 2, (im.height - ch) / 2, (im.width + cw) / 2, (im.height + ch) / 2))
        ah = int(aw * im.height / im.width); a = crop.resize((aw, ah), Image.LANCZOS)
        f = self.bg.copy(); x, y = (W - aw) // 2, int(cy - ah / 2)
        sh = Image.new("L", (aw + 80, ah + 80), 0); ImageDraw.Draw(sh).rectangle((40, 40, aw + 40, ah + 40), fill=170)
        f.paste((0, 0, 0), (x - 40 + 10, y - 40 + 18), sh.filter(ImageFilter.GaussianBlur(22)))
        f.paste(a, (x, y)); return f


def hook_frames():
    s = Scene(art(0)); n = int(T_HOOK * FPS)
    for k in range(n):
        t = k / n; f = s.frame(t, (1.0, 1.12)); d = ImageDraw.Draw(f)
        lines = [("This calendar", 92, CREAM, 0.0), ("was drawn by", 92, CREAM, 0.15), ("EQUATIONS", 150, GOLD, 0.35)]
        y = 300
        for s_, sz, col, start in lines:
            a = ease(min(1, max(0, (t - start) / 0.25)))
            if a > 0:
                ff = font("cinzel", sz)
                layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
                ctext(ld, y + (1 - a) * 40, s_, ff, col + (int(255 * a),))
                f = Image.alpha_composite(f.convert("RGBA"), layer).convert("RGB")
            y += sz * 1.2
        d = ImageDraw.Draw(f)
        ctext(d, 1480, "no AI  ·  no clip-art  ·  just math", font("semi", 52), CREAM)
        yield f


def month_frames():
    n = int(T_MONTH * FPS); prev = None
    for i, (mn, key, name) in enumerate(MONTHS):
        s = Scene(art(i))
        for k in range(n):
            t = k / n; f = s.frame(t, (1.0, 1.06)); d = ImageDraw.Draw(f)
            ctext(d, 330, mn, font("cinzel", 120), CREAM)
            ctext(d, 470, "2027", font("cinzel", 64), GOLD)
            ctext(d, 1420, name, font("bold", 76), CREAM)
            ctext(d, 1520, f"{i + 1} of 12", font("light", 46), (220, 220, 230))
            if prev is not None and k < 6:  # quick crossfade
                f = Image.blend(prev, f, (k + 1) / 7)
            yield f
        prev = f


def hero_frames():
    hero = Image.open(os.path.join(CAL, "ai_mockups", "calendar_study_hero.jpg")).convert("RGB")
    s = Scene(hero); n = int(T_HERO * FPS)
    for k in range(n):
        t = k / n; f = s.frame(t, (1.0, 1.07), aw=1040, cy=1000); d = ImageDraw.Draw(f)
        ctext(d, 215, "THE 2027", font("cinzel", 84), GOLD)
        ctext(d, 315, "MATHEMATICAL ART CALENDAR", font("cinzel", 58), CREAM)
        ctext(d, 1560, "12 months  ·  12 equations", font("semi", 56), CREAM)
        ctext(d, 1645, "2 sizes, printed to order", font("light", 46), (225, 225, 235))
        yield f


def cta_frames():
    n = int(T_CTA * FPS)
    for k in range(n):
        t = k / n; f = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(f)
        # golden-angle dots blooming in the background
        ga = math.pi * (3 - 5 ** 0.5); m = int(60 + 900 * ease(min(1, t * 1.4)))
        for i in range(1, m):
            r = 22 * math.sqrt(i); a = i * ga; x, y = W / 2 + r * math.cos(a), 1000 + r * math.sin(a)
            rr = 5 + i / 300; col = (40 + i % 3 * 10, 56, 98)
            d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=col)
        a = ease(min(1, t * 2.5))
        ctext(d, 520, "MathRelaxing", font("cinzel", 120), tuple(int(c * a + NAVY[j] * (1 - a)) for j, c in enumerate(GOLD)))
        ctext(d, 680, "on Etsy", font("semi", 72), CREAM)
        ctext(d, 1040, "Real mathematics,", font("cinzel", 70), CREAM)
        ctext(d, 1130, "made beautiful", font("cinzel", 70), CREAM)
        ctext(d, 1380, "Link in bio", font("bold", 64), GOLD)
        yield f


# ------------------------------------------------------------------ music from pi
def music(path, dur=TOTAL, sr=44100):
    n = int(dur * sr); tt = np.arange(n) / sr; mix = np.zeros(n)
    A = 220.0; scale = [0, 3, 5, 7, 10, 12, 15, 17, 19, 22]  # A minor pentatonic, 2 octaves; digit -> note
    def note(f, start, length, amp, pluck=True):
        i0 = int(start * sr); m = int(length * sr); i1 = min(n, i0 + m)
        if i0 >= n:
            return
        t = np.arange(i1 - i0) / sr
        env = np.exp(-t * (3.2 if pluck else 0.6)) * np.minimum(1, t / 0.008)
        w = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t)
        mix[i0:i1] += amp * env * w
    # pad chords every 2 s: Am, F, C, G
    chords = [[0, 3, 7], [-4, 0, 3], [3, 7, 10], [-2, 2, 5]]
    for b in range(int(dur / 2) + 1):
        for st in chords[b % 4]:
            note(A * 2 ** (st / 12) / 2, b * 2.0, 2.4, 0.10, pluck=False)
    # melody: one note every beat (0.5 s) from the digits of pi, accents on each cut
    digits = GC.pi_digits(200)
    for k in range(int(dur / 0.5)):
        dgt = int(digits[k]); f = A * 2 ** (scale[dgt] / 12)
        note(f, k * 0.5, 0.9, 0.16)
        if T_HOOK <= k * 0.5 < T_HOOK + 12 and k % 2 == 0:
            note(f * 2, k * 0.5, 0.4, 0.07)
    # simple echo
    d1 = int(0.375 * sr); out = mix.copy(); out[d1:] += 0.35 * mix[:-d1]
    fade = np.ones(n); fl = int(1.2 * sr); fade[-fl:] = np.linspace(1, 0, fl); fade[:int(0.3 * sr)] = np.linspace(0, 1, int(0.3 * sr))
    out *= fade; out /= np.abs(out).max() / 0.8
    st = np.stack([out, np.roll(out, int(0.012 * sr))], axis=1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((st * 32767).astype(np.int16).tobytes())


def main():
    wav = os.path.join(OUT, "pi_music.wav"); music(wav)
    mp4 = os.path.join(OUT, "calendar_2027_promo.mp4")
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
           "-c:a", "aac", "-b:a", "160k", "-shortest", mp4]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE); count = 0
    for gen in (hook_frames(), month_frames(), hero_frames(), cta_frames()):
        for fr in gen:
            if count == int(1.6 * FPS):
                fr.save(os.path.join(OUT, "calendar_2027_promo_cover.png"))
            p.stdin.write(fr.tobytes()); count += 1
    p.stdin.close(); p.wait()
    print(f"{mp4}: {count} frames ({count / FPS:.1f} s), {os.path.getsize(mp4) // 1024} KB")


if __name__ == "__main__":
    main()
