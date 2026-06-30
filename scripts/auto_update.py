"""
GameVault Auto-Updater (GameSpot Redesign)
Runs daily via GitHub Actions. Fetches gaming news, free games, GTA 6 updates
and generates new HTML pages. Commits changes to trigger Cloudflare deploy.
"""
import os, sys, json, hashlib, re, html as html_mod
from datetime import datetime, timezone
from xml.etree import ElementTree
from urllib.request import urlopen, Request
from urllib.error import URLError

SITE_URL = "https://gamevault2-9tj.pages.dev"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HEADER = '''<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{title}</title><meta name="description" content="{desc}"><meta name="robots" content="index, follow"><meta name="date" content="{date}"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Kanit:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet"><style>
*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#00191D;color:#e8e8e8;line-height:1.6}}.container{{max-width:1100px;margin:auto;padding:0 24px}}header{{background:#0a2428;border-bottom:1px solid #1a3a40;position:sticky;top:0;z-index:100}}.header-inner{{display:flex;justify-content:space-between;align-items:center;height:56px}}.logo{{font-family:'Kanit',sans-serif;font-size:22px;font-weight:800;color:#FFC501;text-decoration:none;text-transform:uppercase;letter-spacing:1px}}.logo span{{color:#fff}}nav{{display:flex;gap:2px}}nav a{{font-family:'Kanit',sans-serif;color:#9ab0b4;text-decoration:none;padding:17px 14px;font-size:13px;font-weight:500;border-bottom:2px solid transparent;transition:.2s}}nav a:hover{{color:#FFC501;background:rgba(255,197,1,0.06);border-bottom-color:#FFC501}}.trending-bar{{background:#0d2b30;border-bottom:1px solid #1a3a40;padding:8px 0;overflow:hidden;white-space:nowrap}}.trending-bar .container{{display:flex;align-items:center;gap:0}}.trending-bar .label{{font-family:'Kanit',sans-serif;color:#FFC501;font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-right:16px;flex-shrink:0}}.trending-bar .scroll-wrap{{overflow-x:auto;white-space:nowrap;scrollbar-width:none;-ms-overflow-style:none}}.trending-bar .scroll-wrap::-webkit-scrollbar{{display:none}}.trending-bar a{{display:inline-block;color:#7aaab2;text-decoration:none;font-size:12px;margin-right:20px;transition:.2s;white-space:nowrap}}.trending-bar a:hover{{color:#FFC501}}.trending-bar a::before{{content:"/ ";color:#3a6a72;margin-right:4px}}.ad-box{{background:#0a2428;border:1px dashed #1a3a40;padding:16px;text-align:center;margin:20px 0;min-height:90px;display:flex;align-items:center;justify-content:center;color:#3a6a72;font-size:13px}}h1{{font-family:'Kanit',sans-serif;font-size:32px;font-weight:700;margin:28px 0 6px;color:#fff;line-height:1.15}}h2{{font-family:'Kanit',sans-serif;color:#FFC501;font-size:18px;font-weight:600;margin:24px 0 10px;text-transform:uppercase;letter-spacing:0.5px}}h3{{font-family:'Kanit',sans-serif;color:#fff;font-size:16px;margin:14px 0 6px;font-weight:500}}p{{margin-bottom:10px;color:#9ab0b4;font-size:14px;line-height:1.7}}ul{{margin:8px 0 16px 18px;color:#9ab0b4}}li{{margin-bottom:4px;font-size:14px}}a{{color:#9ab0b4}}a:hover{{color:#FFC501}}.hero{{background:linear-gradient(135deg,#0d2b30 0%,#00191D 100%);border:1px solid #1a3a40;padding:36px 32px;margin-bottom:24px;position:relative}}.hero .hero-tag{{font-family:'Kanit',sans-serif;display:inline-block;background:#FFC501;color:#00191D;padding:2px 10px;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px}}.hero h2{{font-family:'Kanit',sans-serif;font-size:24px;font-weight:700;color:#fff;margin-bottom:4px;line-height:1.2;text-transform:none;letter-spacing:0}}.hero h2 a{{color:#fff;text-decoration:none}}.hero h2 a:hover{{color:#FFC501}}.hero p{{color:#7aaab2;font-size:13px;margin-bottom:0}}.article{{background:#0a2428;border:1px solid #1a3a40;padding:20px 24px;margin:12px 0;transition:border-color .2s}}.article:hover{{border-color:#FFC501}}.article h3{{margin-bottom:4px;font-size:15px}}.article h3 a{{font-family:'Kanit',sans-serif;color:#fff;text-decoration:none;font-weight:500;font-size:16px;line-height:1.3;display:block}}.article h3 a:hover{{color:#FFC501}}.article p{{color:#7aaab2;font-size:13px;margin-bottom:4px;line-height:1.5}}.article .source{{color:#4a7a82;font-size:11px;margin-top:6px}}.card{{background:#0a2428;border:1px solid #1a3a40;padding:20px 24px;margin:12px 0;transition:border-color .2s;text-decoration:none;color:inherit;display:block}}.card:hover{{border-color:#FFC501}}.card h3{{font-family:'Kanit',sans-serif;color:#fff;margin-bottom:6px;font-size:16px;font-weight:500}}.card p{{color:#7aaab2;font-size:13px;margin-bottom:4px}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px;margin:20px 0 30px}}.post-meta{{color:#4a7a82;font-size:13px;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid #1a3a40}}.tag{{display:inline-block;background:rgba(255,197,1,0.12);color:#FFC501;padding:2px 8px;font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-right:4px;font-family:'Kanit',sans-serif}}.source-badge{{display:inline-block;background:rgba(255,197,1,0.12);color:#FFC501;font-size:10px;font-weight:600;text-transform:uppercase;padding:2px 8px;letter-spacing:0.5px;margin-bottom:6px;font-family:'Kanit',sans-serif}}.score-badge{{display:inline-flex;align-items:center;justify-content:center;width:36px;height:36px;background:#FFC501;color:#00191D;font-family:'Kanit',sans-serif;font-weight:700;font-size:15px;flex-shrink:0;margin-right:12px}}.related{{background:#0a2428;border:1px solid #1a3a40;padding:24px;margin:30px 0}}.related h3{{font-family:'Kanit',sans-serif;color:#FFC501;margin-bottom:12px;font-size:14px;text-transform:uppercase;letter-spacing:1px}}.related a{{display:block;color:#7aaab2;text-decoration:none;padding:6px 0;font-size:13px;border-bottom:1px solid #1a3a40}}.related a:hover{{color:#FFC501}}.newsletter{{background:linear-gradient(135deg,#0a2428 0%,#0d2b30 100%);border:1px solid #1a3a40;padding:28px 32px;text-align:center;margin:24px 0}}.newsletter h3{{font-family:'Kanit',sans-serif;color:#FFC501;font-size:16px;margin-bottom:4px;text-transform:uppercase;letter-spacing:1px}}.newsletter p{{color:#7aaab2;font-size:13px;margin-bottom:14px}}.newsletter .btn{{display:inline-block;background:#FFC501;color:#00191D;padding:10px 28px;font-family:'Kanit',sans-serif;font-weight:600;font-size:13px;text-decoration:none;text-transform:uppercase;letter-spacing:1px;transition:background .2s}}.newsletter .btn:hover{{background:#e6b001}}.tip-box{{background:#0a2428;border-left:3px solid #FFC501;padding:14px 18px;margin:16px 0;font-size:14px;color:#7aaab2}}.btn{{display:inline-block;background:#FFC501;color:#00191D;padding:10px 24px;font-family:'Kanit',sans-serif;font-weight:600;font-size:13px;text-decoration:none;text-transform:uppercase;letter-spacing:1px;transition:background .2s}}.btn:hover{{background:#e6b001}}footer{{background:#0a2428;border-top:1px solid #1a3a40;margin-top:40px}}.footer-inner{{padding:40px 0 0}}.footer-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:28px;margin-bottom:24px}}footer h4{{font-family:'Kanit',sans-serif;color:#FFC501;font-size:12px;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:12px}}footer a{{display:block;color:#5a8a92;text-decoration:none;font-size:13px;padding:3px 0;transition:color .2s}}footer a:hover{{color:#FFC501}}.footer-bottom{{text-align:center;padding:16px;border-top:1px solid #1a3a40;color:#3a6a72;font-size:12px}}.footer-logo{{font-family:'Kanit',sans-serif;font-size:18px;font-weight:800;color:#FFC501;text-decoration:none;text-transform:uppercase;letter-spacing:1px;display:block;margin-bottom:6px}}.footer-logo span{{color:#fff}}.footer-social{{display:flex;gap:8px;margin-top:8px}}.footer-social a{{display:inline-flex;align-items:center;justify-content:center;width:30px;height:30px;background:rgba(255,197,1,0.08);color:#FFC501;font-size:12px;transition:background .2s;text-decoration:none}}.footer-social a:hover{{background:rgba(255,197,1,0.25)}}.footer-desc{{color:#4a7a82;font-size:12px;margin-bottom:12px;line-height:1.5}}
</style></head>
<body>
<header><div class="container"><div class="header-inner"><a href="/" class="logo">Game<span>Vault</span></a><nav>
<a href="/">Home</a><a href="/gta-6/">GTA 6</a><a href="/gaming-setups/">Setups</a><a href="/free-games/">Free Games</a><a href="/gaming-codes/">Codes</a><a href="/news/">News</a>
</nav></div></div></header>
<div class="trending-bar"><div class="container"><span class="label">Trending</span><div class="scroll-wrap"><a href="/gta-6/">GTA 6</a><a href="/gaming-setups/budget-pc/">Budget PC Build</a><a href="/free-games/">Free Games</a><a href="/gaming-codes/">Codes</a><a href="/gta-6/trailers/">GTA 6 Trailer</a><a href="/gta-6/release-date/">Release Date</a><a href="/news/">Gaming News</a></div></div></div>
<div class="container">'''

