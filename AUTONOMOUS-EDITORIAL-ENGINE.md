# MGC Autonomous Cycling Intelligence Engine

## What it does

The scheduled GitHub Actions workflow researches, drafts, validates and publishes one MGC Cycling Intelligence edition on each Monday and Thursday at 06:00 AWST.

Schedule: `0 22 * * 0,3` UTC (Sunday and Wednesday 22:00 UTC).

The workflow:
1. Checks out the current `main` publication.
2. Uses the OpenAI Responses API with web search to research current cycling developments.
3. Generates structured editorial content with source names, dates, URLs, status labels and editorial checks.
4. Requires each story's source URL to match a URL citation returned by the web-search tool.
5. Refuses publication if there are fewer than four source-backed stories, missing citations, malformed content, or an existing edition for that date.
6. Builds homepage, archive, editions, RSS and sitemap outputs.
7. Validates the candidate and generated outputs.
8. Publishes the edition and all indexes in one commit to `main`. A failed step exits before the push.

No image is inserted by this first engine release. This is the deliberate fail-safe until a separate image stage can establish both reuse rights and genuine relevance. The edition remains publishable without a photograph.

## Required repository configuration

Before enabling the workflow on `main`, configure:

- Repository secret `OPENAI_API_KEY`: an API key with access to the Responses API and web search.
- Repository variable `MGC_OPENAI_MODEL`: the exact model identifier enabled for that API project.

Do not put API keys in workflow files, source code, commits, or logs. If either setting is absent or invalid, the job fails closed and does not publish.

## Important operating limits

- The engine is an automated editorial assistant, not a guarantee that every generated claim is correct. URL citation matching confirms that a source URL was returned by web search; it does not independently prove every sentence in the article.
- It uses source-first instructions, duplicate checks against recent editions, explicit claim-status labels and strict failure conditions.
- Human-readable source links are retained in the article.
- The first release intentionally uses a four-story minimum and does not pad categories with recycled stories.
- GitHub Actions scheduled jobs can start late. The cron is configured for the correct Perth wall-clock time in AWST.
- A workflow failure leaves the previous live edition and site indexes untouched.

## Safe rollout

This workflow must first be tested on a development branch. Do not merge to `main` until repository configuration is present and a full workflow run has been observed. After merge, the schedule becomes active. A manual run should only be used when no edition already exists for the current Perth date.
