"""
generate_teacher_tumbler_wrap.py — Exclusive mathematical sublimation wraps

Differentiator vs Etsy "teacher life / crayon / retro" flood:
  computed math art + real LaTeX (matplotlib Computer Modern), seamless 20oz wrap.

Size: 9.3" × 8.2" @ 300 DPI  →  2790 × 2460 px

Designs
  A  euler_field     — dark seamless equation constellation + hero identity
  B  fourier_wave    — square-wave Fourier partial sums as full-bleed graphic
  C  complex_plane   — Julia set field + iteration equation

  python generate_teacher_tumbler_wrap.py
  python generate_teacher_tumbler_wrap.py --upload
"""
from __future__ import annotations

import argparse
import io
import zipfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import patheffects as pe
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

BASE = Path(__file__).resolve().parent
OUT = BASE / "teacher_tumbler_wrap"
PRINTS = OUT / "prints"
PREVIEWS = OUT / "previews"

W_IN, H_IN = 9.3, 8.2
DPI = 300
W, H = int(W_IN * DPI), int(H_IN * DPI)  # 2790 × 2460

plt.rcParams["mathtext.fontset"] = "cm"
plt.rcParams["mathtext.rm"] = "serif"


def _pil_font(size: int, bold: bool = False):
    cands = (
        [r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\georgiab.ttf"]
        if bold
        else [r"C:\Windows\Fonts\georgia.ttf", r"C:\Windows\Fonts\arial.ttf"]
    )
    for p in cands:
        if Path(p).is_file():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def _fig_to_rgba(fig, dpi=200, transparent: bool = True) -> Image.Image:
    buf = io.BytesIO()
    fc = "none" if transparent else fig.get_facecolor()
    fig.savefig(
        buf,
        format="png",
        dpi=dpi,
        transparent=transparent,
        facecolor=fc,
        edgecolor="none",
        pad_inches=0,
    )
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).convert("RGBA")


def _latex_rgba(tex: str, fontsize: float = 48, color: str = "#e9ecf5",
                dpi: int = 220) -> Image.Image:
    """Render a single LaTeX math expression to transparent RGBA."""
    fig = plt.figure(figsize=(8, 2.2), dpi=dpi)
    fig.patch.set_alpha(0.0)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    t = ax.text(0.5, 0.5, tex, fontsize=fontsize, ha="center", va="center", color=color)
    t.set_path_effects([pe.withStroke(linewidth=0.0, foreground=color)])
    return _fig_to_rgba(fig, dpi=dpi)


def _paste_center(base: Image.Image, overlay: Image.Image, cy: float, scale: float = 1.0):
    """Paste overlay centered horizontally at fractional vertical cy (0–1)."""
    ow = int(overlay.width * scale)
    oh = int(overlay.height * scale)
    ov = overlay.resize((max(1, ow), max(1, oh)), Image.Resampling.LANCZOS)
    x = (base.width - ov.width) // 2
    y = int(cy * base.height - ov.height / 2)
    base.paste(ov, (x, y), ov)


# ═══════════════════════════════════════════════════════════════════════════
# DESIGN A — Euler Field (dark observatory, seamless equation constellation)
# ═══════════════════════════════════════════════════════════════════════════

