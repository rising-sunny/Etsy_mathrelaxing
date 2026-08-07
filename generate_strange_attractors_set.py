"""
generate_strange_attractors_set.py — Strange Attractors Poster Set of 6
=======================================================================
Dark-observatory scientific plates. Strict zones (same family as
physics_formula_set) so titles, captions and equations never collide with the
attractor ink:

  HEADER  | GRAPH (full-bleed attractor on panel) | CAPTION | FOOTER eqs

Attractors: Lorenz, Rössler, Thomas, Halvorsen, Chen, Aizawa.

  python generate_strange_attractors_set.py
  python generate_strange_attractors_set.py --preview-only
  python generate_strange_attractors_set.py --only lorenz,rossler
"""
from __future__ import annotations

import argparse
import zipfile
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle
import numpy as np
from scipy.integrate import odeint
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
OUT = BASE / "special_plates" / "strange_attractors_set"

BG = "#0a0c12"
PANEL = "#0e1118"
LINE = "#2b3242"
INK = "#e9ecf5"
SUB = "#828aa0"
MUTED = "#5c6478"
ACC = "#6fc9d8"
GOLD = "#e8c98a"

DPI_PRINT = 300
DPI_PREVIEW = 140
SIZES = {
    "2x3": (12.0, 18.0),
    "3x4": (12.0, 16.0),
    "4x5": (16.0, 20.0),
    "5x7": (10.0, 14.0),
    "A4": (8.27, 11.69),
    "A3": (11.69, 16.54),
}

SANS = font_manager.FontProperties(family="DejaVu Sans")
SERIF = font_manager.FontProperties(family="DejaVu Serif")
plt.rcParams["mathtext.fontset"] = "cm"
plt.rcParams["mathtext.rm"] = "serif"
plt.rcParams["axes.unicode_minus"] = False

# Custom gradient: deep navy → cyan → soft gold
_CMAP = LinearSegmentedColormap.from_list(
    "attractor_obs",
    ["#0a0c12", "#1a2744", "#2d5a7b", "#6fc9d8", "#c8e8f0", "#e8c98a"],
    N=256,
)

Z_GRAPH_BOT = 0.28
Z_GRAPH_TOP = 0.82


def _fs(fig_w: float, frac: float) -> float:
    return max(6.5, fig_w * 72 * frac)


def _new_fig(w: float, h: float, dpi: int):
    fig = plt.figure(figsize=(w, h), dpi=dpi, facecolor=BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_axis_off()
    ax.set_facecolor(BG)
    ax.add_patch(
        Rectangle((0.035, 0.028), 0.93, 0.944, fill=False, edgecolor=LINE, lw=0.9, zorder=2)
    )
    for (x0, y0, dx, dy) in (
        (0.035, 0.028, 0.025, 0),
        (0.035, 0.028, 0, 0.02),
        (0.965, 0.028, -0.025, 0),
        (0.965, 0.028, 0, 0.02),
        (0.035, 0.972, 0.025, 0),
        (0.035, 0.972, 0, -0.02),
        (0.965, 0.972, -0.025, 0),
        (0.965, 0.972, 0, -0.02),
    ):
        ax.plot([x0, x0 + dx], [y0, y0 + dy], color=GOLD, lw=1.0, solid_capstyle="butt", zorder=3)
    return fig, ax


def _header(ax, title: str, fig_label: str, subtitle: str, fig_w: float):
    ax.text(0.06, 0.945, title.upper(), fontproperties=SANS, fontsize=_fs(fig_w, 0.028),
            color=INK, ha="left", va="center", zorder=5)
    ax.text(0.94, 0.945, fig_label, fontproperties=SANS, fontsize=_fs(fig_w, 0.012),
            color=MUTED, ha="right", va="center", zorder=5)
    ax.text(0.06, 0.905, subtitle, fontproperties=SERIF, fontsize=_fs(fig_w, 0.011),
            color=GOLD, ha="left", va="center", zorder=5, style="italic")
    ax.plot([0.06, 0.94], [0.875, 0.875], color=LINE, lw=0.85, zorder=4)


def _caption(ax, text: str, fig_w: float):
    ax.text(0.06, 0.235, text, fontproperties=SANS, fontsize=_fs(fig_w, 0.009),
            color=SUB, ha="left", va="top", zorder=5, linespacing=1.45)


def _footer_eqs(ax, items: list[tuple[str, str]], fig_w: float):
    n = min(3, len(items))
    xs = [0.06, 0.50, 0.94] if n == 3 else ([0.06, 0.94] if n == 2 else [0.50])
    has = ["left", "center", "right"] if n == 3 else (["left", "right"] if n == 2 else ["center"])
    for i in range(n):
        eq, lab = items[i]
        ax.text(xs[i], 0.125, eq, fontsize=_fs(fig_w, 0.0125 if has[i] == "center" else 0.0115),
                color=INK if has[i] == "center" else (ACC if has[i] == "right" else SUB),
                ha=has[i], va="center", zorder=5)
        ax.text(xs[i], 0.078, lab, fontproperties=SANS, fontsize=_fs(fig_w, 0.0076),
                color=MUTED, ha=has[i], va="center", zorder=5)


def fig_to_image(fig) -> Image.Image:
    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba())
    img = Image.fromarray(buf[:, :, :3].copy(), "RGB")
    plt.close(fig)
    return img


