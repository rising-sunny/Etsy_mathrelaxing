"""
build_resume_video_real.py — REAL Word promo with CONTINUOUS rapid zoom
======================================================================
Camera never rests: zoom ramps hard and often while typing a fictional
persona into the Editorial template.

  python build_resume_video_real.py
"""
from __future__ import annotations

import math
import random
import shutil
import struct
import subprocess
import tempfile
import threading
import time
import wave
import zipfile
from pathlib import Path

import mss
import win32com.client
import win32con
import win32gui
from PIL import Image

import brand

BASE = Path(__file__).resolve().parent
OUT = BASE / "resume_kit"
DOCX = OUT / "templates" / "02_Editorial_Resume_Template.docx"
FRAMES = OUT / "_real_frames"
AUDIO_DIR = OUT / "_real_audio"
VIDEO = OUT / "Editorial_Resume_Kit_promo.mp4"
VIDEO_SILENT = OUT / "_promo_real_silent.mp4"

FPS = 30
RNG = random.Random(44)
TARGET_SEC = 18.0

# Fast live edits
EDITS = [
    ("YOUR FULL NAME", "ALEX RIVERA"),
    ("Target Role  ·  Specialty", "Data Scientist  ·  Applied Math"),
    ("Job Title", "Senior Data Scientist"),
    ("Company  ·  Location", "Northline Analytics  ·  SF"),
    ("Impact bullet with metric.", "Lifted conversion +12% ($4.2M ARR)."),
]

# Continuous camera path (percent). Oscillates hard for kinetic feel.
ZOOM_PATH = [
    118, 148, 168, 138, 158, 125, 170, 142, 160, 130,
    175, 145, 155, 120, 165, 140, 172, 128, 150, 115,
]


def _write_wav(path: Path, samples: list[float], rate: int = 44100):
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(
            b"".join(
                struct.pack("<h", max(-32767, min(32767, int(s * 32767)))) for s in samples
            )
        )


def _synth_key(rate=44100, kind="key") -> list[float]:
    dur = 0.026 if kind == "key" else 0.045
    n = int(rate * dur)
    f0 = RNG.uniform(1800, 3800) if kind == "key" else RNG.uniform(400, 900)
    out = []
    for i in range(n):
        t = i / rate
        env = math.exp(-t * (120 if kind == "key" else 55))
        tone = math.sin(2 * math.pi * f0 * t) * 0.26
        noise = (RNG.random() * 2 - 1) * 0.42 * math.exp(-t * 250)
        thump = math.sin(2 * math.pi * 100 * t) * 0.15 * math.exp(-t * 70)
        out.append((tone + noise + thump) * env * (0.55 if kind == "key" else 0.68))
    return out


def _mix_sfx(events: list[tuple[float, str]], path: Path, total_sec: float, rate=44100):
    total_n = int((total_sec + 0.4) * rate)
    mix = [0.0] * total_n
    keys = [_synth_key(rate, "key") for _ in range(14)]
    clicks = [_synth_key(rate, "click") for _ in range(5)]
    for t, kind in events:
        pool = keys if kind == "key" else clicks
        clip = pool[RNG.randint(0, len(pool) - 1)]
        start = int(t * rate)
        for i, s in enumerate(clip):
            if 0 <= start + i < total_n:
                mix[start + i] += s
    peak = max(1e-6, max(abs(x) for x in mix))
    _write_wav(path, [x * 0.9 / peak for x in mix], rate)


def _dismiss_nags():
    def cb(hwnd, _):
        try:
            if not win32gui.IsWindowVisible(hwnd):
                return True
            title = (win32gui.GetWindowText(hwnd) or "").lower()
            cls = win32gui.GetClassName(hwnd) or ""
            if cls == "NUIDialog" or any(
                x in title
                for x in (
                    "inicia sesión",
                    "inicia sesion",
                    "sign in",
                    "activar",
                    "activate",
                    "comenzar a usar",
                    "licencia",
                )
            ):
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        except Exception:
            pass
        return True

    try:
        win32gui.EnumWindows(cb, None)
    except Exception:
        pass


def _bbox(hwnd) -> dict:
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    left, top = max(0, left), max(0, top)
    return {
        "left": left,
        "top": top,
        "width": max(100, right - left),
        "height": max(100, bottom - top),
    }


def _square(img: Image.Image) -> Image.Image:
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    return img.crop((left, 0, left + side, side)).resize((1080, 1080), Image.Resampling.LANCZOS)


