#!/usr/bin/env python3
"""Regenerate all Cycling Intelligence indexes from dated edition HTML files."""
from datetime import date, datetime, time, timezone, timedelta
from html.parser import HTMLParser
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree
import re

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://motleygravelcrew.com"
AWST = timezone(timedelta(hours=8))
EDITION_RE = re.compile(r"^20\\d{2}-\\d{2}-\\d{2}\\.html$")

class EditionParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.headings = []
        self.in_title = False
        self.in_h3 = False
        self.current_heading = ""
        self.summary = []
        self.in_blockquote = False
        self.in_summary_p = False
    def handle_starttag(self, tag, attrs):
        if tag == "title": self.in_title = True
        if tag == "h3":
            self.in_h3 = True
            self.current_heading = ""
        if tag == "blockquote": self.in_blockquote = True
        if tag == "p" and self.in_blockquote and not self.summary:
            self.in_summary_p = True
    def handle_endtag(self, tag):
        if tag == "title": self.in_title = False
        if tag == "h3" and self.in_h3:
            self.headings.append(" ".join(self.current_heading.split()))
            self.in_h3 = False
        if tag == "p": self.in_summary_p = False
        if tag == "blockquote": self.in_blockquote = False
    def handle_data(self, data):
        value = " ".join(data.split())
        if not value: return
        if self.in_title: self.title += value
        if self.in_h3: self.current_heading += " " + value
        if self.in_summary_p: self.summary.append(value)

def editions():
    found = []
    for path in ROOT.iterdir():
        if not EDITION_RE.match(path.name): continue
        try: published = date.fromisoformat(path.stem)
        except ValueError: continue
        parser = EditionParser()
        parser.feed(path.read_text(encoding="utf-8"))
        found.append({
            "date": published, "path": path.name,
            "title": parser.title.strip() or f"MGC Cycling Intelligence — {published:%d %B %Y}",
            "lead": parser.headings[0] if parser.headings else "The Intelligence Edition",
            "summary": " ".join(parser.summary).strip() or "Read the latest MGC Cycling Intelligence edition."
        })
    return sorted(found, key=lambda item: item["date"], reverse=True)

def edition_card(item, featured=False):
    month = item["date"].strftime("%B %Y").upper()
    label = "LATEST EDITION" if featured else month
    klass = "edition-item edition-item-featured" if featured else "edition-item"
    lead = item["lead"]
    return (f'<a class="{klass}" href="{item["path"]}">'
            f'<span class="category {"cyan" if featured else "purple"}">{label}</span>'
            f'<strong>{item["date"]:%d %B %Y}</strong>'
            f'<small>{lead}</small><b>{"READ EDITION" if featured else "OPEN EDITION"} ↗</b></a>')

def replace_list_page(path, heading, items, empty):
    doc = path.read_text(encoding="utf-8")
    cards = "".join(edition_card(item, i == 0 and heading == "LATEST INTELLIGENCE EDITIONS")
                    for i, item in enumerate(items))
    if not cards: cards = f'<p class="muted-note">{empty}</p>'
    pattern = r'(<h2 class="subheading">' + re.escape(heading) + r'</h2>\s*<div class="edition-list">).*?(</div>)'
    if heading == "LATEST INTELLIGENCE EDITIONS":
        updated, count = re.subn(pattern, lambda m: m.group(1) + cards + m.group(2), doc, count=1, flags=re.S)
    else:
        pattern = r'(<div class="edition-list">).*?(</div>)'
        updated, count = re.subn(pattern, lambda m: m.group(1) + cards + m.group(2), doc, count=1, flags=re.S)
    if count != 1: raise RuntimeError(f"Could not safely locate edition list in {path.name}")
    path.write_text(updated, encoding="utf-8")

def update_home(latest):
    path = ROOT / "index.html"
    doc = path.read_text(encoding="utf-8")
    if not latest: return
    date_label = latest["date"].strftime("%d %B %Y").upper()
    heading = latest["lead"]
    summary = latest["summary"][:240]
    edition_html = (ROOT / latest["path"]).read_text(encoding="utf-8")
    image_match = re.search(r'<figure[^>]*class="[^"]*story-feature-image[^"]*"[^>]*>.*?</figure>', edition_html, re.S)
    image_block = '<div class="feature-image-wrap"><div class="feature-mark">MGC</div></div>'
    if image_match:
        src = re.search(r'<img[^>]+src="([^"]+)"', image_match.group(0))
        alt = re.search(r'<img[^>]+alt="([^"]*)"', image_match.group(0))
        caption = re.search(r'<figcaption>(.*?)</figcaption>', image_match.group(0), re.S)
        if src:
            image_block = (f'<div class="feature-image-wrap"><img class="lead-story-image" src="{src.group(1)}" '
                           f'alt="{alt.group(1) if alt else heading}">'
                           f'<small>{caption.group(1) if caption else "Image credit recorded in the edition."}</small></div>')
    panel = (f'{image_block}<div><span class="category cyan">{date_label} · LEAD STORY</span>'
             f'<h3>{heading}</h3><p>{summary}</p>'
             f'<a class="text-link" href="{latest["path"]}">READ THE INTELLIGENCE EDITION <span>↗</span></a></div>')
    pattern = r'(<section class="section">.*?<div class="feature-panel">).*?(</section>)'
    updated, count = re.subn(pattern, lambda m: m.group(1) + panel + m.group(2), doc, count=1, flags=re.S)
    if count != 1: raise RuntimeError("Could not safely locate homepage Cycling Intelligence feature section")
    path.write_text(updated, encoding="utf-8")

def update_sitemap(items):
    path = ROOT / "sitemap.xml"
    doc = path.read_text(encoding="utf-8")
    core = ["", "editions.html", "archive.html", "events.html", "links.html", "routes.html", "about.html"]
    existing = re.findall(r'<url>.*?</url>', doc, re.S)
    by_loc = {}
    for block in existing:
        m = re.search(r"<loc>https://motleygravelcrew\\.com/([^<]*)</loc>", block)
        if m: by_loc[m.group(1)] = block
    today = date.today().isoformat()
    for name in core:
        if name not in by_loc:
            by_loc[name] = f"<url><loc>{SITE}/{name}</loc><lastmod>{today}</lastmod></url>"
    for item in items:
        name = item["path"]
        by_loc[name] = f"<url><loc>{SITE}/{name}</loc><lastmod>{item['date'].isoformat()}</lastmod></url>"
    route = by_loc.get("mgc-jarrahdale-loop.html")
    if route: by_loc["mgc-jarrahdale-loop.html"] = route
    blocks = [by_loc[k] for k in core if k in by_loc]
    blocks += [by_loc[item["path"]] for item in items]
    if route: blocks.append(route)
    path.write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  ' + "\n  ".join(blocks) + '\n</urlset>\n', encoding="utf-8")

def main():
    items = editions()
    latest = items[0] if items else None
    replace_list_page(ROOT / "archive.html", "ARCHIVE", items, "No editions have been published yet.")
    replace_list_page(ROOT / "editions.html", "LATEST INTELLIGENCE EDITIONS", items[:5], "No editions have been published yet.")
    update_home(latest)
    update_sitemap(items)
    # Keep the existing RSS builder as the single feed implementation.
    import subprocess, sys
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build_rss_feed.py")], check=True)
    print(f"Publication indexes regenerated for {len(items)} editions.")

if __name__ == "__main__":
    main()
