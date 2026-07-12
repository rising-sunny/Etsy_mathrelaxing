"""
build_lowpoly_svg_previews.py — listing previews + promo video for Geometric CBN SVG
"""
import math
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.collections import PolyCollection

import brand
from build_lowpoly_ipad_svg import get_polygons, CFG

OUT_DIR = CFG.out_dir
PREVIEWS_DIR = os.path.join(OUT_DIR, "previews")
os.makedirs(PREVIEWS_DIR, exist_ok=True)


def get_cells(n, reverse_sort=True, fill_order="spiral"):
    """
    fill_order:
      'spiral'  — angle then radius (pretty radial reveal for video)
      'radial'  — outside-in / inside-out via dist
    """
    result = get_polygons(n)
    cells = result["cells"]
    palette = result["palette"]
    if fill_order == "spiral":
        def key(c):
            # representative point via poly centroid
            p = c["poly"].representative_point()
            ang = math.atan2(p.y, p.x)
            return (round(c.get("dist", 0) * 40) / 40.0, ang)
        cells = sorted(cells, key=key, reverse=reverse_sort)
    else:
        cells = sorted(cells, key=lambda c: c.get("dist", 0), reverse=reverse_sort)
    R_out = max((c.get("dist", 0) for c in cells), default=0.5) or 0.5
    return cells, R_out, palette


def draw_palette(ax, x, y, w, h, palette, active_idx=None):
    ax.add_patch(plt.Rectangle((x, y), w, h, color="#1A1D24", zorder=10))
    n_colors = len(palette)
    swatch_w = min((w - 0.2) / max(n_colors, 1), h * 0.8)
    padding = (w - n_colors * swatch_w) / 2
    for i, color in enumerate(palette):
        cx = x + padding + i * swatch_w + swatch_w / 2
        cy = y + h / 2
        r = swatch_w * (0.46 if active_idx == i else 0.38)
        ax.add_patch(plt.Circle((cx, cy), r, color=color, zorder=11,
                                ec="white", lw=1.2 if active_idx == i else 0.4))
        ax.text(cx, cy, str(i + 1), ha="center", va="center", fontsize=7,
                color="#1A1D24", zorder=12, **brand.SANS)


def draw_design(ax, cells, R_out, colored_count, cx, cy, w, h, palette,
                zoom=1.0, show_numbers=True, lw=0.35):
    scale = (min(w, h) / (2 * R_out)) * zoom * 0.92
    clip_rect = Rectangle((cx - w / 2, cy - h / 2), w, h, transform=ax.transData)

    verts, facecolors = [], []
    number_pts = []  # (x, y, label, fs) only if show_numbers

    for i, cell in enumerate(cells):
        is_colored = i < colored_count
        c_idx = cell["color_idx"] % len(palette)
        color = palette[c_idx] if is_colored else "white"

        geoms = ([cell["poly"]] if cell["poly"].geom_type == "Polygon"
                 else list(cell["poly"].geoms))
        for g in geoms:
            coords = list(g.exterior.coords)
            verts.append([(cx + x * scale, cy - y * scale) for x, y in coords])
            facecolors.append(color)

            if show_numbers and not is_colored:
                pt = g.representative_point()
                clearance = g.boundary.distance(pt)
                fs = max(2.5, min(11.0, clearance * scale * 72 * 0.9))
                number_pts.append((cx + pt.x * scale, cy - pt.y * scale, str(c_idx + 1), fs))

    coll = PolyCollection(
        verts, facecolors=facecolors, edgecolors="#1A1D24",
        linewidths=lw, zorder=3,
    )
    coll.set_clip_path(clip_rect)
    ax.add_collection(coll)

    for x, y, label, fs in number_pts:
        t = ax.text(x, y, label, ha="center", va="center", fontsize=fs,
                    color="#555555", zorder=4, **brand.SANS)
        t.set_clip_path(clip_rect)


