from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from .extractor import extract_invoice_from_pdf
from .models import ExtractionConfidence, Invoice
from .rules import decide_invoice, make_duplicate_key
from .store import InvoiceStore


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _initial_stage(route: str) -> str | None:
    if route == "manager_approval": return "manager"
    if route == "manager_then_finance_approval": return "manager"
    if route == "manual_review": return "review"
    return None


class InvoiceService:
    def __init__(self, store: InvoiceStore) -> None:
        self.store = store

    def process_pdf(self, path: str | Path, source_filename: str) -> dict:
        invoice = extract_invoice_from_pdf(path)
        decision = decide_invoice(invoice, self.store.duplicate_keys())
        now = _now()
        record = {"id":str(uuid4()),"source_filename":source_filename,"invoice_number":invoice.invoice_number,"supplier_name":invoice.supplier_name,"purchase_order":invoice.purchase_order,"invoice_total":str(invoice.invoice_total) if invoice.invoice_total is not None else None,"tax":str(invoice.tax) if invoice.tax is not None else None,"currency":invoice.currency,"confidence_invoice_number":invoice.confidence.invoice_number,"confidence_supplier_name":invoice.confidence.supplier_name,"confidence_invoice_total":invoice.confidence.invoice_total,"duplicate_key":decision.duplicate_key,"status":decision.status,"route":decision.route,"approval_stage":_initial_stage(decision.route),"reason":decision.reason,"created_at":now,"updated_at":now}
        self.store.insert(record)
        return self.store.get(record["id"]) or record

    def approve(self, record_id: str, outcome: str) -> dict:
        record = self._require(record_id)
        if record["status"] != "Pending Approval": raise ValueError("Invoice is not waiting for approval.")
        if outcome not in {"approve","reject"}: raise ValueError("Outcome must be 'approve' or 'reject'.")
        changes = {"updated_at": _now()}
        if outcome == "reject": changes.update(status="Rejected", approval_stage=None, reason="Rejected during approval simulation.")
        elif record["route"] == "manager_approval": changes.update(status="Approved", approval_stage=None, reason="Approved by manager.")
        elif record["route"] == "manager_then_finance_approval" and record["approval_stage"] == "manager": changes.update(approval_stage="finance", reason="Manager approved; awaiting finance approval.")
        elif record["route"] == "manager_then_finance_approval" and record["approval_stage"] == "finance": changes.update(status="Approved", approval_stage=None, reason="Approved by manager and finance.")
        else: raise ValueError("Approval stage is inconsistent with the invoice route.")
        self.store.update(record_id, changes)
        return self._require(record_id)

    def correct_and_revalidate(self, record_id: str, *, invoice_number: str | None = None, supplier_name: str | None = None, invoice_total: Decimal | None = None) -> dict:
        record = self._require(record_id)
        if record["status"] != "Needs Review": raise ValueError("Only invoices in Needs Review can be corrected.")
        original = Invoice(invoice_number=record["invoice_number"], supplier_name=record["supplier_name"], invoice_total=Decimal(record["invoice_total"]) if record["invoice_total"] else None, purchase_order=record["purchase_order"], tax=Decimal(record["tax"]) if record["tax"] else None, currency=record["currency"], confidence=ExtractionConfidence(record["confidence_invoice_number"], record["confidence_supplier_name"], record["confidence_invoice_total"]))
        corrected = replace(original, invoice_number=invoice_number if invoice_number is not None else original.invoice_number, supplier_name=supplier_name if supplier_name is not None else original.supplier_name, invoice_total=invoice_total if invoice_total is not None else original.invoice_total, confidence=ExtractionConfidence(1.0 if invoice_number is not None else original.confidence.invoice_number,1.0 if supplier_name is not None else original.confidence.supplier_name,1.0 if invoice_total is not None else original.confidence.invoice_total))
        other_keys = [key for key in self.store.duplicate_keys() if key != record["duplicate_key"]]
        decision = decide_invoice(corrected, other_keys)
        self.store.update(record_id,{"invoice_number":corrected.invoice_number,"supplier_name":corrected.supplier_name,"invoice_total":str(corrected.invoice_total) if corrected.invoice_total is not None else None,"confidence_invoice_number":corrected.confidence.invoice_number,"confidence_supplier_name":corrected.confidence.supplier_name,"confidence_invoice_total":corrected.confidence.invoice_total,"duplicate_key":make_duplicate_key(corrected),"status":decision.status,"route":decision.route,"approval_stage":_initial_stage(decision.route),"reason":decision.reason,"updated_at":_now()})
        return self._require(record_id)

    def _require(self, record_id: str) -> dict:
        record = self.store.get(record_id)
        if not record: raise KeyError(record_id)
        return record
