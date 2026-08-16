from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any


FRONTMATTER_BOUNDARY = "---"


@dataclass(frozen=True)
class MarkdownDocument:
    frontmatter: dict[str, Any]
    body: str
    raw_frontmatter: str


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "":
        return ""
    lowered = value.lower()
    if lowered in {"null", "~"}:
        return None
    if lowered in {"true", "false"}:
        return lowered == "true"
    if value.startswith('"') and value.endswith('"'):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(item) for item in _split_inline_list(inner)]
    if re.fullmatch(r"-?\d+", value):
        try:
            return int(value)
        except ValueError:
            pass
    return value


def _split_inline_list(value: str) -> list[str]:
    items: list[str] = []
    current: list[str] = []
    quote: str | None = None
    escaped = False
    for char in value:
        if escaped:
            current.append(char)
            escaped = False
            continue
        if char == "\\" and quote == '"':
            current.append(char)
            escaped = True
            continue
        if char in {'"', "'"}:
            if quote == char:
                quote = None
            elif quote is None:
                quote = char
            current.append(char)
            continue
        if char == "," and quote is None:
            items.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    items.append("".join(current).strip())
    return items


def parse_frontmatter_block(block: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    lines = block.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        index += 1
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        if line.startswith((" ", "\t")):
            continue
        key, raw_value = line.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        if raw_value:
            result[key] = _parse_scalar(raw_value)
            continue
        items: list[Any] = []
        cursor = index
        while cursor < len(lines):
            candidate = lines[cursor]
            match = re.match(r"^\s+-\s+(.+?)\s*$", candidate)
            if not match:
                break
            items.append(_parse_scalar(match.group(1)))
            cursor += 1
        if items:
            result[key] = items
            index = cursor
        else:
            result[key] = ""
    return result


def parse_markdown(text: str) -> MarkdownDocument:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if not normalized.startswith("---\n"):
        return MarkdownDocument({}, normalized, "")
    end = normalized.find("\n---\n", 4)
    if end == -1:
        return MarkdownDocument({}, normalized, "")
    block = normalized[4:end]
    body = normalized[end + 5 :]
    return MarkdownDocument(parse_frontmatter_block(block), body, block)


def quote_yaml(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        return "[" + ", ".join(quote_yaml(item) for item in value) + "]"
    return json.dumps(str(value), ensure_ascii=False)


def render_frontmatter(fields: dict[str, Any]) -> str:
    lines = ["---"]
    for key, value in fields.items():
        lines.append(f"{key}: {quote_yaml(value)}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def first_heading(body: str) -> str | None:
    match = re.search(r"(?m)^#\s+(.+?)\s*$", body)
    return match.group(1).strip() if match else None

