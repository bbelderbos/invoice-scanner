from datetime import date
from decimal import Decimal

from invoice_scanner import ExtractedExpense
from invoice_scanner.models import REVIEW_FIELDS
from invoice_scanner.review import flagged_fields, render, review

CONFIDENT = {f: 0.95 for f in REVIEW_FIELDS}


def make_expense(**overrides: object) -> ExtractedExpense:
    data = {
        "supplier": "Hetzner",
        "date": "2026-03-01",
        "currency": "EUR",
        "net_amount": "12.50",
        "vat_rate": "0.19",
        "field_confidence": {**CONFIDENT, "vat_rate": 0.4, "supplier_tax_id": 0.6},
        "evidence": {"vat_rate": "VAT 19%: EUR 2.38"},
    }
    return ExtractedExpense.model_validate({**data, **overrides})


def scripted(*answers: str):
    queue = list(answers)
    prompts: list[str] = []

    def ask(prompt: str) -> str:
        prompts.append(prompt)
        return queue.pop(0)

    return ask, prompts


def test_flagged_fields_sorted_least_confident_first():
    assert flagged_fields(make_expense(), threshold=0.8) == ["vat_rate", "supplier_tax_id"]


def test_missing_field_confidence_counts_as_unsure():
    expense = make_expense(field_confidence={})
    assert flagged_fields(expense, threshold=0.8) == list(REVIEW_FIELDS)


def test_render_marks_flagged_fields_and_shows_evidence():
    lines = {line[2:].split()[0]: line for line in render(make_expense(), 0.8).splitlines()}
    assert lines["vat_rate"].startswith("!")
    assert "VAT 19%: EUR 2.38" in lines["vat_rate"]
    assert lines["supplier"].startswith(" ")


def test_review_only_prompts_flagged_fields_then_accepts():
    ask, prompts = scripted("", "", "")
    result = review(make_expense(), ask, show=lambda _: None)
    assert result == make_expense()
    assert [p.split()[0] for p in prompts[:2]] == ["vat_rate", "supplier_tax_id"]
    assert len(prompts) == 3


def test_review_applies_corrections():
    ask, _ = scripted("0.21", "DE812871812", "")
    result = review(make_expense(), ask, show=lambda _: None)
    assert result is not None
    assert result.vat_rate == Decimal("0.21")
    assert result.supplier_tax_id == "DE812871812"


def test_review_can_edit_unflagged_field():
    ask, _ = scripted("", "", "date", "2026-03-02", "")
    result = review(make_expense(), ask, show=lambda _: None)
    assert result is not None
    assert result.date == date(2026, 3, 2)


def test_review_reprompts_on_invalid_value():
    shown: list[str] = []
    ask, _ = scripted("abc", "0.21", "", "")
    result = review(make_expense(), ask, show=shown.append)
    assert result is not None
    assert result.vat_rate == Decimal("0.21")
    assert any(s.startswith("invalid vat_rate") for s in shown)


def test_review_reject_returns_none():
    ask, _ = scripted("", "", "q")
    assert review(make_expense(), ask, show=lambda _: None) is None
