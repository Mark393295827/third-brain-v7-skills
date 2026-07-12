# 3-Minute Quickstart: Ingest One Source

Use this when you want the fastest visible win from Third Brain V7 Skills.

## Before

You have a useful article, PDF, transcript, or rough note, but it is not connected to your long-term knowledge base.

## Input

```text
Source: one article, PDF excerpt, meeting note, transcript, or copied paragraph.
Goal: preserve source provenance and create reusable wiki pages.
```

## Prompt

```text
Use wiki-ingest on this source.

Goal: turn it into reusable wiki knowledge, not a loose summary.

Create:
1. one immutable source note in `SOURCES_DIR` (default: `sources/`)
2. 3-7 key insights with source references
3. at least one concept page in `CONCEPTS_DIR` (default: `wiki/concepts/`)
4. relevant entity pages in `ENTITIES_DIR` (default: `wiki/entities/`)
5. links from the new pages to existing related pages when possible
6. a short log entry in `LOG_FILE` (default: `system/log.md`)

After writing files, run a quick verification:
- list created or updated files
- check each wiki page has at least two wikilinks
- state any claims that are single-source only
```

## Expected Output

- A source note that preserves the original source metadata.
- One or more concept/entity notes that can be reused later.
- A short ingestion log.
- A verification note showing what changed.

## After

The loose source becomes a linked knowledge unit with traceable claims, reusable concepts, and a clear next retrieval path.

## Verification Receipt

The run is successful when the agent can point to the created files and every new concept page has:

- frontmatter
- at least two `[[wikilinks]]`
- source references
- a timeline entry
