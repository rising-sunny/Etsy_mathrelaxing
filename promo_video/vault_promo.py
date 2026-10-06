"""
Vertical promo video (1080 x 1920, 30 fps, ~23 s) for The Mathematician's Vault
(printable escape room for adults). The vault dial spins in the hook and the finale;
the password is never shown. Music from the digits of pi.

  python vault_promo.py   -> out/vault_escape_room_promo.mp4 (+ cover PNG)
"""
import os, sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(REPO, "escape_room_adults"))
import calendar_promo as CP
from calendar_promo import font, ctext, ease, Scene, W, H, FPS, CREAM
import design

VA = os.path.join(REPO, "escape_room_adults")
PG = os.path.join(VA, "out", "_Letter")
GOLD = (236, 200, 120); NAVY_D = (14, 20, 38)
EXHIBITS = [(3, "a Caesar cipher"), (4, "Dürer's 1514 magic square"), (10, "SEND + MORE = MONEY"),
            (8, "a code in the desk lamps"), (11, "Fibonacci's rabbit problem")]
T_HOOK, T_COVER, T_EX, T_VAULT, T_HERO, T_CTA = 3.0, 2.0, 1.8, 3.0, 3.0, 3.0
TOTAL = T_HOOK + T_COVER + len(EXHIBITS) * T_EX + T_VAULT + T_HERO + T_CTA


def page(n):
    return Image.open(os.path.join(PG, f"p{n:02d}.jpg")).convert("RGB")


# ------------------------------------------------------------------ vault door with a spinning dial
def door_layers(R=430):
    S = int(R * 2.3); bg = (0, 0, 0)
    base = Image.new("RGB", (S, S), bg); design.vault_door(base, S / 2, S / 2, R, font)
    mask = Image.new("L", (S, S), 0); ImageDraw.Draw(mask).ellipse((S / 2 - R * 0.995, S / 2 - R * 0.995, S / 2 + R * 0.995, S / 2 + R * 0.995), fill=255)
    door = base.convert("RGBA"); door.putalpha(mask)
    rd = int(R * 0.665); box = (int(S / 2 - rd), int(S / 2 - rd), int(S / 2 + rd), int(S / 2 + rd))
    dial = base.crop(box).convert("RGBA")
    m2 = Image.new("L", dial.size, 0); ImageDraw.Draw(m2).ellipse((0, 0, dial.width - 1, dial.height - 1), fill=255); dial.putalpha(m2)
    return door, dial, box


DOOR, DIAL, DBOX = door_layers()


def door_at(angle):
    im = DOOR.copy(); d = DIAL.rotate(angle, resample=Image.BICUBIC)
    im.alpha_composite(d, (DBOX[0], DBOX[1])); return im


def bg_navy():
    g = np.linspace(0, 1, H)[:, None, None]
    arr = (np.array((30, 42, 74)) * (1 - g) + np.array(NAVY_D) * g) * np.ones((1, W, 1))
    return Image.fromarray(arr.astype(np.uint8))


BG = bg_navy()


def spin_angle(t):
    # turn right, pause, turn left, pause: like dialling a combination
    return 140 * ease(min(1, t / 0.35)) - 90 * ease(min(1, max(0, (t - 0.5) / 0.35)))


