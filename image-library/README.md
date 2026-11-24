# MGC Wikimedia image scout

This GitHub Actions workflow searches Wikimedia Commons for cycling-related image candidates and records machine-readable creator and licence metadata.

## What it does
- Searches gravel, road, MTB, bikepacking and Western Australian cycling subjects.
- Uses the Commons MediaWiki Action API and imageinfo/extmetadata.
- Keeps only candidates with a recognised CC0, public-domain, CC BY or CC BY-SA licence field and a named creator.
- Produces a JSON catalogue and a readable Markdown review list in this folder.
- Runs weekly and can also be started manually from GitHub Actions.

## What it deliberately does not do
- It does not download, hotlink into the live site, or publish images.
- It does not treat metadata as legal approval. The Commons file page must still be opened and checked for the exact licence, credit wording, restrictions, accuracy and any non-copyright rights.
- It rejects records where the licence or creator field is missing or not on the allow-list.

The catalogue is an editorial shortlist, not an approved image bank. Keep the source-page and licence details with any image later approved for MGC use.