def save_rgb(img: Image.Image, path: Path, dpi: int = DPI_PRINT, quality: int = 91):
    path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(
        str(path), "JPEG", quality=quality, optimize=True, progressive=True, dpi=(dpi, dpi)
    )
    print(f"  wrote {path.name}  ({path.stat().st_size / 1024:.0f} KB)")


# ── Trajectory engine ─────────────────────────────────────────────────────────

def _integrate(deriv, s0, tmax, n):
    t = np.linspace(0, tmax, n)
    return odeint(deriv, s0, t, atol=1e-8, rtol=1e-7)


def _draw_trajectory(a, x, y, lw=0.42, n_skip=0):
    """Gradient line collection; dense points, no axis labels overlapping ink."""
    if n_skip:
        x, y = x[n_skip:], y[n_skip:]
    # denser line for visual mass (cap ~25k segments)
    step = max(1, len(x) // 25000)
    x, y = x[::step], y[::step]
    pts = np.array([x, y]).T.reshape(-1, 1, 2)
    segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
    lc = LineCollection(
        segs,
        cmap=_CMAP,
        linewidths=lw,
        alpha=0.92,
        antialiased=True,
        capstyle="round",
        joinstyle="round",
    )
    lc.set_array(np.linspace(0, 1, len(segs)))
    a.add_collection(lc)
    pad_x = (x.max() - x.min()) * 0.08
    pad_y = (y.max() - y.min()) * 0.08
    a.set_xlim(x.min() - pad_x, x.max() + pad_x)
    a.set_ylim(y.min() - pad_y, y.max() + pad_y)
    a.set_aspect("equal", adjustable="datalim")
    a.set_xticks([])
    a.set_yticks([])
    for sp in a.spines.values():
        sp.set_visible(False)
    a.set_facecolor(PANEL)


def _graph_axes(fig):
    a = fig.add_axes([0.08, Z_GRAPH_BOT, 0.84, Z_GRAPH_TOP - Z_GRAPH_BOT], zorder=3)
    a.set_facecolor(PANEL)
    return a


def _compose_attractor(
    w, h, dpi, title, fig_label, subtitle, caption, footer_items, traj_fn
):
    fig, ax = _new_fig(w, h, dpi)
    _header(ax, title, fig_label, subtitle, w)
    a = _graph_axes(fig)
    x, y = traj_fn()
    _draw_trajectory(a, x, y)
    _caption(ax, caption, w)
    _footer_eqs(ax, footer_items, w)
    return fig_to_image(fig)


# ── Six attractors ────────────────────────────────────────────────────────────

def traj_lorenz():
    def f(s, t):
        x, y, z = s
        return [10 * (y - x), x * (28 - z) - y, x * y - (8 / 3) * z]

    s = _integrate(f, [1.0, 1.0, 1.0], 80, 50000)
    # drop transient
    return s[2000:, 0], s[2000:, 2]


def traj_rossler():
    def f(s, t):
        x, y, z = s
        return [-y - z, x + 0.2 * y, 0.2 + z * (x - 5.7)]

    s = _integrate(f, [0.1, 0.0, 0.0], 350, 60000)
    return s[3000:, 0], s[3000:, 1]


def traj_thomas():
    b = 0.208
    def f(s, t):
        x, y, z = s
        return [np.sin(y) - b * x, np.sin(z) - b * y, np.sin(x) - b * z]

    s = _integrate(f, [1.1, 1.1, -0.01], 400, 70000)
    return s[5000:, 0], s[5000:, 1]


def traj_fourwing():
    """Four-wing attractor — denser than Halvorsen for gallery plates."""
    def f(s, t):
        x, y, z = s
        return [
            0.2 * x + y * z,
            -0.01 * x - 0.4 * y - x * z,
            -z - x * y,
        ]

    s = _integrate(f, [1.0, 0.0, -1.0], 350, 90000)
    return s[4000:, 0], s[4000:, 2]


def traj_chen():
    def f(s, t):
        x, y, z = s
        return [35 * (y - x), -7 * x - x * z + 28 * y, x * y - 3 * z]

    s = _integrate(f, [-10.0, 0.0, 37.0], 50, 60000)
    return s[1500:, 0], s[1500:, 2]


def traj_aizawa():
    a, b, c, d, e, f = 0.95, 0.7, 0.6, 3.5, 0.25, 0.1
    def dv(s, t):
        x, y, z = s
        return [
            (z - b) * x - d * y,
            d * x + (z - b) * y,
            c + a * z - z**3 / 3 - (x**2 + y**2) * (1 + e * z) + f * z * x**3,
        ]

    s = _integrate(dv, [0.1, 0.0, 0.0], 150, 80000)
    return s[3000:, 0], s[3000:, 2]


def compose_lorenz(w, h, dpi):
    return _compose_attractor(
        w, h, dpi,
        "Lorenz",
        "FIG. 01",
        "Deterministic chaos  ·  $\\sigma=10,\\;\\rho=28,\\;\\beta=8/3$",
        "The butterfly of convection. Tiny changes in initial state diverge,\n"
        "yet the orbit stays on a compact strange attractor in phase space.",
        [
            (r"$\dot x=\sigma(y-x)$", "convection"),
            (r"$\dot y=x(\rho-z)-y$", "temperature"),
            (r"$\dot z=xy-\beta z$", "profile"),
        ],
        traj_lorenz,
    )


def compose_rossler(w, h, dpi):
    return _compose_attractor(
        w, h, dpi,
        "Rössler",
        "FIG. 02",
        "Minimal continuous chaos  ·  $a=b=0.2,\\;c=5.7$",
        "Only one nonlinear term, yet a spiral fold creates chaos.\n"
        "A geometric sketch of stretching and folding in three dimensions.",
        [
            (r"$\dot x=-y-z$", ""),
            (r"$\dot y=x+ay$", "linear spiral"),
            (r"$\dot z=b+z(x-c)$", "fold"),
        ],
        traj_rossler,
    )


def compose_thomas(w, h, dpi):
    return _compose_attractor(
        w, h, dpi,
        "Thomas",
        "FIG. 03",
        "Cyclically symmetric labyrinth  ·  $b=0.208$",
        "Sine coupling on a cycle of three variables builds a symmetric cloud.\n"
        "Friction $b$ tunes the density of the strange orbit.",
        [
            (r"$\dot x=\sin y - bx$", ""),
            (r"$\dot y=\sin z - by$", "cyclic"),
            (r"$\dot z=\sin x - bz$", ""),
        ],
        traj_thomas,
    )


def compose_fourwing(w, h, dpi):
    return _compose_attractor(
        w, h, dpi,
        "Four-Wing",
        "FIG. 04",
        "Multi-scroll quadratic chaos",
        "A four-wing structure from bilinear products of state variables.\n"
        "Visually richer than many textbook 3-D systems — pure gallery chaos.",
        [
            (r"$\dot x=0.2x+yz$", ""),
            (r"$\dot y=-0.01x-0.4y-xz$", "four-wing"),
            (r"$\dot z=-z-xy$", ""),
        ],
        traj_fourwing,
    )


def compose_chen(w, h, dpi):
    return _compose_attractor(
        w, h, dpi,
        "Chen",
        "FIG. 05",
        "Dual-wing chaos related to Lorenz  ·  $a=35,\\;b=3,\\;c=28$",
        "Topologically distinct from Lorenz, yet born of similar quadratic terms.\n"
        "A dual-wing structure for the gallery of dissipative flows.",
        [
            (r"$\dot x=a(y-x)$", ""),
            (r"$\dot y=(c-a)x-xz+cy$", "Chen system"),
            (r"$\dot z=xy-bz$", ""),
        ],
        traj_chen,
    )


def compose_aizawa(w, h, dpi):
    return _compose_attractor(
        w, h, dpi,
        "Aizawa",
        "FIG. 06",
        "Sphere-like strange attractor  ·  classic parameters",
        "A soft, nearly spherical cloud of chaos — denser near the equator,\n"
        "with a delicate vertical structure unique among textbook attractors.",
        [
            (r"$\dot x=(z-b)x-dy$", ""),
            (r"$\dot y=dx+(z-b)y$", "Aizawa"),
            (r"$\dot z=c+az-z^{3}/3-\cdots$", "nonlinear $z$"),
        ],
        traj_aizawa,
    )


@dataclass
class Plate:
    slug: str
    title: str
    compose: callable


PLATES = [
    Plate("lorenz", "Lorenz", compose_lorenz),
    Plate("rossler", "Rossler", compose_rossler),
    Plate("thomas", "Thomas", compose_thomas),
    Plate("fourwing", "Four-Wing", compose_fourwing),
    Plate("chen", "Chen", compose_chen),
    Plate("aizawa", "Aizawa", compose_aizawa),
]


def render_plate(plate: Plate, size_name: str, dpi: int) -> Image.Image:
    w, h = SIZES[size_name]
    return plate.compose(w, h, dpi)


def build_prints(only: set[str] | None, preview_only: bool):
    prints_dir = OUT / "prints"
    previews_dir = OUT / "previews"
    prints_dir.mkdir(parents=True, exist_ok=True)
    previews_dir.mkdir(parents=True, exist_ok=True)
    plates = [p for p in PLATES if only is None or p.slug in only]
    print_paths: list[Path] = []
    for plate in plates:
        print(f"\n=== {plate.slug} ===")
        if not preview_only:
            for size in ("2x3", "A4"):
                img = render_plate(plate, size, DPI_PRINT)
                path = prints_dir / f"{plate.slug}_{size}_300dpi.jpg"
                save_rgb(img, path, DPI_PRINT)
                print_paths.append(path)
        img = render_plate(plate, "2x3", DPI_PREVIEW)
        save_rgb(img, previews_dir / f"{plate.slug}_plate.jpg", DPI_PREVIEW, quality=88)
    return plates, print_paths


def build_set_previews(plates: list[Plate]):
    prev = OUT / "previews"
    plate_imgs = []
    for p in plates:
        path = prev / f"{p.slug}_plate.jpg"
        if path.is_file():
            plate_imgs.append(Image.open(path).convert("RGB"))

    W = H = 2000
    canvas = Image.new("RGB", (W, H), (10, 12, 18))
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 50)
        font_s = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 26)
    except Exception:
        font = ImageFont.load_default()
        font_s = font
    draw.rectangle([0, 0, W, 210], fill=(8, 10, 16))
    draw.text((W // 2, 70), "STRANGE ATTRACTORS", fill=(233, 236, 245), font=font, anchor="mt")
    draw.text((W // 2, 140), "Set of 6  ·  chaos theory wall art  ·  MathRelaxing",
              fill=(140, 150, 175), font=font_s, anchor="mt")

    cols, rows = 3, 2
    pad = 28
    top = 240
    gw = (W - pad * (cols + 1)) // cols
    gh = (H - top - pad * (rows + 1)) // rows
    for i, im in enumerate(plate_imgs[:6]):
        r, c = divmod(i, cols)
        x = pad + c * (gw + pad)
        y = top + pad + r * (gh + pad)
        thumb = im.copy()
        thumb.thumbnail((gw, gh), Image.Resampling.LANCZOS)
        canvas.paste(thumb, (x + (gw - thumb.width) // 2, y + (gh - thumb.height) // 2))
    hero = prev / "strange_attractors_preview_1_hero.jpg"
    canvas.save(hero, quality=90)
    print(f"  wrote {hero.name}")

    card = Image.new("RGB", (2000, 2000), (245, 242, 235))
    d = ImageDraw.Draw(card)
    d.text((100, 90), "What's included", fill=(20, 24, 36), font=font)
    lines = [
        "1. Lorenz — the classic butterfly",
        "2. Rössler — minimal continuous chaos",
        "3. Thomas — cyclic sine labyrinth",
        "4. Four-Wing — multi-scroll chaos",
        "5. Chen — dual-wing dissipative flow",
        "6. Aizawa — sphere-like strange cloud",
        "",
        "Each plate: multi-ratio prints @ 300 dpi",
        "Dark observatory aesthetic · ODE trajectories",
        "Set price: $12.99",
    ]
    y = 220
    for line in lines:
        d.text((120, y), line, fill=(40, 44, 58), font=font_s)
        y += 58
    included = prev / "strange_attractors_preview_2_included.jpg"
    card.save(included, quality=90)
    print(f"  wrote {included.name}")

    for i, im in enumerate(plate_imgs[:4], start=3):
        tw, th = im.size
        side = min(tw, int(th * 0.55))
        left = (tw - side) // 2
        topc = int(th * 0.28)
        crop = im.crop((left, topc, left + side, min(topc + side, th)))
        crop = crop.resize((1600, 1600), Image.Resampling.LANCZOS)
        path = prev / f"strange_attractors_preview_{i}_eq.jpg"
        crop.save(path, quality=90)
        print(f"  wrote {path.name}")


def build_zip(print_paths: list[Path]):
    zpath = OUT / "Strange_Attractors_Poster_Set_of_6.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "README.txt",
            "MathRelaxing — Strange Attractors Poster Set of 6\n"
            "Print-ready JPG @ 300 dpi (2x3 and A4 per design).\n"
            "Personal use only.\nhttps://www.etsy.com/shop/TheMathRelaxing\n",
        )
        for p in print_paths:
            zf.write(p, f"prints/{p.name}")
    print(f"\nZIP {zpath.name} ({zpath.stat().st_size / 1024:.0f} KB)")
    return zpath


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview-only", action="store_true")
    ap.add_argument("--only", type=str, default="")
    args = ap.parse_args()
    only = {s.strip() for s in args.only.split(",") if s.strip()} or None

    print("Strange Attractors Set — dark observatory plates")
    plates, print_paths = build_prints(only, args.preview_only)
    build_set_previews(plates if only is None else plates)
    if not args.preview_only and print_paths:
        # if --only, still zip whatever prints exist on disk for full set
        all_prints = sorted((OUT / "prints").glob("*_300dpi.jpg"))
        build_zip(all_prints if all_prints else print_paths)
    print("\nDone →", OUT)


if __name__ == "__main__":
    main()
