"""
build_3d_cbn.py — PoC: interactive 3D color-by-number for iPad Safari.
=====================================================================
A single self-contained HTML app (Three.js inlined) showing a low-poly 3D
figure whose faces are NUMBERED. The user rotates / zooms / pans it and taps a
face to fill it with the matching palette colour — the number vanishes and the
colour stays, revealing the shaded 3-D form. Runs offline in Safari, no app.

Reuses the real math meshes (math_meshes.py). Per-face colour numbers come from
the facet lighting (normal · light), so colouring 1->N reconstructs a lit 3-D
object — the same idea as the flat Sacred-Geometry SVG line, but truly 3-D and
interactive.

  python build_3d_cbn.py     # -> Torus_3D_CBN.html
"""
import os
import sys
import json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(os.path.dirname(HERE), "lulu_books", "core"))
from math_meshes import gen_torus, gen_sphere_bumpy, add_noise

N_SHADES = 8
# navy -> gold -> cream, ordered by luminance (same "sacred gem" ramp)
PALETTE = ["#0d1124", "#1b2440", "#2f3d64", "#4a5570",
           "#7a7360", "#a98d4e", "#d0ab5f", "#f2e6c4"]
LIGHT = np.array([-0.45, 0.55, 0.75]); LIGHT = LIGHT / np.linalg.norm(LIGHT)


def build_mesh(kind="torus"):
    if kind == "torus":
        verts, faces = gen_torus(R=1.0, r=0.42, u_steps=16, v_steps=10)
    else:
        verts, faces = gen_sphere_bumpy(bumps=4, bump_depth=0.22, u_steps=16, v_steps=14)
    verts = add_noise(verts, 0.02, seed=1)
    verts = verts - verts.mean(axis=0)
    verts = verts / np.abs(verts).max()

    positions, face_color, centroids, normals = [], [], [], []
    for f in faces:
        v0, v1, v2 = verts[f[0]], verts[f[1]], verts[f[2]]
        nrm = np.cross(v1 - v0, v2 - v0)
        nl = np.linalg.norm(nrm)
        if nl < 1e-9:
            continue
        nrm = nrm / nl
        inten = max(0.05, float(np.dot(nrm, LIGHT)))
        positions.extend([*v0, *v1, *v2])
        centroids.append(list((v0 + v1 + v2) / 3.0))
        normals.append(list(nrm))
        face_color.append(inten)
    ints = np.array(face_color)
    lo, hi = ints.min(), ints.max()
    idx = np.clip(((ints - lo) / (hi - lo + 1e-9)) ** 0.72 * N_SHADES, 0, N_SHADES - 1).astype(int)
    return {
        "positions": [round(x, 4) for x in positions],
        "faceColor": idx.tolist(),
        "centroids": [[round(c, 4) for c in ct] for ct in centroids],
        "normals": [[round(n, 3) for n in nm] for nm in normals],
        "palette": PALETTE,
        "title": "Torus" if kind == "torus" else "Gem",
    }


