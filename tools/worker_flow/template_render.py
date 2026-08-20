"""Typed two-phase renderer for contract-declared Markdown templates."""

from __future__ import annotations

import json
import re
from typing import Any

from .frontmatter import quote_yaml


TOKEN_RE = re.compile(r"\{\{([A-Za-z0-9_.]+)\}\}")


def _quoted_fragment(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, dict)):
        raise ValueError("structured values cannot be embedded in a quoted scalar")
    return json.dumps(str(value), ensure_ascii=False)[1:-1]


def render_host_template(
    template: str,
    values: dict[str, Any],
    token_contract: dict[str, Any],
) -> str:
    """Render host-owned tokens and leave only declared ``semantic.*`` tokens."""
    host_tokens = set(token_contract.get("host_tokens", []))
    semantic_tokens = set(token_contract.get("semantic_tokens", []))
    missing_values = sorted(host_tokens - set(values))
    unknown_values = sorted(set(values) - host_tokens)
    if missing_values or unknown_values:
        raise ValueError(
            f"host render values mismatch: missing={missing_values}, unknown={unknown_values}"
        )

    normalized = template.replace("\r\n", "\n").replace("\r", "\n")
    if not normalized.startswith("---\n") or "\n---\n" not in normalized[4:]:
        raise ValueError("template has no complete frontmatter block")
    boundary = normalized.find("\n---\n", 4)
    frontmatter = normalized[: boundary + 5]
    body = normalized[boundary + 5 :]
    frontmatter_tokens = set(TOKEN_RE.findall(frontmatter))
    semantic_frontmatter = sorted(frontmatter_tokens & semantic_tokens)
    if semantic_frontmatter:
        raise ValueError(f"semantic tokens are forbidden in frontmatter: {semantic_frontmatter}")

    rendered_lines: list[str] = []
    for line in frontmatter.splitlines():
        rendered_line = line
        for token in TOKEN_RE.findall(line):
            value = values[token]
            if isinstance(value, str) and "\n" in value:
                raise ValueError(f"multiline frontmatter value is forbidden: {token}")
            marker = "{{" + token + "}}"
            if re.search(rf"^\s*[^:#]+:\s*{re.escape(marker)}\s*$", line):
                replacement = quote_yaml(value)
            else:
                replacement = _quoted_fragment(value)
            rendered_line = rendered_line.replace(marker, replacement)
        rendered_lines.append(rendered_line)
    rendered_frontmatter = "\n".join(rendered_lines) + "\n"

    rendered_body = body
    for token in sorted(host_tokens, key=len, reverse=True):
        value = values[token]
        if isinstance(value, (list, dict)):
            replacement = quote_yaml(value)
        elif value is None:
            replacement = "null"
        else:
            replacement = str(value)
        rendered_body = rendered_body.replace("{{" + token + "}}", replacement)

    rendered = rendered_frontmatter + rendered_body
    unresolved = set(TOKEN_RE.findall(rendered))
    if unresolved != semantic_tokens:
        raise ValueError(
            f"post-host-render tokens mismatch: expected={sorted(semantic_tokens)}, observed={sorted(unresolved)}"
        )
    return rendered