FOOTER = '</div>\n<footer><div class="footer-inner container"><div class="footer-grid"><div><a href="/" class="footer-logo">Game<span>Vault</span></a><p class="footer-desc">Auto-updated gaming news, GTA 6 coverage, free games, gift codes and setup guides.</p><div class="footer-social"><a href="#" aria-label="Twitter">X</a><a href="#" aria-label="YouTube">YT</a><a href="#" aria-label="Discord">DC</a></div></div><div><h4>Explore</h4><a href="/gta-6/">GTA 6</a><a href="/gaming-setups/">Gaming Setups</a><a href="/free-games/">Free Games</a><a href="/gaming-codes/">Gift Codes</a><a href="/news/">News</a></div><div><h4>GTA 6</h4><a href="/gta-6/release-date/">Release Date</a><a href="/gta-6/trailers/">Trailers</a><a href="/gta-6/leaks/">Leaks &amp; Rumors</a></div><div><h4>Guides</h4><a href="/gaming-setups/budget-pc/">Budget PC Build</a><a href="/gaming-setups/best-monitors/">Best Monitors</a><a href="/free-games/epic-games/">Epic Games</a></div></div></div><div class="footer-bottom">GameVault &copy; 2026 &mdash; Auto-updated daily</div></footer>\n</body>\n</html>'