def design_euler_field() -> Image.Image:
    """
    Deep navy field with a clear hierarchy:
      hero LaTeX identity + readable secondary equations in orbit positions.
    """
    bg = "#0a0c14"
    fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
    fig.patch.set_facecolor(bg)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(bg)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # soft orbital rings (structure, not dominant)
    for rad, alpha in [(0.22, 0.35), (0.34, 0.28), (0.46, 0.22)]:
        ax.add_patch(plt.Circle((0.5, 0.52), rad, fill=False, ec="#2b3242", lw=1.2, alpha=alpha))

    # secondary equations — larger & brighter than before
    snippets = [
        (r"$\nabla\cdot\mathbf{E}=\rho/\varepsilon_0$", 0.18, 0.88, 13, "#8ad4e0"),
        (r"$\int_{-\infty}^{\infty}e^{-x^{2}}\,dx=\sqrt{\pi}$", 0.78, 0.88, 12, "#a8b0c0"),
        (r"$\sum_{n=1}^{\infty}1/n^{2}=\pi^{2}/6$", 0.18, 0.18, 12, "#a8b0c0"),
        (r"$E=mc^{2}$", 0.82, 0.20, 16, "#ffe2b0"),
        (r"$F=ma$", 0.85, 0.55, 15, "#ffe2b0"),
        (r"$i^{2}=-1$", 0.15, 0.55, 14, "#e9ecf5"),
        (r"$\Delta x\,\Delta p\geq\hbar/2$", 0.50, 0.14, 12, "#8ad4e0"),
        (r"$\sin^{2}\theta+\cos^{2}\theta=1$", 0.50, 0.90, 12, "#a8b0c0"),
    ]
    for tex, x, y, fs, col in snippets:
        ax.text(x, y, tex, fontsize=fs, ha="center", va="center", color=col, alpha=0.95, zorder=2)

    # hero plate
    ax.add_patch(plt.Rectangle((0.10, 0.38), 0.80, 0.28, facecolor="#11141d",
                               edgecolor="#3a4255", lw=1.4, alpha=0.92, zorder=3))
    ax.text(0.5, 0.56, r"$e^{i\pi}+1=0$", fontsize=48, ha="center", va="center",
            color="#f8f4eb", zorder=5)
    ax.text(0.5, 0.44, "Euler's identity", fontsize=13, ha="center", va="center",
            color="#6fc9d8", style="italic", zorder=5)

    ax.text(0.5, 0.05, "MATH TEACHER", fontsize=13, ha="center", va="center",
            color="#6a7388", fontname="DejaVu Sans", zorder=5)

    im = _fig_to_rgba(fig, dpi=100, transparent=False).convert("RGB")
    return ImageEnhance.Contrast(im.resize((W, H), Image.Resampling.LANCZOS)).enhance(1.12)


# ═══════════════════════════════════════════════════════════════════════════
# DESIGN B — Fourier Wave (full-bleed harmonic series)
# ═══════════════════════════════════════════════════════════════════════════

def design_fourier_wave() -> Image.Image:
    """
    Full wrap: square wave built from odd harmonics (true Fourier series).
    Large LaTeX sum + partial-sum curves in cream/navy plate style.
    Seamless in x: the wave is a periodic function over [0, 4π] mapped to width.
    """
    fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
    fig.patch.set_facecolor("#F4F1EA")
    ax = fig.add_axes([0.04, 0.08, 0.92, 0.84])
    ax.set_facecolor("#F4F1EA")
    ax.axis("off")

    # domain one full period of the series display (seamless if period matches width)
    x = np.linspace(0, 4 * np.pi, 2000)
    # square wave target
    square = np.sign(np.sin(x))
    ax.plot(x, 1.15 * square, color="#C8C2B4", lw=1.0, alpha=0.55, zorder=1)

    # partial sums S_N = (4/π) Σ_{k=0}^{N} sin((2k+1)x)/(2k+1)
    colors = ["#1A7A8A", "#2E5A88", "#B85C38", "#1A1A1A"]
    for i, N in enumerate([1, 3, 7, 15]):
        s = np.zeros_like(x)
        for k in range(N):
            n = 2 * k + 1
            s += np.sin(n * x) / n
        s *= 4 / np.pi
        ax.plot(x, s, color=colors[i % len(colors)], lw=1.6 + 0.15 * i, alpha=0.9, zorder=2 + i)

    ax.set_xlim(0, 4 * np.pi)
    ax.set_ylim(-1.85, 2.35)
    ax.axhline(0, color="#C8C2B4", lw=0.7, alpha=0.8)

    # LaTeX formula plate (axes fraction)
    fig.text(0.5, 0.88, r"$f(x)=\frac{4}{\pi}\sum_{k=0}^{N}\frac{\sin((2k+1)x)}{2k+1}$",
             ha="center", va="center", fontsize=15, color="#1A1A1A")
    fig.text(0.5, 0.80, "Fourier series  ·  square wave  ·  odd harmonics",
             ha="center", va="center", fontsize=9, color="#1A7A8A", style="italic")
    fig.text(0.5, 0.05, "MATH TEACHER", ha="center", va="center",
             fontsize=11, color="#555555", fontname="DejaVu Sans")

    im = _fig_to_rgba(fig, dpi=100, transparent=False).convert("RGB")
    return im.resize((W, H), Image.Resampling.LANCZOS)


