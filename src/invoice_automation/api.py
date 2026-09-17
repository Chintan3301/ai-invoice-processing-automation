from __future__ import annotations

import os
import tempfile
from decimal import Decimal, InvalidOperation
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from .service import InvoiceService
from .store import InvoiceStore

DB_PATH = os.getenv("INVOICE_DEMO_DB", "invoice-demo.db")
store = InvoiceStore(DB_PATH)
service = InvoiceService(store)
app = FastAPI(title="AI Invoice Processing Reference Demo", version="1.0.0")


class ApprovalRequest(BaseModel):
    outcome: str


class ReviewRequest(BaseModel):
    invoice_number: str | None = None
    supplier_name: str | None = None
    invoice_total: str | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/invoices")
def list_invoices(status: str | None = None) -> list[dict]:
    return store.list(status)


@app.get("/api/invoices/{record_id}")
def get_invoice(record_id: str) -> dict:
    record = store.get(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return record


@app.post("/api/invoices/upload")
async def upload_invoice(file: UploadFile = File(...)) -> dict:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF invoices are accepted")
    content = await file.read()
    if not content.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid PDF")

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(content)
        temp_path = Path(tmp.name)
    try:
        return service.process_pdf(temp_path, file.filename)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not process invoice: {exc}") from exc
    finally:
        temp_path.unlink(missing_ok=True)


@app.post("/api/invoices/{record_id}/approval")
def approval(record_id: str, request: ApprovalRequest) -> dict:
    try:
        return service.approve(record_id, request.outcome.lower())
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Invoice not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/api/invoices/{record_id}/review")
def review(record_id: str, request: ReviewRequest) -> dict:
    parsed_total: Decimal | None = None
    if request.invoice_total is not None:
        try:
            parsed_total = Decimal(request.invoice_total)
        except InvalidOperation as exc:
            raise HTTPException(status_code=400, detail="invoice_total must be a decimal amount") from exc
    try:
        return service.correct_and_revalidate(
            record_id,
            invoice_number=request.invoice_number,
            supplier_name=request.supplier_name,
            invoice_total=parsed_total,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Invoice not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/", response_class=HTMLResponse)
def dashboard() -> str:
    return """<!doctype html>
<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Invoice Automation Demo</title>
<style>
body{font-family:system-ui,-apple-system,Segoe UI,sans-serif;margin:0;background:#f5f7fb;color:#172033}main{max-width:1100px;margin:40px auto;padding:0 20px}h1{margin-bottom:4px}.sub{color:#5c667a;margin-top:0}.card{background:white;border:1px solid #e4e8f0;border-radius:14px;padding:20px;margin:20px 0;box-shadow:0 4px 18px rgba(0,0,0,.04)}button{background:#172033;color:white;border:0;border-radius:8px;padding:10px 14px;cursor:pointer}input{padding:10px}table{width:100%;border-collapse:collapse;font-size:14px}th,td{text-align:left;border-bottom:1px solid #edf0f5;padding:10px}.pill{padding:4px 8px;border-radius:999px;background:#eef2f8;display:inline-block}code{background:#f1f3f7;padding:2px 5px;border-radius:5px}</style></head>
<body><main><h1>AI Invoice Processing & Approval Automation</h1><p class='sub'>Local reference implementation for testing the Power Platform routing logic.</p>
<div class='card'><h2>Upload synthetic PDF invoice</h2><input id='file' type='file' accept='.pdf'> <button onclick='upload()'>Process invoice</button><pre id='result'></pre></div>
<div class='card'><h2>Invoice records</h2><button onclick='load()'>Refresh</button><div style='overflow:auto'><table><thead><tr><th>Supplier</th><th>Invoice</th><th>Total</th><th>Status</th><th>Stage</th><th>Route</th></tr></thead><tbody id='rows'></tbody></table></div></div>
<p class='sub'>Production extraction uses Microsoft AI Builder; production approvals use Power Automate Approvals. This demo is deliberately deterministic and uses synthetic data only.</p>
<script>
async function upload(){const f=document.getElementById('file').files[0];if(!f)return;const fd=new FormData();fd.append('file',f);const r=await fetch('/api/invoices/upload',{method:'POST',body:fd});document.getElementById('result').textContent=JSON.stringify(await r.json(),null,2);load()}
async function load(){const data=await (await fetch('/api/invoices')).json();document.getElementById('rows').innerHTML=data.map(x=>`<tr><td>${x.supplier_name??''}</td><td>${x.invoice_number??''}</td><td>${x.currency} ${x.invoice_total??''}</td><td><span class='pill'>${x.status}</span></td><td>${x.approval_stage??''}</td><td><code>${x.route}</code></td></tr>`).join('')}
load()</script></main></body></html>"""
