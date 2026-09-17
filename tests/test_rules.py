from decimal import Decimal

from invoice_automation.models import ExtractionConfidence, Invoice
from invoice_automation.rules import decide_invoice, make_duplicate_key, normalize_text


def conf(value: float = 0.95) -> ExtractionConfidence:
    return ExtractionConfidence(value, value, value)


def invoice(total: str = "100.00", number: str | None = "INV-001", supplier: str | None = "Contoso Ltd", confidence=None):
    return Invoice(number, supplier, Decimal(total) if total is not None else None, confidence=confidence or conf())


def test_normalization_collapses_case_and_whitespace():
    assert normalize_text("  CONTOSO   Ltd ") == "contoso ltd"


def test_duplicate_key_is_stable():
    assert make_duplicate_key(invoice(number=" Inv-001 ", supplier="CONTOSO  LTD")) == "contoso ltd|inv-001"


def test_duplicate_invoice_is_stopped():
    inv = invoice()
    result = decide_invoice(inv, ["contoso ltd|inv-001"])
    assert result.status == "Duplicate"
    assert result.route == "stop"


def test_missing_required_field_routes_to_review():
    result = decide_invoice(invoice(number=None), [])
    assert result.status == "Needs Review"
    assert result.route == "manual_review"


def test_low_confidence_routes_to_review():
    c = ExtractionConfidence(invoice_number=0.93, supplier_name=0.77, invoice_total=0.95)
    result = decide_invoice(invoice(confidence=c), [])
    assert result.route == "manual_review"


def test_small_invoice_auto_approves():
    result = decide_invoice(invoice("500.00"), [])
    assert result.status == "Approved"
    assert result.route == "auto_approve"


def test_mid_value_invoice_routes_to_manager():
    result = decide_invoice(invoice("500.01"), [])
    assert result.status == "Pending Approval"
    assert result.route == "manager_approval"


def test_high_value_invoice_routes_to_manager_then_finance():
    result = decide_invoice(invoice("5000.01"), [])
    assert result.route == "manager_then_finance_approval"


def test_missing_field_is_reviewed_before_duplicate_check():
    inv = invoice(number=None, supplier="Contoso Ltd")
    result = decide_invoice(inv, ["contoso ltd|"])
    assert result.status == "Needs Review"
    assert result.route == "manual_review"


def test_low_confidence_is_reviewed_before_duplicate_check():
    c = ExtractionConfidence(invoice_number=0.50, supplier_name=0.95, invoice_total=0.95)
    inv = invoice(number="INV-001", supplier="Contoso Ltd", confidence=c)
    result = decide_invoice(inv, ["contoso ltd|inv-001"])
    assert result.status == "Needs Review"
    assert result.route == "manual_review"
