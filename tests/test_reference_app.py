from pathlib import Path

from fastapi.testclient import TestClient

import invoice_automation.api as api_module
from invoice_automation.api import app
from invoice_automation.service import InvoiceService
from invoice_automation.store import InvoiceStore

ROOT = Path(__file__).resolve().parents[1]
INVOICES = ROOT / "test-data" / "invoices"


def fresh_client(tmp_path, monkeypatch):
    store = InvoiceStore(tmp_path / "test.db")
    monkeypatch.setattr(api_module, "store", store)
    monkeypatch.setattr(api_module, "service", InvoiceService(store))
    return TestClient(app)


def upload(client, filename):
    with (INVOICES / filename).open("rb") as handle:
        return client.post("/api/invoices/upload", files={"file": (filename, handle, "application/pdf")})


def test_health(tmp_path, monkeypatch):
    client = fresh_client(tmp_path, monkeypatch)
    assert client.get("/health").json() == {"status": "ok"}


def test_upload_auto_approve(tmp_path, monkeypatch):
    client = fresh_client(tmp_path, monkeypatch)
    response = upload(client, "01-auto-approve.pdf")
    assert response.status_code == 200
    payload = response.json()
    assert payload["invoice_number"] == "INV-1001"
    assert payload["status"] == "Approved"
    assert payload["route"] == "auto_approve"


def test_manager_approval(tmp_path, monkeypatch):
    client = fresh_client(tmp_path, monkeypatch)
    record = upload(client, "02-manager-approval.pdf").json()
    assert record["approval_stage"] == "manager"
    approved = client.post(f"/api/invoices/{record['id']}/approval", json={"outcome": "approve"}).json()
    assert approved["status"] == "Approved"


def test_two_stage_approval(tmp_path, monkeypatch):
    client = fresh_client(tmp_path, monkeypatch)
    record = upload(client, "03-high-value.pdf").json()
    manager = client.post(f"/api/invoices/{record['id']}/approval", json={"outcome": "approve"}).json()
    assert manager["status"] == "Pending Approval"
    assert manager["approval_stage"] == "finance"
    finance = client.post(f"/api/invoices/{record['id']}/approval", json={"outcome": "approve"}).json()
    assert finance["status"] == "Approved"


def test_duplicate_is_detected(tmp_path, monkeypatch):
    client = fresh_client(tmp_path, monkeypatch)
    first = upload(client, "04-duplicate-original.pdf").json()
    second = upload(client, "05-duplicate-copy.pdf").json()
    assert first["status"] == "Approved"
    assert second["status"] == "Duplicate"


def test_review_correction_revalidates(tmp_path, monkeypatch):
    client = fresh_client(tmp_path, monkeypatch)
    record = upload(client, "06-missing-invoice-number.pdf").json()
    assert record["status"] == "Needs Review"
    corrected = client.post(
        f"/api/invoices/{record['id']}/review",
        json={"invoice_number": "INV-1005"},
    ).json()
    assert corrected["status"] == "Pending Approval"
    assert corrected["route"] == "manager_approval"
