"""Make the side-by-side BEFORE / AFTER image used in outreach.

Usage:
  python before_after.py <old-site-url> <new-site-url> out.jpg [accent-hex]
Example:
  python before_after.py https://old-site.example.com/ http://localhost:4812/ before-after.jpg "#1AAE9F"
"""
import asyncio, os, sys
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFont


async def grab(url, path):
    async with async_playwright() as p:
        kw = {'executable_path': os.environ['CHROME_PATH']} if os.environ.get('CHROME_PATH') else {}
        b = await p.chromium.launch(**kw)
        pg = await b.new_page(viewport={'width': 1440, 'height': 900})
        await pg.goto(url, wait_until='load', timeout=60000); await pg.wait_for_timeout(3000)
        await pg.screenshot(path=path); await b.close()


def font(size):
    for f in ['C:/Windows/Fonts/arialbd.ttf', '/System/Library/Fonts/Supplemental/Arial Bold.ttf', '/Library/Fonts/Arial Bold.ttf']:
        if os.path.exists(f): return ImageFont.truetype(f, size)
    return ImageFont.load_default()


if __name__ == '__main__':
    if len(sys.argv) < 4: sys.exit(__doc__)
    old, new, out = sys.argv[1:4]; accent = sys.argv[4] if len(sys.argv) > 4 else '#F4821F'
    asyncio.run(grab(old, '_before.png')); asyncio.run(grab(new, '_after.png'))
    W = 900
    a, c = Image.open('_before.png'), Image.open('_after.png')
    a = a.resize((W, int(a.height * W / a.width))); c = c.resize((W, int(c.height * W / c.width)))
    img = Image.new('RGB', (W * 2 + 30, a.height + 70), '#111122'); img.paste(a, (0, 70)); img.paste(c, (W + 30, 70))
    d = ImageDraw.Draw(img); f = font(32)
    d.text((20, 18), 'BEFORE', fill='#ffffff', font=f); d.text((W + 50, 18), 'AFTER', fill=accent, font=f)
    img.convert('RGB').save(out, quality=88); os.remove('_before.png'); os.remove('_after.png'); print('saved', out)
