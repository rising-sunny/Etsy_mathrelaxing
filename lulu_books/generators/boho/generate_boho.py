"""Boho / mid-century abstract botanical wall art — generated with math.
Print-ready 2:3 panels. Palette-driven. Primitives: parametric leaf, curved
branch, concentric arches, discs, diamond, thin ring."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.dirname(os.path.abspath(__file__))
LW = 2.2

PALETTES = {
    "blue":    dict(bg="#efe9dc", fill="#5f6e8e", fill2="#8b96ac", ink="#39465e"),
    "terra":   dict(bg="#f4ecdf", fill="#c0674a", fill2="#d89b83", ink="#5a3526"),
    "sage":    dict(bg="#eaece0", fill="#879578", fill2="#a9b39a", ink="#3c4636"),
    "mustard": dict(bg="#f4ecd9", fill="#c89a3c", fill2="#dcc07e", ink="#4a3717"),
    "noir":    dict(bg="#efeae0", fill="#2f2d2a", fill2="#7a756d", ink="#1e1c1a"),
    "blush":   dict(bg="#f6ece6", fill="#c88b83", fill2="#e0bbb2", ink="#6d4239"),
}
WALL_TONE = {"blue": "#d8cfc0", "terra": "#ddd0bf", "sage": "#d9d6c6",
             "mustard": "#dcd2bd", "noir": "#d6d0c4", "blush": "#ddd0c8"}


def leaf(ax, base, tip, width, P, lw=LW, veins=5):
    base, tip = np.array(base, float), np.array(tip, float)
    axis = tip - base; L = np.linalg.norm(axis); u = axis / L
    perp = np.array([-u[1], u[0]])
    t = np.linspace(0, 1, 260)
    w = width * np.sin(np.pi * t) ** 0.62
    center = base[None, :] + (t[:, None] * L) * u[None, :]
    outline = np.vstack([center + w[:, None]*perp, (center - w[:, None]*perp)[::-1]])
    ax.plot(outline[:, 0], outline[:, 1], color=P["ink"], lw=lw, solid_capstyle="round")
    ax.plot([base[0], tip[0]], [base[1], tip[1]], color=P["ink"], lw=lw*0.65)
    for tv in np.linspace(0.18, 0.8, veins):
        c = base + tv*L*u; te = min(tv+0.11, 0.97); we = width*np.sin(np.pi*te)**0.62
        ce = base + te*L*u
        for s in (1, -1):
            ax.plot([c[0], (ce+s*we*perp)[0]], [c[1], (ce+s*we*perp)[1]], color=P["ink"], lw=lw*0.45)


def branch(ax, p0, p1, ctrl, P, n=5, leaf_len=0.85, lw=LW):
    p0, p1, ctrl = map(lambda p: np.array(p, float), (p0, p1, ctrl))
    t = np.linspace(0, 1, 200)
    bez = ((1-t)**2)[:, None]*p0 + (2*(1-t)*t)[:, None]*ctrl + (t**2)[:, None]*p1
    ax.plot(bez[:, 0], bez[:, 1], color=P["ink"], lw=lw*0.8)
    for i, tv in enumerate(np.linspace(0.14, 0.92, n)):
        b = ((1-tv)**2)*p0 + (2*(1-tv)*tv)*ctrl + (tv**2)*p1
        d = 2*(1-tv)*(ctrl-p0) + 2*tv*(p1-ctrl); d = d/np.linalg.norm(d)
        perp = np.array([-d[1], d[0]]) * (1 if i % 2 else -1)
        ang = perp*0.72 + d*0.5; ang = ang/np.linalg.norm(ang)
        sc = leaf_len*(1.0 - 0.4*tv)
        leaf(ax, b, b+ang*sc, 0.15*sc, P, lw, veins=5)


def arches(ax, cx, cy, r0, n, dr, P, lw=LW):
    th = np.linspace(0, np.pi, 200)
    for k in range(n):
        r = r0 + k*dr
        ax.plot(cx+r*np.cos(th), cy+r*np.sin(th), color=P["ink"], lw=lw)


def disc(ax, c, r, P, light=False):
    th = np.linspace(0, 2*np.pi, 220)
    ax.fill(c[0]+r*np.cos(th), c[1]+r*np.sin(th), color=P["fill2"] if light else P["fill"], lw=0)


def ring(ax, c, r, P, lw=LW):
    th = np.linspace(0, 2*np.pi, 220)
    ax.plot(c[0]+r*np.cos(th), c[1]+r*np.sin(th), color=P["ink"], lw=lw)


def diamond(ax, c, s, P, lw=LW):
    p = np.array([[0, s], [s, 0], [0, -s], [-s, 0], [0, s]]) + np.array(c)
    ax.plot(p[:, 0], p[:, 1], color=P["ink"], lw=lw)


def panel(ax, kind, P):
    ax.set_facecolor(P["bg"]); ax.set_xlim(0, 2); ax.set_ylim(0, 3); ax.axis("off"); ax.set_aspect("equal")
    if kind == 0:
        disc(ax, (0.57, 2.45), 0.42, P)
        ring(ax, (0.5, 1.72), 0.13, P)
        branch(ax, (1.68, 2.52), (0.9, 1.86), (1.62, 2.06), P, n=5, leaf_len=0.7)
        arches(ax, 0.95, 0.36, 0.15, 6, 0.12, P)
    elif kind == 1:
        diamond(ax, (1.0, 2.05), 0.66, P)
        branch(ax, (1.35, 2.62), (0.78, 1.75), (1.5, 2.25), P, n=5, leaf_len=0.72)
        disc(ax, (1.0, 1.05), 0.5, P)
    else:
        arches(ax, 1.0, 1.95, 0.15, 8, 0.115, P)
        disc(ax, (0.6, 0.85), 0.32, P, light=True)
        branch(ax, (1.66, 1.5), (0.98, 0.62), (1.66, 0.95), P, n=5, leaf_len=0.7)


def render(pal_name):
    P = PALETTES[pal_name]
    # print-ready panels 2000x3000 (PNG, lossless for print)
    for i in range(3):
        fig = plt.figure(figsize=(4, 6), dpi=500); ax = fig.add_axes([0, 0, 1, 1])
        panel(ax, i, P)
        fig.savefig(os.path.join(OUT, f"{pal_name}_panel{i+1}.png"), facecolor=P["bg"]); plt.close(fig)
    # coordinated preview triptych on a neutral wall tone
    fig, axes = plt.subplots(1, 3, figsize=(12, 6), dpi=170)
    wall = WALL_TONE.get(pal_name, "#d8cfc0")
    fig.patch.set_facecolor(wall)
    for i, ax in enumerate(axes):
        panel(ax, i, P)
    plt.subplots_adjust(wspace=0.07, left=0.02, right=0.98, top=0.97, bottom=0.03)
    fig.savefig(os.path.join(OUT, f"{pal_name}_triptych.jpg"), facecolor=wall); plt.close(fig)
    print(pal_name, "done")


if __name__ == "__main__":
    for name in PALETTES:
        render(name)
