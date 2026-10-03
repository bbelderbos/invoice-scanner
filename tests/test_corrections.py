from pathlib import Path

from invoice_scanner import ExtractedExpense
from invoice_scanner.corrections import edit_stats, edited_fields, log_review, read_log

BEFORE = ExtractedExpense(supplier="Hetzner", vat_rate="0.19", currency="EUR")


def test_edited_fields_lists_changed_values_only():
    after = ExtractedExpense.model_validate(
        {**BEFORE.model_dump(), "vat_rate": "0.21", "confidence": 0.1}
    )
    assert edited_fields(BEFORE, after) == ["vat_rate"]


def test_log_review_appends_jsonl(tmp_path: Path):
    log = tmp_path / "nested" / "corrections.jsonl"
    after = ExtractedExpense.model_validate({**BEFORE.model_dump(), "supplier": "Hetzner GmbH"})
    for _ in range(2):
        log_review(
            log,
            pdf=Path("a.pdf"),
            backend="claude",
            model=None,
            extracted=BEFORE,
            final=after,
            flagged=["vat_rate"],
        )
    records = read_log(log)
    assert len(records) == 2
    assert records[0]["edited"] == ["supplier"]
    assert records[0]["flagged"] == ["vat_rate"]
    assert records[0]["extracted"]["supplier"] == "Hetzner"
    assert records[0]["final"]["supplier"] == "Hetzner GmbH"


def test_read_log_missing_file_is_empty(tmp_path: Path):
    assert read_log(tmp_path / "nope.jsonl") == []


def test_edit_stats_ranks_fields_and_counts_missed():
    records = [
        {"edited": ["vat_rate", "supplier"], "flagged": ["vat_rate"]},
        {"edited": ["vat_rate"], "flagged": []},
        {"edited": [], "flagged": ["date"]},
    ]
    stats = edit_stats(records)
    assert [(s.field, s.edits, s.missed) for s in stats] == [
        ("vat_rate", 2, 1),
        ("supplier", 1, 1),
    ]
