"""
build_3d_cbn.py — "3D Color by Number" interactive app for iPad Safari.
======================================================================
Builds ONE self-contained HTML app (Three.js inlined once) with a MENU of
low-poly 3D figures — Platonic solids, a geodesic sphere, a torus, a faceted
gem and a Möbius band. Every face is numbered by its facet lighting; the user
rotates / pinch-zooms the figure and taps a face to fill it with the matching
palette colour. Colouring 1->8 reveals the lit 3-D form. Runs offline in
Safari, no app, progress saved per figure.

  python build_3d_cbn.py     # -> MathRelaxing_3D_CBN.html
"""
import os
import json
import numpy as np

import poly_meshes

HERE = os.path.dirname(os.path.abspath(__file__))
N_SHADES = 8
PALETTE = ["#0d1124", "#1b2440", "#2f3d64", "#4a5570",
           "#7a7360", "#a98d4e", "#d0ab5f", "#f2e6c4"]
LIGHT = np.array([-0.45, 0.55, 0.75]); LIGHT = LIGHT / np.linalg.norm(LIGHT)


def mesh_data(name, verts, faces):
    positions, centroids, normals, light, height = [], [], [], [], []
    for f in faces:
        v0, v1, v2 = verts[f[0]], verts[f[1]], verts[f[2]]
        nrm = np.cross(v1 - v0, v2 - v0)
        nl = np.linalg.norm(nrm)
        if nl < 1e-9:
            continue
        nrm = nrm / nl
        ct = (v0 + v1 + v2) / 3.0
        positions.extend([*v0, *v1, *v2])
        centroids.append(list(ct)); normals.append(list(nrm))
        light.append(max(0.05, float(np.dot(nrm, LIGHT))))
        height.append(float(np.dot(ct, LIGHT)))       # gradient along the light axis
    L = np.array(light); H = np.array(height)
    Ln = (L - L.min()) / (np.ptp(L) + 1e-9)
    Hn = (H - H.min()) / (np.ptp(H) + 1e-9)
    # lighting reveals the 3-D form; the height gradient makes flat faces vary
    # (so a Platonic face isn't a single number) and widens the shade range.
    comb = 0.6 * Ln + 0.4 * Hn
    idx = np.clip(comb ** 0.9 * N_SHADES, 0, N_SHADES - 1).astype(int)
    return {
        "name": name,
        "positions": [round(x, 4) for x in positions],
        "faceColor": idx.tolist(),
        "centroids": [[round(c, 4) for c in ct] for ct in centroids],
        "normals": [[round(n, 3) for n in nm] for nm in normals],
    }


