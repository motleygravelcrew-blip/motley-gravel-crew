# MGC Cycling Intelligence — Manual Publishing Procedure

## Operating model

Cycling Intelligence is prepared manually with ChatGPT and published through the existing GitHub website workflow. This avoids OpenAI API usage and API charges.

The autonomous research engine and its scripts are retained in the repository for possible future use. The paid scheduled workflow is paused and is not required for manual editions.

## Publication schedule

- Target editions: Monday and Thursday.
- Target publication time: 6:00 am Perth time (AWST).
- An edition may also be prepared and published on another day when useful.
- The schedule is an editorial target, not an unattended scheduled action. A person must start the ChatGPT preparation and publishing process.

## Preparation

1. In the MGC development conversation, ask ChatGPT: "Prepare the MGC Cycling Intelligence edition for [publication date]. Use the standing MGC editorial brief and manual publishing procedure."
2. ChatGPT researches current cycling developments using public sources and prepares the complete edition.
3. Require coverage of the established editorial areas:
   - Road
   - Gravel
   - XCO/XCM
   - Cyclocross
   - Technology
   - Western Australian cycling
4. Prioritise material developments, primary sources and official announcements. Use reputable independent reporting for context and corroboration.
5. Each story must include its publication/event date where relevant, a clear factual summary, why it matters, and direct source links.
6. Distinguish confirmed facts from forecasts, rumours, provisional information and manufacturer claims. Do not pad the edition to fill a category; state when there is no material update.
7. Check for overlap with recent editions. Do not recycle an old story as new without a meaningful update.
8. Use Australian English and MGC's established editorial voice.

## Editorial and image checks

Before publication, check:
- Names, dates, results, event details, figures and quotations against the linked sources.
- Each source link opens the source cited and supports the adjacent claims.
- No invented quotes, claims, attributions or dates.
- No duplicate or stale stories presented as new.
- The lead summary accurately reflects the edition.
- The page date and weekday are correct in Perth time.

Images are optional. Publish without an image if reuse rights and relevance cannot be verified. A search result or public webpage is not permission to republish. Any image used must meet `EDITORIAL-IMAGE-STANDARD.md`, with creator, source, licence/permission and any material edits credited visibly.

## Website article format

Create a dated HTML file in the repository root named `YYYY-MM-DD.html`, using the existing dated edition pages as the visual and structural template. Preserve:
- The existing MGC dark theme, typography, header and navigation.
- A clear edition date and location (Perth, Western Australia).
- A concise "THE MGC READ" lead summary inside a blockquote.
- The established editorial section headings and numbered layout.
- Story headlines, readable paragraphs, "Why it matters" analysis and direct source links.
- Optional properly credited story images only when verified.
- The footer and links consistent with recent editions.

Do not edit unrelated pages or replace the existing publication design.

## Publishing

1. Review the complete HTML edition and confirm the filename date is correct.
2. Add the dated HTML file to the repository's `main` branch in a commit. This is the publication action and may trigger the website host to deploy the new article.
3. The existing `.github/workflows/cycling-intelligence-publication.yml` workflow detects a new dated edition on `main`, runs the existing editorial image discovery safeguards, regenerates:
   - Homepage latest-edition feature
   - Editions listing
   - Archive
   - RSS feed (`feed.xml`)
   - Sitemap (`sitemap.xml`)
4. The workflow validates the generated XML and publication files, then commits the updated indexes to `main`.
5. Check the GitHub Actions run. If it fails, inspect the logs and correct the cause. Do not claim the full publication is complete until the index workflow succeeds.
6. Verify the public dated article, homepage feature, editions listing, archive, RSS and sitemap after deployment.

The index workflow is separate from article preparation. It does not perform editorial research or write the story.

## No-cost rule

- Do not call the OpenAI API or run `scripts/generate_cycling_intelligence.py` for manual editions.
- Do not trigger or recreate a paid scheduled research workflow without a separate decision.
- ChatGPT manual research and drafting uses the user's existing ChatGPT access; any applicable ChatGPT plan limits still apply.
- Existing website hosting, GitHub and domain-provider terms or charges are separate from OpenAI API charges.

## Completion checklist

- [ ] Correct dated filename and edition date
- [ ] All stories checked against direct sources
- [ ] No invented facts, quotes, sources or image permissions
- [ ] Required editorial areas considered
- [ ] Duplicates checked against recent editions
- [ ] HTML structure and links reviewed
- [ ] Dated article committed to `main`
- [ ] GitHub publication/index workflow successful
- [ ] Homepage, editions page and archive verified
- [ ] RSS and sitemap valid and updated
- [ ] Public article and homepage checked after deployment
