#!/usr/bin/env python3
"""Autonomous MGC Cycling Intelligence editor.

Uses the OpenAI Responses API with web search. It fails closed when credentials,
research evidence, source attribution, or output validation are insufficient.
"""
from __future__ import annotations
import datetime as dt
import html
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://motleygravelcrew.com"
AWST = ZoneInfo("Australia/Perth")
MODEL = os.environ.get("MGC_OPENAI_MODEL", "").strip()
API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
RESEARCH_DATE = dt.datetime.now(AWST).date()
EDITION_DATE = dt.date.fromisoformat((os.environ.get("MGC_EDITION_DATE") or RESEARCH_DATE.isoformat()))
DATE_FILE = ROOT / f"{EDITION_DATE.isoformat()}.html"
CATEGORIES = ["ROAD", "GRAVEL", "XCO / XCM", "CYCLOCROSS", "TECHNOLOGY", "WESTERN AUSTRALIA"]

SCHEMA = {
  "type":"object","additionalProperties":False,
  "properties":{
    "edition_title":{"type":"string"},
    "standfirst":{"type":"string"},
    "lead_story":{"type":"string"},
    "sections":{"type":"array","minItems":4,"maxItems":6,"items":{
      "type":"object","additionalProperties":False,
      "properties":{
        "category":{"type":"string","enum":CATEGORIES},
        "stories":{"type":"array","minItems":0,"maxItems":3,"items":{
          "type":"object","additionalProperties":False,
          "properties":{
            "headline":{"type":"string"},
            "published_or_event_date":{"type":"string"},
            "body":{"type":"string"},
            "why_it_matters":{"type":"string"},
            "status":{"type":"string","enum":["confirmed","provisional","manufacturer claim","no verified material update"]},
            "sources":{"type":"array","minItems":0,"maxItems":5,"items":{
              "type":"object","additionalProperties":False,
              "properties":{"name":{"type":"string"},"url":{"type":"string"},"source_date":{"type":"string"},"type":{"type":"string","enum":["primary","governing body","organiser","team","manufacturer","reputable media","other"]}},
              "required":["name","url","source_date","type"]
            }}
          },
          "required":["headline","published_or_event_date","body","why_it_matters","status","sources"]
        }}
      },
      "required":["category","stories"]
    }},
    "editorial_check":{"type":"array","items":{"type":"string"},"minItems":2,"maxItems":8}
  },
  "required":["edition_title","standfirst","lead_story","sections","editorial_check"]
}