def build(out=None):
    meshes = [mesh_data(n, v, f) for n, v, f in poly_meshes.figure_library()]
    three = open(os.path.join(HERE, "three.min.js"), encoding="utf-8").read()
    html = (TEMPLATE
            .replace("%THREE%", three)
            .replace("%MESHES%", json.dumps(meshes))
            .replace("%PALETTE%", json.dumps(PALETTE)))
    out = out or os.path.join(HERE, "MathRelaxing_3D_CBN.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    tot = sum(len(m["faceColor"]) for m in meshes)
    print(f"{len(meshes)} figures, {tot} faces total -> {out} ({len(html)//1024} KB)")
    return out


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>3D Color by Number — MathRelaxing</title>
<style>
 html,body{margin:0;height:100%;background:#14151b;overflow:hidden;color:#eee;
  font-family:-apple-system,Helvetica,Arial,sans-serif;-webkit-user-select:none;user-select:none;touch-action:none;}
 #c{position:fixed;inset:0;}
 #bar{position:fixed;top:0;left:0;right:0;display:flex;gap:6px;padding:8px;overflow-x:auto;z-index:6;
  background:linear-gradient(#14151bcc,#14151b00);}
 #bar button{flex:0 0 auto;background:#20222c;color:#cfd2da;border:none;border-radius:16px;padding:7px 13px;font-size:13px;}
 #bar button.on{background:#c9a24b;color:#161616;font-weight:700;}
 #top{position:fixed;top:52px;right:10px;display:flex;gap:7px;z-index:6;}
 #top button{background:#20222c;color:#ddd;border:none;border-radius:16px;padding:7px 12px;font-size:13px;}
 #prog{position:fixed;top:56px;left:12px;z-index:6;color:#9aa;font-size:12px;}
 #pal{position:fixed;left:0;right:0;bottom:0;background:#181a22;padding:9px 8px calc(9px + env(safe-area-inset-bottom));
  display:flex;gap:7px;justify-content:center;flex-wrap:wrap;z-index:6;}
 .sw{width:38px;height:38px;border-radius:8px;border:2px solid #333;display:flex;align-items:center;justify-content:center;
  color:#fff;font-weight:700;font-size:13px;text-shadow:0 1px 2px #000;}
 .sw.sel{border-color:#f2e6c4;box-shadow:0 0 0 2px #f2e6c4;}
</style></head><body>
<canvas id="c"></canvas>
<div id="bar"></div>
<div id="prog"></div>
<div id="top"><button id="reset">Reset view</button><button id="undo">Undo</button><button id="clear">Clear</button></div>
<div id="pal"></div>
<script>%THREE%</script>
<script>
const MESHES = %MESHES%, PAL = %PALETTE%, NS = PAL.length;
const UNCOLORED = new THREE.Color(0x2a2d38);
const renderer = new THREE.WebGLRenderer({canvas:document.getElementById('c'),antialias:true});
renderer.setPixelRatio(Math.min(2,devicePixelRatio));
const scene = new THREE.Scene(); scene.background = new THREE.Color(0x14151b);
const camera = new THREE.PerspectiveCamera(45, innerWidth/innerHeight, 0.1, 100);
let camDist = 3.9;
scene.add(new THREE.AmbientLight(0xffffff,0.55));
const dl = new THREE.DirectionalLight(0xffffff,0.8); dl.position.set(-4,5,7); scene.add(dl);

// shared number textures (1..NS)
function numTexture(n){const s=128,cv=document.createElement('canvas');cv.width=cv.height=s;const x=cv.getContext('2d');
  x.clearRect(0,0,s,s);x.fillStyle='#dcdce2';x.font='bold 84px -apple-system,Arial';x.textAlign='center';x.textBaseline='middle';
  x.fillText(n,s/2,s/2+4);const t=new THREE.CanvasTexture(cv);t.anisotropy=4;return t;}
const numTex=[];for(let i=0;i<NS;i++)numTex.push(numTexture(i+1));

let group,mesh,geo,col,sprites,normVecs,colored,history,cur=-1,selected=null;

function loadFigure(idx){
  if(group){scene.remove(group);geo.dispose();
    group.traverse(o=>{if(o.material&&o.material.dispose&&o.isSprite)o.material.dispose();});}
  cur=idx; const M=MESHES[idx]; const nF=M.faceColor.length;
  group=new THREE.Group();
  const pos=new Float32Array(M.positions);
  col=new Float32Array(nF*9);
  for(let i=0;i<nF*3;i++){col[i*3]=UNCOLORED.r;col[i*3+1]=UNCOLORED.g;col[i*3+2]=UNCOLORED.b;}
  geo=new THREE.BufferGeometry();
  geo.setAttribute('position',new THREE.BufferAttribute(pos,3));
  geo.setAttribute('color',new THREE.BufferAttribute(col,3));
  geo.computeVertexNormals();
  mesh=new THREE.Mesh(geo,new THREE.MeshLambertMaterial({vertexColors:true,flatShading:true,side:THREE.DoubleSide}));
  group.add(mesh);
  group.add(new THREE.LineSegments(new THREE.EdgesGeometry(geo,1),new THREE.LineBasicMaterial({color:0x0c0d12})));
  sprites=[];normVecs=[];
  for(let f=0;f<nF;f++){
    const sp=new THREE.Sprite(new THREE.SpriteMaterial({map:numTex[M.faceColor[f]],depthTest:true,transparent:true}));
    const c=M.centroids[f],n=M.normals[f];
    sp.position.set(c[0]+n[0]*0.02,c[1]+n[1]*0.02,c[2]+n[2]*0.02);sp.scale.setScalar(0.12);
    group.add(sp);sprites.push(sp);normVecs.push(new THREE.Vector3(n[0],n[1],n[2]));
  }
  scene.add(group);
  colored=new Array(nF).fill(-1);history=[];
  try{const s=JSON.parse(localStorage.getItem(key())||'[]');s.forEach((ci,f)=>{if(ci>=0)paint(f,ci);});}catch(e){}
  resetView();updateProg();updateBar();
}
function key(){return 'cbn3d_'+MESHES[cur].name;}
function paint(f,ci){const c=new THREE.Color(PAL[ci]);
  for(let k=0;k<3;k++){col[f*9+k*3]=c.r;col[f*9+k*3+1]=c.g;col[f*9+k*3+2]=c.b;}
  geo.attributes.color.needsUpdate=true;colored[f]=ci;}
function unpaint(f){for(let k=0;k<3;k++){col[f*9+k*3]=UNCOLORED.r;col[f*9+k*3+1]=UNCOLORED.g;col[f*9+k*3+2]=UNCOLORED.b;}
  geo.attributes.color.needsUpdate=true;colored[f]=-1;}
function save(){try{localStorage.setItem(key(),JSON.stringify(colored));}catch(e){}}
function updateProg(){const n=colored.filter(x=>x>=0).length;
  document.getElementById('prog').textContent=MESHES[cur].name+' — '+Math.round(100*n/colored.length)+'%';}

// figure menu
const bar=document.getElementById('bar');
MESHES.forEach((m,i)=>{const b=document.createElement('button');b.textContent=m.name;b.onclick=()=>loadFigure(i);bar.appendChild(b);});
function updateBar(){[...bar.children].forEach((b,i)=>b.classList.toggle('on',i===cur));}

// palette
const palEl=document.getElementById('pal');
PAL.forEach((hex,i)=>{const d=document.createElement('div');d.className='sw';d.style.background=hex;d.textContent=i+1;
  d.onclick=()=>{selected=i;[...palEl.children].forEach(e=>e.classList.remove('sel'));d.classList.add('sel');};palEl.appendChild(d);});

document.getElementById('clear').onclick=()=>{for(let f=0;f<colored.length;f++)if(colored[f]>=0)unpaint(f);history=[];save();updateProg();};
document.getElementById('undo').onclick=()=>{const f=history.pop();if(f!==undefined){unpaint(f);save();updateProg();}};
document.getElementById('reset').onclick=()=>resetView();
function resetView(){group.rotation.set(0.5,0.6,0);camDist=3.9;}

// interaction
const ray=new THREE.Raycaster();let px=0,py=0,drag=false,moved=0,pinchD=0,flashT=0;
function ndc(x,y){return{x:(x/innerWidth)*2-1,y:-(y/innerHeight)*2+1};}
function down(x,y){drag=true;moved=0;px=x;py=y;}
function move(x,y){if(!drag)return;const dx=x-px,dy=y-py;px=x;py=y;moved+=Math.abs(dx)+Math.abs(dy);
  group.rotation.y+=dx*0.01;group.rotation.x+=dy*0.01;}
function up(x,y){drag=false;if(moved>7||selected===null)return;
  ray.setFromCamera(ndc(x,y),camera);const hit=ray.intersectObject(mesh,false);
  if(hit.length){const f=hit[0].faceIndex,num=MESHES[cur].faceColor[f];
    if(num===selected&&colored[f]<0){paint(f,selected);history.push(f);save();updateProg();}else flashT=6;}}
addEventListener('mousedown',e=>down(e.clientX,e.clientY));
addEventListener('mousemove',e=>move(e.clientX,e.clientY));
addEventListener('mouseup',e=>up(e.clientX,e.clientY));
addEventListener('wheel',e=>{camDist=Math.max(1.6,Math.min(7,camDist+e.deltaY*0.002));},{passive:true});
addEventListener('touchstart',e=>{if(e.touches.length===1)down(e.touches[0].clientX,e.touches[0].clientY);
  else if(e.touches.length===2){pinchD=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY);drag=false;}},{passive:true});
addEventListener('touchmove',e=>{if(e.touches.length===1)move(e.touches[0].clientX,e.touches[0].clientY);
  else if(e.touches.length===2){const d=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY);
    camDist=Math.max(1.6,Math.min(7,camDist*(pinchD/d)));pinchD=d;}},{passive:true});
addEventListener('touchend',e=>{if(e.changedTouches.length)up(e.changedTouches[0].clientX,e.changedTouches[0].clientY);});
addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);});
renderer.setSize(innerWidth,innerHeight);

const q=new THREE.Quaternion(),wn=new THREE.Vector3();
function animate(){requestAnimationFrame(animate);
  camera.position.set(0,0,camDist);camera.lookAt(0,0,0);
  group.getWorldQuaternion(q);
  for(let f=0;f<sprites.length;f++){wn.copy(normVecs[f]).applyQuaternion(q);
    sprites[f].visible = colored[f]<0 && wn.z>0.15;}   // hide coloured & back-facing numbers
  if(flashT>0){flashT--;scene.background.setHex(flashT%2?0x3a1414:0x14151b);}else scene.background.setHex(0x14151b);
  renderer.render(scene,camera);}
loadFigure(4);   // start on the Icosahedron
animate();
</script></body></html>"""


if __name__ == "__main__":
    build()
