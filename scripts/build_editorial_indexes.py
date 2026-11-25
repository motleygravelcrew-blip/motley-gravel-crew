#!/usr/bin/env python3
"""Build MGC editorial indexes from approved dated edition pages."""
from datetime import date, datetime
from html.parser import HTMLParser
from html import escape
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo
from xml.etree.ElementTree import Element, SubElement, ElementTree

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://motleygravelcrew.com"
AWST = ZoneInfo("Australia/Perth")
START = "<!-- MGC_GENERATED_START -->"
END = "<!-- MGC_GENERATED_END -->"


class EditionParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.summary_parts = []
        self.in_blockquote = False
        self.in_summary_p = False
        self.in_figure = False
        self.in_caption = False
        self.image = None
        self.caption_parts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "blockquote":
            self.in_blockquote = True
        elif tag == "p" and self.in_blockquote and not self.summary_parts:
            self.in_summary_p = True
        elif tag == "figure" and self.image is None:
            self.in_figure = True
        elif tag == "img" and self.in_figure and self.image is None:
            self.image = {"src": attrs.get("src", ""), "alt": attrs.get("alt", "")}
        elif tag == "figcaption" and self.in_figure:
            self.in_caption = True

    def handle_endtag(self, tag):
        if tag == "blockquote":
            self.in_blockquote = False
        elif tag == "p" and self.in_summary_p:
            self.in_summary_p = False
        elif tag == "figcaption":
            self.in_caption = False
        elif tag == "figure":
            self.in_figure = False

    def handle_data(self, data):
        value = " ".join(data.split())
        if not value:
            return
        if self.in_summary_p:
            self.summary_parts.append(value)
        if self.in_caption:
            self.caption_parts.append(value)


def safe_image(image):
    if not image:
        return None
    src = image.get("src", "").strip()
    parsed = urlparse(src)
    if not (src.startswith("/") or parsed.scheme in ("http", "https")):
        return None
    return {
        "src": escape(src, quote=True),
        "alt": escape(image.get("alt", "").strip() or "Motley Gravel Crew edition image", quote=True),
        "caption": escape(" ".join(image.get("caption", []))[:220], quote=False),
    }


def editions():
    result = []
    for path in sorted(ROOT.glob("20??-??-??.html"), reverse=True):
        try:
            published = date.fromisoformat(path.stem)
        except ValueError:
            continue
        parser = EditionParser()
        parser.feed(path.read_text(encoding="utf-8"))
        summary = " ".join(parser.summary_parts).strip()
        summary = summary.replace("THE MGC READ", "").strip(" :-")
        if not summary:
            summary = "Read the latest Motley Gravel Crew Cycling Intelligence edition."
        image = dict(parser.image or {})
        image["caption"] = parser.caption_parts
        result.append({
            "date": published,
            "href": path.name,
            "date_label": published.strftime("%d %B %Y").upper(),
            "month_label": published.strftime("%B %Y").upper(),
            "summary": escape(summary[:260], quote=False),
            "image": safe_image(image),
        })
    return result


def cards(items, featured=False):
    output = []
    for index, item in enumerate(items):
        latest = featured and index == 0
        category = "LATEST EDITION" if latest else item["month_label"]
        classes = "edition-item edition-item-featured" if latest else "edition-item"
        thumb = ""
        if latest and item["image"]:
            thumb = (f'<img class="edition-thumb" src="{item["image"]["src"]}" '
                     f'alt="{item["image"]["alt"]}" loading="lazy">')
        output.append(
            f'<a class="{classes}" href="{item["href"]}">{thumb}'
            f'<span class="category {"cyan" if latest else "purple"}">{category}</span>'
            f'<strong>{item["date_label"]}</strong>'
            f'<small>{item["summary"]}</small>'
            f'<b>{"READ EDITION" if featured else "OPEN EDITION"} ↗</b></a>'
        )
    return "\n".join(output)


def replace_generated(path, content):
    text = path.read_text(encoding="utf-8")
    start = text.find(START)
    end = text.find(END)
    if start < 0 or end < 0 or end < start:
        raise SystemExit(f"Missing or invalid generated-content markers in {path.name}")
    text = text[:start + len(START)] + "\n" + content + "\n" + text[end:]
    path.write_text(text, encoding="utf-8")


def build_sitemap(items):
    today = datetime.now(AWST).date().isoformat()
    static_pages = ["", "editions.html", "archive.html", "events.html", "links.html", "routes.html", "about.html"]
    root = Element("urlset", {"xmlns": "http://www.sitemaps.org/schemas/sitemap/0.9"})
    for page in static_pages:
        node = SubElement(root, "url")
        SubElement(node, "loc").text = SITE + ("/" if not page else "/" + page)
        SubElement(node, "lastmod").text = today
    for item in items:
        node = SubElement(root, "url")
        SubElement(node, "loc").text = SITE + "/" + item["href"]
        SubElement(node, "lastmod").text = item["date"].isoformat()
    ElementTree(root).write(ROOT / "sitemap.xml", encoding="utf-8", xml_declaration=True)


def main():
    items = editions()
    if not items:
        raise SystemExit("No valid dated editions found; refusing to publish empty indexes.")
    replace_generated(ROOT / "editions.html", cards(items, featured=True))
    replace_generated(ROOT / "archive.html", cards(items, featured=False))
    latest = items[0]
    if latest["image"]:
        image = latest["image"]
        visual = (
            '<div class="feature-image-wrap" style="min-width:0;width:100%;max-width:100%;overflow:hidden">'
            f'<img style="display:block;width:100%;max-width:100%;height:220px;max-height:220px;'
            f'object-fit:contain;position:static;float:none" class="lead-story-image" '
            f'src="{image["src"]}" alt="{image["alt"]}">'
            f'<small style="display:block;font-size:9px;line-height:1.35;color:#748198;opacity:.72">'
            f'{image["caption"]}</small></div>'
        )
    else:
        visual = '<div class="feature-mark" aria-label="Motley Gravel Crew">MGC<span>·</span></div>'
    home = (
        visual + '<div><span class="category cyan">' + latest["date_label"] + ' · LATEST EDITION</span>'
        '<h3>THE INTELLIGENCE EDITION</h3>'
        '<p>' + latest["summary"] + '</p>'
        '<a class="text-link" href="' + latest["href"] + '">READ THE INTELLIGENCE EDITION <span>↗</span></a></div>'
    )
    replace_generated(ROOT / "index.html", home)
    build_sitemap(items)
    print(f"Generated homepage, editions, archive and sitemap for {len(items)} dated editions.")


if __name__ == "__main__":
    main()
