import json
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from os import environ
from pathlib import Path

from invoice_scanner.models import REVIEW_FIELDS, ExtractedExpense

DEFAULT_LOG = (
    Path(environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    / "invoice-scanner"
    / "corrections.jsonl"
)


@dataclass(frozen=True)
class FieldStats:
    field: str
    edits: int
    missed: int  # edited although the model was confident


def edited_fields(before: ExtractedExpense, after: ExtractedExpense) -> list[str]:
    old, new = before.model_dump(mode="json"), after.model_dump(mode="json")
    return [f for f in REVIEW_FIELDS if old[f] != new[f]]


def log_review(
    path: Path,
    *,
    pdf: Path,
    backend: str,
    model: str | None,
    extracted: ExtractedExpense,
    final: ExtractedExpense,
    flagged: list[str],
) -> None:
    """Append one review to the JSONL log; unedited reviews count too, as the denominator."""
    record = {
        "ts": datetime.now(UTC).isoformat(timespec="seconds"),
        "pdf": str(pdf),
        "backend": backend,
        "model": model,
        "flagged": flagged,
        "edited": edited_fields(extracted, final),
        "extracted": extracted.model_dump(mode="json"),
        "final": final.model_dump(mode="json"),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as fh:
        fh.write(json.dumps(record) + "\n")


def read_log(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def edit_stats(records: list[dict]) -> list[FieldStats]:
    """Fields ranked by how often a human corrected them."""
    edits = Counter(f for r in records for f in r["edited"])
    missed = Counter(f for r in records for f in r["edited"] if f not in r["flagged"])
    return [FieldStats(f, n, missed[f]) for f, n in edits.most_common()]


def render_stats(records: list[dict]) -> str:
    if not records:
        return "no reviews logged yet"
    total = len(records)
    with_edits = sum(1 for r in records if r["edited"])
    lines = [
        f"{total} reviews, {with_edits} with edits",
        "",
        f"{'field':<16}{'edits':>6}{'rate':>7}{'missed':>8}",
    ]
    lines += [
        f"{s.field:<16}{s.edits:>6}{s.edits / total:>7.0%}{s.missed:>8}"
        for s in edit_stats(records)
    ]
    lines += ["", "missed = edited although the model was confident (not flagged)"]
    return "\n".join(lines)
