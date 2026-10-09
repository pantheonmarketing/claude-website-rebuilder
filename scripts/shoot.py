"""Verify a rebuilt site: full-page desktop + mobile screenshots of every page, horizontal-overflow
check, console errors, and a screen recording of the homepage scroll.

Usage:
  python shoot.py http://localhost:4812 index,services,portfolio,contact out_dir
Needs: pip install playwright && playwright install chromium
(or set CHROME_PATH to an existing chrome.exe / chromium binary)
"""
import asyncio, os, sys
from playwright.async_api import async_playwright

REVEAL = "document.querySelectorAll('[data-aos]').forEach(e=>e.classList.add('aos-animate'));"


async def main(base, pages, out):
    os.makedirs(out, exist_ok=True)
    async with async_playwright() as p:
        kw = {'executable_path': os.environ['CHROME_PATH']} if os.environ.get('CHROME_PATH') else {}
        b = await p.chromium.launch(**kw)
        for name, vp in [('desktop', {'width': 1440, 'height': 900}), ('mobile', {'width': 390, 'height': 844})]:
            ctx = await b.new_context(viewport=vp, is_mobile=(name == 'mobile'))
            pg = await ctx.new_page(); errs = []
            pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
            pg.on('pageerror', lambda e: errs.append(str(e)))
            for page in pages:
                await pg.goto(f'{base}/{page}.html', wait_until='networkidle'); await pg.wait_for_timeout(1500)
                await pg.evaluate(REVEAL)
                for y in range(0, 9000, 600):  # trigger counters / lazy stuff
                    await pg.evaluate(f'window.scrollTo(0,{y})'); await pg.wait_for_timeout(120)
                await pg.evaluate('window.scrollTo(0,0)'); await pg.wait_for_timeout(2200)
                ox = await pg.evaluate('document.documentElement.scrollWidth - innerWidth')
                await pg.screenshot(path=os.path.join(out, f'{name}-{page}.png'), full_page=True)
                print(f'{name:8} {page:12} overflowX={ox}' + ('   <-- FIX' if ox > 0 else ''))
            print(f'{name} console errors: {errs or "none"}')
            await ctx.close()
        ctx = await b.new_context(viewport={'width': 1440, 'height': 900}, record_video_dir=os.path.join(out, '_vid'))
        pg = await ctx.new_page(); await pg.goto(base + '/', wait_until='networkidle'); await pg.wait_for_timeout(3000)
        for _ in range(40):
            await pg.mouse.wheel(0, 160); await pg.wait_for_timeout(180)
        path = await pg.video.path(); await ctx.close()
        os.replace(path, os.path.join(out, 'home-scroll.webm')); print('video:', os.path.join(out, 'home-scroll.webm'))
        await b.close()


if __name__ == '__main__':
    if len(sys.argv) < 4: sys.exit(__doc__)
    asyncio.run(main(sys.argv[1].rstrip('/'), sys.argv[2].split(','), sys.argv[3]))
