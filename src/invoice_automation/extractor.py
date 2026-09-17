from __future__ import annotations

import re
from decimal import Decimal
from pathlib import Path

from pypdf import PdfReader

from .models import ExtractionConfidence, Invoice


_AMOUNT = r"(?:GBP\s*)?([0-9][0-9,]*\.\d{2})"


def _amount_after(label: str, text: str) -> Decimal | None:
    match = re.search(rf"{re.escape(label)}\s*\n{_AMOUNT}", text, re.IGNORECASE)
    if not match:
        return None
    return Decimal(match.group(1).replace(",", ""))


def extract_invoice_from_pdf(path: str | Path) -> Invoice:
    """Parse the synthetic portfolio invoices used by the local reference app.

    Production extraction is intentionally delegated to AI Builder. This parser exists
    only so CI and reviewers can exercise the routing logic without a Power Platform
    tenant.
    """
    reader = PdfReader(str(path))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    supplier_name: str | None = None
    try:
        invoice_heading = next(i for i, line in enumerate(lines) if line.upper() == "INVOICE")
        supplier_name = lines[invoice_heading + 1] if invoice_heading + 1 < len(lines) else None
    except StopIteration:
        supplier_name = None

    invoice_match = re.search(r"\bINV-[A-Z0-9-]+\b", text, re.IGNORECASE)
    po_match = re.search(r"\bPO-[A-Z0-9-]+\b", text, re.IGNORECASE)
    invoice_total = _amount_after("Invoice Total", text)
    tax = _amount_after("Total Tax", text)

    invoice_number = invoice_match.group(0).upper() if invoice_match else None
    purchase_order = po_match.group(0).upper() if po_match else None

    return Invoice(
        invoice_number=invoice_number,
        supplier_name=supplier_name,
        invoice_total=invoice_total,
        purchase_order=purchase_order,
        tax=tax,
        currency="GBP",
        confidence=ExtractionConfidence(
            invoice_number=0.99 if invoice_number else 0.0,
            supplier_name=0.99 if supplier_name else 0.0,
            invoice_total=0.99 if invoice_total is not None else 0.0,
        ),
    )
