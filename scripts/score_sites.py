"""Score business websites for how outdated they look. Higher score = better rebuild prospect.

Usage:
  python score_sites.py https://site1.com https://site2.com ...
  python score_sites.py -f urls.txt        (one URL per line)
"""
import re, ssl, sys, urllib.request, concurrent.futures as cf

ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
BUILDERS = r'lnwshop|readyplanet|wix|weebly|tarad|jimdo'


def score(url):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=20, context=ctx)
        h = r.read(600000).decode('utf-8', 'replace'); final = r.geturl()
    except Exception as e:
        return (-1, url, 'ERROR ' + str(e)[:60])
    s, f = 0, []
    if 'name="viewport"' not in h and "name='viewport'" not in h: s += 3; f.append('no-viewport')
    t = len(re.findall(r'<table', h, re.I))
    if t > 3: s += 2; f.append(f'tables:{t}')
    yrs = [int(y) for y in re.findall(r'(?:©|&copy;|copyright)\D{0,15}((?:19|20)\d\d)', h, re.I)]
    if yrs and max(yrs) < 2022: s += 2; f.append(f'©{max(yrs)}')
    jq = re.search(r'jquery[-.]?(\d)\.(\d+)', h, re.I)
    if jq and int(jq.group(1)) < 2: s += 1; f.append('old-jquery')
    if final.startswith('http:'): s += 2; f.append('no-https')
    if re.search(r'<font|<marquee|<center>|\.swf|bgcolor=', h, re.I): s += 2; f.append('font/marquee')
    g = re.search(r'name="generator" content="([^"]+)', h, re.I)
    if g: f.append('gen:' + g.group(1)[:25])
    b = re.search(BUILDERS, h, re.I)
    if b: f.append('builder:' + b.group(0))
    f.append('FORM' if re.search(r'<form[^>]*>[\s\S]{0,4000}?<textarea', h, re.I) else 'noform')
    return (s, final, ' '.join(f))


if __name__ == '__main__':
    args = sys.argv[1:]
    urls = open(args[1], encoding='utf-8').read().split() if args[:1] == ['-f'] else args
    if not urls: sys.exit(__doc__)
    with cf.ThreadPoolExecutor(10) as ex:
        for s, u, f in sorted(ex.map(score, urls), reverse=True):
            print(s, u, f)