AD = lambda l: '<div class="ad-box">' + l + '</div>'
P = lambda s: '<p>' + s + '</p>'
H2 = lambda s: '<h2>' + s + '</h2>'
UL = lambda items: '<ul>' + ''.join('<li>' + x + '</li>' for x in items) + '</ul>'
H = lambda t, d, date, cls="": '<div class="article">' + (('<span class="tag">' + cls + '</span>') if cls else '') + '<h3><a href="' + t + '">' + d + '</a></h3><p>' + date[:200] + ('...' if len(date) > 200 else '') + '</p></div>'
MT = lambda s: '<div class="post-meta">' + s + '</div>'

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"

def fetch_rss(url, timeout=15):
    try:
        req = Request(url, headers={"User-Agent": UA})
        resp = urlopen(req, timeout=timeout)
        data = resp.read()
        root = ElementTree.fromstring(data)
        ns = {"atom": "http://www.w3.org/2005/Atom", "rss": ""}
        entries = []
        is_atom = root.find(".//atom:entry", ns) is not None
        if is_atom:
            for item in root.findall(".//atom:entry", ns):
                title = (item.findtext("atom:title", ns) or "")
                link_el = item.find("atom:link", ns)
                link = (link_el.get("href", "") if link_el is not None else "")
                desc_raw = (item.findtext("atom:summary", ns) or item.findtext("atom:content", ns) or "")
                desc = re.sub(r'<[^>]+>', '', desc_raw)[:500]
                pub = (item.findtext("atom:published", ns) or item.findtext("atom:updated", ns) or "")
                if title and link:
                    entries.append({"title": html_mod.unescape(title.strip()), "link": link.strip(), "desc": html_mod.unescape(desc.strip()), "date": pub.strip()})
        else:
            for item in root.findall(".//item"):
                title = (item.findtext("title") or "")
                link = (item.findtext("link") or "")
                desc_raw = (item.findtext("description") or "")
                desc = re.sub(r'<[^>]+>', '', desc_raw)[:500]
                pub = (item.findtext("pubDate") or "")
                if title and link:
                    entries.append({"title": html_mod.unescape(title.strip()), "link": link.strip(), "desc": html_mod.unescape(desc.strip()), "date": pub.strip()})
        return entries
    except Exception as e:
        log(f"RSS fetch failed for {url}: {e}")
        return []

