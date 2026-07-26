"""plate_library.py — ~38 graphic renderers + metadata for the full art book.
Each g_* returns a trim-sized PIL image. Reuses mini_book helpers/constants."""
import numpy as np
from scipy.integrate import odeint
from scipy.special import jn, jn_zeros
from PIL import Image, ImageOps
import mini_book as MB

fig_trim, to_pil, grad = MB.fig_trim, MB.to_pil, MB._grad_line
DARK, PAPER, CMAP, FRACT, TRIM_PX, GEO = MB.DARK, MB.PAPER, MB.CMAP, MB.FRACT, MB.TRIM_PX, MB.GEO


# ---------------- attractors (dark) ----------------
def _attr(deriv, s0, tmax, n, ij=(0, 2), lims=None, lw=0.5):
    t = np.linspace(0, tmax, n); s = odeint(deriv, s0, t)
    a, b = s[:, ij[0]], s[:, ij[1]]
    fig, ax = fig_trim(DARK); grad(ax, a, b, CMAP, lw)
    if lims:
        ax.set_xlim(lims[0]); ax.set_ylim(lims[1])
    else:
        ax.set_xlim(a.min() - 1, a.max() + 1); ax.set_ylim(b.min() - 1, b.max() + 1)
    ax.set_aspect("auto"); return to_pil(fig, DARK)


def g_lorenz():   return _attr(lambda s, t: [10*(s[1]-s[0]), s[0]*(28-s[2])-s[1], s[0]*s[1]-8/3*s[2]], [1,1,1], 60, 24000, (0,2))
def g_rossler():  return _attr(lambda s, t: [-s[1]-s[2], s[0]+0.2*s[1], 0.2+s[2]*(s[0]-5.7)], [0,1,0], 320, 40000, (0,1))
def g_thomas():   return _attr(lambda s, t: [np.sin(s[1])-0.208*s[0], np.sin(s[2])-0.208*s[1], np.sin(s[0])-0.208*s[2]], [1.1,1.1,-1], 340, 44000, (0,1))
def g_halvorsen():
    a=1.89
    return _attr(lambda s,t:[-a*s[0]-4*s[1]-4*s[2]-s[1]**2, -a*s[1]-4*s[2]-4*s[0]-s[2]**2, -a*s[2]-4*s[0]-4*s[1]-s[0]**2], [-5,0,0], 100, 40000, (0,1))
def g_chen():     return _attr(lambda s,t:[35*(s[1]-s[0]), (28-35)*s[0]-s[0]*s[2]+28*s[1], s[0]*s[1]-3*s[2]], [-7,-4,35], 40, 40000, (0,1))
def g_dadras():   return _attr(lambda s,t:[s[1]-3*s[0]+2.7*s[1]*s[2], 1.7*s[1]-s[0]*s[2]+s[2], 2*s[0]*s[1]-9*s[2]], [1.1,2.1,-2], 80, 40000, (0,1))
def g_aizawa():
    a,b,c,d,e,f=0.95,0.7,0.6,3.5,0.25,0.1
    def dv(s,t):
        x,y,z=s
        return [(z-b)*x-d*y, d*x+(z-b)*y, c+a*z-z**3/3-(x**2+y**2)*(1+e*z)+f*z*x**3]
    return _attr(dv,[0.1,0,0],130,60000,(0,1))
def g_sprott():   return _attr(lambda s,t:[s[1]+2.07*s[0]*s[1]+s[0]*s[2], 1-1.79*s[0]**2+s[1]*s[2], s[0]-s[0]**2-s[1]**2], [0.63,0.47,-0.54], 200, 50000, (0,1))
def g_fourwing(): return _attr(lambda s,t:[0.2*s[0]+s[1]*s[2], -0.01*s[0]-0.4*s[1]-s[0]*s[2], -s[2]-s[0]*s[1]], [1,0,-1], 300, 50000, (0,1))


