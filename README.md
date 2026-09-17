 AI Invoice Processing & Approval Automation

A graduate-level Microsoft Power Platform portfolio project for processing PDF invoices with AI-assisted extraction, Dataverse validation, approval routing, manual review and conversational status lookup.

> Important: The repository contains a complete implementation specification, test harness and ALM scaffolding. Genuine Power Apps / Power Automate / Copilot solution artifacts must be created and exported from your own Power Platform developer environment because connection references, AI Builder bindings and tenant identities are environment-specific. The repo deliberately does not include fake hand-written `.msapp` files or a fabricated "importable" solution zip.

 Stack

Microsoft Copilot Studio · Power Automate · AI Builder · Dataverse · Power Apps · SharePoint · Teams · Outlook · GitHub Actions

 What the project does

1. A finance user uploads a PDF invoice to a SharePoint `Invoices/Incoming` folder.
2. Power Automate sends the PDF to AI Builder's prebuilt invoice-processing model.
3. Supplier, invoice number, PO, dates, subtotal, tax, invoice total, amount due and confidence values are normalized.
4. The flow checks a normalized supplier + invoice-number key to prevent duplicate processing.
5. Missing required fields or a required confidence score below 0.80 move the invoice to Needs Review.
6. Valid invoices are routed by configurable amount:
   - <= £500.00: auto-approved.
   - £500.01 - £5,000.00: manager approval.
   - > £5,000.00: manager approval followed by finance approval.
7. Dataverse stores status, extracted values, confidence, source link and approval comments.
8. Teams and email notifications report exceptions and final status.
9. A Power Apps Canvas app provides a manual-review queue.
10. A read-only Copilot Studio agent can retrieve an invoice's status or list items needing review.

 Repository map

- `power-automate/` - exact flow design and Power Automate expressions.
- `dataverse/` - table, columns, choice values and duplicate-key definition.
- `power-apps/` - screen design and Power Fx formulas.
- `copilot-studio/` - agent instructions, tool contracts and test utterances.
- `test-data/` - synthetic invoice PDFs and expected values.
- `src/` + `tests/` - executable routing logic, PDF reference extractor, REST API and automated tests.
- `deployment/` + `.github/workflows/` - Power Platform ALM/deployment scaffolding.
- `solution/` - destination for the real solution source exported from your tenant.

 Run the automated checks

```bash
python -m pip install -r requirements.txt
PYTHONPATH=src pytest -q
python scripts/validate_repo.py
```

The suite currently covers 22 scenarios, including routing boundaries, duplicate detection, PDF upload, manual review correction and sequential manager/finance approval.

 Run the local reference demo

This is a tenant-independent test harness for the workflow logic. It is not presented as a replacement for AI Builder, Dataverse, Power Apps or Power Automate. Production extraction and approvals remain in Microsoft Power Platform.

```bash
python -m pip install -r requirements.txt
$env:PYTHONPATH="src"    PowerShell
python scripts/run_reference_demo.py
```

On macOS/Linux, use `export PYTHONPATH=src` instead. Open `http://127.0.0.1:8000`, upload the synthetic PDFs under `test-data/invoices/`, and inspect the resulting status and approval route. The REST endpoints are documented automatically at `http://127.0.0.1:8000/docs`.

Docker is also supported:

```bash
docker build -t invoice-automation-demo .
docker run --rm -p 8000:8000 -v invoice-demo-data:/data invoice-automation-demo
```

 Build the real Power Platform solution

Follow [`docs/build-guide.md`](docs/build-guide.md). It specifies the exact Dataverse schema, flow branches, formulas, Copilot tools, test cases and export process.

Microsoft's current guidance supports AI Builder invoice extraction in Power Automate, standard approval actions, Copilot agent flows with `When an agent calls the flow` / `Respond to the agent`, and source-controlling complete solution assets using Dataverse Git integration or current `pac` solution tooling.

 Portfolio evidence to capture

After deployment, add screenshots (with synthetic data only) showing:

- a successful AI Builder extraction run;
- the Dataverse invoice row and confidence values;
- a manager approval and a two-stage high-value approval;
- the Power Apps review queue correcting a low-confidence invoice;
- Copilot Studio returning status for a test invoice;
- GitHub Actions CI passing.

 Scope boundaries

This project does not execute payments and the Copilot agent cannot approve or reject invoices. Those controls are intentionally left in Power Automate approvals / the review app to keep authorization explicit and auditable.

 References

- Microsoft Learn - AI Builder invoice processing: https://learn.microsoft.com/en-us/ai-builder/prebuilt-invoice-processing
- Microsoft Learn - Use invoice processing in Power Automate: https://learn.microsoft.com/en-us/ai-builder/flow-invoice-processing
- Microsoft Learn - Power Automate approvals: https://learn.microsoft.com/en-us/power-automate/get-started-approvals
- Microsoft Learn - Copilot Studio agent flows: https://learn.microsoft.com/en-us/microsoft-copilot-studio/flow-agent
- Microsoft Learn - Power Platform solution YAML source control: https://learn.microsoft.com/en-us/power-platform/alm/solution-source-control-yaml-format
- Microsoft Power Platform GitHub Actions: https://github.com/microsoft/powerplatform-actions
