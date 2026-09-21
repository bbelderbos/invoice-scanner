from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from invoice_scanner import ExtractedExpense, extract, parse_json

SAMPLE = (
    '{"supplier":"Hetzner","supplier_tax_id":"DE812","date":"2026-03-01",'
    '"description":"VPS","category":"hosting","currency":"eur","net_amount":"12.50",'
    '"vat_rate":"0.19","payment_method":"card","confidence":0.9,"uncertain_fields":[]}'
)


def test_parse_json_ignores_prose_and_fences():
    assert parse_json("here you go:\n```json\n" + SAMPLE + "\n```")["supplier"] == "Hetzner"


def test_parse_json_raises_without_object():
    with pytest.raises(ValueError):
        parse_json("no json here")


def test_extract_builds_model():
    exp = extract(Path("x.pdf"), lambda pdf, instruction: SAMPLE)
    assert exp.supplier == "Hetzner"
    assert exp.date == date(2026, 3, 1)
    assert exp.net_amount == Decimal("12.50")
    assert exp.currency == "EUR"
    assert exp.confidence == 0.9


def test_extract_passes_categories_to_prompt():
    seen = {}

    def backend(pdf, instruction):
        seen["instruction"] = instruction
        return SAMPLE

    extract(Path("x.pdf"), backend, categories=["hosting", "software"])
    assert "one of: hosting, software" in seen["instruction"]


def test_empty_date_becomes_none():
    exp = ExtractedExpense.model_validate({"supplier": "X", "date": ""})
    assert exp.date is None