# ---------------- fractals (dark) ----------------
def _escape(C, z0mode, it=240, power=2, transform=None):
    Z = np.zeros(C.shape, complex) if z0mode == "mandel" else C.copy()
    Cc = C if z0mode == "mandel" else np.full(C.shape, z0mode, complex)
    out = np.zeros(C.shape); m = np.ones(C.shape, bool)
    for k in range(it):
        z = Z[m]
        if transform: z = transform(z)
        Z[m] = z**power + Cc[m] if z0mode == "mandel" else z**power + Cc[m]
        esc = np.abs(Z) > 2; out[esc & m] = k; m &= ~esc
    out[m] = it; return (out/it)**0.5


def _grid(xl, yl, S=2000):
    x = np.linspace(*xl, S); y = np.linspace(*yl, S); X, Y = np.meshgrid(x, y)
    return X + 1j*Y


def _fract_img(v):
    fig, ax = fig_trim(DARK); ax.imshow(v, cmap=FRACT, origin="lower", vmin=0, vmax=1)
    return to_pil(fig, DARK)


def g_julia():     return _fract_img(_escape(_grid((-1.6,1.6),(-1.6,1.6)), complex(-0.8,0.156)))
def g_mandel():    return _fract_img(_escape(_grid((-2.2,0.9),(-1.35,1.35)), "mandel"))
def g_burning():
    C=_grid((-2.2,1.2),(-2.0,0.55)); return _fract_img(_escape(C, "mandel", transform=lambda z: abs(z.real)+1j*abs(z.imag)))
def g_tricorn():   return _fract_img(_escape(_grid((-2,1.2),(-1.6,1.6)), "mandel", transform=lambda z: np.conj(z)))
def g_multibrot(): return _fract_img(_escape(_grid((-1.4,1.4),(-1.4,1.4)), "mandel", power=5))
def g_newton():
    S=2000; x=np.linspace(-1.5,1.5,S); X,Y=np.meshgrid(x,x); Z=X+1j*Y
    conv=np.zeros(Z.shape); done=np.zeros(Z.shape, bool)
    for k in range(60):
        Z=Z-(Z**3-1)/(3*Z**2+1e-9)
        newly=(np.abs(Z**3-1)<1e-6)&~done; conv[newly]=k; done|=newly
    v=(conv/max(conv.max(),1))**0.6
    fig,ax=fig_trim(DARK); ax.imshow(v, cmap=FRACT, origin="lower", vmin=0, vmax=1); return to_pil(fig,DARK)


# ---------------- curves (cream + color) ----------------
def _curve(x, y, lw=2.2, lim=1.15, face=PAPER):
    fig, ax = fig_trim(face); grad(ax, x, y, CMAP, lw)
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_aspect("equal")
    return to_pil(fig, face)


def g_rose():
    th=np.linspace(0,2*np.pi,6000); r=np.cos(7*th); return _curve(r*np.cos(th), r*np.sin(th))
def g_lissajous():
    t=np.linspace(0,2*np.pi,5000); return _curve(np.sin(5*t+np.pi/2), np.sin(4*t))
def g_harmono():
    t=np.linspace(0,60,40000); e=np.exp(-0.006*t)
    x=e*(np.sin(2.01*t)+np.sin(3*t+1.3)); y=e*(np.sin(3*t)+np.sin(2*t+0.5))
    return _curve(x,y,1.4,max(np.abs(x).max(),np.abs(y).max())*1.08)
def g_butterfly():
    t=np.linspace(0,12*np.pi,12000); e=np.exp(np.cos(t))-2*np.cos(4*t)-np.sin(t/12)**5
    x=np.sin(t)*e; y=np.cos(t)*e; return _curve(x,y,1.6,np.abs(np.r_[x,y]).max()*1.08)
def g_hypotrochoid():
    R,r,d=5,3,5; t=np.linspace(0,6*np.pi,8000)
    x=(R-r)*np.cos(t)+d*np.cos((R-r)/r*t); y=(R-r)*np.sin(t)-d*np.sin((R-r)/r*t)
    return _curve(x,y,1.8,np.abs(np.r_[x,y]).max()*1.08)
