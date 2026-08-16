from __future__ import annotations

import json
import re
from datetime import date, datetime
from typing import Any


def _matches_type(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "null":
        return value is None
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return True


def validate_schema(instance: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    """Validate the JSON-Schema subset used by the V8.1 note contracts."""

    violations: list[str] = []
    declared_type = schema.get("type")
    if declared_type is not None:
        allowed = declared_type if isinstance(declared_type, list) else [declared_type]
        if not any(_matches_type(instance, str(item)) for item in allowed):
            return [f"{path}: expected type {allowed}, got {type(instance).__name__}"]

    if "const" in schema and instance != schema["const"]:
        violations.append(f"{path}: expected constant {schema['const']!r}")
    if "enum" in schema and instance not in schema["enum"]:
        violations.append(f"{path}: value is not in enum {schema['enum']!r}")

    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                violations.append(f"{path}.{key}: required property is missing")
        properties = schema.get("properties") if isinstance(schema.get("properties"), dict) else {}
        if schema.get("additionalProperties") is False:
            for key in sorted(set(instance) - set(properties)):
                violations.append(f"{path}.{key}: additional property is not allowed")
        for key, subschema in properties.items():
            if key in instance and isinstance(subschema, dict):
                violations.extend(validate_schema(instance[key], subschema, f"{path}.{key}"))

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < int(schema["minItems"]):
            violations.append(f"{path}: expected at least {schema['minItems']} items")
        if "maxItems" in schema and len(instance) > int(schema["maxItems"]):
            violations.append(f"{path}: expected at most {schema['maxItems']} items")
        if schema.get("uniqueItems"):
            fingerprints = [json.dumps(item, ensure_ascii=False, sort_keys=True) for item in instance]
            if len(fingerprints) != len(set(fingerprints)):
                violations.append(f"{path}: items must be unique")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(instance):
                violations.extend(validate_schema(item, item_schema, f"{path}[{index}]"))

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < int(schema["minLength"]):
            violations.append(f"{path}: string is shorter than {schema['minLength']}")
        pattern = schema.get("pattern")
        if pattern and re.search(str(pattern), instance) is None:
            violations.append(f"{path}: value does not match {pattern}")
        format_name = schema.get("format")
        try:
            if format_name == "date":
                date.fromisoformat(instance)
            elif format_name == "date-time":
                datetime.fromisoformat(instance.replace("Z", "+00:00"))
        except ValueError:
            violations.append(f"{path}: invalid {format_name} value")
    return violations