HTML = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>3D Color by Number — %TITLE%</title>
<style>
 html,body{margin:0;height:100%;background:#14151b;overflow:hidden;
   font-family:-apple-system,Helvetica,Arial,sans-serif;-webkit-user-select:none;user-select:none;touch-action:none;}
 #c{position:fixed;inset:0;}
 #top{position:fixed;top:12px;right:12px;display:flex;gap:8px;z-index:5;}
 #top button{background:#20222c;color:#eee;border:none;border-radius:20px;padding:9px 15px;font-size:14px;}
 #pal{position:fixed;left:0;right:0;bottom:0;background:#181a22;padding:10px 8px calc(10px + env(safe-area-inset-bottom));
   display:flex;gap:8px;justify-content:center;flex-wrap:wrap;z-index:5;}
 .sw{width:40px;height:40px;border-radius:8px;border:2px solid #333;display:flex;align-items:center;justify-content:center;
   color:#fff;font-weight:700;font-size:14px;text-shadow:0 1px 2px #000;}
 .sw.sel{border-color:#f2e6c4;box-shadow:0 0 0 2px #f2e6c4;}
 #hint{position:fixed;top:12px;left:12px;color:#8b8f9a;font-size:12px;z-index:5;max-width:52%;line-height:1.4;}
</style></head><body>
<canvas id="c"></canvas>
<div id="hint">Drag to rotate · pinch/scroll to zoom · pick a colour then tap a matching numbered face</div>
<div id="top"><button id="undo">Undo</button><button id="clear">Clear</button></div>
<div id="pal"></div>
<script>%THREE%</script>
<script>
const MESH = %MESH%;
const PAL = MESH.palette, NS = PAL.length;
const UNCOLORED = new THREE.Color(0x2a2d38);

const renderer = new THREE.WebGLRenderer({canvas:document.getElementById('c'),antialias:true});
renderer.setPixelRatio(Math.min(2,devicePixelRatio));
const scene = new THREE.Scene(); scene.background = new THREE.Color(0x14151b);
const camera = new THREE.PerspectiveCamera(45, innerWidth/innerHeight, 0.1, 100);
let camDist = 3.4;
scene.add(new THREE.AmbientLight(0xffffff,0.55));
const dl = new THREE.DirectionalLight(0xffffff,0.8); dl.position.set(-4,5,7); scene.add(dl);

const nFaces = MESH.faceColor.length;
const pos = new Float32Array(MESH.positions);
const col = new Float32Array(nFaces*9);
for(let i=0;i<nFaces*3;i++){ col[i*3]=UNCOLORED.r; col[i*3+1]=UNCOLORED.g; col[i*3+2]=UNCOLORED.b; }
const geo = new THREE.BufferGeometry();
geo.setAttribute('position', new THREE.BufferAttribute(pos,3));
geo.setAttribute('color', new THREE.BufferAttribute(col,3));
geo.computeVertexNormals();
const mat = new THREE.MeshLambertMaterial({vertexColors:true, flatShading:true, side:THREE.DoubleSide});
const mesh = new THREE.Mesh(geo, mat);
const group = new THREE.Group(); group.add(mesh);
const edges = new THREE.LineSegments(new THREE.EdgesGeometry(geo, 1),
    new THREE.LineBasicMaterial({color:0x0c0d12})); group.add(edges);
scene.add(group);

// number labels: one shared sprite texture per number, reused per face
function numTexture(n){
  const s=128,cv=document.createElement('canvas');cv.width=cv.height=s;const x=cv.getContext('2d');
  x.fillStyle='rgba(0,0,0,0)';x.fillRect(0,0,s,s);
  x.fillStyle='#d8d8de';x.font='bold 84px -apple-system,Arial';x.textAlign='center';x.textBaseline='middle';
  x.fillText(n,s/2,s/2+4);
  const t=new THREE.CanvasTexture(cv);t.anisotropy=4;return t;
}
const numTex=[]; for(let i=0;i<NS;i++) numTex.push(numTexture(i+1));
const sprites=[];
for(let f=0; f<nFaces; f++){
  const ci=MESH.faceColor[f];
  const sp=new THREE.Sprite(new THREE.SpriteMaterial({map:numTex[ci],depthTest:true,transparent:true}));
  const c=MESH.centroids[f], n=MESH.normals[f];
  sp.position.set(c[0]+n[0]*0.02, c[1]+n[1]*0.02, c[2]+n[2]*0.02);
  sp.scale.setScalar(0.11);
  group.add(sp); sprites.push(sp);
}

// palette bar
const palEl=document.getElementById('pal'); let selected=null;
PAL.forEach((hex,i)=>{const d=document.createElement('div');d.className='sw';d.style.background=hex;d.textContent=i+1;
  d.onclick=()=>{selected=i;[...palEl.children].forEach(e=>e.classList.remove('sel'));d.classList.add('sel');};
  palEl.appendChild(d);});

// state + persistence
const KEY='cbn3d_%TITLE%'; let colored=new Array(nFaces).fill(-1); const history=[];
function setFace(f,ci){
  const c=new THREE.Color(PAL[ci]);
  for(let k=0;k<3;k++){col[f*9+k*3]=c.r;col[f*9+k*3+1]=c.g;col[f*9+k*3+2]=c.b;}
  geo.attributes.color.needsUpdate=true; sprites[f].visible=false; colored[f]=ci;
}
function uncolorFace(f){
  for(let k=0;k<3;k++){col[f*9+k*3]=UNCOLORED.r;col[f*9+k*3+1]=UNCOLORED.g;col[f*9+k*3+2]=UNCOLORED.b;}
  geo.attributes.color.needsUpdate=true; sprites[f].visible=true; colored[f]=-1;
}
function save(){try{localStorage.setItem(KEY,JSON.stringify(colored));}catch(e){}}
function load(){try{const s=JSON.parse(localStorage.getItem(KEY)||'[]');
  s.forEach((ci,f)=>{if(ci>=0)setFace(f,ci);});}catch(e){}}
load();

document.getElementById('clear').onclick=()=>{for(let f=0;f<nFaces;f++)if(colored[f]>=0)uncolorFace(f);history.length=0;save();};
document.getElementById('undo').onclick=()=>{const f=history.pop();if(f!==undefined){uncolorFace(f);save();}};

// interaction: orbit + pinch + tap-to-fill
const ray=new THREE.Raycaster(); let px=0,py=0,drag=false,moved=0,pinchD=0;
function ndc(x,y){return {x:(x/innerWidth)*2-1, y:-(y/innerHeight)*2+1};}
function onDown(x,y){drag=true;moved=0;px=x;py=y;}
function onMove(x,y){if(!drag)return;const dx=x-px,dy=y-py;px=x;py=y;moved+=Math.abs(dx)+Math.abs(dy);
  group.rotation.y+=dx*0.01; group.rotation.x+=dy*0.01;}
function onUp(x,y){drag=false; if(moved>6||selected===null)return;
  const p=ndc(x,y); ray.setFromCamera(p,camera); const hit=ray.intersectObject(mesh,false);
  if(hit.length){const f=hit[0].faceIndex; const num=MESH.faceColor[f];
    if(num===selected && colored[f]<0){setFace(f,selected);history.push(f);save();}
    else{flash();}}}
let flashT=0; function flash(){flashT=6;}
addEventListener('mousedown',e=>onDown(e.clientX,e.clientY));
addEventListener('mousemove',e=>onMove(e.clientX,e.clientY));
addEventListener('mouseup',e=>onUp(e.clientX,e.clientY));
addEventListener('wheel',e=>{camDist=Math.max(1.6,Math.min(7,camDist+e.deltaY*0.002));},{passive:true});
addEventListener('touchstart',e=>{if(e.touches.length===1)onDown(e.touches[0].clientX,e.touches[0].clientY);
  else if(e.touches.length===2){pinchD=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY);drag=false;}},{passive:true});
addEventListener('touchmove',e=>{if(e.touches.length===1)onMove(e.touches[0].clientX,e.touches[0].clientY);
  else if(e.touches.length===2){const d=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY);
    camDist=Math.max(1.6,Math.min(7,camDist*(pinchD/d)));pinchD=d;}},{passive:true});
addEventListener('touchend',e=>{if(e.changedTouches.length)onUp(e.changedTouches[0].clientX,e.changedTouches[0].clientY);});
addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);});
renderer.setSize(innerWidth,innerHeight);

function animate(){requestAnimationFrame(animate);
  camera.position.set(0,0,camDist); camera.lookAt(0,0,0);
  if(flashT>0){flashT--; scene.background.setHex(flashT%2?0x3a1414:0x14151b);} else scene.background.setHex(0x14151b);
  renderer.render(scene,camera);}
animate();
</script></body></html>"""


def build(kind="torus", out=None):
    mesh = build_mesh(kind)
    three = open(os.path.join(HERE, "three.min.js"), encoding="utf-8").read()
    html = (HTML.replace("%THREE%", three)
                .replace("%MESH%", json.dumps(mesh))
                .replace("%TITLE%", mesh["title"]))
    out = out or os.path.join(HERE, f"{mesh['title']}_3D_CBN.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"{mesh['title']}: {len(mesh['faceColor'])} faces -> {out} ({len(html)//1024} KB)")
    return out


if __name__ == "__main__":
    build("torus")
