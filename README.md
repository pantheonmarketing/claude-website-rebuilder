# Claude Website Rebuilder

A free Claude Code skill that finds local businesses with ugly, outdated websites and rebuilds them as premium, modern websites, then makes a before/after image you can send the owner.

What it does, step by step:

1. **Finds prospects:** searches for businesses in your niche and city and scores their websites for how outdated they look.
2. **Checks they are alive:** Google Maps reviews, owner posts, domain and SSL dates, so you only build for busy businesses.
3. **Harvests their real content:** services, phone numbers, address and photos from the old site.
4. **Makes AI hero images** where their own photos fall short.
5. **Builds a 4-page site:** home, services, portfolio or team, contact, with animations, mobile layout and click-to-call.
6. **Checks its own work:** desktop and mobile screenshots, no sideways scrolling, no console errors.
7. **Makes the pitch:** a BEFORE / AFTER card showing their old site next to the new one, on a computer and a phone.

## Install

You need [Claude Code](https://claude.com/claude-code) and Python 3.

```bash
git clone https://github.com/pantheonmarketing/claude-website-rebuilder.git
cd claude-website-rebuilder
pip install playwright pillow
playwright install chromium
```

Add the skill to Claude Code:

```bash
# macOS / Linux
mkdir -p ~/.claude/skills && cp -r skills/website-rebuilder ~/.claude/skills/
```

```powershell
# Windows (PowerShell)
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
Copy-Item -Recurse skills\website-rebuilder "$HOME\.claude\skills\"
```

## Use it

Open Claude Code **inside this folder** (so it can run the scripts) and say:

> Use the website-rebuilder skill: find an ugly old website for a dental clinic in Austin and rebuild it.

Or, if you already have a business in mind:

> Use the website-rebuilder skill on https://their-old-site.com

Claude will show you the best prospect first and only build after you say yes.

## What's in here

| Path | What |
|---|---|
| `skills/website-rebuilder/SKILL.md` | The skill: find, check, harvest, build, verify, pitch |
| `scripts/score_sites.py` | Score a list of URLs for how outdated they look |
| `scripts/alive_check.py` | Is the business still alive? Domain, SSL, site activity, socials |
| `scripts/scrape_site.py` | Pull text, links and images off an old site |
| `scripts/shoot.py` | Desktop + mobile full-page screenshots, overflow and console check, scroll video |
| `scripts/before_after.py` | Side-by-side BEFORE / AFTER image |
| `scripts/pitch_card.py` | Owner-facing pitch card (desktop + phone, old vs new, Thai or English labels) |

## Good manners

- Testimonials and ratings you could not verify stay marked as samples until the owner gives you real ones.
- Only show a business's old website publicly (ads, posts) with their permission.
- Preview sites you deploy should be `noindex` so they don't compete with the business in Google.

## Credits

Made by [Jonny West](https://www.instagram.com/officialjonnywest/) / The AI CEOs. Design approach inspired by Albert Olgaard's free Claude skills.

MIT licence. See `LICENSE`.
