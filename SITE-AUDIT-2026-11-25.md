# MGC Website Audit — 25 November 2026

## Scope and evidence
Reviewed the GitHub `main` branch source for all nine HTML pages (home, About, Archive, Cycling Intelligence, Events, Cycling Links, Route Library, and the 21/22 November editions), the shared CSS and JavaScript, image assets, RSS feed, sitemap, robots.txt, newsletter form, and GitHub Actions workflows. The live site could not be fetched from the audit runtime because external DNS/network resolution was unavailable. Therefore live HTTP status, browser rendering, Core Web Vitals, mobile interaction, form submission, Strava embed behaviour, and Cloudflare deployment status remain unverified.

## Findings

### High priority
1. **Newsletter retained old Pages URLs.** The homepage form action uses Simple Newsletter and its hidden feed/return fields still pointed to `motley-gravel-crew.pages.dev`. The form provider has not been replaced. Actual subscription/confirmation/unsubscribe could not be tested without submitting a real address and validating the provider response.
2. **Publishing automation is incomplete.** The RSS workflow rebuilds `feed.xml` when a dated HTML edition is pushed, but it does not regenerate `sitemap.xml`, `archive.html`, or the latest-edition list on `editions.html`. Those are currently maintained as static lists.
3. **Image discovery workflow can push directly to main.** The image workflow has write permissions and commits discovered image placements/assets directly to `main`, which can trigger live deployment. Its checks are conservative (Commons reuse licence allow-list, creator/source metadata, minimum dimensions, type/signature and download-size checks, and keyword overlap), but they are not a substitute for editorial review or end-to-end testing. No workflow run logs were verified during this audit.
4. **SEO metadata is inconsistent.** Before this audit, most inner pages and dated editions lacked descriptions, canonical URLs and social metadata; homepage was more complete.
5. **Sitemap is manually maintained.** It lists the current seven core pages and two dated editions, but no generator currently keeps it in sync with new editions.

### Medium priority
6. **Archive and edition indexes are manually maintained.** Their copy says new editions will appear automatically, but the current workflow does not update these lists.
7. **Cross-page brand language was inconsistent.** Some pages still used the phrase “Independent Cycling Journalism” in the top strip, and dated edition navigation still used “Community Routes”.
8. **Strava links were inconsistent.** Several pages used a Strava app-link rather than the canonical MGC club URL.
9. **Cycling Links markup contained literal escaped newline characters** between cards, which could render as stray text.
10. **Image weight.** The approved transparent logo asset is approximately 788 KB and the hero banner approximately 346 KB. They work as source assets but are candidates for properly generated responsive/compressed variants. Do not alter the approved logo artwork.

### Content and organisational checks
- No occurrences of “Bike Place Port Kennedy”, “orange jersey”, or explicit rider-team claims were found in the repository text search performed.
- The About page describes MGC as a publication and community platform, not an established race team.
- Events page includes a legend distinguishing confirmed and TBC dates and includes a dated editorial note (24 November 2026). Event accuracy should be rechecked against organisers before relying on the calendar; this audit did not independently re-verify every event.
- Facebook and Strava links are present. Strava club CTA is prominent on the homepage. The Strava route embed and its external dependency need a real browser test.

## Corrections prepared on this branch
- Added unique meta descriptions and canonical URLs to all nine HTML pages.
- Added Open Graph and Twitter card metadata across all nine pages.
- Added homepage Organization and WebSite JSON-LD using the published MGC website, Facebook page and Strava club URLs.
- Replaced the old Pages-domain newsletter feed and return URLs with the canonical custom domain.
- Standardised the top-strip phrase to “ONE CREW. EVERY RIDE.”
- Replaced Strava app-links with the direct MGC Strava club URL where they appeared.
- Removed literal escaped newline text from Cycling Links markup.

These changes are on the audit branch only and have not been deployed.

## Verification completed
- Confirmed the repository is public, default branch is `main`, and the connected GitHub integration has push/admin permissions.
- Checked local page references against the repository's known root-page inventory; no missing local HTML/CSS/JS page references were found in the nine reviewed pages.
- Confirmed all nine pages on the audit branch now have a canonical URL and meta description.
- Confirmed the homepage no longer contains the old Pages-domain newsletter URL.
- Confirmed text search found no Bike Place Port Kennedy or orange jersey references.
- Confirmed `robots.txt` allows crawling and declares the canonical sitemap URL.
- Confirmed `sitemap.xml` currently lists the core pages and two dated editions.
- Confirmed RSS is generated by `scripts/build_rss_feed.py` and its workflow triggers on dated HTML changes.

## Outstanding work before declaring complete
1. Review and merge the audit pull request only after visual review; Cloudflare Pages deployment will then need to complete successfully.
2. Verify custom-domain HTTP/HTTPS responses for every page, `/sitemap.xml`, `/robots.txt`, `/feed.xml`, favicon, logo and all local assets.
3. Test newsletter subscription with a controlled test address, including confirmation, return URL and unsubscribe; check Simple Newsletter account settings for domain/feed restrictions.
4. Build and test a single publication-index generator that updates archive, latest editions, RSS and sitemap from dated edition pages. Keep a clear editorial approval gate before a new edition reaches `main`.
5. Change image discovery to produce a reviewable pull request (or a report-only candidate manifest) rather than pushing unreviewed image changes directly to `main`. Validate attribution, licence version, story relevance and actual image display before merge.
6. Recheck every event listing against official organiser sources and update the calendar's “checked” date.
7. Run browser-based desktop/mobile checks, keyboard/accessibility checks, broken external-link checks, Lighthouse/PageSpeed and Cloudflare deployment checks.
8. Review image compression and responsive delivery without changing the approved brand artwork.

## Deployment safety
No changes from this branch have been deployed. Merge only after review. Cloudflare Pages is connected to GitHub `main`, so a merge to `main` is expected to trigger production deployment. Verify the Cloudflare deployment status and live custom domain after merge. Do not change DNS for this work.
