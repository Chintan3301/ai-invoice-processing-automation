from __future__ import annotations

import argparse
import json
from decimal import Decimal
from pathlib import Path

from .models import ExtractionConfidence, Invoice
from .rules import decide_invoice


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the invoice routing reference logic against extracted JSON.")
    parser.add_argument("json_file", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.json_file.read_text(encoding="utf-8"))
    invoice = Invoice(invoice_number=payload.get("invoice_number"), supplier_name=payload.get("supplier_name"), invoice_total=Decimal(str(payload["invoice_total"])) if payload.get("invoice_total") is not None else None, purchase_order=payload.get("purchase_order"), tax=Decimal(str(payload["tax"])) if payload.get("tax") is not None else None, currency=payload.get("currency", "GBP"), confidence=ExtractionConfidence(**payload.get("confidence", {})))
    decision = decide_invoice(invoice, payload.get("existing_duplicate_keys", []))
    print(json.dumps(decision.__dict__, indent=2))


if __name__ == "__main__":
    main()
