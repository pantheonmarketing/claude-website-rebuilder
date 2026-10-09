"""Pull the real content off a prospect's old site: text, internal links, image URLs.
Optionally downloads the images so you can pick usable ones.

Usage:
  python scrape_site.py https://oldsite.com [page2-path page3-path ...] [--download out_dir]
Example:
  python scrape_site.py https://old-site.example.com/ about/ contact/ --download raw
"""
import html, os, re, sys, urllib.request, urllib.parse

UA = {'User-Agent': 'Mozilla/5.0'}


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode('utf-8', 'replace')


def text_of(h):
    t = re.sub(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>', '', h)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args: sys.exit(__doc__)
    out = None
    if '--download' in args:
        i = args.index('--download'); out = args[i + 1]; args = args[:i] + args[i + 2:]
    base, pages = args[0], [''] + args[1:]
    host = urllib.parse.urlparse(base).netloc
    imgs = set()
    sys.stdout.reconfigure(encoding='utf-8')
    for p in pages:
        url = urllib.parse.urljoin(base, p)
        h = get(url)
        print(f'\n===== {url}\n{text_of(h)[:4000]}')
        if p == '':
            links = sorted(set(l for l in re.findall(r'href="([^"#?]+)"', h) if host in l or l.startswith('/')))
            print('\nLINKS:\n' + '\n'.join(urllib.parse.unquote(l) for l in links[:80]))
        imgs |= set(urllib.parse.urljoin(url, s) for s in re.findall(r'(?:src|data-src|href)="([^"]+\.(?:jpe?g|png|webp))"', h, re.I))
    print(f'\nIMAGES ({len(imgs)}):\n' + '\n'.join(sorted(imgs)))
    if out:
        os.makedirs(out, exist_ok=True)
        for i, u in enumerate(sorted(imgs)):
            try:
                data = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read()
                if len(data) > 15000:
                    open(os.path.join(out, f'{i:02d}-' + os.path.basename(urllib.parse.urlparse(u).path)[-40:]), 'wb').write(data)
            except Exception:
                pass
        print(f'\nDownloaded to {out}/ (files under 15KB skipped)')
