import sys, math, os
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "core"))
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import matplotlib.path as mpath
from matplotlib.backends.backend_pdf import PdfPages
from math_meshes import get_mesh

import matplotlib.colors as mcolors

def generate_palette(colors):
    cmap = mcolors.LinearSegmentedColormap.from_list("custom", colors, N=8)
    return {i+1: mcolors.to_hex(cmap(i/7.0)) for i in range(8)}

PALETTES = [
    generate_palette(['#FFFA70', '#E55807', '#5C0029']), # Sunset (Yellow -> Orange -> Deep Red/Purple)
    generate_palette(['#E0FBFC', '#3D5A80', '#0B132B']), # Ocean (Light cyan -> Blue -> Navy)
    generate_palette(['#D8F3DC', '#2D6A4F', '#081C15']), # Emerald (Mint -> Green -> Very dark green)
    generate_palette(['#FDE2E4', '#C9184A', '#38040E']), # Ruby (Light pink -> Red -> Very dark red)
    generate_palette(['#E0AAFF', '#7B2CBF', '#10002B']), # Amethyst (Light purple -> Violet -> Very dark purple)
    generate_palette(['#FFFFFF', '#808080', '#000000']), # Monochrome (White -> Gray -> Black)
]

def get_palette(idx):
    return PALETTES[idx % len(PALETTES)]

def lookat(eye, target, up):
    zaxis = target - eye
    n = np.linalg.norm(zaxis)
    if n == 0: zaxis = np.array([0,0,1])
    else: zaxis = zaxis / n
    xaxis = np.cross(up, zaxis)
    n = np.linalg.norm(xaxis)
    if n == 0: xaxis = np.array([1,0,0])
    else: xaxis = xaxis / n
    yaxis = np.cross(zaxis, xaxis)
    view = np.eye(4)
    view[0, 0:3] = xaxis
    view[1, 0:3] = yaxis
    view[2, 0:3] = zaxis
    view[0:3, 3] = -np.array([np.dot(xaxis, eye), np.dot(yaxis, eye), np.dot(zaxis, eye)])
    return view

def perspective(fov, aspect, near, far):
    f = 1.0 / math.tan(math.radians(fov) / 2)
    proj = np.zeros((4, 4))
    proj[0, 0] = f / aspect
    proj[1, 1] = f
    proj[2, 2] = (far + near) / (near - far)
    proj[2, 3] = (2 * far * near) / (near - far)
    proj[3, 2] = -1.0
    return proj

def get_incenter(pts):
    A, B, C = pts[0], pts[1], pts[2]
    a = np.linalg.norm(B - C)
    b = np.linalg.norm(A - C)
    c = np.linalg.norm(A - B)
    P = a + b + c
    if P == 0: return A, 0
    Ix = (a*A[0] + b*B[0] + c*C[0]) / P
    Iy = (a*A[1] + b*B[1] + c*C[1]) / P
    area = 0.5 * abs((B[0]-A[0])*(C[1]-A[1]) - (C[0]-A[0])*(B[1]-A[1]))
    s = P / 2
    r = area / s if s > 0 else 0
    return np.array([Ix, Iy]), r