def api_research():
    if not API_KEY or not MODEL:
        raise RuntimeError("Missing OPENAI_API_KEY or MGC_OPENAI_MODEL repository secret/variable.")
    previous = sorted(ROOT.glob("20??-??-??.html"), reverse=True)[:4]
    previous_text = []
    for p in previous:
        text = re.sub(r"<[^>]+>", " ", p.read_text(encoding="utf-8"))
        previous_text.append(f"\n--- {p.name} ---\n" + re.sub(r"\s+", " ", html.unescape(text))[:5000])
    prompt = f"""
You are the independent editorial desk of Motley Gravel Crew (MGC), a Western Australian cycling community publication.
Prepare the {RESEARCH_DATE.strftime('%A, %d %B %Y')} Cycling Intelligence edition for publication at 6:00am AWST.
Research current, genuinely material developments available as at today. Use web search extensively across:
{', '.join(CATEGORIES)}.
Prioritise primary sources: UCI, AusCycling, event organisers, teams, race timing/results, manufacturers for their own announcements. Use reputable cycling media for context and cross-checking.
Rules:
- Never invent facts, quotations, results, dates, prices, sources, or URLs.
- Every reported story must cite at least one direct source; important/high-impact claims should have two independent sources where available.
- Use source URLs actually returned/visited during research. No homepages or guessed URLs.
- Separate confirmed facts, provisional information and manufacturer claims. Attribute claims.
- Compare with previous MGC editions below. Do not repeat an item unless a material update occurred; explain the update.
- Include Western Australian cycling developments when verifiable. Do not pad with low-value news.
- Every category may contain zero stories. For empty categories include one story object with headline "No verified material update", status "no verified material update", body explaining the scope searched, empty sources, and why_it_matters empty.
- Aim for 6–10 substantial stories overall, across at least four categories where news permits. Quality beats quota.
- Article body must be factual, readable Australian English, concise and specific. Include why_it_matters analysis. Avoid unsupported speculation.
- lead_story must exactly match one story headline.
- Return strict JSON matching the schema. Use complete canonical source URLs and source publication dates or "date not stated".
Previous editions for duplicate control:
{''.join(previous_text)}
"""
    payload = {
      "model": MODEL,
      "input": [{"role":"user","content":[{"type":"input_text","text":prompt}]}],
      "tools":[{"type":"web_search"}],
      "tool_choice":"auto",
      "text":{"format":{"type":"json_schema","name":"mgc_cycling_intelligence","strict":True,"schema":SCHEMA}}
    }
    req=urllib.request.Request("https://api.openai.com/v1/responses",data=json.dumps(payload).encode(),
      headers={"Authorization":f"Bearer {API_KEY}","Content-Type":"application/json","User-Agent":"MGC-Cycling-Intelligence/1.0"})
    try:
        with urllib.request.urlopen(req,timeout=240) as res: response=json.loads(res.read())
    except urllib.error.HTTPError as exc:
        detail=exc.read().decode("utf-8","replace")[:2000]
        raise RuntimeError(f"OpenAI Responses API error {exc.code}: {detail}") from exc
    output=[]
    verified_urls=set()
    for item in response.get("output",[]):
        for part in item.get("content",[]):
            if part.get("type")=="output_text":
                output.append(part.get("text",""))
                for annotation in part.get("annotations",[]):
                    if annotation.get("type")=="url_citation" and annotation.get("url"):
                        verified_urls.add(annotation["url"])
    if not output: raise RuntimeError("Research engine returned no structured output.")
    try: return json.loads(output[-1]), verified_urls
    except json.JSONDecodeError as exc: raise RuntimeError("Research engine returned invalid JSON.") from exc

def validate(data, verified_urls):
    if not isinstance(data,dict) or not data.get("sections"): raise RuntimeError("No editorial sections returned.")
    all_stories=[]
    for section in data["sections"]:
        if section["category"] not in CATEGORIES: raise RuntimeError("Unknown editorial category.")
        for story in section["stories"]:
            if story["status"]=="no verified material update": continue
            if len(story["body"].strip())<80: raise RuntimeError(f"Story too short: {story['headline']}")
            if not story["sources"]: raise RuntimeError(f"Story has no sources: {story['headline']}")
            for source in story["sources"]:
                if not re.match(r"^https://",source["url"]) or not source["name"].strip():
                    raise RuntimeError(f"Invalid or unattributed source in {story['headline']}")
                if source["url"] not in verified_urls:
                    raise RuntimeError(f"Source URL was not present in web-search citations: {source['url']}")
            all_stories.append(story)
    if len(all_stories)<4: raise RuntimeError(f"Only {len(all_stories)} sourced stories; minimum is four. Fail-safe: no publication.")
    headlines=[s["headline"] for s in all_stories]
    if data["lead_story"] not in headlines: raise RuntimeError("Lead story does not match a sourced story.")
    return all_stories

