"""
GameVault Auto-Updater
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
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{title}</title><meta name="description" content="{desc}"><meta name="robots" content="index, follow"><meta name="date" content="{date}"><style>
*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#0a0a0f;color:#e0e0e0;line-height:1.7}}
.container{{max-width:800px;margin:auto;padding:0 20px}}
header{{background:#0f0f1a;border-bottom:1px solid #2a2a4a;padding:16px 0;position:sticky;top:0;z-index:100}}
header .container{{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px}}
.logo{{font-size:22px;font-weight:800;color:#fff;text-decoration:none}}.logo span{{color:#ff4444}}
nav a{{color:#aaa;text-decoration:none;margin-left:18px;font-size:13px}}nav a:hover{{color:#fff}}
h1{{font-size:26px;margin:30px 0 8px}}h2{{color:#ff4444;font-size:18px;margin:24px 0 8px}}h3{{color:#ddd;font-size:15px;margin:14px 0 6px}}
p{{margin-bottom:10px;color:#bbb;font-size:14px}}ul{{margin:8px 0 16px 18px;color:#bbb}}li{{margin-bottom:3px;font-size:14px}}
.ad-box{{background:#12121a;border:1px dashed #333;border-radius:8px;padding:16px;text-align:center;margin:20px 0;min-height:90px;display:flex;align-items:center;justify-content:center;color:#444;font-size:13px}}
.article{{background:#12121a;border:1px solid #2a2a3a;border-radius:10px;padding:20px;margin:12px 0;transition:.2s}}
.article:hover{{border-color:#ff4444}}.article h3{{color:#ff4444;margin-bottom:4px;font-size:15px}}.article p{{color:#999;font-size:13px}}.article .source{{color:#555;font-size:11px;margin-top:4px}}
.post-meta{{color:#666;font-size:13px;margin-bottom:16px}}
.related{{background:#12121a;border-radius:10px;padding:20px;margin:30px 0}}.related h3{{color:#fff;margin-bottom:10px}}.related a{{display:block;color:#ff4444;text-decoration:none;padding:3px 0;font-size:13px}}.related a:hover{{text-decoration:underline}}
footer{{text-align:center;padding:40px;color:#555;font-size:13px;border-top:1px solid #1a1a2a;margin-top:40px}}
.tag{{display:inline-block;background:#ff444422;color:#ff4444;padding:2px 8px;border-radius:4px;font-size:10px;margin-right:4px}}
</style></head>
<body>
<header><div class="container"><a href="/" class="logo">Game<span>Vault</span></a><nav>
<a href="/">Home</a><a href="/gta-6/">GTA 6</a><a href="/gaming-setups/">Setups</a><a href="/free-games/">Free Games</a><a href="/gaming-codes/">Codes</a><a href="/news/">News</a></nav></div></header>
<div class="container">'''

FOOTER = '</div>\n<footer>GameVault &copy; 2026 &mdash; All rights reserved | Auto-updated daily</footer>\n</body>\n</html>'

AD = lambda l: '<div class="ad-box">' + l + '</div>'
P = lambda s: '<p>' + s + '</p>'
H2 = lambda s: '<h2>' + s + '</h2>'
UL = lambda items: '<ul>' + ''.join('<li>' + x + '</li>' for x in items) + '</ul>'
H = lambda t, d, date, cls="": f'<div class="{cls or "article"}">{cls and "<span class=\"tag\">"+cls+"</span>" or ""}<h3><a href="{t if isinstance(t,str) else t[0]}" style="color:#ff4444;text-decoration:none">{d}</a></h3><p>{date[:200]}{"..." if len(date)>200 else ""}</p><div class="source">{t[3] if isinstance(t,tuple) and len(t)>3 else ""}</div></div>'
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
    
    content = f'<h1>{title}</h1>\n{MT(f"{date_str} &middot; {category} &middot; <a href=\'{html_mod.escape(entry["link"])}\' style=\'color:#ff4444\'>Source</a>")}\n'
    content += AD("AD PLACEHOLDER \u2014 Leaderboard")
    content += P(entry["desc"][:2000])
    content += AD("AD PLACEHOLDER \u2014 In-article")
    content += f'<p>Read the full article at <a href="{html_mod.escape(entry["link"])}" style="color:#ff4444" target="_blank" rel="noopener">{html_mod.escape(entry["title"])}</a></p>'
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
    content += '<div class="grid" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px">'
    for p in posts[:30]:
        tag = f'<span class="tag">{html_mod.escape(p.get("source","News"))}</span>'
        content += f'<div class="article">{tag}<h3><a href="{p["link"]}" style="color:#ff4444;text-decoration:none">{html_mod.escape(p["title"])}</a></h3><p>{html_mod.escape(p["desc"][:150])}</p><div class="source">{p.get("date","")}</div></div>\n'
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
        content += f'<div class="article"><h3><a href="{html_mod.escape(e["link"])}" style="color:#ff4444;text-decoration:none" target="_blank">{html_mod.escape(e["title"])}</a></h3><p>{html_mod.escape(e["desc"][:200])}</p><div class="source">r/GTA6 \u2022 {e.get("date","")[:10]}</div></div>\n'
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
            content += f'<div class="article"><h3><a href="{html_mod.escape(g["link"])}" style="color:#ff4444;text-decoration:none" target="_blank">{html_mod.escape(g["title"])}</a></h3><p>{html_mod.escape(g["desc"][:200])}</p><div class="source">{g.get("date","")}</div></div>\n'
    else:
        content += P("No free games found right now. Check back Thursday when Epic Games updates their store.")
    content += AD("AD PLACEHOLDER \u2014 In-article")
    content += H2("How to Claim") + UL(["Create an Epic Games account (free)", "Download the Epic Games Launcher", "Visit the Store page", "Click Get on the free game", "It is permanently added to your library"])
    content += '\n<div class="related"><h3>Related</h3><a href="/gaming-codes/">Gift Codes</a><a href="/news/">Gaming News</a></div>'
    
    path = os.path.join(ROOT, "free-games", "index.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(HEADER.format(title="Free Games This Week | GameVault", desc="Current free games from Epic Games Store, Steam and more. Updated daily.", date=datetime.now().strftime("%Y-%m-%d")) + content + FOOTER)
    log("Updated: free-games/index.html")

def update_homepage(post_count, gta6_count):
    content = f'''
<div class="hero" style="text-align:center;padding:40px 20px;background:linear-gradient(180deg,#1a1a2e,#0a0a0f);border-radius:0 0 20px 20px;margin-bottom:20px">
<h1 style="font-size:30px;">Welcome to GameVault</h1>
<p style="color:#888;font-size:15px;">GTA 6 news, gaming setups, free games, codes &amp; exclusive guides \u2014 auto-updated daily</p>
<p style="color:#555;font-size:12px;margin-top:8px">{post_count} news articles &middot; {gta6_count} GTA 6 updates &middot; Updated {datetime.now().strftime("%B %d, %Y")}</p>
</div>
''' + AD('AD PLACEHOLDER \u2014 Leaderboard (728x90)') + '''
<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px;margin:20px 0 30px">
H('/gta-6/', 'GTA 6 \u2014 Everything We Know', 'Live updates from the community', 'HOT') + '\n' + H('/gaming-setups/', 'Best Gaming Setups 2026', 'PC builds, monitors, headsets', '') + '\n' + H('/free-games/', 'Free Games This Week', 'Epic Games, Steam freebies', 'FREE') + '\n' + H('/gaming-codes/', 'Gift Codes & Rewards', 'Roblox, Fortnite, Free Fire codes', '') + '\n' + H('/news/', 'Gaming News', 'Latest updates aggregated daily', 'NEW') + '\n</div>\n' + AD('AD PLACEHOLDER \u2014 In-page') + '\n<h2>Latest News</h2>\n<a href="/news/" style="display:block;text-align:right;color:#ff4444;font-size:13px;margin-bottom:10px">View all news \u2192</a>\n'''
    
    path = os.path.join(ROOT, "index.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(HEADER.format(title="GameVault \u2014 GTA 6, Gaming Setups, Free Games & Codes | Auto-Updated Daily", desc="GameVault automatically aggregates GTA 6 news, gaming deals, free games and gift codes daily.", date=datetime.now().strftime("%Y-%m-%d"), mw=1000).replace("800px", "1000px") + content + FOOTER)
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
    update_homepage(len(all_posts), len(gta6_entries))
    
    log(f"=== Complete: {len(all_posts)} new posts, 4 pages updated ===")

if __name__ == "__main__":
    main()
