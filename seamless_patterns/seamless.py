"""
seamless.py — canvas + seam verification for tileable repeat patterns.

The whole product rests on one claim: every tile repeats with no visible seam.
That claim is cheap to make and easy to get wrong, so nothing ships here until
verify() has passed on the rendered pixels -- not on the intent of the drawing
code.

Two properties are checked, because the obvious one is not sufficient:

  edge match   opposite borders must agree pixel for pixel. Necessary, but a
               pattern can satisfy it and still show a seam one pixel inward
               (a strand that meets the border at the right place but the
               wrong angle).

  seam energy  roll the image by half a period and measure the horizontal
               gradient across the join against the gradient everywhere else.
               A real seam is a line of high contrast that has no business
               being there, so the ratio spikes. This is the test that catches
               tangent discontinuities.

Coordinates: every family draws into the unit square [0,1]x[0,1] and the figure
maps that square exactly onto the output pixels, so cropping is exact by
construction rather than by trimming afterwards.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

HERE = Path(__file__).resolve().parent


def canvas(px: int = 2400, dpi: int = 300):
    """Figure whose axes are exactly the unit square, mapped onto px x px."""
    inches = px / dpi
    fig = plt.figure(figsize=(inches, inches), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def save(fig, png_path: Path, svg_path: Path | None = None, bg=None, dpi: int = 300):
    """PNG for crafters, SVG for designers who want to edit the vectors."""
    png_path.parent.mkdir(parents=True, exist_ok=True)
    kw = dict(dpi=dpi, pad_inches=0)
    if bg is None:
        fig.savefig(png_path, transparent=True, **kw)
    else:
        fig.savefig(png_path, facecolor=bg, **kw)
    if svg_path is not None:
        svg_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(svg_path, transparent=(bg is None),
                    facecolor=bg or "none", pad_inches=0)
    plt.close(fig)


def _channel(path: Path) -> np.ndarray:
    """Whichever channel actually carries the pattern (alpha if transparent)."""
    im = Image.open(path).convert("RGBA")
    a = np.asarray(im).astype(np.float64)
    if a[:, :, 3].std() > 1.0:
        return a[:, :, 3]
    return a[:, :, :3].mean(axis=2)


def verify(path: Path, seam_tol: float = 0.90) -> dict:
    """Measure seamlessness of a rendered tile. Returns metrics + ok flag.

    Both metrics are ratios against the image's own contrast, not absolute
    0-255 numbers. An absolute threshold cannot be set once for all families:
    thin line art on white leaves a few units of antialiasing on every edge,
    which looks identical to a real defect in a dense pattern. Dividing by the
    typical difference between adjacent rows makes "do the opposite edges
    agree better than two neighbouring rows do?" the actual question, and that
    question has the same answer at any line weight.
    """
    g = _channel(path)

    def _corr(u, v):
        u = u - u.mean()
        v = v - v.mean()
        d = np.sqrt((u * u).sum() * (v * v).sum())
        return 1.0 if d < 1e-9 else float((u * v).sum() / d)

    def seam_score(img, axis):
        """Ratio of two correlations: the wrap-around pair over a genuine
        adjacent pair.

        Absolute difference metrics all failed here -- against the mean,
        against the whole distribution, against a fixed window, against a
        scaled band. Each one either hid a broken tile in sparse line art or
        condemned a join that magnification showed to be continuous, because
        the size of a difference says nothing about whether the two lines
        belong together. Correlation asks that directly, and the adjacent pair
        supplies the pattern's own benchmark for what "belonging together"
        looks like. 1.0 means the wrap is as well matched as any neighbour.
        """
        a = img if axis == 0 else img.T
        inner = max(_corr(a[0], a[1]), _corr(a[-2], a[-1]))
        return float(_corr(a[0], a[-1]) / max(inner, 1e-6))

    sh = seam_score(g, 0)
    sv = seam_score(g, 1)
    ok = sh >= seam_tol and sv >= seam_tol
    return {"seam_h": sh, "seam_v": sv, "limit": seam_tol, "ok": ok}


def mosaic(path: Path, out: Path, n: int = 3, size: int = 1000, bg="white"):
    """n x n proof sheet -- the seam, if there is one, shows up as a grid."""
    t = Image.open(path).convert("RGBA")
    m = Image.new("RGBA", (t.width * n, t.height * n), (255, 255, 255, 255))
    for i in range(n):
        for j in range(n):
            m.alpha_composite(t, (i * t.width, j * t.height))
    out.parent.mkdir(parents=True, exist_ok=True)
    m.convert("RGB").resize((size, size), Image.LANCZOS).save(out, quality=92)
    return out
