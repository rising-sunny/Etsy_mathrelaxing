import os
import shutil
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import fitz
import brand

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "stem_planner")
PDF_PATH = os.path.join(OUT, "STEM_Focus_Planner_v3.pdf")
FRAMES = os.path.join(OUT, "_frames")

NAVY = brand.IPAD_NAVY
CREAM = brand.CREAM

S = 10.8
FPS = 30

def _get_page_img(page_num):
    doc = fitz.open(PDF_PATH)
    page = doc[page_num]
    # Use higher resolution for zooming!
    pix = page.get_pixmap(matrix=fitz.Matrix(3, 3), alpha=False)
    tmp = os.path.join(OUT, f"_tmp_p{page_num}.png")
    pix.save(tmp)
    doc.close()
    img = mpimg.imread(tmp)
    return img

def main():
    if os.path.exists(FRAMES):
        shutil.rmtree(FRAMES)
    os.makedirs(FRAMES)

    print("Rendering base pages...")
    img_idx = _get_page_img(0)
    img_for = _get_page_img(3)
    img_mon = _get_page_img(13)
    
    # iPad frame coordinates
    cx, cy = 5.4, 5.0
    w, h = 8.8, 6.6
    
    fig = plt.figure(figsize=(S, S), dpi=100)
    fig.patch.set_facecolor(NAVY)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(NAVY)
    
    def draw_frame(img, cursor_pos, click_radius, cam_cx, cam_cy, cam_s):
        ax.clear()
        ax.axis("off")
        
        # Camera zoom and pan by setting axis limits
        # cam_s is the width of the view (S means fully zoomed out)
        half = cam_s / 2
        ax.set_xlim(cam_cx - half, cam_cx + half)
        ax.set_ylim(cam_cy - half, cam_cy + half)
        
        ax.text(S / 2, S - 0.8, "STEM Focus Planner", ha="center",
                fontsize=36, family="serif", color=CREAM, zorder=6)
        ax.text(S / 2, S - 1.4, "Tap instantly between pages", ha="center",
                fontsize=16, color=brand.IPAD_GOLD, style="italic", zorder=6)
                
        brand.ipad_frame(ax, cx-w/2, cy-h/2, w, h)
        ax.imshow(img, extent=(cx-w/2+0.3, cx+w/2-0.3, cy-h/2+0.25, cy+h/2-0.25), zorder=3, aspect="auto")
        
        if click_radius > 0:
            circle = plt.Circle(cursor_pos, click_radius, color='white', alpha=0.6, zorder=5)
            ax.add_patch(circle)
            
        if cursor_pos:
            # Stylus tip
            circle = plt.Circle(cursor_pos, 0.08, color=brand.IPAD_TEAL, zorder=6)
            ax.add_patch(circle)
            
        brand.ipad_logo(ax, 5.4, 0.6, 1.5)

    frame = 0
    def save():
        nonlocal frame
        fig.savefig(os.path.join(FRAMES, f"f_{frame:04d}.png"), facecolor=NAVY, dpi=100)
        frame += 1

    # Animation Points
    p_idx = (cx + 2.0, cy + 0.3)  # Formula button
    p_mon = (cx - w/2 + 0.45, cy - 1.8) # MON tab
    p_start = (cx, cy - 4.0)

    # Camera base
    cam_base_c = S / 2
    cam_base_s = S

    print("Generating frames with cinematic zoom...")
    
    # 1. Start fully zoomed out, hold
    for _ in range(15):
        draw_frame(img_idx, p_start, 0, cam_base_c, cam_base_c, cam_base_s)
        save()

    # 2. Zoom in towards Formula button while moving cursor
    frames_move1 = 15
    cam_zoom_c1_x = p_idx[0] - 1.5
    cam_zoom_c1_y = p_idx[1]
    cam_zoom_s1 = S * 0.7 # 30% zoom in
    
    for i in range(frames_move1):
        t = i / frames_move1
        t_ease = t * t * (3 - 2 * t)
        
        cur_x = p_start[0] + (p_idx[0] - p_start[0]) * t_ease
        cur_y = p_start[1] + (p_idx[1] - p_start[1]) * t_ease
        
        c_x = cam_base_c + (cam_zoom_c1_x - cam_base_c) * t_ease
        c_y = cam_base_c + (cam_zoom_c1_y - cam_base_c) * t_ease
        c_s = cam_base_s + (cam_zoom_s1 - cam_base_s) * t_ease
        
        draw_frame(img_idx, (cur_x, cur_y), 0, c_x, c_y, c_s)
        save()
        
    # 3. Click Formula
    for i in range(6):
        r = 0.5 * (i/6)
        draw_frame(img_idx, p_idx, r, cam_zoom_c1_x, cam_zoom_c1_y, cam_zoom_s1)
        save()
        
    # 4. Swap to Formula, start zooming out slowly (hold)
    frames_hold1 = 15
    cam_zoom_s2 = S * 0.85 # Zoom out a bit
    for i in range(frames_hold1):
        t = i / frames_hold1
        t_ease = t * t * (3 - 2 * t)
        
        c_s = cam_zoom_s1 + (cam_zoom_s2 - cam_zoom_s1) * t_ease
        c_x = cam_zoom_c1_x + (cam_base_c - cam_zoom_c1_x) * t_ease * 0.5
        c_y = cam_zoom_c1_y + (cam_base_c - cam_zoom_c1_y) * t_ease * 0.5
        
        draw_frame(img_for, p_idx, 0, c_x, c_y, c_s)
        save()
    
    # 5. Move to MON tab while zooming and panning left
    frames_move2 = 20
    cam_zoom_c3_x = p_mon[0] + 1.5
    cam_zoom_c3_y = p_mon[1]
    cam_zoom_s3 = S * 0.65 # tight zoom
    
    c_x_start = cam_zoom_c1_x + (cam_base_c - cam_zoom_c1_x) * 0.5
    c_y_start = cam_zoom_c1_y + (cam_base_c - cam_zoom_c1_y) * 0.5
    
    for i in range(frames_move2):
        t = i / frames_move2
        t_ease = t * t * (3 - 2 * t)
        
        cur_x = p_idx[0] + (p_mon[0] - p_idx[0]) * t_ease
        cur_y = p_idx[1] + (p_mon[1] - p_idx[1]) * t_ease
        
        c_x = c_x_start + (cam_zoom_c3_x - c_x_start) * t_ease
        c_y = c_y_start + (cam_zoom_c3_y - c_y_start) * t_ease
        c_s = cam_zoom_s2 + (cam_zoom_s3 - cam_zoom_s2) * t_ease
        
        draw_frame(img_for, (cur_x, cur_y), 0, c_x, c_y, c_s)
        save()
        
    # 6. Click MON
    for i in range(6):
        r = 0.5 * (i/6)
        draw_frame(img_for, p_mon, r, cam_zoom_c3_x, cam_zoom_c3_y, cam_zoom_s3)
        save()
        
    # 7. Swap to MON, zoom ALL the way out to full view dynamically
    frames_move3 = 15
    for i in range(frames_move3):
        t = i / frames_move3
        t_ease = t * t * (3 - 2 * t)
        
        cur_x = p_mon[0] + (p_start[0] - p_mon[0]) * t_ease
        cur_y = p_mon[1] + (p_start[1] - p_mon[1]) * t_ease
        
        c_x = cam_zoom_c3_x + (cam_base_c - cam_zoom_c3_x) * t_ease
        c_y = cam_zoom_c3_y + (cam_base_c - cam_zoom_c3_y) * t_ease
        c_s = cam_zoom_s3 + (cam_base_s - cam_zoom_s3) * t_ease
        
        draw_frame(img_mon, (cur_x, cur_y), 0, c_x, c_y, c_s)
        save()
        
    # 8. Handwriting Sequence: Multiple texts
    persistent_texts = []
    
    def render_texts():
        for pt in persistent_texts:
            ax.text(pt['x'], pt['y'], pt['text'], fontsize=12, family="Segoe Print", color="#1c213a", zorder=4)

    def write_text(start_x, start_y, end_x, text_content):
        nonlocal cur_x, cur_y
        
        # Move cursor to start
        move_f = 12
        orig_x, orig_y = cur_x, cur_y
        for i in range(move_f):
            t = i / move_f
            t_e = t * t * (3 - 2 * t)
            cur_x = orig_x + (start_x - orig_x) * t_e
            cur_y = orig_y + (start_y - orig_y) * t_e
            draw_frame(img_mon, (cur_x, cur_y), 0, cam_base_c, cam_base_c, cam_base_s)
            render_texts()
            save()
            
        # Write
        write_f = 20
        text_w = end_x - start_x
        for i in range(write_f + 1):
            t = i / write_f
            t_ease = 1 - (1 - t) * (1 - t)
            cur_w = text_w * t_ease
            cur_x = start_x + cur_w
            cur_y = start_y + math.sin(t * math.pi * 8.0) * 0.05
            
            draw_frame(img_mon, (cur_x, cur_y), 0, cam_base_c, cam_base_c, cam_base_s)
            render_texts()
            
            txt = ax.text(start_x, start_y, text_content, fontsize=12, family="Segoe Print", color="#1c213a", zorder=4)
            rect = plt.Rectangle((start_x, start_y - 0.2), cur_w, 0.4, transform=ax.transData, facecolor='none', edgecolor='none')
            ax.add_patch(rect)
            txt.set_clip_path(rect)
            save()
            
        # Commit
        persistent_texts.append({'x': start_x, 'y': start_y, 'text': text_content})
        
    cur_x, cur_y = p_start
    
    tasks = [
        (cx - 3.2, cy + 1.8, cx - 1.2, "Lab meeting @ 10am"),
        (cx - 1.0, cy + 1.8, cx + 1.0, "Read Smith et al."),
        (cx + 1.2, cy + 1.8, cx + 3.0, "Data Analysis"),
        (cx - 3.2, cy + 1.2, cx - 1.6, "Submit Draft")
    ]
    
    for tx, ty, ex, tcontent in tasks:
        write_text(tx, ty, ex, tcontent)

    # Move stylus away quickly
    move_away = 10
    orig_x, orig_y = cur_x, cur_y
    for i in range(move_away):
        t = i / move_away
        cur_x = orig_x + (p_start[0] - orig_x) * t
        cur_y = orig_y + (p_start[1] - orig_y) * t
        draw_frame(img_mon, (cur_x, cur_y), 0, cam_base_c, cam_base_c, cam_base_s)
        render_texts()
        save()
        
    # Final hold
    for _ in range(15):
        draw_frame(img_mon, p_start, 0, cam_base_c, cam_base_c, cam_base_s)
        render_texts()
        save()
    
    plt.close(fig)
    print(f"Rendered {frame} frames.")
    
    out = os.path.join(OUT, "STEM_Planner_Promo.mp4")
    brand.encode_mp4(FRAMES, out, fps=30, pattern="f_%04d.png", crf=20)
    print("Video listo:", out)

if __name__ == "__main__":
    main()