# ═══════════════════════════════════════════════════════════════════════════
# DESIGN C — Complex Plane (Julia set field + iteration)
# ═══════════════════════════════════════════════════════════════════════════

def design_complex_plane() -> Image.Image:
    """
    Julia set for c = −0.8 + 0.156i (connected, ornate).
    Overlay LaTeX iteration rule. High-end math art, not school clipart.
    """
    # render julia at wrap aspect
    res_x, res_y = 1400, int(1400 * H / W)
    xmin, xmax = -1.6, 1.6
    ymin, ymax = -1.4, 1.4
    # match aspect of wrap roughly
    ar = W / H
    xspan = 3.2
    yspan = xspan / ar
    xmin, xmax = -xspan / 2, xspan / 2
    ymin, ymax = -yspan / 2, yspan / 2

    xs = np.linspace(xmin, xmax, res_x)
    ys = np.linspace(ymin, ymax, res_y)
    X, Y = np.meshgrid(xs, ys)
    Z = X + 1j * Y
    C = -0.8 + 0.156j
    M = np.zeros(Z.shape, dtype=int)
    z = Z.copy()
    max_iter = 120
    for i in range(max_iter):
        mask = np.abs(z) <= 2
        z[mask] = z[mask] ** 2 + C
        M[mask] = i

    # dark scientific colormap via matplotlib
    fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
    fig.patch.set_facecolor("#05060a")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(
        M,
        extent=[xmin, xmax, ymin, ymax],
        origin="lower",
        cmap="magma",
        aspect="auto",
        interpolation="bilinear",
    )
    ax.axis("off")

    # translucent plate for equation readability
    ax.add_patch(plt.Rectangle((xmin, ymin + 0.08 * yspan), xspan, 0.28 * yspan,
                               facecolor="#0a0c14", edgecolor="none", alpha=0.55,
                               transform=ax.transData, zorder=5))

    fig.text(0.5, 0.16, r"$z_{n+1}=z_n^{2}+c$", fontsize=28, ha="center", va="center",
             color="#f4f1ea", zorder=10)
    fig.text(0.5, 0.09, r"$c=-0.8+0.156\,i$  ·  Julia set", fontsize=11, ha="center",
             va="center", color="#6fc9d8", zorder=10)
    fig.text(0.5, 0.04, "COMPLEX DYNAMICS", fontsize=9, ha="center", va="center",
             color="#828aa0", fontname="DejaVu Sans", zorder=10)

    im = _fig_to_rgba(fig, dpi=100, transparent=False).convert("RGB")
    return im.resize((W, H), Image.Resampling.LANCZOS)


DESIGNS = {
    "euler_field": ("Euler_Field_Math_Teacher_Wrap_20oz.png", design_euler_field),
    "fourier_wave": ("Fourier_Wave_Math_Teacher_Wrap_20oz.png", design_fourier_wave),
    "complex_plane": ("Julia_Set_Math_Teacher_Wrap_20oz.png", design_complex_plane),
}


def render_all():
    PRINTS.mkdir(parents=True, exist_ok=True)
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    paths = []
    for key, (fname, fn) in DESIGNS.items():
        print("rendering", key, "…")
        im = fn()
        assert im.size == (W, H), im.size
        p = PRINTS / fname
        im.save(p, "PNG", optimize=True)
        print(" ", p.name, im.size)
        paths.append(p)
        # flat preview
        im.resize((1200, int(1200 * H / W)), Image.Resampling.LANCZOS).save(
            PREVIEWS / f"preview_{key}.jpg", quality=93
        )
    return paths


