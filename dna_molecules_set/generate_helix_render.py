"""
generate_helix_render.py — real 3D B-DNA double-helix render via pyvista/VTK,
built to read like an actual molecular-graphics render (PyMOL/ChimeraX style)
rather than a simple cartoon: PBR materials, three-point lighting, SSAO,
anti-aliasing, and phosphate "bead" markers along each backbone.

B-form geometry: ~10.5 bp/turn, strand angular offset ~145 deg (giving the
characteristic asymmetric major/minor groove). Transparent background so it
composites cleanly onto the cream plate.

  xvfb-run -a python3 generate_helix_render.py <out.png> [n_bp]
"""
import sys
import numpy as np
import pyvista as pv

pv.OFF_SCREEN = True

INK = "#242019"
BRONZE = "#a07f42"
ROSE = "#b8547a"
TEAL = "#3f8f82"
ROSE_HI = "#e9bdd0"
TEAL_HI = "#b3e3d8"
BEAD = "#d8cdb3"

BP_PER_TURN = 10.5
STRAND_OFFSET_DEG = 145.0
RISE_PER_BP = 1.0
RADIUS = 3.0


def strand_point(n_bp, angle_offset_deg=0.0):
    theta = 2 * np.pi * n_bp / BP_PER_TURN + np.radians(angle_offset_deg)
    x = RADIUS * np.cos(theta)
    y = RADIUS * np.sin(theta)
    z = n_bp * RISE_PER_BP
    return x, y, z


def render(out_path, n_bp=20, w=4200, h=5400):
    pl = pv.Plotter(off_screen=True, window_size=(w, h), lighting="none")
    pl.set_background("white")
    pl.enable_anti_aliasing("msaa")

    t = np.linspace(0, n_bp, 1400)

    def backbone(offset_deg, color, specular, spec_power):
        theta = 2 * np.pi * t / BP_PER_TURN + np.radians(offset_deg)
        x = RADIUS * np.cos(theta)
        y = RADIUS * np.sin(theta)
        z = t * RISE_PER_BP
        pts = np.stack([x, y, z], axis=-1)
        tube = pv.lines_from_points(pts).tube(radius=0.155, n_sides=28)
        pl.add_mesh(tube, color=color, smooth_shading=True, specular=specular,
                    specular_power=spec_power, ambient=0.28, diffuse=0.8)
        # phosphate "bead" markers at each integer bp along this strand
        for n in range(n_bp + 1):
            bx, by, bz = strand_point(n, offset_deg)
            sph = pv.Sphere(radius=0.20, center=(bx, by, bz), theta_resolution=24, phi_resolution=24)
            pl.add_mesh(sph, color=BEAD, smooth_shading=True, specular=0.85,
                        specular_power=35, ambient=0.32, diffuse=0.75)

    backbone(0.0, INK, specular=0.55, spec_power=28)
    backbone(STRAND_OFFSET_DEG, BRONZE, specular=0.85, spec_power=32)

    rng = np.random.default_rng(11)
    pair_types = rng.choice(["AT", "GC"], size=n_bp + 1, p=[0.5, 0.5])
    for n in range(n_bp + 1):
        x1, y1, z1 = strand_point(n, 0.0)
        x2, y2, z2 = strand_point(n, STRAND_OFFSET_DEG)
        pts = np.array([[x1, y1, z1], [x2, y2, z2]])
        tube = pv.lines_from_points(pts).tube(radius=0.082, n_sides=20)
        color = ROSE if pair_types[n] == "AT" else TEAL
        pl.add_mesh(tube, color=color, smooth_shading=True, specular=0.7,
                    specular_power=24, ambient=0.32, diffuse=0.75)
        hi = ROSE_HI if pair_types[n] == "AT" else TEAL_HI
        for pt in (pts[0], pts[1]):
            sph = pv.Sphere(radius=0.135, center=pt, theta_resolution=24, phi_resolution=24)
            pl.add_mesh(sph, color=hi, smooth_shading=True, specular=0.9,
                        specular_power=40, ambient=0.35, diffuse=0.7)

    # three-point lighting for real depth (key / fill / rim)
    pl.add_light(pv.Light(position=(18, -14, n_bp * RISE_PER_BP * 0.75), focal_point=(0, 0, n_bp / 2),
                           color="white", intensity=1.05, light_type="scenelight"))
    pl.add_light(pv.Light(position=(-16, 10, n_bp * RISE_PER_BP * 0.3), focal_point=(0, 0, n_bp / 2),
                           color="#dfe6f2", intensity=0.45, light_type="scenelight"))
    pl.add_light(pv.Light(position=(2, 16, n_bp * RISE_PER_BP), focal_point=(0, 0, n_bp / 2),
                           color="#fff3df", intensity=0.55, light_type="scenelight"))
    try:
        pl.enable_ssao(radius=0.9, bias=0.03, kernel_size=128)
    except Exception:
        pass

    pl.camera.up = (0, 0, 1)
    pl.camera.position = (14.5, -3.5, n_bp * RISE_PER_BP * 0.5)
    pl.camera.focal_point = (0, 0, n_bp * RISE_PER_BP / 2)
    pl.reset_camera()
    pl.camera.zoom(1.18)
    pl.screenshot(out_path, transparent_background=True)
    print("wrote", out_path)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "helix.png"
    n_bp = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    render(out, n_bp)
