# -*- coding: utf-8 -*-
import json, os

PAGES = json.load(open('/tmp/phd_pages/pages.json'))
LOGO = open('/tmp/phd_pages/logo.txt').read()

# section content
SECTIONS = [
    dict(key="dashboard", label="The Dashboard",
         title="Every section, one tap away",
         blurb="A single hyperlinked home screen. Tap any hub to jump straight there — no scrolling through 136 pages to find your reading log at 2 a.m.",
         callouts=["9 hyperlinked hubs + side tabs", "Undated — start any day", "Duplicate any page infinitely"]),
    dict(key="roadmap", label="Research Roadmap",
         title="See the whole PhD at a glance",
         blurb="A milestone Gantt for the long game: coursework, literature review, proposal, data, analysis, writing, revisions, defense — one grid per year.",
         callouts=["8 phases × 12 months", "Shade what’s active, star the milestones", "One roadmap per PhD year"]),
    dict(key="chapters", label="Chapter Progress",
         title="Know exactly where every chapter stands",
         blurb="Stop guessing how close you are. Track each chapter from first draft to advisor-approved, with word-count targets alongside.",
         callouts=["Draft · Revised · Sent · Approved", "Word-count targets per section", "14 chapters & sections"]),
    dict(key="literature", label="Literature Log",
         title="Never lose a paper again",
         blurb="Turn a pile of half-remembered PDFs into a searchable record. Every card holds the citation, the one finding that matters, and why it matters to you.",
         callouts=["72 structured citation cards", "Key finding + relevance rating", "Tag by theme"]),
    dict(key="meetings", label="Advisor Meetings",
         title="Walk in prepared, leave with a plan",
         blurb="An agenda before, a record after. Capture discussion, decisions, and the action items due before you meet again — for 24 meetings.",
         callouts=["Agenda & feedback", "Decisions logged in writing", "Action items before next meeting"]),
    dict(key="weekly", label="Weekly Research",
         title="Protect your writing time",
         blurb="The week that actually moves the thesis: three real priorities, a daily writing-word tracker, and a seven-day task plan.",
         callouts=["Top 3 priorities", "Daily writing-word tracker", "7-day research task planner"]),
    dict(key="monthly", label="Monthly Review",
         title="Zoom out and course-correct",
         blurb="Once a month, step back. Set objectives, mark milestones reached, and answer the only question that counts: what moved the thesis forward?",
         callouts=["Objectives & milestones", "“What moved the thesis forward?”", "12 monthly reviews"]),
    dict(key="deadlines", label="Conferences & Deadlines",
         title="One table for every submission",
         blurb="Abstracts, papers, travel, funding — all the dates that sneak up on you, in one place, with status at a glance.",
         callouts=["Submissions & venues", "Travel & funding", "Status at a glance"]),
    dict(key="defense", label="The Defense",
         title="Cross the finish line",
         blurb="The last mile, de-stressed: a complete defense checklist and space to rehearse the questions you’ll be asked — plus qualifying-exam prep earlier in the book.",
         callouts=["Full defense checklist", "Anticipated Q&A prep", "Qualifying-exam pages too"]),
]

DATA = {s["key"]: PAGES[s["key"]] for s in SECTIONS}

