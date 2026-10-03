from collections.abc import Callable

from pydantic import ValidationError

from invoice_scanner.models import REVIEW_FIELDS, ExtractedExpense

Ask = Callable[[str], str]
Show = Callable[[str], None]

DEFAULT_THRESHOLD = 0.8


def _confidence(expense: ExtractedExpense, field: str) -> float:
    # A field the model didn't score is treated as unsure, so it gets reviewed.
    return expense.field_confidence.get(field, 0.0)


def flagged_fields(expense: ExtractedExpense, threshold: float) -> list[str]:
    """Fields below the confidence threshold, least confident first."""
    flagged = [f for f in REVIEW_FIELDS if _confidence(expense, f) < threshold]
    return sorted(flagged, key=lambda f: _confidence(expense, f))


def render(expense: ExtractedExpense, threshold: float) -> str:
    """One line per field: flag, name, confidence, value and the invoice text it came from."""
    values = expense.model_dump(mode="json")
    width = max(map(len, REVIEW_FIELDS))
    lines = []
    for field in REVIEW_FIELDS:
        confidence = _confidence(expense, field)
        mark = "!" if confidence < threshold else " "
        value = "" if values[field] is None else values[field]
        line = f"{mark} {field:<{width}}  {confidence:4.2f}  {value}"
        if evidence := expense.evidence.get(field):
            line += f'   <- "{evidence}"'
        lines.append(line)
    return "\n".join(lines)


def _edit(expense: ExtractedExpense, field: str, ask: Ask, show: Show) -> ExtractedExpense:
    current = expense.model_dump(mode="json")[field]
    while True:
        answer = ask(f"{field} [{'' if current is None else current}]: ").strip()
        if not answer:
            return expense
        try:
            return ExtractedExpense.model_validate({**expense.model_dump(), field: answer})
        except ValidationError as e:
            show(f"invalid {field}: {e.errors()[0]['msg']}")


def review(
    expense: ExtractedExpense, ask: Ask, show: Show, threshold: float = DEFAULT_THRESHOLD
) -> ExtractedExpense | None:
    """Walk the flagged fields, allow edits to any field; None means the human rejected it."""
    show(render(expense, threshold))
    original = expense
    for field in flagged_fields(expense, threshold):
        expense = _edit(expense, field, ask, show)
    if expense != original:
        show(render(expense, threshold))
    while True:
        answer = ask("Field to edit, Enter to accept, q to reject: ").strip()
        if not answer:
            return expense
        if answer == "q":
            return None
        if answer in REVIEW_FIELDS:
            expense = _edit(expense, answer, ask, show)
        else:
            show(f"unknown field {answer!r}; one of: {', '.join(REVIEW_FIELDS)}")
