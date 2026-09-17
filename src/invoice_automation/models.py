from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class ExtractionConfidence:
    invoice_number: float = 0.0
    supplier_name: float = 0.0
    invoice_total: float = 0.0

    @property
    def minimum(self) -> float:
        return min(self.invoice_number, self.supplier_name, self.invoice_total)


@dataclass(frozen=True)
class Invoice:
    invoice_number: Optional[str]
    supplier_name: Optional[str]
    invoice_total: Optional[Decimal]
    purchase_order: Optional[str] = None
    tax: Optional[Decimal] = None
    currency: str = "GBP"
    confidence: ExtractionConfidence = ExtractionConfidence()


@dataclass(frozen=True)
class Decision:
    status: str
    route: str
    reason: str
    duplicate_key: str
