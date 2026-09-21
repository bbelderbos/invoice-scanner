import json
from collections.abc import Sequence
from pathlib import Path

from invoice_scanner.backends import Backend
from invoice_scanner.models import ExtractedExpense
from invoice_scanner.prompt import build_prompt


def parse_json(text: str) -> dict:
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError(f"no JSON object in backend output: {text!r}")
    return json.loads(text[start : end + 1])


def extract(
    pdf: Path, backend: Backend, categories: Sequence[str] | None = None
) -> ExtractedExpense:
    raw = backend(pdf, build_prompt(categories))
    return ExtractedExpense.model_validate(parse_json(raw))
