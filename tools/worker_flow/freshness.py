from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Iterable

from .frontmatter import parse_markdown


@dataclass(frozen=True)
class FreshnessDecision:
    status: str
    next_review: str | None
    reason: str


def _date(value: Any) -> date | None:
    if value is None:
        return None
    text = str(value).strip()
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def evaluate_freshness(
    frontmatter: dict[str, Any], policy: dict[str, Any], today: date | None = None
) -> FreshnessDecision:
    today = today or date.today()
    tier = str(frontmatter.get("freshness_tier") or policy["default_tier"])
    tiers = policy["tiers"]
    if tier not in tiers:
        return FreshnessDecision("unknown", None, f"unknown freshness tier: {tier}")
    if tier == "snapshot":
        valid_as_of = _date(frontmatter.get("valid_as_of"))
        if valid_as_of is None:
            return FreshnessDecision("unknown", None, "snapshot is missing valid_as_of")
        if valid_as_of > today:
            return FreshnessDecision("unknown", None, "snapshot valid_as_of cannot be in the future")
        return FreshnessDecision("snapshot", None, "immutable as-of evidence")

    last_verified = _date(frontmatter.get("last_verified"))
    if last_verified is None:
        return FreshnessDecision("unknown", None, "missing or invalid last_verified")
    valid_as_of = _date(frontmatter.get("valid_as_of"))
    if valid_as_of is None:
        return FreshnessDecision("unknown", None, "missing or invalid valid_as_of")
    if valid_as_of > today or last_verified > today:
        return FreshnessDecision("unknown", None, "freshness dates cannot be in the future")
    if last_verified < valid_as_of:
        return FreshnessDecision("unknown", None, "last_verified precedes valid_as_of")
    configured_next = _date(frontmatter.get("next_review"))
    review_days = tiers[tier]["review_days"]
    calculated = min(valid_as_of, last_verified) + timedelta(days=int(review_days))
    if configured_next is not None and configured_next != calculated:
        return FreshnessDecision(
            "unknown",
            calculated.isoformat(),
            f"next_review must equal policy-derived date {calculated.isoformat()}",
        )
    next_review = calculated
    if next_review < today:
        status = "stale"
    elif next_review == today:
        status = "due"
    else:
        status = "current"
    reason = f"{tier} knowledge reviewed {last_verified.isoformat()} with next review {next_review.isoformat()}"
    return FreshnessDecision(status, next_review.isoformat(), reason)


def scan_freshness(
    paths: Iterable[Path], policy: dict[str, Any], today: date | None = None, root: Path | None = None
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for path in paths:
        try:
            document = parse_markdown(path.read_text(encoding="utf-8", errors="replace"))
        except OSError as exc:
            label = path.relative_to(root).as_posix() if root is not None else str(path)
            findings.append({"path": label, "status": "unknown", "reason": str(exc)})
            continue
        decision = evaluate_freshness(document.frontmatter, policy, today=today)
        if decision.status in {"due", "stale", "unknown"}:
            label = path.relative_to(root).as_posix() if root is not None else str(path)
            findings.append(
                {
                    "path": label,
                    "status": decision.status,
                    "next_review": decision.next_review,
                    "reason": decision.reason,
                }
            )
    return findings
