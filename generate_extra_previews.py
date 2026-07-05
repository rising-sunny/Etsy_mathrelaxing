import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.image as mpimg
import fitz
import brand

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "stem_planner")
PREV = os.path.join(OUT, "previews")
PDF_PATH = os.path.join(OUT, "STEM_Focus_Planner_v3.pdf")
STICKERS_DIR = os.path.join(OUT, "stickers")

def _render_page_png(page_num, out_path):
    doc = fitz.open(PDF_PATH)
    page = doc[page_num]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    pix.save(out_path)
    doc.close()

def _prev_stickers():
    fig, ax = brand.ipad_fig()
    ax.text(5, 9.2, "14 Math Stickers Included", ha="center", fontsize=34,
            color=brand.CREAM, **brand.SERIF)
    ax.text(5, 8.65, "pre-cropped PNGs \u00b7 drag & drop ready",
            ha="center", fontsize=14, style="italic", color=brand.IPAD_GOLD, **brand.SERIF)
    
    # Draw a nice container for stickers
    ax.add_patch(FancyBboxPatch((1.5, 2.5), 7.0, 5.5,
                 boxstyle="round,pad=0,rounding_size=0.1", facecolor="#f8f6f2",
                 edgecolor=brand.GOLD, lw=2, zorder=1))
    
    stickers = ["pi_symbol.png", "integral_symbol.png", "sigma_symbol.png", "infinity_symbol.png",
                "square_root.png", "delta_symbol.png", "theta_symbol.png", "alpha_symbol.png"]
    
    # Draw some stickers
    x_positions = [2.5, 4.0, 5.5, 7.0, 2.5, 4.0, 5.5, 7.0]
    y_positions = [6.0, 6.0, 6.0, 6.0, 4.0, 4.0, 4.0, 4.0]
    for i, s in enumerate(stickers):
        path = os.path.join(STICKERS_DIR, s)
        if os.path.exists(path):
            img = mpimg.imread(path)
            # Center the image
            ax.imshow(img, extent=(x_positions[i]-0.6, x_positions[i]+0.6, y_positions[i]-0.6, y_positions[i]+0.6), zorder=3)
    
    brand.ipad_logo(ax, 5, 0.55, 1.35)
    fig.savefig(os.path.join(PREV, "stem_planner_preview_5_stickers.jpg"),
                dpi=200, facecolor=brand.IPAD_NAVY)
    plt.close(fig)

def _prev_formula(mock_formula):
    fig, ax = brand.ipad_fig()
    ax.text(5, 9.2, "Your Master Cheat Sheet", ha="center", fontsize=34,
            color=brand.CREAM, **brand.SERIF)
    ax.text(5, 8.65, "build your personal formula library",
            ha="center", fontsize=14, style="italic", color=brand.IPAD_GOLD, **brand.SERIF)
    
    brand.ipad_frame(ax, 2.5, 4.2, 5.0, 3.8)
    img = mpimg.imread(mock_formula)
    ax.imshow(img, extent=(1.2, 8.8, 2.3, 8.0), zorder=3, aspect="auto")
    
    ax.text(5, 1.1, "Organized by Algebra, Calculus, Physics & more",
            ha="center", fontsize=13, color="#b9bccb")
    brand.ipad_logo(ax, 5, 0.55, 1.35)
    fig.savefig(os.path.join(PREV, "stem_planner_preview_6_formula.jpg"),
                dpi=200, facecolor=brand.IPAD_NAVY)
    plt.close(fig)

def _prev_academic(mock_lit, mock_data):
    fig, ax = brand.ipad_fig()
    ax.text(5, 9.2, "Academic Excellence", ha="center", fontsize=34,
            color=brand.CREAM, **brand.SERIF)
    ax.text(5, 8.65, "structured templates for university & research",
            ha="center", fontsize=14, style="italic", color=brand.IPAD_GOLD, **brand.SERIF)
    
    brand.ipad_frame(ax, 3.2, 4.6, 3.6, 2.7)
    brand.ipad_frame(ax, 6.8, 4.6, 3.6, 2.7)
    img_l = mpimg.imread(mock_lit)
    ax.imshow(img_l, extent=(1.3, 5.1, 3.35, 5.85), zorder=3, aspect="auto")
    img_d = mpimg.imread(mock_data)
    ax.imshow(img_d, extent=(4.9, 8.7, 3.35, 5.85), zorder=3, aspect="auto")
    
    ax.text(3.2, 2.85, "Literature Review", ha="center", fontsize=15, color=brand.IPAD_TEAL, **brand.SERIF)
    ax.text(6.8, 2.85, "Data Analysis", ha="center", fontsize=15, color=brand.IPAD_TEAL, **brand.SERIF)
    
    brand.ipad_logo(ax, 5, 0.55, 1.35)
    fig.savefig(os.path.join(PREV, "stem_planner_preview_7_academic.jpg"),
                dpi=200, facecolor=brand.IPAD_NAVY)
    plt.close(fig)

def _prev_compatibility():
    fig, ax = brand.ipad_fig()
    ax.text(5, 8.5, "Maximum Compatibility", ha="center", fontsize=38,
            color=brand.CREAM, **brand.SERIF)
    ax.text(5, 7.8, "Works seamlessly on any PDF annotation app",
            ha="center", fontsize=16, style="italic", color=brand.IPAD_GOLD, **brand.SERIF)
    
    apps = [
        ("GoodNotes", 6.0),
        ("Notability", 5.0),
        ("Xodo", 4.0),
        ("Noteshelf", 3.0),
        ("Adobe Acrobat", 2.0)
    ]
    
    for txt, y in apps:
        ax.add_patch(FancyBboxPatch((2.5, y - 0.25), 5.0, 0.5,
                     boxstyle="round,pad=0,rounding_size=0.1", facecolor="#1e2440",
                     edgecolor=brand.GOLD, lw=1.5, zorder=2))
        ax.text(2.8, y, "\u2714", ha="center", va="center", fontsize=20, color=brand.GOLD, zorder=3)
        ax.text(5.0, y, txt, ha="center", va="center", fontsize=16, color=brand.CREAM, **brand.SERIF_BOLD)
    
    brand.ipad_logo(ax, 5, 0.6, 1.4)
    fig.savefig(os.path.join(PREV, "stem_planner_preview_8_compat.jpg"),
                dpi=200, facecolor=brand.IPAD_NAVY)
    plt.close(fig)

if __name__ == "__main__":
    print("Generando imagenes extra...")
    mock_formula = os.path.join(PREV, "_mock_formula.png")
    mock_lit = os.path.join(PREV, "_mock_lit.png")
    mock_data = os.path.join(PREV, "_mock_data.png")
    
    # We need to find the page numbers. In SECTIONS, Formula=3, Data=4, LitReview=5.
    # We'll just render those pages. (Wait, section 1 is graph, 2 is dotgrid, 3 is formula. So pages 1, 2, 3)
    # The actual page numbers can be inferred. Page 0 = index. Page 1 = graph. Page 2 = dotgrid. Page 3 = formula. Page 4 = data. Page 5 = lit.
    _render_page_png(3, mock_formula)
    _render_page_png(5, mock_lit)
    _render_page_png(4, mock_data)
    
    _prev_stickers()
    print("Stickers preview listo.")
    _prev_formula(mock_formula)
    print("Formula preview listo.")
    _prev_academic(mock_lit, mock_data)
    print("Academic preview listo.")
    _prev_compatibility()
    print("Compat preview listo.")
    
    print("Previsualizaciones completadas.")