def _is_nag_frame(img: Image.Image) -> bool:
    small = img.resize((32, 32))
    data = list(small.getdata())
    whites = sum(1 for r, g, b in data if r > 242 and g > 242 and b > 242)
    return whites > 32 * 32 * 0.62


def _is_blankish(img: Image.Image) -> bool:
    """Drop frames that are almost empty cream (lost the page)."""
    small = _square(img).resize((48, 48))
    data = list(small.getdata())
    # dark ink pixels
    ink = sum(1 for r, g, b in data if (r + g + b) < 420)
    return ink < 48  # almost no text/UI dark pixels


def _pin_word(hwnd, x=30, y=30, w=1320, h=940):
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetWindowPos(
        hwnd, win32con.HWND_TOPMOST, x, y, w, h, win32con.SWP_SHOWWINDOW
    )
    try:
        win32gui.SetForegroundWindow(hwnd)
    except Exception:
        try:
            import ctypes

            ctypes.windll.user32.AllowSetForegroundWindow(-1)
            win32gui.SetForegroundWindow(hwnd)
        except Exception:
            pass


def _zoom(word, pct: int):
    try:
        word.ActiveWindow.View.Zoom.Percentage = int(max(80, min(200, pct)))
    except Exception:
        pass


def _zoom_ramp(word, start: int, end: int, ms_per_step: float = 0.035):
    """Fast continuous zoom from start→end (~one step every 35ms)."""
    delta = end - start
    steps = max(4, abs(delta) // 3)  # ~3% per step = snappy
    for i in range(steps + 1):
        pct = int(start + delta * (i / steps))
        _zoom(word, pct)
        time.sleep(ms_per_step)


def _zoom_burst(word, center: int, amplitude: int = 25, cycles: int = 2, speed: float = 0.03):
    """Rapid in-out pulses around a center zoom."""
    for _ in range(cycles):
        _zoom_ramp(word, center, center + amplitude, ms_per_step=speed)
        _zoom_ramp(word, center + amplitude, center - amplitude // 2, ms_per_step=speed)
        _zoom_ramp(word, center - amplitude // 2, center, ms_per_step=speed)


def _home(word):
    try:
        word.Selection.HomeKey(Unit=6)
    except Exception:
        pass


def _find_select(word, text: str) -> bool:
    _home(word)
    find = word.Selection.Find
    find.ClearFormatting()
    find.Text = text
    find.Forward = True
    find.Wrap = 1
    find.Format = False
    find.MatchCase = False
    find.MatchWholeWord = False
    return bool(find.Execute())


def _goto_text(word, text: str) -> bool:
    try:
        if not _find_select(word, text):
            return False
        word.ActiveWindow.ScrollIntoView(word.Selection.Range, True)
        try:
            word.Selection.Collapse(Direction=0)
        except Exception:
            pass
        return True
    except Exception:
        return False


def _type_text(word, text: str, sfx: list, t0: float, delay: float, zoom_cb=None):
    for i, ch in enumerate(text):
        word.Selection.TypeText(ch)
        sfx.append((time.time() - t0, "key"))
        if zoom_cb and i % 2 == 0:
            zoom_cb(i, len(text))
        time.sleep(delay + RNG.uniform(0, 0.012))
        if ch in " .":
            time.sleep(0.015)


def _docx_replace(src: Path, dst: Path, mapping: dict[str, str]):
    with zipfile.ZipFile(src, "r") as zin, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/document.xml":
                text = data.decode("utf-8")
                for a, b in mapping.items():
                    text = text.replace(a, b)
                data = text.encode("utf-8")
            zout.writestr(item, data)


def _build_filled(tmp: Path) -> Path:
    mapping = {
        "YOUR FULL NAME": "ALEX RIVERA",
        "Target Role  ·  Specialty": "Data Scientist  ·  Applied Mathematics",
        "email@domain.com  ·  (555) 000-0000  ·  City, ST  ·  linkedin.com/in/you": (
            "alex.rivera@email.com  ·  (555) 014-2088  ·  San Francisco, CA"
        ),
        "email@domain.com": "alex.rivera@email.com",
        "Job Title": "Senior Data Scientist",
        "Company  ·  Location": "Northline Analytics  ·  San Francisco",
        "Impact bullet with metric.": "Lifted paid conversion +12% ($4.2M ARR).",
        "Ownership and scope.": "Owned experimentation across 40+ product squads.",
    }
    p = tmp / "filled_demo.docx"
    _docx_replace(DOCX, p, mapping)
    return p


def main():
    if not DOCX.is_file():
        raise SystemExit(f"Missing {DOCX}")

    for d in (FRAMES, AUDIO_DIR):
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)

    try:
        subprocess.run(
            ["taskkill", "/F", "/IM", "WINWORD.EXE"], capture_output=True, timeout=8
        )
        time.sleep(1.0)
    except Exception:
        pass

    tmp = Path(tempfile.mkdtemp(prefix="resume_vid_"))
    work = tmp / "demo_editorial_resume.docx"
    shutil.copy2(DOCX, work)
    filled = _build_filled(tmp)

    print("Launching Word…")
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = True
    word.DisplayAlerts = 0
    word.WindowState = 0
    try:
        word.FeatureInstall = 0
    except Exception:
        pass

    doc = word.Documents.Open(str(work.resolve()), ReadOnly=False, AddToRecentFiles=False)
    time.sleep(0.9)
    _dismiss_nags()

    hwnd = None
    for _ in range(15):
        try:
            hwnd = int(word.ActiveWindow.Hwnd)
            if hwnd and win32gui.IsWindow(hwnd):
                break
        except Exception:
            hwnd = None
        time.sleep(0.2)
    if not hwnd:
        try:
            doc.Close(False)
            word.Quit()
        except Exception:
            pass
        raise SystemExit("No Word hwnd")

    print(f"hwnd={hwnd} title={win32gui.GetWindowText(hwnd)!r}")
    _pin_word(hwnd)
    _dismiss_nags()
    try:
        word.ActiveWindow.View.Type = 3
    except Exception:
        pass
    _zoom(word, 120)

    sfx: list[tuple[float, str]] = []
    t0 = time.time()
    frames: list[tuple[float, Image.Image]] = []
    recording = True
    z_idx = 0
    current_zoom = 120

    def capture_loop():
        with mss.MSS() as sct:
            while recording:
                try:
                    if not win32gui.IsWindow(hwnd):
                        break
                    shot = sct.grab(_bbox(hwnd))
                    img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
                    frames.append((time.time() - t0, img.copy()))
                except Exception:
                    pass
                time.sleep(1.0 / FPS)

    def fly(segments: int = 1, speed: float = 0.028):
        """Advance continuous zoom path — call constantly so camera never rests."""
        nonlocal z_idx, current_zoom
        for _ in range(segments):
            a = ZOOM_PATH[z_idx % len(ZOOM_PATH)]
            b = ZOOM_PATH[(z_idx + 1) % len(ZOOM_PATH)]
            _zoom_ramp(word, a, b, ms_per_step=speed)
            current_zoom = b
            z_idx += 1

    thr_cap = threading.Thread(target=capture_loop, daemon=True)
    thr_cap.start()
    time.sleep(0.25)
    _pin_word(hwnd)

    # ── Act 1: kinetic open — pure rapid zoom ──
    print("Act 1: kinetic open (continuous zoom)")
    fly(4, speed=0.025)  # several hard ramps immediately

    # ── Act 2: type with zoom between every char burst ──
    print("Act 2: type + continuous zoom")
    done = 0
    for find_text, replace_text in EDITS:
        if time.time() - t0 > 9.0:
            print("  live budget")
            break
        _dismiss_nags()
        _pin_word(hwnd)
        try:
            fly(1, speed=0.025)
            if not _find_select(word, find_text):
                print(f"  skip: {find_text[:40]!r}")
                continue
            print(f"  type: {find_text[:32]!r} → {replace_text[:32]!r}")
            sfx.append((time.time() - t0, "click"))
            try:
                word.ActiveWindow.ScrollIntoView(word.Selection.Range, True)
            except Exception:
                pass

            # Punch to high zoom then type while creeping further in
            punch = 162 if done == 0 else 150
            _zoom_ramp(word, current_zoom, punch, ms_per_step=0.022)
            current_zoom = punch

            def mid_zoom(i, n):
                nonlocal current_zoom
                # continuous creep + micro oscillation while typing
                target = punch + int(18 * (i / max(1, n - 1)))
                if i % 3 == 0:
                    target += 8
                elif i % 3 == 1:
                    target -= 5
                current_zoom = target
                _zoom(word, target)

            _type_text(
                word,
                replace_text,
                sfx,
                t0,
                delay=0.028 if done == 0 else 0.02,
                zoom_cb=mid_zoom,
            )
            done += 1
            fly(2, speed=0.024)
            if done == 2:
                _goto_text(word, "EXPERIENCE")
                fly(1, speed=0.022)
        except Exception as e:
            print(f"  edit fail: {e}")
            break

    # ── Act 3: filled doc — pure camera thrash + section hops ──
    print("Act 3: filled doc + hard continuous zoom")
    try:
        try:
            doc.Close(SaveChanges=False)
        except Exception:
            pass
        doc = word.Documents.Open(
            str(filled.resolve()), ReadOnly=True, AddToRecentFiles=False
        )
        time.sleep(0.25)
        try:
            hwnd = int(word.ActiveWindow.Hwnd)
        except Exception:
            pass
        _pin_word(hwnd)
        try:
            word.ActiveWindow.View.Type = 3
        except Exception:
            pass

        hops = [
            "ALEX RIVERA",
            "EXPERIENCE",
            "Senior Data Scientist",
            "PROFESSIONAL SUMMARY",
            "ALEX RIVERA",
            "Northline",
            "ALEX RIVERA",
        ]
        for label in hops:
            if time.time() - t0 > TARGET_SEC - 1.6:
                break
            _goto_text(word, label)
            sfx.append((time.time() - t0, "click"))
            # 2–3 rapid zoom segments per hop = continuous feel
            fly(2, speed=0.022)
    except Exception as e:
        print(f"  filled act fail: {e}")

    # ── Act 4: settle on name ──
    print("Act 4: settle")
    try:
        _goto_text(word, "ALEX RIVERA")
        fly(1, speed=0.03)
        _zoom_ramp(word, current_zoom, 122, ms_per_step=0.035)
        _pin_word(hwnd)
        time.sleep(0.9)
    except Exception:
        time.sleep(0.6)

    recording = False
    thr_cap.join(timeout=2.0)
    total = time.time() - t0
    print(f"Captured {len(frames)} frames in {total:.1f}s, edits={done}")

    try:
        doc.Close(SaveChanges=False)
    except Exception:
        pass
    try:
        word.Quit()
    except Exception:
        pass
    time.sleep(0.3)
    try:
        subprocess.run(
            ["taskkill", "/F", "/IM", "WINWORD.EXE"], capture_output=True, timeout=6
        )
    except Exception:
        pass
    shutil.rmtree(tmp, ignore_errors=True)

    if len(frames) < 40:
        raise SystemExit("Too few frames")

    # Filter nags + blank page frames
    clean = []
    for t, im in frames:
        try:
            sq = _square(im)
            if _is_nag_frame(sq) or _is_blankish(im):
                continue
            clean.append((t, im))
        except Exception:
            continue
    if len(clean) >= max(40, int(len(frames) * 0.4)):
        print(f"filter: {len(clean)}/{len(frames)}")
        t0b = clean[0][0]
        frames = [(t - t0b, im) for t, im in clean]
    else:
        print(f"filter light ({len(clean)}/{len(frames)})")
        frames = clean if len(clean) > 40 else frames

    duration = min(frames[-1][0], TARGET_SEC)
    n_out = max(int(duration * FPS), 1)
    print(f"Writing {n_out} frames ({duration:.1f}s) from {len(frames)} caps…")
    fi = 0
    for i in range(n_out):
        t = i / FPS
        while fi + 1 < len(frames) and frames[fi + 1][0] <= t:
            fi += 1
        _square(frames[fi][1]).save(FRAMES / f"f_{i:04d}.png")
        if i % 90 == 0:
            print(f"  {i}/{n_out}")

    sfx_path = AUDIO_DIR / "sfx.wav"
    _mix_sfx(sfx, sfx_path, duration + 0.2)

    brand.encode_mp4(
        str(FRAMES), str(VIDEO_SILENT), fps=FPS, pattern="f_%04d.png", crf=17, cleanup=False
    )
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(VIDEO_SILENT),
            "-i",
            str(sfx_path),
            "-t",
            str(TARGET_SEC),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-crf",
            "17",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            "-movflags",
            "+faststart",
            str(VIDEO),
        ],
        check=True,
        capture_output=True,
    )
    shutil.rmtree(FRAMES, ignore_errors=True)
    shutil.rmtree(AUDIO_DIR, ignore_errors=True)
    if VIDEO_SILENT.exists():
        VIDEO_SILENT.unlink()

    check_dir = OUT / "_video_checks"
    check_dir.mkdir(exist_ok=True)
    for ss, name in ((1, "z1"), (4, "z4"), (8, "z8"), (12, "z12"), (16, "z16")):
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-ss",
                str(ss),
                "-i",
                str(VIDEO),
                "-frames:v",
                "1",
                str(check_dir / f"{name}.png"),
            ],
            capture_output=True,
        )

    mb = VIDEO.stat().st_size / (1024 * 1024)
    print(f"OK {VIDEO} ({mb:.2f} MB, ~{duration:.1f}s)")


if __name__ == "__main__":
    main()
