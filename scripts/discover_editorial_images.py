#!/usr/bin/env python3
"""Discover and publish only Wikimedia Commons images with machine-verifiable reuse licences.

This is deliberately conservative: unknown licences, NC/ND terms, missing creators,
missing source metadata, weak story matches and download failures are skipped.
"""
from __future__ import annotations
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "editorial"
MAX_IMAGES = 4
MAX_BYTES = 12 * 1024 * 1024
UA = "MotleyGravelCrewEditorialBot/1.0 (https://motleygravelcrew.com; editorial image licence verification)"

STOP = set("""the and for with from into over under after before about across latest new says said
cycling cycling's team teams race racing rider riders event events official announce announcement
professional world tour road gravel mountain bike""".split())

def request_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as response:
        return json.loads(response.read().decode("utf-8"))

def clean_text(raw):
    return html.unescape(re.sub(r"<[^>]+>", " ", raw or "")).strip()

def words(value):
    return {w for w in re.findall(r"[a-z0-9]{3,}", value.lower()) if w not in STOP}

def allowed_license(short, url):
    s = (short or "").strip().lower()
    u = (url or "").strip().lower()
    if not s or not u or "noncommercial" in s or "no derivative" in s or "nd" in s.split():
        return False
    if "creativecommons.org/publicdomain/zero/" in u:
        return True
    if "creativecommons.org/licenses/by/" in u or "creativecommons.org/licenses/by-sa/" in u:
        return True
    if s in {"public domain", "cc0", "cc0 1.0"}:
        return True
    return False

def image_candidates(query, heading):
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrnamespace": 6, "gsrlimit": 18, "gsrsearch": query,
        "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata",
    }
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    data = request_json(url)
    pages = (data.get("query") or {}).get("pages") or {}
    target = words(heading)
    results = []
    for page in pages.values():
        info = (page.get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata") or {}
        def val(key):
            entry = meta.get(key) or {}
            return clean_text(entry.get("value", ""))
        short, lic_url = val("LicenseShortName"), val("LicenseUrl")
        creator, credit, desc = val("Artist"), val("Credit"), val("ImageDescription")
        source = "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(page.get("title", "").replace(" ", "_"))
        mime = info.get("mime", "")
        if not allowed_license(short, lic_url):
            continue
        if not creator or not desc or not info.get("url") or not mime.startswith("image/"):
            continue
        if info.get("width", 0) < 700 or info.get("height", 0) < 350:
            continue
        if mime not in {"image/jpeg", "image/png", "image/webp"}:
            continue
        candidate_words = words(page.get("title", "") + " " + desc)
        score = len(target & candidate_words)
        if score < 2:
            continue
        results.append((score, {
            "title": page.get("title", ""), "url": info["url"], "mime": mime,
            "creator": creator, "credit": credit or creator, "description": desc,
            "source": source, "licence": short, "licence_url": lic_url,
        }))
    results.sort(key=lambda item: item[0], reverse=True)
    return [item[1] for item in results]

def download(asset, path):
    req = urllib.request.Request(asset["url"], headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=35) as response:
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("image exceeds size limit")
    signatures = {
        "image/jpeg": data.startswith(b"\xff\xd8\xff"),
        "image/png": data.startswith(b"\x89PNG\r\n\x1a\n"),
        "image/webp": data.startswith(b"RIFF") and data[8:12] == b"WEBP",
    }
    if not signatures.get(asset["mime"], False):
        raise ValueError("download content does not match declared image type")
    path.write_bytes(data)

def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:48] or "story"

def discover_story_sections(document):
    # Match article H3 blocks only; avoid generic editorial/round-up headings.
    pattern = re.compile(r"(<h3\b[^>]*>)(.*?)(</h3>)", re.I | re.S)
    matches = list(pattern.finditer(document))
    stories = []
    for match in matches:
        heading = clean_text(match.group(2))
        low = heading.lower()
        if len(words(heading)) < 3 or any(x in low for x in (
            "quiet on the", "no new", "looking ahead", "results & editorial",
            "editorial check", "desk note"
        )):
            continue
        # Keep the search narrow and story-specific; heading text is the query.
        query_words = [w for w in re.findall(r"[A-Za-z0-9]+", heading) if w.lower() not in STOP]
        query = " ".join(query_words[:7])
        if len(query) < 8:
            continue
        stories.append((match, heading, query))
    return pattern, stories

def figure_markup(asset, heading, relpath):
    alt = html.escape(asset["description"][:220], quote=True)
    creator = html.escape(asset["credit"])
    source = html.escape(asset["source"], quote=True)
    licence = html.escape(asset["licence"])
    licence_url = html.escape(asset["licence_url"], quote=True)
    caption = (f"Photo: <a href=\"{source}\" target=\"_blank\" rel=\"noopener\">{creator}</a> · "
               f"<a href=\"{licence_url}\" target=\"_blank\" rel=\"noopener\">{licence}</a>. "
               "Image description and licence metadata checked against Wikimedia Commons.")
    return (f'\n<!-- MGC-AUTO-IMAGE-START -->\n<figure class="story-feature-image mgc-auto-image">'
            f'<img src="{relpath}" alt="{alt}" loading="lazy">'
            f'<figcaption>{caption}</figcaption></figure>\n'
            f'<!-- MGC-AUTO-IMAGE-END -->\n')

