"""Offline checks for the scoring fixes. Run: python tests/test_scoring.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from datetime import datetime
from score_sites import score_html
import alive_check

flags = lambda h: score_html(h, 'https://x.com')[2]

# viewport: any attribute order, quoting or case counts as present
for h in ['<meta name=viewport content=x>', '<META NAME="viewport">', '<meta content="w" name="viewport">']:
    assert 'no-viewport' not in flags(h), h
assert 'no-viewport' in flags('<html><body>old</body></html>')

# copyright ranges use the end year
assert '©' not in flags('<meta name="viewport">&copy; 2008 - 2025 Acme')
assert '©2010' in flags('<meta name="viewport">Copyright 2010 Acme')

# rdap no longer crashes on single-label hosts
assert 'note' in alive_check.rdap('localhost')

# newest year follows the clock: this year counts, next year (a price, a phone fragment) does not
y = datetime.now().year
class Page:
    def __init__(self, b): self.b = b
    def read(self): return self.b
alive_check.urllib.request.urlopen = lambda *a, **k: Page(f'<p>since {y}, call 0{y + 1}</p>'.encode())
alive_check.rdap = alive_check.cert = lambda host: {}
assert alive_check.check('https://x.com')['newest_year_on_page'] == y
# social: profile links only, no CSS/JSON-LD/filename/email noise, no share widgets, no look-alike domains
alive_check.urllib.request.urlopen = lambda *a, **k: Page(b'''<style>@media x{}</style><img src="logo@2x.png">
<script type="application/ld+json">{"@context":"x","@type":"Org"}</script> mail info@acme-dental.com
<a href="https://www.facebook.com/AcmeDental/">fb</a> <a href="https://instagram.com/acme.dental">ig</a>
<a href="https://www.facebook.com/sharer/sharer.php?u=x">share</a> <a href="https://netflix.com/title/1">n</a>''')
social = alive_check.check('https://x.com')['social']
assert social == ['facebook.com/AcmeDental', 'instagram.com/acme.dental'], social
print('ok')