def scrape_epic_free_games():
    """Scrape Epic Games Store free games via their API."""
    freebies = []
    try:
        req = Request("https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US", headers={"User-Agent": UA})
        resp = urlopen(req, timeout=10)
        data = json.loads(resp.read())
        games = data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", [])
        for g in games:
            title = g.get("title", "")
            if not title:
                continue
            desc = (g.get("description") or "")[:300]
            slug = g.get("productSlug") or (g.get("catalogNs") or {}).get("mappings", [{}])[0].get("pageSlug", "") if (g.get("catalogNs") or {}).get("mappings") else ""
            link = f"https://store.epicgames.com/en-US/p/{slug}" if slug else "https://store.epicgames.com/en-US/free-games"
            promos = g.get("promotions") or {}
            for ptype in ["promotionalOffers", "upcomingPromotionalOffers"]:
                offers = promos.get(ptype, [])
                for o in offers:
                    inner = o.get("promotionalOffers", [])
                    for po in inner:
                        if po.get("discountSetting", {}).get("discountPercentage") == 0:
                            freebies.append({"title": title, "desc": desc, "link": link, "date": "Free now"})
                            if len(freebies) >= 5:
                                return freebies
    except Exception as e:
        log(f"Epic Games fetch failed: {e}")
    return freebies

def fetch_reddit_top(sub, limit=10):
    """Fetch top posts from a subreddit."""
    entries = fetch_rss(f"https://www.reddit.com/r/{sub}/hot/.rss?limit={limit}")
    for e in entries:
        e["date"] = e.get("date", "")[:16]
    return entries

def scrape_gaming_news():
    """Fetch gaming news from multiple RSS feeds."""
    all_news = []
    feeds = [
        ("https://www.gamespot.com/feeds/mashup/", "GameSpot"),
        ("https://www.pcgamer.com/rss/", "PC Gamer"),
        ("https://www.ign.com/rss/articles/feed", "IGN"),
        ("https://www.eurogamer.net/feed", "Eurogamer"),
        ("https://feed.rockpapershotgun.com/", "Rock Paper Shotgun"),
    ]
    for url, name in feeds:
        entries = fetch_rss(url)
        for e in entries[:4]:
            e["source"] = name
            all_news.append(e)
    return all_news

