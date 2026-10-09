"""Website-level 'is this business still alive?' signals.

For each URL: domain registration/renewal dates (RDAP), SSL certificate issue date,
LnwShop activity banners (owner last login, last shop update, shop opened), newest
year mentioned on the page, and social/LINE links to check by hand.

Usage:
  python alive_check.py https://site1.com http://shop.lnwshop.com ...
  python alive_check.py -f urls.txt
Output: one JSON object per line.
"""
import json, re, socket, ssl, sys, urllib.request, urllib.parse
from datetime import datetime, timezone

UA = {'User-Agent': 'Mozilla/5.0'}
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
TH_MONTHS = {'ม.ค.': 1, 'ก.พ.': 2, 'มี.ค.': 3, 'เม.ย.': 4, 'พ.ค.': 5, 'มิ.ย.': 6, 'ก.ค.': 7, 'ส.ค.': 8, 'ก.ย.': 9, 'ต.ค.': 10, 'พ.ย.': 11, 'ธ.ค.': 12}


def th_date(s):
    """'2 ก.ย. 2569' -> '2026-09-02' (Buddhist year)."""
    m = re.match(r'(\d{1,2})\s*(\S+\.)\s*(\d{4})', s.strip())
    if not m or m.group(2) not in TH_MONTHS: return s
    return f'{int(m.group(3)) - 543}-{TH_MONTHS[m.group(2)]:02d}-{int(m.group(1)):02d}'


def rdap(host):
    parts = host.split('.')
    if len(parts) > 2 and parts[-2] in ('lnwshop',): return {'note': 'subdomain of lnwshop.com, no own domain'}
    dom = '.'.join(parts[-3:]) if parts[-2] in ('co', 'in', 'or', 'ac', 'go') else '.'.join(parts[-2:])
    try:
        d = json.load(urllib.request.urlopen(urllib.request.Request(f'https://rdap.org/domain/{dom}', headers=UA), timeout=20))
        ev = {e['eventAction']: e['eventDate'][:10] for e in d.get('events', [])}
        return {'domain': dom, 'registered': ev.get('registration'), 'last_changed': ev.get('last changed'), 'expires': ev.get('expiration')}
    except Exception as e:
        return {'domain': dom, 'error': str(e)[:50]}


def cert(host):
    try:
        with socket.create_connection((host, 443), timeout=10) as s:
            with ssl.create_default_context().wrap_socket(s, server_hostname=host) as t:
                c = t.getpeercert()
        f = lambda k: datetime.strptime(c[k], '%b %d %H:%M:%S %Y %Z').date().isoformat()
        return {'ssl_issued': f('notBefore'), 'ssl_expires': f('notAfter')}
    except Exception as e:
        return {'ssl': 'none/invalid (' + str(e)[:40] + ')'}


def check(url):
    host = urllib.parse.urlparse(url).hostname
    out = {'url': url}
    try:
        h = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25, context=ctx).read().decode('utf-8', 'replace')
    except Exception as e:
        out['site'] = 'DOWN: ' + str(e)[:60]; h = ''
    m = re.search(r'ไม่ได้เข้าสู่ระบบเป็นระยะเวลา\s*<?[^0-9]*?(\d+)\s*(?:</[^>]+>)?\s*(วัน|เดือน|ปี)', h)
    if m: out['lnw_owner_last_login'] = f'{m.group(1)} {m.group(2)} ago'
    elif 'lnwshop' in h.lower() and 'ไม่ได้เข้าสู่ระบบ' not in h: out['lnw_owner_last_login'] = 'no inactivity banner (logged in recently)'
    m = re.search(r'ร้านค้าอัพเดท\s*([^<]{6,20})', h)
    if m: out['lnw_last_update'] = th_date(m.group(1))
    m = re.search(r'เปิดร้าน\s*([^<]{6,20})', h)
    if m: out['lnw_opened'] = th_date(m.group(1))
    yrs = [int(y) for y in re.findall(r'\b(20[0-2]\d)\b', h) if 2000 <= int(y) <= 2026]
    th_yrs = [int(y) - 543 for y in re.findall(r'\b(25[4-6]\d)\b', h) if 2543 <= int(y) <= 2569]
    if yrs or th_yrs: out['newest_year_on_page'] = max(yrs + th_yrs)
    socials = sorted(set(re.findall(r'(?:facebook\.com/[^"\'\s<>?]+|line\.me/[^"\'\s<>]+|lin\.ee/[^"\'\s<>]+|@[a-z0-9_.]{4,30}(?=[\s<"]))', h, re.I)))
    out['social'] = [s for s in socials if 'lnwshop' not in s.lower() and 'sharer' not in s][:5]
    out.update(rdap(host)); out.update(cert(host))
    return out


if __name__ == '__main__':
    args = sys.argv[1:]
    urls = open(args[1], encoding='utf-8').read().split() if args[:1] == ['-f'] else args
    if not urls: sys.exit(__doc__)
    sys.stdout.reconfigure(encoding='utf-8')
    for u in urls:
        print(json.dumps(check(u), ensure_ascii=False))
