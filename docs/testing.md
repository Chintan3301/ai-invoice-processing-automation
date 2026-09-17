# Test plan

## Automated repository tests

```bash
python -m pip install -r requirements.txt
PYTHONPATH=src pytest -q
```

The local tests verify deterministic business rules plus the portable reference API: normalization, duplicate detection, required-field validation, confidence threshold, routing boundaries, synthetic PDF upload, manual correction, manager approval and manager-then-finance approval.

## Power Platform end-to-end tests

For each PDF fixture:

1. Upload the file to SharePoint `/Invoices/Incoming`.
2. Confirm the flow run succeeds.
3. Check AI Builder output against `expected-extraction.json`.
4. Verify a Dataverse Invoice row is created with the correct source metadata.
5. Verify expected status/route.
6. For approval cases, approve/reject and confirm status/comments persist.
7. Confirm Teams and email notifications contain no invented values.
8. Query the invoice through Copilot Studio and confirm it returns the Dataverse status.

## Acceptance criteria

- No valid PDF is processed twice as a normal invoice.
- Missing required fields never auto-approve.
- Any required field confidence below 0.80 goes to manual review.
- £500.00 or less auto-approves; £500.01-£5,000.00 goes to manager; above £5,000.00 requires manager then finance.
- A rejected approval updates Dataverse and notification text.
- Agent status response comes from Dataverse, not model guessing.

## Local API smoke test

Run `python scripts/run_reference_demo.py` with `PYTHONPATH=src`, then check `/health`, upload each synthetic PDF through `/api/invoices/upload`, and confirm the browser dashboard and REST responses match the automated tests.