def scrape_gta6_news():
    """Fetch GTA 6 specific news from multiple sources."""
    all_news = []
    feeds = [
        ("https://www.gamespot.com/feeds/mashup/?tags=grand-theft-auto-6", "GameSpot"),
        ("https://www.pcgamer.com/rss/tag/gta-6/", "PC Gamer"),
        ("https://www.ign.com/rss/articles/feed?tags=gta-6", "IGN"),
    ]
    for url, name in feeds:
        entries = fetch_rss(url)
        for e in entries[:6]:
            e["source"] = name
            all_news.append(e)
    return all_news

def sanitize_filename(title):
    s = title.lower().replace(" ", "-")[:60]
    s = re.sub(r'[^a-z0-9-]', '', s)
    return s.strip("-") or "post"

def generate_post_page(entry, section="news", category="Gaming News"):
    slug = sanitize_filename(entry["title"])
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{date_str}-{slug}.html"
    rel_path = f"{section}/{filename}"

    title = html_mod.escape(entry["title"])
    desc = html_mod.escape(entry["desc"][:160])

    content = f'<h1>{title}</h1>\n{MT(f"{date_str} &middot; {category} &middot; <a href=\'{html_mod.escape(entry["link"])}\'>Source</a>")}\n'
    content += AD("AD PLACEHOLDER \u2014 Leaderboard")
    content += P(entry["desc"][:2000])
    content += AD("AD PLACEHOLDER \u2014 In-article")
    content += f'<p>Read the full article at <a href="{html_mod.escape(entry["link"])}" target="_blank" rel="noopener">{html_mod.escape(entry["title"])}</a></p>'
    content += '\n<div class="related"><h3>More News</h3><a href="/news/">All News</a><a href="/gta-6/">GTA 6 Updates</a><a href="/free-games/">Free Games</a></div>'

    full_path = os.path.join(ROOT, section, filename)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(HEADER.format(title=title + " | GameVault", desc=desc, date=date_str) + content + FOOTER)
    log(f"Created: {section}/{filename}")
    return {"filename": filename, "title": entry["title"], "desc": entry["desc"][:200], "date": date_str, "link": f"/{section}/{filename}", "source": entry.get("source", "Gaming News")}

