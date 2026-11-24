# MGC image sourcing and reuse policy

## Purpose
Use relevant cycling, event, landscape and equipment imagery to make Motley Gravel Crew more visual without taking images from publishers, photographers or event organisers without permission.

## Approved source order
1. **Wikimedia Commons** — use individual files only after checking the file page and its exact licence. Some files require attribution, a licence link, or share-alike treatment.
2. **Unsplash** — use through the official Unsplash API and follow its current API rules, including the required image URLs, attribution and download-tracking requirements where applicable.
3. **Pexels** — use through its official API and current terms. Do not scrape or systematically bulk-download the site.
4. **Event organisers, clubs and photographers** — use only when the specific image is supplied for media use or written permission is recorded.
5. **MGC community submissions** — request permission from the photographer and confirm that identifiable riders have appropriate consent before publication.

A photo being visible online or described as “free” does not automatically mean MGC has permission to republish it. Do not scrape images from news articles, Facebook, Instagram, race galleries or other websites.

## Required image record
Keep this information with every published image:
- Image filename or stable image URL
- Original source-page URL
- Creator / photographer
- Licence name and licence URL, or written permission reference
- Date accessed or permission received
- Required attribution wording and any restrictions
- Story or page where the image is used

Do not publish an image if its licence or permission cannot be verified. Preserve licence and attribution information if an image is resized or converted.

## Editorial matching
- Prefer a photograph that genuinely depicts the story, event, place or equipment being discussed.
- Never present generic stock photography as if it depicts a named race or incident.
- If a relevant event photograph is unavailable, use a clearly generic cycling image, an original graphic, or a labelled AI-generated illustration.
- Do not imply that an AI illustration is documentary photography or depicts real riders or an actual event.

## Automated publishing workflow
For any future automated story workflow:
1. Identify the story subject and image needs.
2. Search only approved providers or an MGC-approved image library.
3. Retrieve the licence and creator metadata with the image.
4. Reject results with missing or incompatible reuse terms.
5. Select an image that accurately matches the story.
6. Store the image and its attribution record together.
7. Display the creator and source/licence credit on the page where required.
8. Optimise image sizes and formats for mobile and desktop.

The current MGC site is a static website. This policy prepares the editorial standard and page styling; automatic provider searches, licence checks, image downloads and publishing still require a separate publishing workflow and any provider API credentials. They are not silently enabled by this website styling change.

## Display
Use wide editorial crops for lead stories and responsive image cards for supporting stories. Keep image credits readable and visible. Use modern responsive formats such as WebP or AVIF when the publishing pipeline can preserve the original and its licence record.


## Wikimedia Commons discovery automation
The draft repository now includes a GitHub Actions image scout at `.github/workflows/commons-image-scout.yml` and `scripts/commons_image_scout.py`. It searches cycling-related subjects and writes a review-only candidate catalogue to `image-library/commons-candidates.json` and `image-library/commons-candidates.md`.

The scout reads per-file `imageinfo/extmetadata` fields for the licence and creator. It filters out missing creator/licence data and known restrictive licence labels, but metadata extraction is not a legal guarantee and can be incomplete or unreliable for multi-licensed files. Every candidate therefore remains marked **REVIEW REQUIRED** and is not automatically displayed or published. See the [Commons machine-readable metadata guidance](https://commons.wikimedia.org/wiki/Commons:Machine-readable_data) and [Commons licensing policy](https://commons.wikimedia.org/wiki/Commons:Licensing).