def main():
    files = sorted(ROOT.glob("20??-??-??.html"), reverse=True)
    if not files:
        print("No dated editions found.")
        return
    # Process the newest edition only; older pages remain untouched.
    edition = files[0]
    doc = edition.read_text(encoding="utf-8")
    # Idempotence: do not duplicate images on reruns.
    if "MGC-AUTO-IMAGE-START" in doc:
        print(f"{edition.name} already has automated image placements; leaving unchanged.")
        return
    pattern, stories = discover_story_sections(doc)
    ASSETS.mkdir(parents=True, exist_ok=True)
    selected = []
    used_titles = set()
    for match, heading, query in stories:
        if len(selected) >= MAX_IMAGES:
            break
        try:
            candidates = image_candidates(query + " cycling", heading)
        except Exception as exc:
            print(f"Discovery failed for '{heading}': {exc}")
            continue
        for asset in candidates:
            if asset["title"] in used_titles:
                continue
            ext = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}[asset["mime"]]
            filename = f"{edition.stem}-{slugify(heading)}{ext}"
            path = ASSETS / filename
            try:
                download(asset, path)
            except Exception as exc:
                print(f"Rejected download for '{heading}': {exc}")
                continue
            selected.append((match.start(), match.group(0), figure_markup(asset, heading, f"assets/editorial/{filename}")))
            used_titles.add(asset["title"])
            print(f"Approved image for '{heading}': {asset['title']} — {asset['licence']}")
            break
        time.sleep(1)
    if not selected:
        print("No images passed all checks. Edition will publish without added images.")
        return
    for _, heading_html, figure in reversed(selected):
        # Insert image immediately after the matching story heading.
        doc = doc.replace(heading_html, heading_html + figure, 1)
    # Every dated briefing has its own inline stylesheet, so add containment there too.
    if "Keep all story images inside the article column" not in doc:
        safe_image_css = """
/* Keep all story images inside the article column */
article img, figure, figure img{box-sizing:border-box;max-width:100%}
figure.story-feature-image{display:block;width:100%;max-width:100%;height:auto;margin:22px 0 28px;overflow:hidden}
figure.story-feature-image img{display:block;width:100%;max-width:100%;height:clamp(160px,32vw,300px);max-height:300px;object-fit:contain;object-position:center;background:#101525;border:1px solid #26314b;border-radius:10px}
figure.story-feature-image figcaption{max-width:100%;overflow-wrap:anywhere}
@media(max-width:600px){figure.story-feature-image img{height:210px;max-height:210px}}
"""
        doc = doc.replace("</style>", safe_image_css + "</style>", 1)

    edition.write_text(doc, encoding="utf-8")

    # Keep the homepage lead panel in sync with the first approved image/story.
    _, lead_heading_html, lead_figure = selected[0]
    lead_heading = clean_text(re.sub(r"<.*?>", " ", lead_heading_html))
    lead_asset_match = re.search(r'<img src="([^"]+)" alt="([^"]*)"', lead_figure)
    lead_credit_match = re.search(r"<figcaption>(.*?)</figcaption>", lead_figure, re.S)
    if lead_asset_match:
        homepage = ROOT / "index.html"
        if homepage.exists():
            home = homepage.read_text(encoding="utf-8")
            image_src, image_alt = lead_asset_match.group(1), lead_asset_match.group(2)
            credit_html = lead_credit_match.group(1) if lead_credit_match else "Image credit and licence verified"
            lead_date = date.fromisoformat(edition.stem).strftime("%d %B %Y").upper()
            panel = (
                '<div class="feature-panel"><div class="feature-image-wrap">'
                f'<img class="lead-story-image" src="{image_src}" alt="{html.escape(image_alt, quote=True)}">'
                f'<small style="display:block;font-size:9px;line-height:1.35;color:#748198;opacity:.72">{credit_html}</small></div><div>'
                f'<span class="category cyan">{lead_date} · LEAD STORY</span>'
                f'<h3>{html.escape(lead_heading)}</h3>'
                f'<p>Selected lead story from the latest MGC Cycling Intelligence briefing.</p>'
                f'<a class="text-link" href="{edition.name}">READ TODAY\\'S BRIEF <span>↗</span></a>'
                '</div></div>'
            )
            home, count = re.subn(
                r'<div class="feature-panel">.*?</div></div>',
                lambda _: panel, home, count=1, flags=re.S
            )
            if count:
                homepage.write_text(home, encoding="utf-8")
                print("Updated homepage lead image and headline.")
            else:
                print("Homepage feature panel not found; article images were still published.")

    print(f"Inserted {len(selected)} verified image(s) into {edition.name}.")

if __name__ == "__main__":
    main()