HTML = r"""<title>PhD & Dissertation Planner — Interactive Tour</title>
<style>
:root{
  --ground:#ece5d6; --panel:#f6f1e6; --panel2:#fbf8f0;
  --gold:#a8823a; --gold-soft:#8a6b2e; --ink:#23252e; --title:#1c2033;
  --muted:#6a6f80; --line:rgba(120,95,40,0.30); --teal:#2f6f7c;
  --frame:#ffffff; --shadow:rgba(30,25,15,0.22);
  --serif:"Iowan Old Style","Palatino Linotype",Palatino,"Book Antiqua",Georgia,"Times New Roman",serif;
  --sans:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  --mono:"SF Mono","JetBrains Mono",ui-monospace,"Cascadia Code",Menlo,Consolas,monospace;
}
@media (prefers-color-scheme: dark){
  :root{
    --ground:#0d1124; --panel:#161d34; --panel2:#1e2743;
    --gold:#cda24e; --gold-soft:#e6c987; --ink:#e7e9f1; --title:#f6f2e8;
    --muted:#9298ac; --line:rgba(205,162,78,0.24); --teal:#5aa6b5;
    --frame:#f7f8fb; --shadow:rgba(0,0,0,0.55);
  }
}
:root[data-theme="light"]{
  --ground:#ece5d6; --panel:#f6f1e6; --panel2:#fbf8f0;
  --gold:#a8823a; --gold-soft:#8a6b2e; --ink:#23252e; --title:#1c2033;
  --muted:#6a6f80; --line:rgba(120,95,40,0.30); --teal:#2f6f7c;
  --frame:#ffffff; --shadow:rgba(30,25,15,0.22);
}
:root[data-theme="dark"]{
  --ground:#0d1124; --panel:#161d34; --panel2:#1e2743;
  --gold:#cda24e; --gold-soft:#e6c987; --ink:#e7e9f1; --title:#f6f2e8;
  --muted:#9298ac; --line:rgba(205,162,78,0.24); --teal:#5aa6b5;
  --frame:#f7f8fb; --shadow:rgba(0,0,0,0.55);
}
*{box-sizing:border-box}
html,body{margin:0}
body{
  background:
    radial-gradient(1200px 700px at 78% -8%, color-mix(in srgb, var(--gold) 12%, transparent), transparent 60%),
    var(--ground);
  color:var(--ink); font-family:var(--sans);
  -webkit-font-smoothing:antialiased; min-height:100vh;
}
.wrap{max-width:1180px; margin:0 auto; padding:26px clamp(16px,4vw,40px) 40px;}

/* top bar */
.topbar{display:flex; align-items:center; justify-content:space-between; gap:16px; margin-bottom:20px;}
.brand{display:flex; align-items:center; gap:12px;}
.brand img{height:34px; width:auto; display:block; filter:drop-shadow(0 1px 2px var(--shadow));}
.brand .bt{font-family:var(--mono); font-size:11px; letter-spacing:.22em; text-transform:uppercase; color:var(--muted);}
.themetoggle{
  font-family:var(--mono); font-size:11px; letter-spacing:.14em; text-transform:uppercase;
  color:var(--muted); background:transparent; border:1px solid var(--line);
  padding:8px 12px; border-radius:999px; cursor:pointer; transition:.2s;
}
.themetoggle:hover{color:var(--gold); border-color:var(--gold);}
.themetoggle:focus-visible{outline:2px solid var(--gold); outline-offset:2px;}

/* eyebrow + heading */
.eyebrow{font-family:var(--mono); font-size:12px; letter-spacing:.28em; text-transform:uppercase; color:var(--gold); margin:0 0 10px;}
h1.lede{font-family:var(--serif); font-weight:600; color:var(--title); text-wrap:balance;
  font-size:clamp(26px,4.4vw,44px); line-height:1.05; margin:0 0 8px; letter-spacing:.005em;}
.sub{color:var(--muted); font-size:clamp(14px,1.6vw,17px); max-width:60ch; margin:0 0 22px; line-height:1.55;}

/* stage */
.stage{display:grid; grid-template-columns: 1.35fr 1fr; gap:clamp(18px,3vw,40px); align-items:center;}
@media (max-width:820px){ .stage{grid-template-columns:1fr;} }

/* device frame */
.device{position:relative; border-radius:16px; padding:14px;
  background:linear-gradient(160deg, var(--panel2), var(--panel));
  border:1px solid var(--line); box-shadow:0 24px 60px -24px var(--shadow), inset 0 1px 0 color-mix(in srgb,#fff 12%, transparent);}
.screen{position:relative; overflow:hidden; border-radius:8px; background:var(--frame);
  aspect-ratio:1320/1020; cursor:zoom-in;}
.screen img{position:absolute; inset:0; width:100%; height:100%; object-fit:cover; display:block;}
.screen .pg{opacity:0; transition:opacity .6s ease;}
.screen .pg.on{opacity:1;}
.screen .pg.kb{animation:ken 14s ease-out both;}
@keyframes ken{from{transform:scale(1.005)} to{transform:scale(1.055)}}
.deck{position:absolute; left:14px; right:14px; bottom:14px; display:flex; gap:6px; z-index:4;}
.deck i{height:3px; flex:1; background:color-mix(in srgb,var(--muted) 40%, transparent); border-radius:2px; overflow:hidden;}
.deck i b{display:block; height:100%; width:0; background:var(--gold);}
.deck i.done b{width:100%}
.deck i.cur b{animation:fill var(--dwell,6s) linear forwards}
@keyframes fill{from{width:0} to{width:100%}}
.hint{position:absolute; top:12px; right:12px; z-index:5; font-family:var(--mono); font-size:10px;
  letter-spacing:.14em; text-transform:uppercase; color:#fff; background:rgba(20,24,42,.62);
  padding:6px 10px; border-radius:999px; display:flex; align-items:center; gap:6px; pointer-events:none;
  opacity:.9; backdrop-filter:blur(3px);}
.hint svg{width:12px;height:12px}

/* loupe */
.loupe{position:absolute; width:190px; height:190px; border-radius:50%; pointer-events:none;
  border:2px solid var(--gold); box-shadow:0 8px 24px rgba(0,0,0,.4), inset 0 0 0 3px rgba(255,255,255,.35);
  background-repeat:no-repeat; display:none; z-index:6;}

/* text panel */
.panel .cnt{font-family:var(--mono); font-size:12px; letter-spacing:.2em; color:var(--muted); margin-bottom:14px;}
.panel .cnt b{color:var(--gold)}
.panel .slabel{font-family:var(--mono); font-size:12px; letter-spacing:.24em; text-transform:uppercase; color:var(--teal); margin-bottom:12px;}
.panel h2{font-family:var(--serif); font-weight:600; color:var(--title); text-wrap:balance;
  font-size:clamp(22px,2.8vw,30px); line-height:1.12; margin:0 0 14px;}
.panel p.blurb{color:var(--ink); opacity:.85; font-size:16px; line-height:1.6; margin:0 0 22px; max-width:46ch;}
.cos{list-style:none; margin:0 0 26px; padding:0; display:flex; flex-direction:column; gap:12px;}
.cos li{display:flex; align-items:flex-start; gap:11px; font-size:15px; color:var(--ink);}
.cos .tk{flex:none; margin-top:2px; width:18px; height:18px; border-radius:50%;
  display:grid; place-items:center; background:color-mix(in srgb,var(--gold) 18%, transparent); }
.cos .tk svg{width:11px; height:11px; stroke:var(--gold);}

/* staged reveal */
.reveal>*{opacity:0; transform:translateY(8px);}
.reveal.play>*{animation:rise .55s cubic-bezier(.2,.7,.2,1) forwards;}
.reveal.play>*:nth-child(1){animation-delay:.02s}
.reveal.play>*:nth-child(2){animation-delay:.10s}
.reveal.play>*:nth-child(3){animation-delay:.18s}
.reveal.play>*:nth-child(4){animation-delay:.26s}
.reveal.play .cos li{opacity:0; transform:translateY(8px); animation:rise .5s cubic-bezier(.2,.7,.2,1) forwards;}
.reveal.play .cos li:nth-child(1){animation-delay:.30s}
.reveal.play .cos li:nth-child(2){animation-delay:.40s}
.reveal.play .cos li:nth-child(3){animation-delay:.50s}
@keyframes rise{to{opacity:1; transform:none}}

/* controls */
.controls{display:flex; align-items:center; gap:14px; margin-top:26px; flex-wrap:wrap;}
.btn{font-family:var(--sans); font-size:14px; color:var(--ink); background:var(--panel);
  border:1px solid var(--line); border-radius:999px; padding:10px 16px; cursor:pointer;
  display:inline-flex; align-items:center; gap:8px; transition:.18s;}
.btn:hover{border-color:var(--gold); color:var(--gold)}
.btn:focus-visible{outline:2px solid var(--gold); outline-offset:2px}
.btn svg{width:15px;height:15px; fill:currentColor}
.btn.primary{background:var(--gold); color:#20180a; border-color:var(--gold); font-weight:600;}
.btn.primary:hover{background:var(--gold-soft); color:#20180a}
.dots{display:flex; gap:9px; margin-left:2px; flex-wrap:wrap;}
.dots button{width:11px; height:11px; padding:0; border-radius:50%; border:1px solid var(--line);
  background:transparent; cursor:pointer; transition:.18s;}
.dots button[aria-current="true"]{background:var(--gold); border-color:var(--gold); transform:scale(1.15);}
.dots button:hover{border-color:var(--gold)}
.dots button:focus-visible{outline:2px solid var(--gold); outline-offset:2px}
.spacer{flex:1}
.stepname{font-family:var(--mono); font-size:11px; letter-spacing:.14em; text-transform:uppercase; color:var(--muted);}

/* intro overlay */
.intro{position:fixed; inset:0; z-index:40; background:
   radial-gradient(900px 600px at 50% 30%, color-mix(in srgb,var(--gold) 14%, transparent), transparent 60%),
   var(--ground);
  display:grid; place-items:center; text-align:center; padding:24px; transition:opacity .7s ease, visibility .7s;}
.intro.hide{opacity:0; visibility:hidden;}
.intro .ib{max-width:640px}
.intro img{height:52px; margin-bottom:22px; filter:drop-shadow(0 2px 6px var(--shadow))}
.intro .k{font-family:var(--mono); font-size:12px; letter-spacing:.3em; text-transform:uppercase; color:var(--gold); margin-bottom:16px}
.intro h1{font-family:var(--serif); font-weight:600; color:var(--title); font-size:clamp(30px,6vw,58px);
  line-height:1.03; margin:0 0 16px; text-wrap:balance;}
.intro p{color:var(--muted); font-size:17px; line-height:1.6; margin:0 auto 30px; max-width:52ch;}
.fadeup{opacity:0; transform:translateY(12px); animation:rise .8s cubic-bezier(.2,.7,.2,1) forwards;}
.fadeup.d1{animation-delay:.15s}.fadeup.d2{animation-delay:.35s}.fadeup.d3{animation-delay:.55s}.fadeup.d4{animation-delay:.8s}

/* lightbox */
.lightbox{position:fixed; inset:0; z-index:60; background:rgba(8,10,20,.9); display:none;
  place-items:center; padding:24px; cursor:zoom-out;}
.lightbox.on{display:grid}
.lightbox img{max-width:96vw; max-height:92vh; border-radius:6px; box-shadow:0 30px 80px rgba(0,0,0,.6);}
.lightbox .x{position:absolute; top:18px; right:20px; font-family:var(--mono); font-size:12px;
  letter-spacing:.16em; color:#eee; background:rgba(255,255,255,.1); border:1px solid rgba(255,255,255,.25);
  border-radius:999px; padding:8px 14px; cursor:pointer;}

.foot{margin-top:30px; padding-top:18px; border-top:1px solid var(--line); display:flex;
  align-items:center; justify-content:space-between; gap:14px; flex-wrap:wrap;
  font-family:var(--mono); font-size:11px; letter-spacing:.12em; text-transform:uppercase; color:var(--muted);}
.foot b{color:var(--gold)}

@media (prefers-reduced-motion: reduce){
  *{animation-duration:.001s !important; animation-delay:0s !important;}
  .screen .pg.kb{animation:none}
  .deck i.cur b{width:100%}
}
</style>

<div class="intro" id="intro">
  <div class="ib">
    <img class="fadeup" src="__LOGO__" alt="MathRelaxing">
    <div class="k fadeup d1">An interactive tour</div>
    <h1 class="fadeup d2">The PhD &amp; Dissertation Planner</h1>
    <p class="fadeup d3">136 hyperlinked pages that carry you from first proposal to final defense. Take a look inside — hover any page to zoom in on the detail.</p>
    <button class="btn primary fadeup d4" id="begin">Begin the tour &nbsp;→</button>
  </div>
</div>

<div class="wrap">
  <div class="topbar">
    <div class="brand"><img src="__LOGO__" alt="MathRelaxing"><span class="bt">MathRelaxing</span></div>
    <button class="themetoggle" id="theme" aria-label="Toggle light or dark theme">Theme</button>
  </div>

  <p class="eyebrow">Undated Academic Planner · GoodNotes · Notability</p>
  <h1 class="lede">A guided look inside every section</h1>
  <p class="sub">Nine tools for the whole doctoral journey — step through them below, or hover a page to inspect the layout up close.</p>

  <div class="stage">
    <div class="device">
      <div class="screen" id="screen" title="Hover to zoom · click to enlarge">
        <div class="hint"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4-4"/><path d="M11 8v6M8 11h6"/></svg> Hover to zoom</div>
        <!-- images injected -->
        <div class="deck" id="deck"></div>
        <div class="loupe" id="loupe"></div>
      </div>
    </div>

    <div class="panel">
      <div class="reveal" id="reveal">
        <div class="cnt">SECTION <b id="cnum">01</b> / 09</div>
        <div class="slabel" id="slabel">The Dashboard</div>
        <h2 id="stitle">Every section, one tap away</h2>
        <p class="blurb" id="sblurb"></p>
        <ul class="cos" id="cos"></ul>
      </div>
      <div class="controls">
        <button class="btn" id="prev" aria-label="Previous section"><svg viewBox="0 0 24 24"><path d="M15 5l-7 7 7 7z"/></svg></button>
        <button class="btn primary" id="play" aria-label="Play or pause the tour">
          <svg id="playicon" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg><span id="playtxt">Play</span>
        </button>
        <button class="btn" id="next" aria-label="Next section"><svg viewBox="0 0 24 24"><path d="M9 5l7 7-7 7z"/></svg></button>
        <span class="stepname" id="stepname"></span>
      </div>
      <div class="dots" id="dots" role="tablist" aria-label="Sections"></div>
    </div>
  </div>

  <div class="foot">
    <span>136 hyperlinked pages · <b>iPad · Android · Windows</b></span>
    <span>mathrelaxing.store</span>
  </div>
</div>

<div class="lightbox" id="lightbox"><button class="x" id="lbx">Close ✕</button><img id="lbimg" alt="Planner page enlarged"></div>

<script>
const SECTIONS = __SECTIONS__;
const PAGES = __DATA__;
const DWELL = 6200;
let i = 0, playing = false, timer = null;

const screen = document.getElementById('screen');
const deck = document.getElementById('deck');
const loupe = document.getElementById('loupe');
const reveal = document.getElementById('reveal');
const dots = document.getElementById('dots');

// build page images + deck + dots
const imgs = SECTIONS.map((s, idx) => {
  const im = document.createElement('img');
  im.className = 'pg'; im.src = PAGES[s.key]; im.alt = s.label + ' page';
  im.loading = idx === 0 ? 'eager' : 'lazy';
  screen.insertBefore(im, deck); return im;
});
SECTIONS.forEach((s, idx) => {
  const d = document.createElement('i'); deck.appendChild(d);
  const b = document.createElement('button'); b.setAttribute('role','tab');
  b.setAttribute('aria-label', s.label); b.addEventListener('click', () => go(idx, true));
  dots.appendChild(b);
});
const deckBars = [...deck.children];
const dotBtns = [...dots.children];

const $ = id => document.getElementById(id);
function render(){
  const s = SECTIONS[i];
  imgs.forEach((im, idx) => { im.classList.toggle('on', idx===i); im.classList.remove('kb'); });
  void imgs[i].offsetWidth; imgs[i].classList.add('kb');
  $('cnum').textContent = String(i+1).padStart(2,'0');
  $('slabel').textContent = s.label;
  $('stitle').textContent = s.title;
  $('sblurb').textContent = s.blurb;
  const cos = $('cos'); cos.innerHTML = '';
  s.callouts.forEach(c => {
    const li = document.createElement('li');
    li.innerHTML = '<span class="tk"><svg viewBox="0 0 24 24" fill="none" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12l5 5L20 6"/></svg></span><span>'+c+'</span>';
    cos.appendChild(li);
  });
  $('stepname').textContent = s.label;
  dotBtns.forEach((b,idx)=> b.setAttribute('aria-current', idx===i ? 'true':'false'));
  deckBars.forEach((bar,idx)=>{ bar.classList.toggle('done', idx<i); bar.classList.toggle('cur', idx===i && playing); });
  // restart staged reveal
  reveal.classList.remove('play'); void reveal.offsetWidth; reveal.classList.add('play');
}
function go(n, user){
  i = (n + SECTIONS.length) % SECTIONS.length;
  render();
  if(user && playing){ schedule(); }
}
function schedule(){ clearTimeout(timer); if(!playing) return;
  deckBars.forEach((bar,idx)=> bar.classList.toggle('cur', idx===i));
  document.documentElement.style.setProperty('--dwell', DWELL+'ms');
  timer = setTimeout(()=> go(i+1, false), DWELL);
}
function setPlay(on){
  playing = on;
  $('playicon').innerHTML = on ? '<path d="M6 5h4v14H6zM14 5h4v14h-4z"/>' : '<path d="M8 5v14l11-7z"/>';
  $('playtxt').textContent = on ? 'Pause' : 'Play';
  if(on){ render(); schedule(); } else { clearTimeout(timer); deckBars.forEach(b=>b.classList.remove('cur')); }
}
$('prev').addEventListener('click', ()=> go(i-1, true));
$('next').addEventListener('click', ()=> go(i+1, true));
$('play').addEventListener('click', ()=> setPlay(!playing));
document.addEventListener('keydown', e=>{
  if(e.key==='ArrowRight'){ go(i+1,true);} else if(e.key==='ArrowLeft'){ go(i-1,true);}
  else if(e.key===' '){ e.preventDefault(); setPlay(!playing);}
  else if(e.key==='Escape'){ lightbox.classList.remove('on'); }
});

// loupe zoom
const ZOOM = 2.5;
let fine = window.matchMedia('(pointer:fine)').matches;
screen.addEventListener('mousemove', e=>{
  if(!fine) return;
  const r = screen.getBoundingClientRect();
  const x = e.clientX - r.left, y = e.clientY - r.top;
  if(x<0||y<0||x>r.width||y>r.height){ loupe.style.display='none'; return; }
  loupe.style.display='block';
  loupe.style.backgroundImage = 'url('+PAGES[SECTIONS[i].key]+')';
  loupe.style.backgroundSize = (r.width*ZOOM)+'px '+(r.height*ZOOM)+'px';
  const lp = 95; // half loupe
  loupe.style.left = (x-lp)+'px'; loupe.style.top = (y-lp)+'px';
  loupe.style.backgroundPosition = (-(x*ZOOM - lp))+'px '+(-(y*ZOOM - lp))+'px';
});
screen.addEventListener('mouseleave', ()=> loupe.style.display='none');

// lightbox
const lightbox = $('lightbox'), lbimg = $('lbimg');
screen.addEventListener('click', ()=>{ lbimg.src = PAGES[SECTIONS[i].key]; lightbox.classList.add('on'); });
$('lbx').addEventListener('click', e=>{ e.stopPropagation(); lightbox.classList.remove('on'); });
lightbox.addEventListener('click', ()=> lightbox.classList.remove('on'));

// theme toggle
const root = document.documentElement;
$('theme').addEventListener('click', ()=>{
  const cur = root.getAttribute('data-theme')
    || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark':'light');
  root.setAttribute('data-theme', cur==='dark' ? 'light':'dark');
});

// intro
const intro = $('intro');
function start(){ intro.classList.add('hide'); if(!playing) setPlay(true); }
$('begin').addEventListener('click', start);
setTimeout(()=>{ if(!intro.classList.contains('hide')) start(); }, 6000);

render();
</script>
"""

html = (HTML
        .replace("__SECTIONS__", json.dumps(SECTIONS, ensure_ascii=False))
        .replace("__DATA__", json.dumps(DATA))
        .replace("__LOGO__", LOGO))

out = '/home/user/Etsy_mathrelaxing/phd_planner/showcase.html'
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)
print('wrote', out, os.path.getsize(out)//1024, 'KB')
