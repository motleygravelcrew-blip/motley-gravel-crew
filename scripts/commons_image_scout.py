#!/usr/bin/env python3
"""Build a review-only catalogue of Wikimedia Commons cycling images.

Only candidates with a recognised reusable licence and a named creator are
listed. Nothing is downloaded or published automatically.
"""
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "MotleyGravelCrewImageScout/1.0 (https://motleygravelcrew.com; editorial image research)"
QUERIES = [
    "gravel cycling",
    "gravel bike race",
    "road cycling race",
    "mountain biking",
    "bikepacking",
    "cycling Western Australia",
]
PER_QUERY = 8
APPROVED_FILE_TITLES = [
    "File:Gravel bike race in southeast Oregon (28438800417).jpg",
    "File:Cyclist on gravel bike descending Eldridge Grade.jpg",
    "File:Gravel-bike-fitted-with-aerobars-for-racing.jpg",
]
APPROVED_REVIEW = {
    "File:Gravel bike race in southeast Oregon (28438800417).jpg": {
        "editorial_title": "Gravel racing",
        "editorial_caption": "Riders competing in the Skull 120/60/30 off-road race in southeast Oregon, 16 June 2018. Illustrative gravel-racing photography, not a current event image.",
        "reviewed_creator": "BLM Oregon & Washington",
        "reviewed_licence": "CC BY 2.0",
        "licence_url": "https://creativecommons.org/licenses/by/2.0/",
    },
    "File:Cyclist on gravel bike descending Eldridge Grade.jpg": {
        "editorial_title": "Gravel riding",
        "editorial_caption": "A cyclist descending Eldridge Grade on a gravel bike. Illustrative cycling photography.",
        "reviewed_creator": "Drakepirates",
        "reviewed_licence": "CC BY-SA 4.0",
        "licence_url": "https://creativecommons.org/licenses/by-sa/4.0/",
    },
    "File:Gravel-bike-fitted-with-aerobars-for-racing.jpg": {
        "editorial_title": "Gravel equipment",
        "editorial_caption": "A gravel bike fitted with clip-on aerobars for racing. Illustrative equipment photography.",
        "reviewed_creator": "Jeff Dieffenbach",
        "reviewed_licence": "CC BY 4.0",
        "licence_url": "https://creativecommons.org/licenses/by/4.0/",
    },
}
OUT = Path("image-library")
OUT.mkdir(exist_ok=True)


def plain(value):
    if isinstance(value, dict):
        value = value.get("value", "")
    value = html.unescape(str(value or ""))
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def api(params):
    url = API + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=35) as response:
        return json.loads(response.read().decode("utf-8"))


def permitted(licence):
    value = licence.lower().replace("-", " ").strip()
    if "noncommercial" in value or "no derivatives" in value or "nd" in value.split():
        return False
    return (
        value.startswith("cc0")
        or value.startswith("public domain")
        or value.startswith("pd ")
        or value.startswith("cc by ")
        or value.startswith("cc by/")
        or value.startswith("cc by sa")
        or value.startswith("cc by-sa")
    )


