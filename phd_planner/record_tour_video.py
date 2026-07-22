import asyncio, os, glob
from playwright.async_api import async_playwright
URL='file:///home/user/Etsy_mathrelaxing/phd_planner/showcase.html'
OUTDIR='/tmp/phd_pages/vids'
os.makedirs(OUTDIR, exist_ok=True)

async def zoom_sweep(pg, box, dur):
    steps=16
    x0,y0=box['x']+box['width']*0.30, box['y']+box['height']*0.32
    x1,y1=box['x']+box['width']*0.70, box['y']+box['height']*0.62
    for k in range(steps+1):
        t=k/steps
        await pg.mouse.move(x0+(x1-x0)*t, y0+(y1-y0)*t, steps=1)
        await pg.wait_for_timeout(int(dur*1000/steps))
    await pg.mouse.move(box['x']-40, box['y']-40)

async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
        ctx=await b.new_context(viewport={'width':1280,'height':720}, color_scheme='dark',
                                record_video_dir=OUTDIR, record_video_size={'width':1280,'height':720})
        pg=await ctx.new_page(); await pg.goto(URL)
        await pg.wait_for_timeout(2000)       # intro
        await pg.click('#begin'); await pg.wait_for_timeout(250)
        await pg.click('#play')               # pause built-in autoplay
        box=await pg.locator('#screen').bounding_box()
        await pg.wait_for_timeout(1200)        # s1 read
        await zoom_sweep(pg, box, 1.0)         # quick zoom accent
        for s in range(2,10):                  # s2..s9
            await pg.click('#next')
            await pg.wait_for_timeout(1250)
        await pg.wait_for_timeout(400)
        await ctx.close(); await b.close()
    v=sorted(glob.glob(OUTDIR+'/*.webm'), key=os.path.getmtime)
    print('VIDEO:', v[-1])
asyncio.run(main())
