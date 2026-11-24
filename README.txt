MOTLEY GRAVEL CREW — WEBSITE

Static website hosted through GitHub and Cloudflare Pages.

PAGES
- index.html: homepage
- editions.html: Monday and Thursday editions
- archive.html: dated archive
- routes.html: community Strava route information and submission route
- about.html: publication purpose and editorial standards
- 2026-11-21.html and 2026-11-22.html: existing dated editions

SHARED FILES
- styles.css: shared responsive visual system
- script.js: mobile navigation and footer year
- config.json: official Facebook and Strava links
- assets/mgc-hero-banner.jpg: approved MGC banner

EDITORIAL SCHEDULE
Monday and Thursday, 6:00 am Australia/Perth.

ROUTE SUBMISSIONS
Until a dedicated form backend is configured, followers submit public Strava route links through the MGC Facebook page. MGC reviews routes before listing them.

DEPLOYMENT
Cloudflare Pages is connected to this GitHub repository. Commits to main should trigger a deployment. This website rebuild is prepared on a separate branch for review before publication.