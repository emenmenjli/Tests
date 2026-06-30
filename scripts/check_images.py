import urllib.request, xml.etree.ElementTree as ET, re

urls = [
    "https://www.gamespot.com/feeds/mashup/",
    "https://www.pcgamer.com/rss/",
    "https://www.ign.com/rss/articles/feed",
    "https://www.eurogamer.net/feed",
]

for url in urls:
    print(f"\n=== {url} ===")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
        resp = urllib.request.urlopen(req, timeout=10)
        root = ET.fromstring(resp.read())
        ns = {"atom": "http://www.w3.org/2005/Atom", "media": "http://search.yahoo.com/mrss/"}
        items = root.findall(".//item") or root.findall(".//atom:entry", ns)
        print(f"  Items: {len(items)}")
        for i, item in enumerate(items[:2]):
            title = (item.findtext("title") or item.findtext("atom:title", ns) or "?")[:60]
            print(f"  [{i+1}] {title}")
            # media:content
            for mc in item.findall(".//media:content", ns):
                print(f"      media:content url={mc.get('url','')[:100]}")
            for mc in item.findall(".//media:thumbnail", ns):
                print(f"      media:thumbnail url={mc.get('url','')[:100]}")
            for mc in item.findall(".//{http://search.yahoo.com/mrss/}content"):
                print(f"      media:content(no ns) url={mc.get('url','')[:100]}")
            for mc in item.findall(".//{http://search.yahoo.com/mrss/}thumbnail"):
                print(f"      media:thumbnail(no ns) url={mc.get('url','')[:100]}")
            for enc in item.findall("enclosure"):
                print(f"      enclosure url={enc.get('url','')[:100]}")
            # Check description for images
            desc = item.findtext("description") or item.findtext("atom:summary", ns) or item.findtext("atom:content", ns) or ""
            imgs = re.findall(r'<img[^>]+src="([^"]+)"', desc)
            if imgs:
                print(f"      img in desc: {imgs[0][:100]}")
    except Exception as e:
        print(f"  Error: {e}")