def render_mesh(idx, aspect=8.5/11.0, angle=None):
    verts, faces, title = get_mesh(idx)
    # Center and normalize
    verts = verts - np.mean(verts, axis=0)
    max_rad = np.max(np.linalg.norm(verts, axis=1))
    verts = verts / (max_rad + 0.001)

    # Make the camera circle around slightly to give different angles for different models
    if angle is None:
        angle = idx * 0.5
    cam_dist = 2.8
    eye = np.array([math.cos(angle)*cam_dist, 1.2, math.sin(angle)*cam_dist])
    target = np.array([0, 0, 0])
    up = np.array([0, 1, 0])
    
    view = lookat(eye, target, up)
    proj = perspective(35, aspect, 0.1, 100.0)
    
    verts_hom = np.hstack((verts, np.ones((len(verts), 1))))
    verts_view = (view @ verts_hom.T).T
    verts_proj = (proj @ verts_view.T).T
    
    w = verts_proj[:, 3].reshape(-1, 1)
    # Avoid division by zero
    w[w == 0] = 0.0001
    verts_2d = verts_proj[:, 0:2] / w
    
    light_dir = np.array([1, 2, 1])
    light_dir = light_dir / np.linalg.norm(light_dir)

    # Real backface culling (skip faces whose normal points away from the
    # camera) only for the Torus (idx 0-9): a smooth tube where the far side
    # of the hole is genuinely hidden behind the near side, so culling
    # removes it outright instead of relying on an unreliable-at-the-
    # silhouette depth sort (see comment in the loop below).
    #
    # Every other family keeps the original double-sided, abs(dot)-shaded
    # render: Mobius (10-19) and Helicoid (20-29) are open/non-orientable, so
    # there's no consistent "outside" to cull to. The bumpy Sphere (40+,
    # including the endless fallback for idx>=50) IS closed, but its
    # self-occlusion comes from concave dimples BETWEEN bumps on the same
    # front-facing hemisphere, not a hidden far side -- culling doesn't
    # address that at all (verified empirically: culled and uncculled bumpy
    # spheres show the same severity of dark, wrongly-ordered slivers). That
    # residual defect needs real z-buffered rendering to fix properly, which
    # is out of scope here.
    cull_backfaces = idx < 10

    face_data = []
    for i, f in enumerate(faces):
        v0, v1, v2 = verts[f[0]], verts[f[1]], verts[f[2]]
        normal = np.cross(v1 - v0, v2 - v0)
        n_len = np.linalg.norm(normal)
        if n_len == 0: continue
        normal = normal / n_len

        centroid = (v0 + v1 + v2) / 3.0
        view_dir = eye - centroid
        view_dir = view_dir / (np.linalg.norm(view_dir) + 1e-9)
        facing = np.dot(normal, view_dir)
        if cull_backfaces:
            if facing <= 0.02:
                continue
            intensity = max(0.1, np.dot(normal, light_dir))
        else:
            intensity = max(0.1, abs(np.dot(normal, light_dir)))
        z_depth = (verts_view[f[0], 2] + verts_view[f[1], 2] + verts_view[f[2], 2]) / 3
        
        pts_2d = verts_2d[f]
        incenter, incircle_r = get_incenter(pts_2d)
        
        face_data.append({
            'pts_2d': pts_2d,
            'intensity': intensity,
            'z': z_depth,
            'incenter': incenter,
            'r': incircle_r
        })
        
    # Painter's algorithm: draw farthest-from-camera first, nearest last, so
    # nearer faces correctly paint over farther ones. verts_view z grows with
    # distance from the camera (see lookat/perspective above), so the list
    # must be sorted FARTHEST-first (descending) -- downstream code treats
    # "later in face_data" as "nearer / in front" for both zorder assignment
    # and the occlusion-for-numbering check. Sorting ascending (nearest
    # first) had it backwards: distant, hidden geometry (e.g. the far side of
    # a torus's hole, or the opposite twist of a Mobius band) was assigned
    # the highest zorder and painted OVER the correct near surface, showing
    # up as dark, wrongly-shaded polygons cutting across the visible design.
    face_data.sort(key=lambda x: x['z'], reverse=True)
    
    if len(face_data) > 0:
        intensities = np.array([fd['intensity'] for fd in face_data])
        min_i, max_i = intensities.min(), intensities.max()
        for fd in face_data:
            normalized_i = (fd['intensity'] - min_i) / (max_i - min_i + 0.001)
            # Add a bit of non-linear gamma so we get more midtones
            normalized_i = math.pow(normalized_i, 0.7)
            color_idx = int(normalized_i * 8)
            fd['color_idx'] = min(7, color_idx) + 1
            
    return face_data, title

def compute_bounds(face_data):
    all_pts = np.vstack([fd['pts_2d'] for fd in face_data])
    min_x, max_x = all_pts[:, 0].min(), all_pts[:, 0].max()
    min_y, max_y = all_pts[:, 1].min(), all_pts[:, 1].max()
    w, h = max_x - min_x, max_y - min_y
    margin = max(w, h) * 0.05
    data_w = (max_x + margin) - (min_x - margin)
    data_h = (max_y + margin) - (min_y - margin)
    axes_w, axes_h = 0.9 * 8.5, 0.8 * 11.0
    if data_h / data_w > axes_h / axes_w:
        scale_pts = (axes_h / data_h) * 72.0
    else:
        scale_pts = (axes_w / data_w) * 72.0
    return min_x, max_x, min_y, max_y, margin, scale_pts


def number_faces(face_data, scale_pts):
    """Pass 1: decide which faces are large/unoccluded enough to carry a
    number (left white for the reader) vs. small pre-coloured accents.
    Mutates face_data in place; returns how many got numbered."""
    for fd in face_data:
        fd['path'] = mpath.Path(fd['pts_2d'])
        fd['has_number'] = False

    numbered_count = 0
    for idx_z, fd in enumerate(face_data):
        ic_x, ic_y = fd['incenter']
        r = fd['r']
        font_size = min(9, 2 * r * scale_pts * 0.35)
        fd['font_size'] = font_size
        if font_size >= 4.5:
            occluded = any(fd_front['path'].contains_point((ic_x, ic_y))
                           for fd_front in face_data[idx_z + 1:])
            if not occluded:
                fd['has_number'] = True
                numbered_count += 1
    return numbered_count