def build_preview_1():
    fig, ax = brand.ipad_fig()
    cells, R_out, palette = get_cells(1)
    colored = int(len(cells) * 0.42)

    scr_x, scr_y, scr_w, scr_h = brand.ipad_frame(ax, 5, 5, 8, 6)
    draw_design(ax, cells, R_out, colored,
                scr_x + scr_w / 2, scr_y + scr_h / 2 + 0.25, scr_w, scr_h - 0.55,
                palette)
    draw_palette(ax, scr_x, scr_y, scr_w, 0.55, palette)

    ax.text(5, 9.2, "Geometric Color by Number", ha="center", va="center",
            fontsize=42, color=brand.CREAM, **brand.SERIF_BOLD)
    ax.text(5, 8.55, "Interactive SVG · Tap to Color on iPad", ha="center",
            va="center", fontsize=24, color=brand.GOLD, **brand.SERIF)
    brand.footer_band(ax, 10, 1.5)

    out = os.path.join(PREVIEWS_DIR, "ipad_svg_preview_1_hero.jpg")
    fig.savefig(out, dpi=100)
    plt.close(fig)
    print("Generated", out)


def build_preview_2():
    fig, ax = brand.ipad_fig()
    cells, R_out, palette = get_cells(12)

    scr_x, scr_y, scr_w, scr_h = brand.ipad_frame(ax, 7.5, 4.5, 4, 3)
    draw_design(ax, cells, R_out, int(len(cells) * 0.75),
                scr_x + scr_w / 2, scr_y + scr_h / 2 + 0.25, scr_w, scr_h - 0.55,
                palette)
    draw_palette(ax, scr_x, scr_y, scr_w, 0.55, palette)

    ax.text(5, 9.2, "How It Works", ha="center", va="center",
            fontsize=50, color=brand.CREAM, **brand.SERIF_BOLD)

    features = [
        (7.0, "1. Select a Color", "Tap a numbered swatch on the palette"),
        (5.0, "2. Tap to Fill", "Tap any matching polygon — it fills instantly"),
        (3.0, "3. Zoom Forever", "True SVG vectors — crisp at any zoom"),
    ]
    for y, title, desc in features:
        ax.text(1.3, y, title, ha="left", va="bottom", fontsize=26,
                color=brand.GOLD, **brand.SERIF_BOLD)
        ax.text(1.3, y - 0.4, desc, ha="left", va="top", fontsize=16,
                color=brand.CREAM, **brand.SERIF)

    brand.footer_band(ax, 10, 1.5)
    out = os.path.join(PREVIEWS_DIR, "ipad_svg_preview_2_features.jpg")
    fig.savefig(out, dpi=100)
    plt.close(fig)
    print("Generated", out)


def build_preview_3():
    fig, ax = brand.ipad_fig()
    cells1, R1, p1 = get_cells(1)
    cells2, R2, p2 = get_cells(13)
    cells3, R3, p3 = get_cells(18)

    ax.text(5, 9.0, "What's Included", ha="center", va="center",
            fontsize=45, color=brand.CREAM, **brand.SERIF_BOLD)

    for x, cells, R, pal in [
        (2, cells1, R1, p1),
        (5, cells2, R2, p2),
        (8, cells3, R3, p3),
    ]:
        cx, cy, cw, ch = brand.ipad_frame(ax, x, 6.5, 3.5, 2.6)
        draw_design(ax, cells, R, len(cells), cx + cw / 2, cy + ch / 2, cw, ch, pal)

    items = [
        f"{CFG.n_designs} Interactive Designs",
        "Domain colorings · Newton · Julia",
        "Infinite SVG Zoom",
        "Auto-Save Progress Offline",
        "Safari on iPad (no app)",
        "Instructions PDF included",
    ]
    for i, item in enumerate(items):
        y = 4.5 - i * 0.5
        ax.text(2.3, y, "•", ha="right", va="center", fontsize=24,
                color=brand.GOLD, **brand.SERIF_BOLD)
        ax.text(2.7, y, item, ha="left", va="center", fontsize=22,
                color=brand.CREAM, **brand.SERIF)

    brand.footer_band(ax, 10, 1.5)
    out = os.path.join(PREVIEWS_DIR, "ipad_svg_preview_3_included.jpg")
    fig.savefig(out, dpi=100)
    plt.close(fig)
    print("Generated", out)