def main():
    candidates = {}
    for query in QUERIES:
        data = api({
            "action": "query",
            "generator": "search",
            "gsrsearch": query,
            "gsrnamespace": 6,
            "gsrlimit": PER_QUERY,
            "prop": "imageinfo",
            "iiprop": "url|extmetadata",
            "iiurlwidth": 1400,
            "format": "json",
            "formatversion": 2,
        })
        for page in data.get("query", {}).get("pages", []):
            info = (page.get("imageinfo") or [{}])[0]
            meta = info.get("extmetadata") or {}
            licence = plain(meta.get("LicenseShortName"))
            artist = plain(meta.get("Artist"))
            if not permitted(licence) or not artist:
                continue
            file_url = info.get("thumburl") or info.get("url")
            original_url = info.get("url")
            page_url = info.get("descriptionurl")
            if not file_url or not page_url:
                continue
            key = page.get("title")
            item = candidates.setdefault(key, {
                "title": plain(meta.get("ObjectName")) or key.removeprefix("File:"),
                "commons_file": key,
                "preview_url": file_url,
                "original_file_url": original_url,
                "source_page": page_url,
                "creator": artist,
                "credit": plain(meta.get("Credit")),
                "licence": licence,
                "licence_url": plain(meta.get("LicenseUrl")),
                "attribution": plain(meta.get("Attribution")),
                "description": plain(meta.get("ImageDescription")),
                "width": info.get("width"),
                "height": info.get("height"),
                "found_for": [],
                "review_status": "REVIEW REQUIRED — NOT APPROVED FOR PUBLICATION",
            })
            if query not in item["found_for"]:
                item["found_for"].append(query)
        time.sleep(1.2)

    ordered = sorted(candidates.values(), key=lambda x: (len(x["found_for"]), x["title"]), reverse=True)
    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source": "Wikimedia Commons MediaWiki Action API",
        "notice": "Candidate discovery only. An editor must open the source page and verify licence, attribution, restrictions, subject accuracy and any non-copyright rights before use.",
        "count": len(ordered),
        "candidates": ordered,
    }
    (OUT / "commons-candidates.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Wikimedia Commons image candidates",
        "",
        f"Generated: {payload['generated_utc']}",
        "",
        f"**{len(ordered)} candidates found. None are approved or automatically published.**",
        "",
        "Open each Commons file page and verify the current licence, creator, attribution wording, restrictions and that the photograph actually matches the proposed story.",
        "",
    ]
    for i, item in enumerate(ordered, 1):
        lines += [
            f"## {i}. {item['title']}",
            "",
            f"- Preview: {item['preview_url']}",
            f"- Commons file page: {item['source_page']}",
            f"- Creator: {item['creator']}",
            f"- Licence: {item['licence']} ({item['licence_url'] or 'licence link not supplied'})",
            f"- Credit: {item['credit'] or 'Not supplied'}",
            f"- Search topics: {', '.join(item['found_for'])}",
            f"- Status: {item['review_status']}",
            "",
        ]
    (OUT / "commons-candidates.md").write_text("\n".join(lines), encoding="utf-8")
    # Refresh the small, human-reviewed allow-list used by the live website.
    approved = []
    for title in APPROVED_FILE_TITLES:
        data = api({
            "action": "query", "titles": title, "prop": "imageinfo",
            "iiprop": "url|extmetadata", "iiurlwidth": 1200,
            "format": "json", "formatversion": 2,
        })
        pages = data.get("query", {}).get("pages", [])
        if not pages or pages[0].get("missing"):
            continue
        info = (pages[0].get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata") or {}
        actual_creator = plain(meta.get("Artist"))
        actual_licence = plain(meta.get("LicenseShortName"))
        review = APPROVED_REVIEW[title]
        # Fail closed if the live Commons metadata no longer matches the reviewed record.
        if (not actual_creator or not actual_licence or
            actual_creator != review["reviewed_creator"] or
            actual_licence != review["reviewed_licence"] or
            not permitted(actual_licence)):
            print(f"Skipping {title}: Commons metadata differs from reviewed allow-list.", file=sys.stderr)
            continue
        if not info.get("thumburl") or not info.get("descriptionurl"):
            continue
        approved.append({
            "file": title,
            "preview_url": info["thumburl"],
            "source_page": info["descriptionurl"],
            "creator": actual_creator,
            "licence": actual_licence,
            "licence_url": review["licence_url"],
            "editorial_title": review["editorial_title"],
            "editorial_caption": review["editorial_caption"],
            "alt": review["editorial_title"] + " — Wikimedia Commons photograph",
        })
        time.sleep(1.2)
    (OUT / "approved-images.json").write_text(
        json.dumps({"updated_utc": datetime.now(timezone.utc).isoformat(), "images": approved},
                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(ordered)} candidates and refreshed {len(approved)} approved website images.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Image discovery failed: {exc}", file=sys.stderr)
        raise
