"""
make_paint_reveal.py — promo video: a pet photo turns into a paint-by-numbers
grid that then fills in, one color at a time, square by square, until the
finished picture appears. Square 1080x1080 for social.

    python make_paint_reveal.py <photo> [out.mp4]
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from sklearn.cluster import KMeans

PAPER = (250, 247, 241); INK = (32, 32, 30); SUB = (122, 118, 104); ACC = (168, 73, 58)
GRIDCOL = (214, 210, 200); NUMCOL = (176, 172, 162)
FDIR = "/usr/share/fonts/truetype/dejavu"
def F(n, s): return ImageFont.truetype(os.path.join(FDIR, n), s)

CELLS = 46            # grid cells per side
CELL_PX = 17          # px per cell in the video
K = 16                # colors
FPS = 24
INTRO = 20            # frames showing the blank numbered grid
REVEAL = 210          # frames to paint everything
OUTRO = 46            # hold + caption
GRID = CELLS * CELL_PX
W = H = 1080
GX = (W - GRID) // 2
GY = 140


def quantize(photo):
    im = ImageOps.fit(Image.open(photo).convert("RGB"), (CELLS, CELLS), Image.Resampling.LANCZOS)
    arr = np.asarray(im).reshape(-1, 3).astype(float)
    km = KMeans(n_clusters=K, n_init=4, random_state=0).fit(arr)
    labels = km.labels_.reshape(CELLS, CELLS)
    palette = km.cluster_centers_.astype(int)
    return labels, palette


def build_base_grid(labels):
    """White grid with light numbers (the blank paint-by-numbers sheet)."""
    img = Image.new("RGB", (GRID, GRID), (255, 255, 255))
    d = ImageDraw.Draw(img)
    fnt = F("DejaVuSans.ttf", int(CELL_PX * 0.52))
    for cy in range(CELLS):
        for cx in range(CELLS):
            x, y = cx * CELL_PX, cy * CELL_PX
            d.rectangle((x, y, x + CELL_PX, y + CELL_PX), outline=GRIDCOL)
            d.text((x + CELL_PX / 2, y + CELL_PX / 2), str(labels[cy, cx] + 1),
                   font=fnt, fill=NUMCOL, anchor="mm")
    return img


def main(photo, out):
    labels, palette = quantize(photo)
    # display number per color = rank; reveal order = biggest areas first
    counts = [(k, int((labels == k).sum())) for k in range(K)]
    order = [k for k, _ in sorted(counts, key=lambda t: -t[1])]
    num_of = {k: i + 1 for i, k in enumerate(order)}  # 1..K for the legend/base

    # relabel base numbers to the display numbers
    disp = np.vectorize(num_of.get)(labels)

    # ordered list of cells (by color group, then scan order)
    cell_seq = []
    for k in order:
        ys, xs = np.where(labels == k)
        for cy, cx in sorted(zip(ys.tolist(), xs.tolist())):
            cell_seq.append((cx, cy, k))
    N = len(cell_seq)
    paint_frame = [INTRO + int(i / N * REVEAL) for i in range(N)]

    # base grid uses display numbers
    base_grid = build_base_grid(disp - 1)
    grid_canvas = base_grid.copy()

    # static full-frame chrome
    full_base = Image.new("RGB", (W, H), PAPER)
    db = ImageDraw.Draw(full_base)
    db.text((W / 2, 74), "PAINT-BY-NUMBERS, ONE COLOR AT A TIME",
            font=F("DejaVuSerif-Bold.ttf", 40), fill=INK, anchor="mm")
    db.text((W / 2, 118), "your pet, painted square by square",
            font=F("DejaVuSerif.ttf", 30), fill=ACC, anchor="mm")

    fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    im_artist = ax.imshow(np.asarray(full_base))

    total_frames = INTRO + REVEAL + OUTRO
    painted = [0]  # how many cells painted so far (mutable)

    def compose(cur_color_k, done_ratio, caption=None):
        frame = full_base.copy()
        frame.paste(grid_canvas, (GX, GY))
        d = ImageDraw.Draw(frame)
        by = GY + GRID + 24
        if caption:
            d.text((W / 2, by + 20), caption, font=F("DejaVuSerif-Bold.ttf", 40),
                   fill=INK, anchor="mm")
            d.text((W / 2, by + 78), "Custom Pet Paint by Numbers  ·  MathRelaxing",
                   font=F("DejaVuSerif.ttf", 28), fill=SUB, anchor="mm")
        else:
            if cur_color_k is not None:
                col = tuple(int(c) for c in palette[cur_color_k])
                d.rounded_rectangle((GX, by, GX + 66, by + 66), radius=10, fill=col,
                                    outline=(210, 205, 195), width=2)
                d.text((GX + 88, by + 33),
                       f"Painting color {num_of[cur_color_k]} of {K}",
                       font=F("DejaVuSans.ttf", 34), fill=(70, 68, 62), anchor="lm")
            # progress bar
            bx0, bx1 = GX, GX + GRID
            pbar_y = by + 84
            d.rounded_rectangle((bx0, pbar_y, bx1, pbar_y + 16), radius=8, fill=(232, 227, 217))
            d.rounded_rectangle((bx0, pbar_y, bx0 + int((bx1 - bx0) * done_ratio), pbar_y + 16),
                                radius=8, fill=ACC)
        return frame

    def frame(f):
        cur_k = None
        if f < INTRO:
            comp = compose(None, 0.0)
        elif f < INTRO + REVEAL:
            # paint all cells scheduled up to this frame
            while painted[0] < N and paint_frame[painted[0]] <= f:
                cx, cy, k = cell_seq[painted[0]]
                col = tuple(int(c) for c in palette[k])
                x, y = cx * CELL_PX, cy * CELL_PX
                ImageDraw.Draw(grid_canvas).rectangle(
                    (x, y, x + CELL_PX, y + CELL_PX), fill=col, outline=(236, 232, 224))
                cur_k = k
                painted[0] += 1
            comp = compose(cur_k, painted[0] / N)
        else:
            # ensure fully painted, then caption
            while painted[0] < N:
                cx, cy, k = cell_seq[painted[0]]
                col = tuple(int(c) for c in palette[k])
                x, y = cx * CELL_PX, cy * CELL_PX
                ImageDraw.Draw(grid_canvas).rectangle(
                    (x, y, x + CELL_PX, y + CELL_PX), fill=col, outline=(236, 232, 224))
                painted[0] += 1
            comp = compose(None, 1.0, caption="Your pet, painted by you")
        im_artist.set_data(np.asarray(comp))
        return [im_artist]

    anim = animation.FuncAnimation(fig, frame, frames=total_frames, interval=1000 / FPS, blit=False)
    writer = animation.FFMpegWriter(fps=FPS, bitrate=5000, codec="libx264",
                                    extra_args=["-pix_fmt", "yuv420p"])
    anim.save(out, writer=writer, dpi=100)
    plt.close(fig)
    print("saved", out, f"({total_frames} frames, {total_frames/FPS:.1f}s)")


if __name__ == "__main__":
    photo = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "paint_reveal.mp4"
    main(photo, out)