def render(data):
    date_label=RESEARCH_DATE.strftime("%A, %d %B %Y")
    out=[f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#070912"><title>{html.escape(data['edition_title'])} | Motley Gravel Crew</title><meta name="description" content="{html.escape(data['standfirst'][:250],quote=True)}"><link rel="stylesheet" href="styles.css"><link rel="canonical" href="{SITE}/{EDITION_DATE.isoformat()}.html"><link rel="alternate" type="application/rss+xml" title="MGC Cycling Intelligence" href="{SITE}/feed.xml"><style>:root{{color-scheme:dark}}body{{background:#070912;color:#f3f5fb;font-family:Arial,sans-serif;line-height:1.7}}main{{max-width:900px;margin:auto;padding:36px 22px}}article h2{{color:#28e4f0;border-bottom:1px solid #26314b;padding-bottom:8px;margin-top:40px}}article h3{{font-size:1.35rem;margin:22px 0 8px}}article p,article li{{color:#d7dced}}article a{{color:#28e4f0;overflow-wrap:anywhere}}blockquote{{background:#101525;border-left:3px solid #ff39bd;padding:14px 18px}}.mast{{border-bottom:1px solid #26314b;margin-bottom:26px}}.eyebrow{{color:#ff39bd;letter-spacing:.16em;font-weight:bold}}.edition-nav{{display:flex;gap:14px;flex-wrap:wrap}}.edition-nav a{{color:#28e4f0}}</style></head><body><main><nav class="edition-nav"><a href="index.html">MGC HOME</a><a href="editions.html">CYCLING INTELLIGENCE</a><a href="archive.html">ARCHIVE</a><a href="routes.html">MGC ROUTE LIBRARY</a></nav><header class="mast"><p class="eyebrow">MGC / CYCLING INTELLIGENCE</p><h1>{html.escape(data['edition_title'])}</h1><p>{date_label} · Perth, Western Australia</p></header><article><p><strong>{date_label} | Perth, Western Australia</strong><br><em>Road · Gravel · XCO/XCM · Cyclocross · Technology · WA Cycling Community</em></p><blockquote><strong>THE MGC READ</strong><br>{html.escape(data['standfirst'])}</blockquote>"""]
    for section in data["sections"]:
        out.append(f"<h2>{html.escape(section['category'])}</h2>")
        if not section["stories"]:
            out.append("<p>No story supplied for this category.</p>"); continue
        for story in section["stories"]:
            if story["status"]=="no verified material update":
                out.append(f"<p><strong>{html.escape(story['headline'])}.</strong> {html.escape(story['body'])}</p>"); continue
            out.append(f"<h3>{html.escape(story['headline'])}</h3>")
            if story["published_or_event_date"] and story["published_or_event_date"]!="date not stated":
                out.append(f"<p><strong>{html.escape(story['published_or_event_date'])}:</strong></p>")
            out.append(f"<p>{html.escape(story['body'])}</p><p><strong>Why it matters:</strong> {html.escape(story['why_it_matters'])}</p>")
            out.append("<p><strong>Sources:</strong> "+" · ".join(f'<a href="{html.escape(s["url"],quote=True)}" rel="noopener">{html.escape(s["name"])} ({html.escape(s["source_date"])})</a>' for s in story["sources"])+"</p>")
    out.append("<h2>EDITORIAL CHECK</h2><ul>")
    out.extend(f"<li>{html.escape(x)}</li>" for x in data["editorial_check"])
    out.append("</ul><p><em>Ride hard. Stay curious. Keep the wheels turning.</em></p><p><strong>MOTLEY GRAVEL CREW</strong><br>One crew. Every ride.</p></article><nav class=\"edition-nav\"><a href=\"index.html\">RETURN TO MGC HOMEPAGE</a><a href=\"archive.html\">VIEW ALL EDITIONS</a></nav></main><footer style=\"text-align:center;padding:24px;color:#aab3c8\">© "+str(EDITION_DATE.year)+" Motley Gravel Crew · Western Australia</footer></body></html>")
    return "\n".join(out)

def main():
    if DATE_FILE.exists(): raise RuntimeError(f"{DATE_FILE.name} already exists. Refusing to overwrite an edition.")
    data, verified_urls=api_research()
    if not verified_urls: raise RuntimeError("Web search returned no attributable URL citations.")
    validate(data, verified_urls)
    DATE_FILE.write_text(render(data),encoding="utf-8")
    print(f"Drafted and validated {DATE_FILE.name} with source-backed stories.")
    print("Images intentionally omitted unless a separate strict image verification stage approves one.")

if __name__=="__main__":
    try: main()
    except Exception as exc:
        print(f"EDITORIAL ENGINE FAILED CLOSED: {exc}",file=sys.stderr)
        sys.exit(1)