def hook_frames():
    n = int(T_HOOK * FPS)
    for k in range(n):
        t = k / n; f = BG.copy()
        door = door_at(spin_angle(t)); f.paste(door, ((W - door.width) // 2, 560), door); d = ImageDraw.Draw(f)
        a = ease(min(1, t * 3))
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ctext(ld, 250, "Can you crack", font("cinzel", 96), CREAM + (int(255 * a),))
        ctext(ld, 370, "THE VAULT?", font("cinzel", 120), GOLD + (int(255 * a),))
        f = Image.alpha_composite(f.convert("RGBA"), lay).convert("RGB"); d = ImageDraw.Draw(f)
        ctext(d, 1650, "a printable escape room for adults", font("semi", 52), CREAM)
        yield f


def cover_frames():
    s = Scene(page(0)); n = int(T_COVER * FPS)
    for k in range(n):
        f = s.frame(k / n, (1.0, 1.05), aw=760, cy=1010); d = ImageDraw.Draw(f)
        ctext(d, 230, "9 puzzles hidden in", font("cinzel", 70), CREAM)
        ctext(d, 320, "a mathematician's study", font("cinzel", 70), GOLD)
        ctext(d, 1560, "2-6 players  ·  60-90 minutes", font("semi", 54), CREAM)
        yield f


def exhibit_frames():
    n = int(T_EX * FPS)
    for i, (pn, label) in enumerate(EXHIBITS):
        im = page(pn); w, h = im.size
        crop = im.crop((int(w * 0.03), int(h * 0.035), int(w * 0.97), int(h * 0.62)))
        for k in range(n):
            t = k / n; z = 1.0 + 0.06 * t; aw = int(1000 * z); ah = int(aw * crop.height / crop.width)
            f = BG.copy(); x, y = (W - aw) // 2, int(990 - ah / 2)
            sh = Image.new("L", (W, H), 0); ImageDraw.Draw(sh).rectangle((x + 14, y + 24, x + aw + 14, y + ah + 24), fill=170)
            f.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(24)))
            f.paste(crop.resize((aw, ah), Image.LANCZOS), (x, y)); d = ImageDraw.Draw(f)
            ctext(d, 250, f"EXHIBIT {pn - 2} OF 9", font("bold", 50), GOLD)
            ctext(d, 1640, label, font("cinzel", 64), CREAM)
            yield f


def vault_frames():
    n = int(T_VAULT * FPS); pg = page(12); w, h = pg.size
    top = pg.crop((0, int(h * 0.03), w, int(h * 0.50)))
    for k in range(n):
        t = k / n; f = BG.copy()
        tw = 1000; th = int(tw * top.height / top.width); f.paste(top.resize((tw, th), Image.LANCZOS), ((W - tw) // 2, 200))
        door = door_at(-200 * ease(t)).resize((560, 560), Image.LANCZOS); f.paste(door, ((W - 560) // 2, 260 + th), door)
        d = ImageDraw.Draw(f)
        ctext(d, 1560, "Nine letters.", font("cinzel", 72), CREAM)
        ctext(d, 1660, "One password.", font("cinzel", 72), GOLD)
        yield f


def hero_frames():
    s = Scene(Image.open(os.path.join(VA, "ai_mockups", "vault_gamenight_hero.jpg")).convert("RGB")); n = int(T_HERO * FPS)
    for k in range(n):
        f = s.frame(k / n, (1.0, 1.08), aw=1040, cy=1000); d = ImageDraw.Draw(f)
        ctext(d, 215, "GAME NIGHT", font("cinzel", 92), GOLD)
        ctext(d, 325, "DATE NIGHT  ·  MATH CLUB", font("cinzel", 56), CREAM)
        ctext(d, 1580, "print it tonight, play tonight", font("semi", 56), CREAM)
        yield f


def main():
    out = CP.OUT
    wav = os.path.join(out, "pi_music_vault.wav"); CP.music(wav, dur=TOTAL)
    mp4 = os.path.join(out, "vault_escape_room_promo.mp4"); ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
           "-c:a", "aac", "-b:a", "160k", "-shortest", mp4]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE); count = 0
    for gen in (hook_frames(), cover_frames(), exhibit_frames(), vault_frames(), hero_frames(), CP.cta_frames()):
        for fr in gen:
            if count == int(2.2 * FPS):
                fr.save(os.path.join(out, "vault_escape_room_promo_cover.png"))
            p.stdin.write(fr.tobytes()); count += 1
    p.stdin.close(); p.wait()
    print(f"{mp4}: {count} frames ({count / FPS:.1f} s), {os.path.getsize(mp4) // 1024} KB")


if __name__ == "__main__":
    main()