def badness_score(face_data):
    """Estimate how much of the page is marred by the residual painter's-
    algorithm defect: a thin, dark, wrongly-ordered sliver poking over the
    correct surface (see gen_sacred_math_book fix notes). Legitimate small
    pre-coloured accents tend to be reasonably compact triangles; the buggy
    ones are near-degenerate slivers (a face seen edge-on at a self-
    occluding silhouette) that also land in the darkest palette bins.
    Returns the fraction of total drawn area covered by such slivers."""
    total_area = 0.0
    bad_area = 0.0
    for fd in face_data:
        pts = fd['pts_2d']
        area = 0.5 * abs((pts[1, 0] - pts[0, 0]) * (pts[2, 1] - pts[0, 1])
                         - (pts[2, 0] - pts[0, 0]) * (pts[1, 1] - pts[0, 1]))
        if area <= 0:
            continue
        total_area += area
        if fd['has_number']:
            continue
        perim = (np.linalg.norm(pts[1] - pts[0]) + np.linalg.norm(pts[2] - pts[1])
                 + np.linalg.norm(pts[0] - pts[2]))
        if perim <= 0:
            continue
        compactness = (4 * math.sqrt(3) * area) / (perim * perim)
        if fd['color_idx'] >= 6 and compactness < 0.22:
            bad_area += area
    return (bad_area / total_area) if total_area > 0 else 0.0


def best_candidate(idx, n_angles=10):
    """Try several camera angles for this mesh index and keep the cleanest
    one (lowest badness_score) that still has enough numbered regions.
    Different angles change how much the mesh self-occludes in projection
    -- this is a much cheaper way to dodge the residual painter's-algorithm
    ambiguity (see fix notes above) than a real z-buffered renderer."""
    best = None
    for a in range(n_angles):
        angle = idx * 0.5 + a * (2 * math.pi / n_angles)
        face_data, title = render_mesh(idx, aspect=8.5 / 11.0, angle=angle)
        if len(face_data) == 0:
            continue
        _, _, _, _, _, scale_pts = compute_bounds(face_data)
        numbered_count = number_faces(face_data, scale_pts)
        if numbered_count < 20:
            continue
        score = badness_score(face_data)
        if best is None or score < best[0]:
            best = (score, face_data, title, numbered_count)
    return best


