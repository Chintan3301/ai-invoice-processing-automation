from __future__ import annotations

from decimal import Decimal
from typing import Iterable

from .models import Decision, Invoice


def normalize_text(value: str | None) -> str:
    """Mirror the Power Automate normalization used to make duplicate checks stable."""
    if value is None:
        return ""
    return " ".join(value.strip().lower().split())


def make_duplicate_key(invoice: Invoice) -> str:
    return f"{normalize_text(invoice.supplier_name)}|{normalize_text(invoice.invoice_number)}"


def find_missing_required_fields(invoice: Invoice) -> list[str]:
    missing: list[str] = []
    if not normalize_text(invoice.invoice_number):
        missing.append("invoice_number")
    if not normalize_text(invoice.supplier_name):
        missing.append("supplier_name")
    if invoice.invoice_total is None:
        missing.append("invoice_total")
    return missing


def decide_invoice(invoice: Invoice, existing_duplicate_keys: Iterable[str], *, minimum_confidence: float = 0.80, auto_approval_limit: Decimal = Decimal("500.00"), manager_approval_limit: Decimal = Decimal("5000.00")) -> Decision:
    key = make_duplicate_key(invoice)
    normalized_existing = {normalize_text(k) for k in existing_duplicate_keys if normalize_text(k)}
    missing = find_missing_required_fields(invoice)
    if missing:
        return Decision(status="Needs Review", route="manual_review", reason=f"Missing required extracted fields: {', '.join(missing)}.", duplicate_key=key)
    if invoice.confidence.minimum < minimum_confidence:
        return Decision(status="Needs Review", route="manual_review", reason=f"At least one required field confidence ({invoice.confidence.minimum:.2f}) is below the configured threshold ({minimum_confidence:.2f}).", duplicate_key=key)
    if normalize_text(key) in normalized_existing:
        return Decision(status="Duplicate", route="stop", reason="A record with the same normalized supplier and invoice number already exists.", duplicate_key=key)
    total = invoice.invoice_total
    assert total is not None
    if total <= auto_approval_limit:
        return Decision(status="Approved", route="auto_approve", reason=f"Invoice total is at or below {auto_approval_limit}.", duplicate_key=key)
    if total <= manager_approval_limit:
        return Decision(status="Pending Approval", route="manager_approval", reason=f"Invoice total is above {auto_approval_limit} and at or below {manager_approval_limit}.", duplicate_key=key)
    return Decision(status="Pending Approval", route="manager_then_finance_approval", reason=f"Invoice total is above {manager_approval_limit} and requires two-stage approval.", duplicate_key=key)
