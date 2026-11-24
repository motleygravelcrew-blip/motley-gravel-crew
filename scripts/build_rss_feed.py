#!/usr/bin/env python3
"""Build the MGC RSS feed from dated edition pages in the repository root."""
from datetime import date, datetime, time, timezone, timedelta
from html.parser import HTMLParser
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree, register_namespace

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://motleygravelcrew.com"
AWST = timezone(timedelta(hours=8))

class EditionParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.in_title = False
        self.in_blockquote = False
        self.in_p = False
        self.summary_parts = []
        self.capture_summary = False
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self.in_title = True
        if tag == "blockquote":
            self.in_blockquote = True
        if tag == "p" and self.in_blockquote and not self.summary_parts:
            self.in_p = True
            self.capture_summary = True
    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag == "p" and self.in_p:
            self.in_p = False
        if tag == "blockquote":
            self.in_blockquote = False
            self.capture_summary = False
    def handle_data(self, data):
        text = " ".join(data.split())
        if not text:
            return
        if self.in_title:
            self.title += text
        if self.capture_summary:
            self.summary_parts.append(text)

items = []
for path in sorted(ROOT.glob("20??-??-??.html"), reverse=True):
    try:
        published = date.fromisoformat(path.stem)
    except ValueError:
        continue
    parser = EditionParser()
    parser.feed(path.read_text(encoding="utf-8"))
    title = parser.title.strip() or f"MGC Cycling Intelligence — The Intelligence Edition — {published:%d %B %Y}"
    summary = " ".join(parser.summary_parts).strip()
    if not summary:
        summary = "Read the latest Motley Gravel Crew cycling intelligence edition."
    items.append((published, title, summary[:1200], f"{SITE}/{path.name}"))

rss = Element("rss", {"version": "2.0", "xmlns:atom": "http://www.w3.org/2005/Atom"})
channel = SubElement(rss, "channel")
for tag, value in [
    ("title", "Motley Gravel Crew — Cycling Intelligence"),
    ("link", SITE + "/"),
    ("description", "Independent cycling journalism covering gravel, road, XCO/XCM, technology and the Western Australian cycling community."),
    ("language", "en-au"),
]:
    SubElement(channel, tag).text = value
atom = SubElement(channel, "{http://www.w3.org/2005/Atom}link", {
    "href": SITE + "/feed.xml", "rel": "self", "type": "application/rss+xml"
})
for published, title, summary, url in items:
    item = SubElement(channel, "item")
    SubElement(item, "title").text = title
    SubElement(item, "link").text = url
    SubElement(item, "guid", {"isPermaLink": "true"}).text = url
    pub_dt = datetime.combine(published, time(6, 0), tzinfo=AWST)
    SubElement(item, "pubDate").text = pub_dt.strftime("%a, %d %b %Y %H:%M:%S %z")
    SubElement(item, "description").text = summary
    SubElement(item, "category").text = "Cycling"
    SubElement(item, "category").text = "Western Australia"

ElementTree(rss).write(ROOT / "feed.xml", encoding="utf-8", xml_declaration=True)
print(f"Built RSS feed with {len(items)} dated editions.")