def build_previews(paths: list[Path]):
    imgs = [Image.open(p).convert("RGB") for p in paths]
    th = 720
    tiles = [im.resize((int(im.width * th / im.height), th), Image.Resampling.LANCZOS) for im in imgs]
    pad = 20
    canvas_w = sum(t.width for t in tiles) + pad * (len(tiles) + 1)
    canvas_h = th + 150
    canvas = Image.new("RGB", (canvas_w, canvas_h), (20, 22, 28))
    d = ImageDraw.Draw(canvas)
    try:
        f = ImageFont.truetype(r"C:\Windows\Fonts\georgia.ttf", 34)
        fs = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 16)
    except Exception:
        f = fs = ImageFont.load_default()
    d.text((canvas_w // 2, 30), "Exclusive Math Tumbler Wraps", fill=(244, 241, 234), font=f, anchor="mt")
    d.text((canvas_w // 2, 78), "Computed art + LaTeX  ·  20oz 9.3×8.2  ·  300 DPI PNG",
           fill=(111, 201, 216), font=fs, anchor="mt")
    x = pad
    for t in tiles:
        canvas.paste(t, (x, 120))
        x += t.width + pad
    canvas.save(PREVIEWS / "01_hero.jpg", quality=93)

    # detail crops
    for i, (p, name) in enumerate(zip(paths, ["02_detail_euler.jpg", "03_detail_fourier.jpg", "04_detail_julia.jpg"])):
        im = Image.open(p).convert("RGB")
        # center crop
        cw, ch = im.width // 2, im.height // 2
        crop = im.crop((im.width // 4, im.height // 4, im.width // 4 + cw, im.height // 4 + ch))
        crop.resize((1100, 900), Image.Resampling.LANCZOS).save(PREVIEWS / name, quality=93)

    # specs
    specs = Image.new("RGB", (1100, 900), (244, 241, 234))
    d = ImageDraw.Draw(specs)
    d.text((550, 80), "WHAT MAKES THESE DIFFERENT", fill=(18, 28, 48), font=f, anchor="mt")
    bullets = [
        "Not crayon / 'teacher life' clipart",
        "Real computed graphics (Fourier, Julia, equation field)",
        "Equations in Computer Modern LaTeX",
        "20oz skinny  ·  9.3 × 8.2 in  ·  300 DPI PNG",
        "3 exclusive designs in one download",
    ]
    y = 220
    for b in bullets:
        d.text((550, y), f"·  {b}", fill=(26, 26, 26), font=fs, anchor="mt")
        y += 70
    specs.save(PREVIEWS / "05_specs.jpg", quality=93)
    print("previews ok")


def build_zip(paths: list[Path]) -> Path:
    zpath = OUT / "Math_Teacher_Tumbler_Wraps_Exclusive_20oz.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            z.write(p, p.name)
        z.writestr(
            "READ-ME.txt",
            "EXCLUSIVE MATH TEACHER TUMBLER WRAPS\n"
            "===================================\n\n"
            "Three original designs — computed mathematical art with LaTeX typography.\n"
            "NOT generic teacher clipart.\n\n"
            "FILES\n"
            "  Euler_Field_Math_Teacher_Wrap_20oz.png   dark equation constellation\n"
            "  Fourier_Wave_Math_Teacher_Wrap_20oz.png  square-wave Fourier series\n"
            "  Julia_Set_Math_Teacher_Wrap_20oz.png     complex dynamics field\n\n"
            "SIZE  9.3 × 8.2 inches @ 300 DPI  (20oz skinny straight)\n"
            "Resize only if your blank requires a different template.\n\n"
            "Digital files for sublimation / POD. Do not resell the digital files.\n",
        )
    print("ZIP", zpath, f"({zpath.stat().st_size/1e6:.2f} MB)")
    return zpath


def upload_draft(zpath: Path, replace_listing_id: int | None = 4543860690):
    """Create new draft, or refresh images/files on existing listing."""
    from etsy_manager import EtsyManager
    import time

    title = (
        "Math Teacher Tumbler Wrap PNG | Fourier Julia LaTeX Sublimation 20oz | "
        "STEM Seamless Design | Back to School"
    )
    if len(title) > 140:
        title = title[:140]
    tags = [
        "tumbler wrap",
        "math teacher",
        "sublimation wrap",
        "teacher tumbler",
        "20oz tumbler wrap",
        "stem teacher",
        "fourier",
        "julia set",
        "back to school",
        "teacher gift",
        "png sublimation",
        "skinny tumbler",
        "math art",
    ]
    assert all(len(t) <= 20 for t in tags)

    desc = (
        "Exclusive math teacher tumbler wraps — three original 20oz skinny sublimation designs "
        "built from real mathematics and LaTeX typography (Computer Modern), not school clipart.\n\n"
        "DESIGNS\n"
        "1. Euler Field — dark constellation of formulas with hero identity e^{iπ}+1=0\n"
        "2. Fourier Wave — square wave reconstructed from odd harmonics (partial sums)\n"
        "3. Julia Set — complex dynamics z_{n+1}=z_n²+c with iteration formula\n\n"
        "SPECS\n"
        "• PNG @ 300 DPI\n"
        "• 9.3 × 8.2 inches (20oz skinny straight)\n"
        "• Instant download — digital files only (no physical tumbler)\n\n"
        "Print with sublimation or your POD provider. Resize only if your blank requires it.\n\n"
        "For personal use and POD physical products you sell. Do not resell or redistribute the digital files."
    )

    images = []
    for name in ["01_hero.jpg", "02_detail_euler.jpg", "03_detail_fourier.jpg",
                 "04_detail_julia.jpg", "preview_euler_field.jpg", "preview_fourier_wave.jpg",
                 "preview_complex_plane.jpg", "05_specs.jpg"]:
        p = PREVIEWS / name
        if p.exists():
            images.append(p)

    m = EtsyManager()
    shop = m.get_shop_id()

    if replace_listing_id:
        lid = replace_listing_id
        print(f"Updating existing listing {lid}…")
        m.update_listing(lid, title=title, description=desc, tags=tags)
        # upload new images
        for i, p in enumerate(images, 1):
            m.upload_listing_image(lid, str(p), rank=i)
            time.sleep(0.25)
        # prune extras
        imgs = m.make_request("GET", f"/listings/{lid}/images")
        results = imgs.get("results") or []
        keep = set()
        by_rank = {}
        for im in results:
            by_rank.setdefault(im.get("rank") or 0, []).append(im)
        for r in range(1, len(images) + 1):
            group = sorted(by_rank.get(r) or [], key=lambda x: x.get("listing_image_id") or 0, reverse=True)
            if group:
                keep.add(group[0]["listing_image_id"])
        for im in results:
            iid = im.get("listing_image_id")
            if iid not in keep:
                try:
                    m.make_request("DELETE", f"/shops/{shop}/listings/{lid}/images/{iid}")
                except Exception as e:
                    print("skip del img", e)
        # file
        try:
            files = m.make_request("GET", f"/shops/{shop}/listings/{lid}/files")
            for f in files.get("results") or []:
                fid = f.get("listing_file_id")
                if fid:
                    try:
                        m.make_request("DELETE", f"/shops/{shop}/listings/{lid}/files/{fid}")
                    except Exception as e:
                        print("skip del file", e)
        except Exception as e:
            print("files", e)
        m.upload_listing_file(lid, str(zpath))
        print("updated listing", lid)
        return lid

    lid = m.create_full_product(
        title=title,
        description=desc,
        price=4.99,
        taxonomy_id=77,
        image_paths=[str(p) for p in images],
        digital_file_paths=[str(zpath)],
        tags=tags,
    )
    print("listing_id", lid)
    return lid


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--upload", action="store_true")
    ap.add_argument("--new-listing", action="store_true", help="Create new draft instead of updating 4543860690")
    args = ap.parse_args()
    paths = render_all()
    build_previews(paths)
    zpath = build_zip(paths)
    if args.upload:
        upload_draft(zpath, replace_listing_id=None if args.new_listing else 4543860690)
    print("DONE ->", OUT)


if __name__ == "__main__":
    main()
