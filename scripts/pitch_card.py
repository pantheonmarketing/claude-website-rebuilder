"""Owner-facing BEFORE / AFTER pitch card: desktop and phone views of the old site vs the new one.

Usage:
  python pitch_card.py <old-url> <new-url> "<Business name>" <out.jpg> [--lang th|en] [--accent "#hex"]
Example:
  python pitch_card.py https://old-site.example.com/ http://localhost:4812/ "Example Dental Clinic" card.jpg --lang en --accent "#1AAE9F"
Set CHROME_PATH to use an existing Chromium. Needs: playwright, pillow.
"""
import asyncio, os, sys
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFont, ImageFilter

LABELS = {
    'th': ('เว็บไซต์ปัจจุบัน', 'เว็บไซต์ใหม่', 'ตัวอย่างเว็บไซต์ใหม่ ที่ออกแบบให้คุณโดยเฉพาะ  ·  บนคอมพิวเตอร์และมือถือ'),
    'en': ('Your website today', 'Your new website', 'A new website preview, made for you  ·  on a computer and on a phone'),
}


async def grab(url, prefix):
    async with async_playwright() as p:
        kw = {'executable_path': os.environ['CHROME_PATH']} if os.environ.get('CHROME_PATH') else {}
        b = await p.chromium.launch(**kw)
        for name, vp, mob in [('d', {'width': 1440, 'height': 900}, False), ('m', {'width': 390, 'height': 844}, True)]:
            ctx = await b.new_context(viewport=vp, is_mobile=mob, device_scale_factor=2 if mob else 1)
            pg = await ctx.new_page()
            await pg.goto(url, wait_until='load', timeout=60000); await pg.wait_for_timeout(3500)
            await pg.screenshot(path=f'{prefix}-{name}.png')
            await ctx.close()
        await b.close()


def font(size, bold=True):
    for f in (['C:/Windows/Fonts/LeelaUIb.ttf', 'C:/Windows/Fonts/leelawdb.ttf'] if bold else ['C:/Windows/Fonts/LeelawUI.ttf', 'C:/Windows/Fonts/leelawad.ttf']) + \
             ['/System/Library/Fonts/Supplemental/Thonburi.ttc', '/usr/share/fonts/truetype/noto/NotoSansThai-Bold.ttf']:
        if os.path.exists(f): return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def framed(img, w, radius, border):
    img = img.convert('RGB'); img = img.resize((w, int(img.height * w / img.width)), Image.LANCZOS)
    mask = Image.new('L', img.size, 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, *img.size), radius, fill=255)
    out = Image.new('RGBA', (img.width + border * 2, img.height + border * 2), (0, 0, 0, 0))
    ImageDraw.Draw(out).rounded_rectangle((0, 0, *out.size), radius + border, fill=(255, 255, 255, 255) if border else (0, 0, 0, 0))
    out.paste(img, (border, border), mask)
    return out


def shadow(canvas, box, radius):
    sh = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((box[0] + 6, box[1] + 14, box[2] + 6, box[3] + 14), radius, fill=(0, 0, 0, 90))
    canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))


def build(name, lang, accent, out):
    lb = LABELS[lang]
    W, colw, gap, ytop = 1800, 790, 80, 190
    x0s = (70, 70 + colw + gap)
    c = Image.new('RGBA', (W, 1400), (17, 19, 26, 255))
    d = ImageDraw.Draw(c)
    d.rectangle((0, 0, W, 8), fill=accent)
    d.text((70, 44), name, font=font(54), fill='white')
    d.text((72, 120), lb[2], font=font(26, False), fill=(150, 158, 172))
    bottom = 0
    for i, (tag, pre) in enumerate([(lb[0], '_old'), (lb[1], '_new')]):
        x = x0s[i]
        pill_col = (70, 76, 90) if i == 0 else accent
        tw = d.textlength(tag, font=font(28))
        d.rounded_rectangle((x, ytop, x + tw + 44, ytop + 50), 25, fill=pill_col)
        d.text((x + 22, ytop + 6), tag, font=font(28), fill='white')
        desk = framed(Image.open(pre + '-d.png'), colw, 14, 0)
        dy = ytop + 76
        shadow(c, (x, dy, x + desk.width, dy + desk.height), 14); c.alpha_composite(desk, (x, dy))
        phone = framed(Image.open(pre + '-m.png'), 240, 26, 8)
        phone = phone.crop((0, 0, phone.width, min(phone.height, 520)))
        px, py = x + colw - phone.width - 24, dy + desk.height - 190
        shadow(c, (px, py, px + phone.width, py + phone.height), 30); c.alpha_composite(phone, (px, py))
        bottom = max(bottom, py + phone.height)
    c = c.crop((0, 0, W, bottom + 60))
    c.convert('RGB').save(out, quality=90)


if __name__ == '__main__':
    a = sys.argv[1:]
    if len(a) < 4: sys.exit(__doc__)
    old, new, name, out = a[:4]
    lang = a[a.index('--lang') + 1] if '--lang' in a else 'en'
    accent = a[a.index('--accent') + 1] if '--accent' in a else '#C9A84C'
    asyncio.run(grab(old, '_old')); asyncio.run(grab(new, '_new'))
    build(name, lang, accent, out)
    for f in ['_old-d.png', '_old-m.png', '_new-d.png', '_new-m.png']: os.remove(f)
    print('saved', out)
