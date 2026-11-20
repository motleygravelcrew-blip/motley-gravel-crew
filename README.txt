MOTLEY GRAVEL CREW — CYCLING HUB WEBSITE STARTER

This is a static website designed for GitHub + Cloudflare Pages free hosting.

FILES
- index.html: page structure
- styles.css: neon MGC visual design and responsive layout
- script.js: date, navigation and daily brief loader
- brief.json: the daily edition content (edit this for each new brief)
- config.json: the supplied Facebook and Strava URLs are already configured in config.json
- assets/mgc-hero-banner.jpg: official supplied MGC neon banner, used as the full-width homepage hero without cropping

HOW TO UPDATE THE DAILY BRIEF
Edit brief.json. Replace the sample titles and summaries with verified, dated information and original source URLs. Keep the same JSON structure. This starter website does not automatically gather or verify news; it is ready for daily editorial content to be added.

HOW TO ADD SOCIAL LINKS
Edit config.json and add:
{
  "facebookUrl": "https://www.facebook.com/groups/YOUR-GROUP",
  "stravaUrl": "https://www.strava.com/clubs/YOUR-CLUB"
}

PUBLISH WITH CLOUDFLARE PAGES
1. Create a GitHub repository (e.g. motley-gravel-crew).
2. Upload all files and folders in this package to the repository root.
3. In Cloudflare, open Workers & Pages > Create > Pages > Connect to Git.
4. Select the repository. Framework preset: None. Build command: leave blank. Build output directory: / (or the repository root as Cloudflare's UI requests).
5. Deploy. Cloudflare provides a preview pages.dev address.
6. Add the custom domain only after confirming the preview works.
7. Before changing GoDaddy nameservers or DNS, record existing DNS records and check whether any email services depend on them.

The site uses Google Fonts if available; system sans-serif fallbacks are included.
No paid services are required for this static starter. Cloudflare and GitHub free-plan terms and limits apply.