def g_epicycloid():
    R,r=1,1/3; t=np.linspace(0,2*np.pi,6000)
    x=(R+r)*np.cos(t)-r*np.cos((R+r)/r*t); y=(R+r)*np.sin(t)-r*np.sin((R+r)/r*t)
    return _curve(x,y,2.0,np.abs(np.r_[x,y]).max()*1.08)
def g_logspiral():
    t=np.linspace(0,6*np.pi,6000); r=np.exp(0.15*t); x=r*np.cos(t); y=r*np.sin(t)
    return _curve(x,y,2.0,r.max()*1.05)
def g_lemniscate():
    t=np.linspace(0,2*np.pi,6000); a=1; d=1+np.sin(t)**2
    x=a*np.cos(t)/d; y=a*np.sin(t)*np.cos(t)/d; return _curve(x,y,2.4,0.75)
def g_cardioid():
    t=np.linspace(0,2*np.pi,6000); r=1-np.cos(t); return _curve(r*np.cos(t), r*np.sin(t),2.4,2.1)
def g_astroid():
    t=np.linspace(0,2*np.pi,6000); return _curve(np.cos(t)**3, np.sin(t)**3,2.4,1.1)
def g_deltoid():
    t=np.linspace(0,2*np.pi,6000); x=2*np.cos(t)+np.cos(2*t); y=2*np.sin(t)-np.sin(2*t)
    return _curve(x,y,2.4,3.2)
def g_fermat():
    t=np.linspace(0,10*np.pi,8000); r=np.sqrt(t); x=r*np.cos(t); y=r*np.sin(t)
    xy=np.r_[x,y]; return _curve(np.r_[x,-x], np.r_[y,-y],1.6,r.max()*1.05)


# ---------------- fields ----------------
def g_chladni():
    n,m=7,4; S=1600; x=np.linspace(0,1,S); X,Y=np.meshgrid(x,x)
    Zf=np.cos(n*np.pi*X)*np.cos(m*np.pi*Y)-np.cos(m*np.pi*X)*np.cos(n*np.pi*Y)
    fig,ax=fig_trim(PAPER)
    ax.contour(X,Y,Zf,levels=[0],colors=["#20201e"],linewidths=1.0)
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.set_aspect("equal"); return to_pil(fig,PAPER)
def g_interference():
    S=1600; x=np.linspace(-6,6,S); X,Y=np.meshgrid(x,x); k=6
    r1=np.sqrt((X+2)**2+Y**2); r2=np.sqrt((X-2)**2+Y**2)
    I=(np.cos(k*r1)+np.cos(k*r2))**2
    fig,ax=fig_trim(DARK); ax.imshow(I,cmap=FRACT,origin="lower"); return to_pil(fig,DARK)
def g_standing():
    S=1400; x=np.linspace(0,1,S); X,Y=np.meshgrid(x,x)
    Zf=np.sin(2*np.pi*X)*np.sin(3*np.pi*Y)+np.sin(3*np.pi*X)*np.sin(2*np.pi*Y)
    fig,ax=fig_trim(DARK); ax.imshow(Zf,cmap=CMAP,origin="lower"); return to_pil(fig,DARK)
def g_bessel():
    S=1400; m=3; a=jn_zeros(m,4)[3]
    x=np.linspace(-1,1,S); X,Y=np.meshgrid(x,x); R=np.sqrt(X**2+Y**2); TH=np.arctan2(Y,X)
    Z=jn(m,a*R)*np.cos(m*TH); Z[R>1]=np.nan
    fig,ax=fig_trim(DARK); ax.imshow(Z,cmap=FRACT,origin="lower"); ax.set_aspect("equal"); return to_pil(fig,DARK)
