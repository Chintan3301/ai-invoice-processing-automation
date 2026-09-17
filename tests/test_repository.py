import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_business_rules_config_is_valid():
    data = json.loads((ROOT / "config/business-rules.json").read_text())
    assert 0 <= data["minimum_required_confidence"] <= 1
    assert data["auto_approval_limit"] < data["manager_approval_limit"]


def test_dataverse_schema_has_duplicate_key():
    data = json.loads((ROOT / "dataverse/invoice-table.schema.json").read_text())
    keys = data["alternateKeys"]
    assert any("cyg_duplicatekey" in key["columns"] for key in keys)


def test_flow_specs_are_valid_json():
    for path in (ROOT / "power-automate").glob("*.flow-spec.json"):
        json.loads(path.read_text())


def test_dataverse_allows_incomplete_extraction_for_review():
    data = json.loads((ROOT / "dataverse/invoice-table.schema.json").read_text())
    by_name = {column["logicalName"]: column for column in data["columns"]}
    assert data["table"]["primaryNameColumn"] == "cyg_recordname"
    assert by_name["cyg_recordname"]["required"] is True
    assert by_name["cyg_invoicenumber"]["required"] is False
    assert by_name["cyg_suppliername"]["required"] is False
    assert by_name["cyg_invoicetotal"]["required"] is False


def test_review_handoff_uses_ready_for_validation_not_pending_approval():
    formulas = (ROOT / "power-apps/formulas.fx.txt").read_text()
    assert "'Invoice Status'.'Ready for Validation'" in formulas
    mark_ready_section = formulas.split("// MARK READY button OnSelect", 1)[1].split("// REJECT button OnSelect", 1)[0]
    assert "'Invoice Status'.'Pending Approval'" not in mark_ready_section


def test_copilot_status_flow_binds_invoice_number_input():
    data = json.loads((ROOT / "power-automate/INV-02-Get-Invoice-Status.flow-spec.json").read_text())
    assert "invoiceNumber" in data["actions"][0]["expression"]