def main():
    out_dir = os.path.join(_ROOT, "output", "sacred-math-coloring-book")
    os.makedirs(out_dir, exist_ok=True)
        
    pdf_path = os.path.join(out_dir, "interior.pdf")
    
    with PdfPages(pdf_path) as pdf:
        # 1. Title Page
        fig = plt.figure(figsize=(8.5, 11))
        fig.text(0.5, 0.62, "SACRED GEOMETRY", ha='center', va='center', fontsize=46, family='serif', weight='light')
        fig.text(0.5, 0.55, "& TOPOLOGY", ha='center', va='center', fontsize=46, family='serif', weight='light')
        fig.text(0.5, 0.45, "A 3D Color-by-Numbers Journey", ha='center', va='center', fontsize=18, family='serif', style='italic', color='#444')
        fig.text(0.5, 0.40, "50 Geometric 3D Models · MathRelaxing", ha='center', va='center', fontsize=11, family='serif', color='#777')
        pdf.savefig(fig)
        plt.close(fig)
        
        # 2. Palette & Instructions Page
        fig = plt.figure(figsize=(8.5, 11))
        ax = fig.add_axes([0.12, 0.1, 0.76, 0.82])
        ax.axis('off')
        ax.text(0.0, 0.97, "How to colour", ha='left', va='top', fontsize=22, family='serif', color='#222')
        intro = ("1. Match the numbers in the polygons to the colour legend at the bottom\n"
                 "   of the page.\n"
                 "2. Relax and enjoy the illusion of 3D volume emerge from flat shapes!\n"
                 "3. Small accent polygons have been pre-coloured for your convenience.\n\n"
                 "Use any pens, pencils, or markers. Slip a spare sheet behind the page\n"
                 "if using wet markers.")
        ax.text(0.0, 0.88, intro, ha='left', va='top', fontsize=12.5, family='serif', color='#333', linespacing=1.5)
        pdf.savefig(fig)
        plt.close(fig)
        
        # 3. Coloring Pages
        all_data = []
        idx = 0
        BADNESS_LIMIT = 0.06
        MAX_ATTEMPTS = 250  # safety valve: guarantee termination even if
        # clean candidates run scarce late in the endless sphere fallback
        while len(all_data) < 50:
            # Past MAX_ATTEMPTS, stop being picky -- relax the limit so the
            # remaining slots still get filled with whatever's best available
            # instead of searching indefinitely.
            limit = BADNESS_LIMIT if idx < MAX_ATTEMPTS else 1.0
            result = best_candidate(idx)
            idx += 1
            if result is None:
                continue
            score, face_data, title, numbered_count = result
            if score > limit:
                print(f"Discarding model '{title}' (best angle still {score:.1%} "
                      f"residual-glitch area).")
                continue

            fig = plt.figure(figsize=(8.5, 11))
            ax = fig.add_axes([0.05, 0.15, 0.9, 0.8])
            ax_legend = fig.add_axes([0.1, 0.05, 0.8, 0.05])
            ax.set_aspect('equal')
            ax.axis('off')
            ax_legend.axis('off')

            min_x, max_x, min_y, max_y, margin, scale_pts = compute_bounds(face_data)
            ax.set_xlim(min_x - margin, max_x + margin)
            ax.set_ylim(min_y - margin, max_y + margin)

            print(f"Generating page {len(all_data)+1}/50: {title} "
                  f"({numbered_count} numbers, {score:.1%} residual)")
            all_data.append((face_data, title))

            # Pass 2: Draw polygons and text
            palette = get_palette(idx)
            for idx_z, fd in enumerate(face_data):
                z = idx_z + 1
                if fd['has_number']:
                    facecolor = 'white'
                else:
                    facecolor = palette[fd['color_idx']]
                    
                poly = Polygon(fd['pts_2d'], closed=True, facecolor=facecolor, edgecolor='black', linewidth=0.5, zorder=z)
                ax.add_patch(poly)
                
                if fd['has_number']:
                    ic_x, ic_y = fd['incenter']
                    ax.text(ic_x, ic_y, str(fd['color_idx']), ha='center', va='center', 
                            fontsize=fd['font_size'], color='#999999', zorder=z)
                                
            # Draw legend
            palette = get_palette(idx)
            box_w = 1.0 / 8.0
            for i in range(1, 9):
                x = (i-1) * box_w
                rect = Polygon([[x, 0], [x+box_w, 0], [x+box_w, 1], [x, 1]], 
                               facecolor=palette[i], edgecolor='black', linewidth=0.5)
                ax_legend.add_patch(rect)
                text_color = 'white' if i <= 4 else 'black'
                if np.mean(mcolors.to_rgb(palette[i])) < 0.5:
                    text_color = 'white'
                else:
                    text_color = 'black'
                ax_legend.text(x + box_w/2, 0.5, str(i), ha='center', va='center', color=text_color, fontsize=10, family='serif')
            ax_legend.set_xlim(0, 1)
            ax_legend.set_ylim(0, 1)
                    
            fig.text(0.5, 0.12, f"{idx+1}. {title}", ha='center', fontsize=12)
            pdf.savefig(fig)
            plt.close(fig)
            
        # 4. Solutions (Thumbnails)
        print("Generating Solution Keys...")
        thumbs_per_page = 9
        for page_idx in range(math.ceil(50 / thumbs_per_page)):
            fig, axs = plt.subplots(3, 3, figsize=(8.5, 11))
            fig.subplots_adjust(hspace=0.4, wspace=0.3)
            fig.text(0.5, 0.95, "Solution Key", ha='center', va='center', fontsize=20, weight='bold')
            
            for i in range(9):
                ax = axs[i//3, i%3]
                ax.axis('off')
                data_idx = page_idx * 9 + i
                if data_idx < 50:
                    face_data, title = all_data[data_idx]
                    all_pts = np.vstack([fd['pts_2d'] for fd in face_data])
                    min_x, max_x = all_pts[:,0].min(), all_pts[:,0].max()
                    min_y, max_y = all_pts[:,1].min(), all_pts[:,1].max()
                    margin = max(max_x - min_x, max_y - min_y) * 0.05
                    ax.set_xlim(min_x - margin, max_x + margin)
                    ax.set_ylim(min_y - margin, max_y + margin)
                    ax.set_aspect('equal')
                    for fd in face_data:
                        palette = get_palette(data_idx)
                        poly = Polygon(fd['pts_2d'], closed=True, facecolor=palette[fd['color_idx']], edgecolor='none')
                        ax.add_patch(poly)
                    ax.set_title(str(data_idx+1), fontsize=10, family='serif', color='#555')
            pdf.savefig(fig)
            plt.close(fig)
            
    print(f"DONE: {pdf_path}")

if __name__ == "__main__":
    main()
