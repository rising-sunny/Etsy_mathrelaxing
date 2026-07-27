"""record_demo.py — record the Etsy listing demo video of the prompt builder.
Drives prompt_studio.html in headless Chromium (Playwright), records a webm,
then convert to mp4 for Etsy (5-15s, silent, h264):
  ffmpeg -i in.webm -an -c:v libx264 -crf 22 -pix_fmt yuv420p -movflags +faststart out.mp4
(A full ffmpeg with libx264 is needed, e.g. `pip install imageio-ffmpeg`.)
"""
from playwright.sync_api import sync_playwright
import pathlib
CHROME="/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
url="file://"+str(pathlib.Path("ai_teacher_prompts/prompt_studio.html").resolve())
VW,VH=1080,1080
SCR="/tmp/claude-0/-home-user-Etsy-mathrelaxing/e24b7ec7-cf86-5f97-890f-aa4cef39fee4/scratchpad/vid"
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CHROME)
    ctx=b.new_context(viewport={'width':VW,'height':VH},
                      record_video_dir=SCR, record_video_size={'width':VW,'height':VH})
    pg=ctx.new_page(); pg.goto(url)
    pg.add_style_tag(content="#__c{position:fixed;z-index:99999;width:24px;height:24px;margin:-12px 0 0 -12px;border-radius:50%;background:rgba(178,58,46,.28);border:2.5px solid #b23a2e;pointer-events:none}")
    pg.evaluate("()=>{const c=document.createElement('div');c.id='__c';c.style.left='540px';c.style.top='540px';document.body.appendChild(c);addEventListener('mousemove',e=>{c.style.left=e.clientX+'px';c.style.top=e.clientY+'px'},true)}")
    def mv(loc):
        bx=loc.bounding_box(); pg.mouse.move(bx['x']+bx['width']/2, bx['y']+bx['height']/2, steps=24); pg.wait_for_timeout(160)
    def click(loc): mv(loc); loc.click()
    def typ(k,txt,d=58):
        el=pg.locator(f'[data-k="{k}"]'); mv(el); el.click(); el.type(txt,delay=d)
    pg.wait_for_timeout(900)
    click(pg.locator('.chip',has_text="STEM"))          # filter to STEM
    pg.wait_for_timeout(350)
    click(pg.locator('.pitem',has_text="3-Act math task"))
    pg.wait_for_timeout(350)
    pg.locator('[data-k="grade"]').select_option(index=4)  # 9-10
    pg.wait_for_timeout(250)
    typ("concept","Volume of cylinders")
    pg.wait_for_timeout(1100)                            # show live-assembled prompt
    click(pg.locator('#copy'))                           # copy -> "Copied ✓"
    pg.wait_for_timeout(1300)
    click(pg.locator('.chip',has_text="ASSESSMENT"))     # show breadth
    pg.wait_for_timeout(300)
    click(pg.locator('.pitem',has_text="misconception distractors"))
    pg.wait_for_timeout(250)
    typ("topic","Photosynthesis",50)
    pg.wait_for_timeout(1200)
    path=pg.video.path()
    ctx.close(); b.close()
print(path)
