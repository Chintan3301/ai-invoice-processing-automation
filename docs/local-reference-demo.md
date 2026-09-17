# Local reference demo

The production design is Microsoft Power Platform. This local service exists only to make the repository independently testable in CI and during portfolio review.

## What it exercises

- PDF upload and basic validation;
- deterministic extraction from the six synthetic PDF fixtures;
- duplicate-key generation;
- required-field and confidence validation;
- amount-based routing;
- SQLite persistence;
- manager approval;
- manager then finance approval;
- manual correction and revalidation;
- status/list REST endpoints.

## What it deliberately does not claim

- It does not replace AI Builder OCR/document intelligence. The local parser is fixture-specific and deterministic.
- It does not replace Dataverse. SQLite is used only for a portable demo.
- It does not send Teams/email notifications. Those remain Power Automate connector actions.
- It does not represent a live Copilot Studio deployment.

## Start

```bash
python -m pip install -r requirements.txt
export PYTHONPATH=src
python scripts/run_reference_demo.py
```

PowerShell:

```powershell
python -m pip install -r requirements.txt
$env:PYTHONPATH="src"
python scripts/run_reference_demo.py
```

Open `http://127.0.0.1:8000` for the small browser UI or `/docs` for OpenAPI.

## Useful API calls

- `GET /health`
- `POST /api/invoices/upload` (multipart field `file`)
- `GET /api/invoices`
- `GET /api/invoices/{id}`
- `POST /api/invoices/{id}/approval` with `{"outcome":"approve"}` or `reject`
- `POST /api/invoices/{id}/review` with corrected fields

Use only the synthetic test invoices in the repository when recording portfolio screenshots.