def update_news_index(posts):
    posts.sort(key=lambda x: x["date"], reverse=True)
    content = f'<h1>Gaming News</h1>\n{MT(f"Aggregated from top gaming sources \u2014 updated daily ({len(posts)} articles)")}\n'
    content += AD("AD PLACEHOLDER \u2014 Leaderboard")
    content += '<div class="grid">'
    for p in posts[:30]:
        tag = f'<span class="source-badge">{html_mod.escape(p.get("source","News"))}</span>'
        content += f'<div class="article">{tag}<h3><a href="{p["link"]}">{html_mod.escape(p["title"])}</a></h3><p>{html_mod.escape(p["desc"][:150])}</p><div class="source">{p.get("date","")}</div></div>\n'
    content += '</div>' + AD("AD PLACEHOLDER \u2014 In-page")

    path = os.path.join(ROOT, "news", "index.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(HEADER.format(title="Gaming News | GameVault", desc="Latest gaming news aggregated daily from top sources.", date=datetime.now().strftime("%Y-%m-%d")) + content + FOOTER)
    log("Updated: news/index.html")

def update_gta6_page(entries):
    entries.sort(key=lambda x: x.get("date", ""), reverse=True)
    content = f'<h1>GTA 6 News</h1>\n{MT(f"Latest updates, rumors &amp; discussions from the community \u2014 auto-updated")}\n'
    content += AD("AD PLACEHOLDER \u2014 Leaderboard")
    content += P("GTA 6 is the most anticipated game ever. Every day, new leaks, rumors, and discussions surface. Here are the latest trending stories from Reddit and gaming news sites.")
    content += H2("Trending Now")
    for e in entries[:15]:
        content += f'<div class="article"><h3><a href="{html_mod.escape(e["link"])}" target="_blank">{html_mod.escape(e["title"])}</a></h3><p>{html_mod.escape(e["desc"][:200])}</p><div class="source">r/GTA6 \u2022 {e.get("date","")[:10]}</div></div>\n'
    content += AD("AD PLACEHOLDER \u2014 In-article") + '\n<div class="related"><h3>Related</h3><a href="/gta-6/release-date/">Release Date</a><a href="/gta-6/trailers/">Trailers</a><a href="/gta-6/leaks/">Leaks</a></div>'

    path = os.path.join(ROOT, "gta-6", "index.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(HEADER.format(title="GTA 6 News & Rumors | GameVault", desc="Latest GTA 6 news, leaks, rumors and community discussions auto-updated daily.", date=datetime.now().strftime("%Y-%m-%d")) + content + FOOTER)
    log("Updated: gta-6/index.html")

def update_free_games_page(freebies):
    content = f'<h1>Free Games This Week</h1>\n{MT(f"Auto-updated from Epic Games Store \u2014 {datetime.now().strftime("%B %d, %Y")}")}\n'
    content += AD("AD PLACEHOLDER \u2014 Leaderboard")
    content += P("Epic Games Store gives away free games every Thursday. Other platforms also offer freebies regularly. Here is the current list.")
    content += H2("Currently Free")
    if freebies:
        for g in freebies:
            content += f'<div class="article"><h3><a href="{html_mod.escape(g["link"])}" target="_blank">{html_mod.escape(g["title"])}</a></h3><p>{html_mod.escape(g["desc"][:200])}</p><div class="source">{g.get("date","")}</div></div>\n'
    else:
        content += P("No free games found right now. Check back Thursday when Epic Games updates their store.")
    content += AD("AD PLACEHOLDER \u2014 In-article")
    content += H2("How to Claim") + UL(["Create an Epic Games account (free)", "Download the Epic Games Launcher", "Visit the Store page", "Click Get on the free game", "It is permanently added to your library"])
    content += '\n<div class="related"><h3>Related</h3><a href="/gaming-codes/">Gift Codes</a><a href="/news/">Gaming News</a></div>'

    path = os.path.join(ROOT, "free-games", "index.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(HEADER.format(title="Free Games This Week | GameVault", desc="Current free games from Epic Games Store, Steam and more. Updated daily.", date=datetime.now().strftime("%Y-%m-%d")) + content + FOOTER)
    log("Updated: free-games/index.html")

def update_homepage(post_count, gta6_count, latest_posts):
    hero_post = latest_posts[0] if latest_posts else None
    content = ''

    # Hero section
    if hero_post:
        content += f'<div class="hero"><div class="hero-content"><span class="hero-tag">Featured Story</span><h2><a href="{hero_post["link"]}">{html_mod.escape(hero_post["title"])}</a></h2><p>{html_mod.escape(hero_post["desc"][:200])}</p></div></div>\n'
    else:
        content += f'<div class="hero"><div class="hero-content"><span class="hero-tag">Welcome</span><h2>GameVault \u2014 Auto-Updated Gaming News</h2><p>GTA 6 news, gaming setups, free games, codes &amp; guides</p></div></div>\n'

    content += AD('AD PLACEHOLDER \u2014 Leaderboard (728x90)')

    # Category cards
    content += '<div class="grid">'
    content += H('/gta-6/', 'GTA 6 \u2014 Everything We Know', 'Live updates from the community', 'HOT')
    content += H('/gaming-setups/', 'Best Gaming Setups 2026', 'PC builds, monitors, headsets', '')
    content += H('/free-games/', 'Free Games This Week', 'Epic Games, Steam freebies', 'FREE')
    content += H('/gaming-codes/', 'Gift Codes & Rewards', 'Roblox, Fortnite, Free Fire codes', '')
    content += H('/news/', 'Gaming News', 'Latest updates aggregated daily', 'NEW')
    content += '</div>\n'

    content += AD('AD PLACEHOLDER \u2014 In-page')

    # Latest News
    content += '<h2>Latest News</h2>\n'
    content += '<a href="/news/" style="display:block;text-align:right;color:#FFC501;font-size:12px;font-weight:600;margin-bottom:10px;text-decoration:none;font-family:\'Kanit\',sans-serif;text-transform:uppercase;letter-spacing:0.5px">View All News \u2192</a>\n'
    for p in latest_posts[:8]:
        tag = f'<span class="source-badge">{html_mod.escape(p.get("source","News"))}</span>'
        content += f'<div class="article">{tag}<h3><a href="{p["link"]}">{html_mod.escape(p["title"])}</a></h3><p>{html_mod.escape(p["desc"][:150])}</p><div class="source">{p.get("date","")}</div></div>\n'

    # Newsletter
    content += '<div class="newsletter"><h3>Stay Updated</h3><p>Get the latest gaming news, free games, and GTA 6 updates delivered daily.</p><a href="/news/" class="btn">Subscribe</a></div>\n'

    # Featured Guides
    content += '<h2>Featured Guides</h2>\n'
    content += '<div class="grid">'
    content += '<a href="/gaming-setups/budget-pc/" class="card"><h3>Best Budget Gaming PC Build 2026</h3><p>Build a gaming PC for under $800 that runs all modern games at 60+ FPS.</p></a>\n'
    content += '<a href="/gaming-setups/best-monitors/" class="card"><h3>Best Gaming Monitors 2026</h3><p>144Hz, 240Hz, 4K \u2014 the best monitors for every budget.</p></a>\n'
    content += '<a href="/free-games/epic-games/" class="card"><h3>Epic Games Free Games</h3><p>Current and upcoming free games on Epic Games Store.</p></a>\n'
    content += '</div>'

    content += AD('AD PLACEHOLDER \u2014 Footer')

    path = os.path.join(ROOT, "index.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(HEADER.format(title="GameVault \u2014 GTA 6, Gaming Setups, Free Games & Codes", desc="GameVault automatically aggregates GTA 6 news, gaming deals, free games and gift codes daily.", date=datetime.now().strftime("%Y-%m-%d")) + content + FOOTER)
    log("Updated: index.html")

def main():
    log("=== GameVault Auto-Updater Started ===")

    # Fetch GTA 6 news
    log("Fetching GTA 6 news...")
    gta6_entries = scrape_gta6_news()
    if not gta6_entries:
        gta6_entries = fetch_reddit_top("GTA6", 10)
    log(f"Got {len(gta6_entries)} GTA 6 entries")

    # Fetch gaming news
    log("Fetching gaming news...")
    news_entries = scrape_gaming_news()
    log(f"Got {len(news_entries)} gaming news entries")

    # Fetch free games
    log("Fetching free games...")
    freebies = scrape_epic_free_games()
    log(f"Got {len(freebies)} free games")

    # Generate post pages for gaming news
    all_posts = []
    for entry in news_entries:
        result = generate_post_page(entry, "news/posts", "Gaming News")
        all_posts.append(result)

    # Also create posts from GTA 6 news
    for entry in gta6_entries[:5]:
        result = generate_post_page(entry, "news/posts", "GTA 6")
        all_posts.append(result)

    # Update index pages
    update_news_index(all_posts)
    update_gta6_page(gta6_entries)
    update_free_games_page(freebies)
    update_homepage(len(all_posts), len(gta6_entries), all_posts)

    log(f"=== Complete: {len(all_posts)} new posts, 4 pages updated ===")

if __name__ == "__main__":
    main()