def g_vectorfield():
    x=np.linspace(-3,3,40); X,Y=np.meshgrid(x,x)
    # two opposite charges (dipole)
    def field(px,py,q):
        dx=X-px; dy=Y-py; r2=dx**2+dy**2+0.05; return q*dx/r2**1.5, q*dy/r2**1.5
    u1,v1=field(-1,0,1); u2,v2=field(1,0,-1); U,V=u1+u2,v1+v2
    sp=np.log(np.hypot(U,V)+1)
    fig,ax=fig_trim(DARK)
    ax.streamplot(X,Y,U,V,color=sp,cmap=CMAP,density=1.4,linewidth=0.7,arrowsize=0.6)
    ax.set_xlim(-3,3); ax.set_ylim(-3,3); ax.set_aspect("equal"); return to_pil(fig,DARK)


# ---------------- tilings (cream, from prints) ----------------
def _print(name):
    im=Image.open(f"{GEO}/{name}_4x5.jpg").convert("RGB")
    return ImageOps.fit(im,(TRIM_PX,TRIM_PX),Image.Resampling.LANCZOS)
def g_penrose():  return _print("penrose")
def g_girih():    return _print("girih")
def g_truchet():  return _print("truchet")
def g_rhombille():return _print("rhombille")
def g_sierpinski():return _print("sierpinski")
def g_flower():   return _print("flower")


ALL = [
    ("g_lorenz",g_lorenz),("g_rossler",g_rossler),("g_thomas",g_thomas),("g_halvorsen",g_halvorsen),
    ("g_chen",g_chen),("g_dadras",g_dadras),("g_aizawa",g_aizawa),("g_sprott",g_sprott),("g_fourwing",g_fourwing),
    ("g_julia",g_julia),("g_mandel",g_mandel),("g_burning",g_burning),("g_tricorn",g_tricorn),
    ("g_multibrot",g_multibrot),("g_newton",g_newton),
    ("g_rose",g_rose),("g_lissajous",g_lissajous),("g_harmono",g_harmono),("g_butterfly",g_butterfly),
    ("g_hypotrochoid",g_hypotrochoid),("g_epicycloid",g_epicycloid),("g_logspiral",g_logspiral),
    ("g_lemniscate",g_lemniscate),("g_cardioid",g_cardioid),("g_astroid",g_astroid),("g_deltoid",g_deltoid),("g_fermat",g_fermat),
    ("g_chladni",g_chladni),("g_interference",g_interference),("g_standing",g_standing),("g_bessel",g_bessel),("g_vectorfield",g_vectorfield),
    ("g_penrose",g_penrose),("g_girih",g_girih),("g_truchet",g_truchet),("g_rhombille",g_rhombille),("g_sierpinski",g_sierpinski),("g_flower",g_flower),
]


def contact_sheet():
    import os
    th = 360; cols = 6; rows = (len(ALL) + cols - 1) // cols
    from PIL import ImageDraw, ImageFont
    fnt = ImageFont.truetype(f"{MB.AF}/Raleway.ttf", 16)
    pad = 12; lab = 26
    W = cols * (th + pad) + pad; H = rows * (th + lab + pad) + pad
    sheet = Image.new("RGB", (W, H), "#cfc7b6"); d = ImageDraw.Draw(sheet)
    for i, (name, fn) in enumerate(ALL):
        r, c = divmod(i, cols); x = pad + c * (th + pad); y = pad + r * (th + lab + pad)
        try:
            im = fn().resize((th, th), Image.Resampling.LANCZOS); sheet.paste(im, (x, y)); tag = name[2:]
        except Exception as e:
            d.rectangle((x, y, x + th, y + th), fill="#8a2020"); tag = name[2:] + " ERR:" + str(e)[:20]
        d.text((x + 2, y + th + 4), tag, font=fnt, fill="#20201e")
        print("  ok" if 'im' in dir() else "  ", name)
    out = os.path.join(MB.OUT, "contact_sheet.jpg"); sheet.save(out, quality=88)
    print("contact sheet ->", out, sheet.size)


if __name__ == "__main__":
    contact_sheet()
