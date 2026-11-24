# MGC Editorial Image Standard

## Purpose
Use photography to clarify and strengthen a specific published story. Images are editorial assets, not decoration.

## Selection rules
- Choose an image that directly depicts the story subject, event, product or location whenever possible.
- Never imply that an illustrative or archive photograph depicts the specific event or announcement being reported.
- Do not copy an image from a linked news article merely because the article is cited.
- A source page, link or public visibility is not permission to republish.
- Prefer original MGC photography with permission, official press/media assets with explicit reuse permission, or files carrying a verified open licence.
- Check the individual file's licence and attribution requirements before use. Record the photographer/creator, source page, licence name and licence URL.
- If the licence or permission cannot be verified, do not publish the image. Run the story without one.
- Store approved image assets in the repository under `assets/editorial/` so published pages do not depend on third-party hotlinking.

## Required credit
Every image must have a visible caption/credit beneath it. Include:
1. What the image depicts, with any illustrative/archive qualification.
2. Photographer or creator.
3. Source page.
4. Licence and licence link, or a clear permission acknowledgement.

For Creative Commons images, include the licence and indicate if the image has been cropped, edited or otherwise changed. Do not imply endorsement by the creator.

## Article image markup
Use this structure and replace all example values with verified details:

```html
<figure class="story-feature-image">
  <img src="assets/editorial/approved-image.jpg" alt="Accurate description of the image">
  <figcaption>
    Accurate caption. Photo: <a href="SOURCE_PAGE">Creator / source</a> ·
    <a href="LICENCE_URL">Licence</a>. Cropped for layout, if applicable.
  </figcaption>
</figure>
```

## Homepage lead story
The homepage Cycling Intelligence feature should use the lead story's approved image, a concise factual headline, a short summary, the edition date and a direct link to that dated edition. Keep the MGC logo in the site identity/header/footer; do not replace the brand mark itself.

## Automation and editorial control
Image discovery may be assisted by the briefing workflow, but image reuse permission must not be inferred automatically. Before publication, a human/editorial check must approve the exact image, source, licence/permission and credit. If no approved image is available by publication time, publish without an image rather than delaying or using an unverified image.

## Current example
The 22 November 2026 lead-story image is an illustrative professional road-racing peloton photograph by Rz98, sourced from Wikimedia Commons under CC BY-SA 4.0. It is explicitly captioned as illustrative and not as a photograph of the Collective Cycling Group announcement.
