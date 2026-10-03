import datetime as dt
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field, field_validator


class ExtractedExpense(BaseModel):
    supplier: str = ""
    supplier_tax_id: str = ""
    date: dt.date | None = None
    description: str = ""
    category: str = ""
    currency: str = "EUR"
    net_amount: Decimal = Decimal(0)
    vat_rate: Decimal = Decimal(0)
    payment_method: str = ""
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    field_confidence: dict[str, Annotated[float, Field(ge=0.0, le=1.0)]] = Field(
        default_factory=dict
    )
    evidence: dict[str, str] = Field(default_factory=dict)

    @field_validator("date", mode="before")
    @classmethod
    def _empty_date_to_none(cls, v: object) -> object:
        return None if v in ("", None) else v

    @field_validator("currency", mode="before")
    @classmethod
    def _upper_currency(cls, v: object) -> object:
        return str(v).upper() if v else "EUR"


_META_FIELDS = {"confidence", "field_confidence", "evidence"}
REVIEW_FIELDS = tuple(f for f in ExtractedExpense.model_fields if f not in _META_FIELDS)
