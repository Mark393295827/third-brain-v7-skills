# Protected-tree drift event

- Mission: `scratch-governance-20260820`
- Detected during T03 attempt 2, before any mission Vault mutation.
- Tree: `.obsidian/`
- Original aggregate: 34 files, 2,805,475 bytes, `29621b98c02332ebf9dc0ffba294f1f4ebb4fa5ca707ac49f4da71696efcc2be`
- Fresh authoritative replay: 34 files, 2,806,067 bytes, `d4f82342d2c25ffca55753bfdd5b3244bdf36500ed8fbf6bc0c5c5030d6a45cb`
- Fresh replay used the same ordinal-path plus per-file SHA-256 aggregation algorithm as `protected-tree-baseline.json`.
- Files with modification times after the original baseline included `.obsidian/workspace.json`, `.obsidian/appearance.json`, `.obsidian/app.json`, `.obsidian/community-plugins.json`, and `.obsidian/core-plugins.json`.
- The scratch executor had not created, deleted, or changed any Vault file when this drift was detected.

## Integration decision

This is concurrent out-of-scope drift in Obsidian's live configuration state. Per the Sol plan, it narrows the final claim rather than being attributed to this mission. T03 may continue the same second attempt only while preserving its command boundary: it must never target `.obsidian/`. Stable content fingerprints remain mandatory for `Clippings/`, `sources/`, `wiki/`, `maps/`, and `system/`; the final receipt must not claim that `.obsidian/` stayed unchanged.
