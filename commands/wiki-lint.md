---
name: wiki-lint
description: Run a health check on the wiki. Invoke with /wiki-lint or "lint the wiki".
---
Run the `wiki-lint` skill as a twelve-check health audit:

1. required frontmatter and stable identifiers;
2. broken wikilinks and unresolved embeds;
3. source references and block locators;
4. orphan concepts and isolated entities;
5. duplicate titles or semantic duplicates;
6. stale notes and unresolved contradictions;
7. single-source or weak-provenance claims;
8. concept structure and understanding-gate integrity;
9. clipping archive and source lifecycle;
10. permission, immutable-source, and human-approval boundaries;
11. daily-loop receipts and flywheel write-back;
12. V8.1 promotion-gate readiness for proposed rules.

Before scanning, resolve paths from `system/config.md` when present. The run is successful only when the skill's `## Success Metrics` and `## Quality Gates` are satisfied, including writing the report to `LINT_REPORT_FILE` and avoiding source-file modifications.