def _ease_out_cubic(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1.0 - (1.0 - t) ** 3


def _ease_in_out(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 3 * t * t - 2 * t * t * t


def build_promo_video(design_n=13, fps=30):
    """
    Promo: start zoomed-in on blank numbered design, then colour polygons
    one-by-one while slowly zooming out until the full mosaic is revealed.

    design_n=13 is Newton Basins z^4-1 — crisp colour regions, great on camera.
    """
    frames_dir = os.path.join(OUT_DIR, "promo_frames")
    os.makedirs(frames_dir, exist_ok=True)

    # Spiral order, outside-in feels like the image "builds" toward the centre
    cells, R_out, palette = get_cells(design_n, reverse_sort=True, fill_order="spiral")
    n_cells = len(cells)
    print(f"Promo design #{design_n}: {n_cells} polygons, {len(palette)} colors")

    # Timeline (seconds @ 30fps ≈ 9.3 s total — Etsy-friendly)
    #  0.0–0.7s  hold zoomed-in, uncolored (read the grid)
    #  0.7–7.5s  color + zoom-out
    #  7.5–9.3s  hold full color wide
    hold_in = int(0.7 * fps)
    color_span = int(6.8 * fps)
    hold_out = int(1.8 * fps)
    n_frames = hold_in + color_span + hold_out

    zoom_start = 3.4
    zoom_end = 1.0

    print(f"Generating {n_frames} frames @ {fps} fps "
          f"({n_frames / fps:.1f}s)...")

    for f in range(n_frames):
        if f < hold_in:
            progress = 0.0
            zoom = zoom_start
            colored = 0
        elif f < hold_in + color_span:
            t = (f - hold_in) / max(1, color_span - 1)
            # Soft ease so early frames linger on detail, then accelerate out
            progress = _ease_in_out(t)
            zoom = zoom_start + (zoom_end - zoom_start) * _ease_out_cubic(t)
            # Nearly one-by-one: map progress → cell count with slight lead
            colored = int(round(progress * n_cells))
            colored = max(0, min(n_cells, colored))
        else:
            progress = 1.0
            zoom = zoom_end
            colored = n_cells

        # Active palette swatch = colour of the most recently filled cell
        active_idx = None
        if 0 < colored <= n_cells:
            active_idx = cells[colored - 1]["color_idx"] % len(palette)

        fig, ax = plt.subplots(figsize=(10, 10))
        ax.axis("off")
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        fig.patch.set_facecolor(brand.IPAD_NAVY)
        ax.set_facecolor(brand.IPAD_NAVY)

        scr_x, scr_y, scr_w, scr_h = brand.ipad_frame(ax, 5, 5.05, 8.2, 6.2)
        # No numbers during video — cleaner + much faster to render
        draw_design(
            ax, cells, R_out, colored,
            scr_x + scr_w / 2, scr_y + scr_h / 2 + 0.22,
            scr_w, scr_h - 0.5, palette,
            zoom=zoom, show_numbers=False, lw=0.28,
        )
        draw_palette(ax, scr_x, scr_y, scr_w, 0.52, palette, active_idx=active_idx)

        ax.text(5, 9.15, "Geometric Color by Number", ha="center", va="center",
                fontsize=36, color=brand.CREAM, **brand.SERIF_BOLD)
        ax.text(5, 8.55, "Interactive SVG · Tap to Color on iPad", ha="center",
                va="center", fontsize=20, color=brand.GOLD, **brand.SERIF)

        brand.footer_band(ax, 10, 1.4)

        out = os.path.join(frames_dir, f"f_{f:04d}.png")
        fig.savefig(out, dpi=100)
        plt.close(fig)

        if f % 15 == 0 or f == n_frames - 1:
            print(f"  frame {f + 1}/{n_frames}  "
                  f"colored={colored}/{n_cells}  zoom={zoom:.2f}")

    out_video = os.path.join(OUT_DIR, "GeometricCBN_SVG_promo.mp4")
    print(f"Encoding {out_video}...")
    brand.encode_mp4(frames_dir, out_video, fps=fps, cleanup=True)
    size_mb = os.path.getsize(out_video) / (1024 * 1024)
    print(f"Video ready: {out_video} ({size_mb:.1f} MB)")
    return out_video


if __name__ == "__main__":
    import sys
    only_video = "--video" in sys.argv
    if not only_video:
        print("Building Geometric CBN SVG previews...")
        build_preview_1()
        build_preview_2()
        build_preview_3()
        print("Done ->", PREVIEWS_DIR)
    print("Building promo video...")
    build_promo_video()

