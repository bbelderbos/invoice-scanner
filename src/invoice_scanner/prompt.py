from collections.abc import Sequence

_FIELDS = (
    "supplier (string), "
    "supplier_tax_id (VAT/tax id, or empty string), "
    "date (YYYY-MM-DD, the invoice date), "
    "description (short, what was purchased), "
    "{category_clause}"
    "currency (ISO 4217 code of the amounts, e.g. EUR, USD, GBP), "
    "net_amount (number, in the invoice's own currency, no conversion), "
    "vat_rate (decimal fraction e.g. 0.21 or 0.00), "
    "payment_method (card or transfer), "
    "confidence (number 0.0-1.0, your overall confidence in this extraction), "
    "field_confidence (object mapping every field name above to your confidence 0.0-1.0 "
    "in that value), "
    "evidence (object mapping every field name above to the exact invoice text you read "
    "it from, or empty string if inferred)"
)


def build_prompt(categories: Sequence[str] | None = None) -> str:
    if categories:
        cats = ", ".join(categories)
        category_clause = f"category (one of: {cats}), "
    else:
        category_clause = "category (short expense category), "
    fields = _FIELDS.format(category_clause=category_clause)
    return (
        "You are reading a supplier invoice or receipt. Extract these fields and output "
        "ONLY a single minified JSON object, no prose, no code fences. Keys: "
        f"{fields}. Amounts as plain numbers in the original currency; do not convert."
    )
