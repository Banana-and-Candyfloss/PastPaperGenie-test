#!/usr/bin/env python3
"""Run from the repo root:  python tools/build.py
Reads data/games.csv and writes every page, the sitemap and assets/games-data.js."""
import csv, html, json
from pathlib import Path
from urllib.parse import urlparse

SITE = "https://pastpapergenie.co.uk"   # no trailing slash
EMAIL = ""   # add one when you have it, e.g. "you@example.com"
SPONSOR = None   # later: {"img": "assets/mine.png", "href": "https://...", "alt": "what it is"}

CONTACT = (f'write to <a href="mailto:{html.escape(EMAIL)}">{html.escape(EMAIL)}</a>' if EMAIL
           else "contact details are being set up and will be here soon")
ROOT = Path(__file__).resolve().parent.parent
BASE = urlparse(SITE).path
e = html.escape
rows = list(csv.DictReader(open(ROOT / "data/games.csv", encoding="utf-8")))
for r in rows:
    r["tags"] = [t for t in r["tags"].split("|") if t]
play = [r for r in rows if r["mode"] in ("embed", "hosted")]
other = [r for r in rows if r["mode"] in ("link", "pending")]
urls = []

def write(path, text):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    if path.endswith("index.html"):
        urls.append(path[:-10])

def shell(path, title, desc, body, slug=""):
    up = "../" * path.count("/")
    side = ""
    if SPONSOR:
        side += (f'<div class="sponsor"><a href="{e(SPONSOR["href"])}" rel="sponsored noopener">'
                 f'<img src="{up}{e(SPONSOR["img"])}" alt="{e(SPONSOR["alt"])}"></a></div>')
    side += '<div class="box" id="recs"></div><div class="box" id="recent"></div>'
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE}/{path[:-10] if path.endswith("index.html") else path}">
<link rel="stylesheet" href="{up}assets/style.css">
</head>
<body data-up="{up}" data-slug="{slug}">
<div id="page">
<header>
<p class="logo"><a href="{up}">pastpapergenie <small>v3</small></a></p>
<p class="blurb">Browser games. Only ones I'm allowed to show.</p>
<nav><a href="{up}">Games</a> <a href="{up}recommended/">Recommended</a> <a href="{up}saved/">Saved</a> <a href="{up}about/">About</a>
<input id="q" type="search" placeholder="search titles or tags" aria-label="Search games"></nav>
</header>
<div id="cols"><main>
{body}
</main><aside>{side}</aside></div>
<footer><p>Licence problem or takedown request: {CONTACT}. Saved games stay in your browser.</p></footer>
</div>
<script src="{up}assets/games-data.js"></script>
<script src="{up}assets/app.js"></script>
</body>
</html>
'''

def tile(g, up):
    if g.get("img"):
        return f'<img class="tile" src="{up}{e(g["img"])}" alt="" width="48" height="36">'
    n = sum(ord(c) * 31 for c in g["slug"]) % 40
    ini = "".join(w[0] for w in g["title"].split())[:3]
    return f'<span class="tile" style="background:hsl({85 + n} 30% 28%)">{e(ini)}</span>'

def table(gs, up):
    out = '<table><tr><th></th><th>Title</th><th class="hm">Players</th><th></th></tr>'
    for g in gs:
        s = (g["title"] + " " + " ".join(g["tags"])).lower()
        out += (f'<tr data-s="{e(s)}"><td>{tile(g, up)}</td><td class="t"><a href="{up}games/{g["slug"]}/">{e(g["title"])}</a>'
                f'<br><span class="small">{e(", ".join(g["tags"]))}</span></td><td class="hm small">{e(g["players"])}</td>'
                f'<td><button data-fav="{g["slug"]}">save</button></td></tr>')
    return out + "</table>"

alltags = sorted({t for g in play for t in g["tags"]})
tagbar = lambda up: '<p class="tags">' + " ".join(f'<a href="{up}tags/{t}/">{e(t)}</a>' for t in alltags) + "</p>"

# home
picks = [g for g in play if g["pick"] == "1"]
write("index.html", shell("index.html", "pastpapergenie v3: free browser games",
    "Free browser games that run in your tab. Puzzle, shooter, chess and text games, each checked for licence.",
    "<h1>Browser games</h1><p>I collect games that I'm allowed to host or embed, and the list grows when I've checked one. "
    "Nothing to install and no account. Your saved games and recent plays stay in your own browser.</p>"
    "<h2>Picked</h2>" + table(picks, "") + "<h2>All games</h2>" + tagbar("") + table(play, "")))

# games
for g in play:
    up = "../../"
    if g["mode"] == "hosted":
        src, sb = f'{up}play/{g["slug"]}/index.html', "allow-scripts allow-pointer-lock allow-fullscreen"
    else:
        src, sb = g["url"], "allow-scripts allow-same-origin allow-pointer-lock allow-fullscreen"
    paras = "".join(f"<p>{e(p)}</p>" for p in g["blurb"].split("||"))
    ctrl = f"<h2>Controls</h2><p>{e(g['controls'])}</p>" if g["controls"] else ""
    rel = [x for x in play if x is not g and set(x["tags"]) & set(g["tags"])][:5]
    relh = "<h2>More like this</h2><ul>" + "".join(f'<li><a href="{up}games/{x["slug"]}/">{e(x["title"])}</a></li>' for x in rel) + "</ul>" if rel else ""
    body = (f'<p class="small"><a href="{up}">All games</a></p><h1>{e(g["title"])}</h1>'
            f'<div class="play"><iframe src="{e(src)}" title="{e(g["title"])}" sandbox="{sb}" referrerpolicy="no-referrer" '
            f'loading="lazy" allow="fullscreen; gamepad" allowfullscreen></iframe></div>'
            f'<p><button data-fav="{g["slug"]}">save</button> <a class="small" href="{e(g["url"])}" target="_blank" rel="noopener noreferrer">open on its own page</a></p>'
            f'{paras}{ctrl}<dl><dt>Players</dt><dd>{e(g["players"])}</dd><dt>Tags</dt><dd>{e(", ".join(g["tags"]))}</dd>'
            f'<dt>Made by</dt><dd>{e(g["credit"])}</dd><dt>Licence</dt><dd>{e(g["license"])}</dd>'
            f'<dt>Source</dt><dd><a href="{e(g["source"])}" target="_blank" rel="noopener">{e(g["source"])}</a></dd></dl>{relh}')
    d = g["blurb"].split("||")[0]
    d = d if len(d) <= 155 else d[:155].rsplit(" ", 1)[0] + "..."
    write(f'games/{g["slug"]}/index.html', shell(f'games/{g["slug"]}/index.html', f'{g["title"]}: play online | pastpapergenie', d, body, g["slug"]))

# tags
for t in alltags:
    gs = [g for g in play if t in g["tags"]]
    write(f"tags/{t}/index.html", shell(f"tags/{t}/index.html", f"{t} games | pastpapergenie",
        f"Browser games tagged {t}.", f'<h1>{e(t)} games</h1>' + table(gs, "../../")))

# recommended (link-outs only)
li = ""
for g in other:
    li += (f'<li><a href="{e(g["url"] or g["source"])}" target="_blank" rel="noopener">{e(g["title"])}</a>: {e(g["blurb"])} '
           f'<span class="small">Players: {e(g["players"])}. Licence: {e(g["license"])}</span></li>')
write("recommended/index.html", shell("recommended/index.html", "Recommended games elsewhere | pastpapergenie",
    "Open-source games and projects worth a look that don't run on this site yet.",
    "<h1>Recommended, but not here yet</h1><p>These need their own game files, a server, or I haven't finished checking them. "
    "Every link goes to the project's own page. I don't copy them.</p><ul>" + li + "</ul>"))

write("saved/index.html", shell("saved/index.html", "Saved games | pastpapergenie", "Your saved games.",
    '<h1>Saved games</h1><div id="savedlist"></div>'))
write("about/index.html", shell("about/index.html", "About | pastpapergenie", "Who runs this site and how to reach me.",
    "<h1>About</h1><p>This is a small game site I run myself. Games here are open source, free to share, or shown with the maker's say-so. "
    "Some are embedded from the maker's own page instead of copied, inside a sandboxed frame that sends no referrer.</p>"
    "<p>Saved games and your recent plays are kept in your browser. I don't get them and there's no account.</p>"
    f"<p>If you made something here and want it gone, or you want your game added: {CONTACT}.</p>"))
write("404.html", shell("404.html", "Not found | pastpapergenie", "Page not found.",
    f'<h1>Not found</h1><p>No page at that address. <a href="{BASE}/">Back to the games</a>.</p>').replace('href="assets', f'href="{BASE}/assets').replace('src="assets', f'src="{BASE}/assets'))

(ROOT / "assets/games-data.js").write_text("const GAMES = " + json.dumps(
    [{"slug": g["slug"], "title": g["title"], "tags": g["tags"], "pick": g["pick"] == "1"} for g in play]) + ";\n", encoding="utf-8")
(ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    "".join(f"<url><loc>{SITE}/{u}</loc></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")
(ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
print(len(play), "playable,", len(other), "recommended,", len(urls), "pages")
