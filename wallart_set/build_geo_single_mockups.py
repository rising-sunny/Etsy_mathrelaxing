"""Per-design framed room mockups for the geometric digital singles."""
import os
os.environ.setdefault("WALLART_MODULE", "designs_geo")
os.environ.setdefault("WALLART_PALETTE", "mono")
import build_mockups as bm
from PIL import Image

W, H = 1600, 2000  # 4:5 listing image
for name in bm.NAMES:
    wall = bm.plaster(W, H).convert("RGB")
    card = bm.framed(name, print_h=1240)
    x = (W - card.width) // 2
    y = (H - card.height) // 2 - 40
    bm.drop(wall, card, x, y, blur=22, off=(14, 20))
    out = os.path.join(bm.LST, f"room_{name}.jpg")
    wall.save(out, quality=90)
    print("saved", os.path.basename(out), wall.size)
