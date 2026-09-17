# Build guide - Microsoft Power Platform

This is the shortest reliable path to a real tenant implementation.

## 1. Create the solution

In `make.powerapps.com`, select a developer environment with Dataverse and create an unmanaged solution:

- Display name: **AI Invoice Processing Automation**
- Unique name: `AIInvoiceProcessingAutomation`
- Publisher prefix: `cyg`

Create every table, choice, environment variable, app, flow and agent in this solution so dependencies can be exported together.

## 2. Create the Dataverse table

Create the **Invoice** table from `dataverse/invoice-table.schema.json` and the **Invoice Status** global choice from `dataverse/choices.json`.

Create an alternate key on **Duplicate Key**. Keep Invoice Number, Supplier Name, Invoice Total and Duplicate Key optional at the Dataverse schema level so incomplete AI extractions can still be stored for review. The stable required primary name is **Invoice Record**. The flows enforce the business-required fields before approval.

The main flow checks for an existing valid duplicate before insertion; the alternate key is the final concurrency safety net.

## 3. Create environment variables

Create solution environment variables for the values in `config/environment-variables.template.json`. Do not store real credentials in environment variables or Git.

## 4. Configure SharePoint

Create a document library named **Invoices** with folders:

- `/Incoming`
- `/Processed` (optional)
- `/Rejected` (optional)

The main flow only triggers on PDFs placed in `/Incoming`.

## 5. Build `INV-01 - Process Invoice`

Follow `power-automate/INV-01-Process-Invoice.flow-spec.json` and paste the expressions from `power-automate/expressions.md`.

Recommended scopes:

- `TRY - Read and Extract`
- `TRY - Validate and Persist`
- `TRY - Approval Routing`
- `TRY - Notify`
- `CATCH - Processing Error`

Configure the Catch scope to run when any Try scope fails or times out. Avoid swallowing an error without updating status or notifying Finance.

For approvals use the current **Start and wait for an approval** action. Two sequential approval actions are used for invoices above the manager limit so the flow is simple to explain and audit.

## 6. Build `INV-04 - Revalidate Reviewed Invoice`

Create the Dataverse-triggered flow from `power-automate/INV-04-Revalidate-Reviewed-Invoice.flow-spec.json`. It only reacts to **Ready for Validation** records, verifies the human-reviewed required fields, re-checks duplicates excluding the current row, and then performs the same amount-based approval routing.

This keeps business rules on the server side instead of allowing a Canvas app button to move an invoice directly into approval.

## 7. Build the Power Apps review app

Create a Canvas app inside the same solution, connect it to the **Invoices** table and use `power-apps/controls.md` plus `power-apps/formulas.fx.txt`.

The app is intentionally a review work queue, not a full accounting application. The **Mark Ready** action must set **Ready for Validation**, not **Pending Approval**.

## 8. Build the Copilot Studio agent

Create **Invoice Assistant** in the same environment. Add two agent flows based on:

- `INV-02-Get-Invoice-Status.flow-spec.json`
- `INV-03-List-Review-Queue.flow-spec.json`

Each flow must use **When an agent calls the flow** and **Respond to the agent**, be published, and have asynchronous response disabled. Add the instructions from `copilot-studio/agent-instructions.md`.

## 9. Test before publishing

Use every fixture in `test-data/invoices/`. Compare AI Builder's extracted result with `test-data/expected-extraction.json` and record actual confidence values. The routing decision should match the expected route after extraction corrections.

Critical cases:

1. normal auto-approved invoice;
2. manager approval boundary;
3. two-stage high-value approval;
4. duplicate upload;
5. missing invoice number;
6. intentionally degraded/low-quality scan to force manual review.

## 10. Export genuine solution source

After all components work in the tenant, export/clone the solution with current Power Platform CLI tooling:

```powershell
./deployment/export-solution.ps1 -EnvironmentUrl "https://YOURORG.crm.dynamics.com"
```

This creates genuine tenant-generated solution source for Git. Do not replace it with hand-written fake `.msapp` or flow export files.
