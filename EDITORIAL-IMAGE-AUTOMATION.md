# MGC Automatic Editorial Image Discovery

## What the workflow does
When a dated MGC edition is added or updated on the main branch, GitHub Actions runs `scripts/discover_editorial_images.py`. The script searches Wikimedia Commons for up to four images matching story headings, checks each file's metadata and downloads only images that pass all automated checks.

## Automated acceptance rules
- Individual Commons file must expose a licence URL and licence name.
- Only CC0 / public-domain, CC BY and CC BY-SA licences are accepted.
- Non-commercial, no-derivatives, unknown and missing licence metadata are rejected.
- Creator/credit, image description, source page and image URL must be present.
- Image must be at least 700 × 350 pixels, use JPEG/PNG/WebP, remain under 12 MB and pass file-signature validation.
- A minimum keyword match between the story heading and image title/description is required.
- A maximum of four images are added per edition, with no repeated Commons file.
- If nothing passes, the article is published without an image.

## Attribution and storage
Approved images are downloaded into `assets/editorial/` and embedded into the story. Captions link to the original Commons file and the licence, and identify the creator. The site does not hotlink the Commons image file.

## Important limitation
This is conservative automated screening, not a legal guarantee. Commons metadata can be incomplete or incorrect, and keyword matching cannot establish that a photograph depicts the exact event or person in a story. The workflow therefore limits itself to explicit, permissive licence metadata and clearly described matches. For high-risk subjects, identifiable individuals, commercial product imagery or event-specific claims, a human editorial review remains advisable. It will never use images from linked news articles merely because they are linked.

## Trigger and test
The workflow runs when a dated edition page changes, or manually from GitHub Actions using `workflow_dispatch`. It can be tested on a draft dated page. A successful workflow run and actual published image placements must be confirmed before treating the process as operational.
