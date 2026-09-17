# Flow implementation details

This document turns the flow specifications into a build sequence that can be followed in the Power Automate designer without relying on undocumented internal output paths.

## INV-01 - Process Invoice

### Trigger

**SharePoint - When a file is created (properties only)**

- Site Address: environment variable `cyg_SharePointSiteUrl`
- Library Name: environment variable `cyg_InvoiceLibraryName`
- Folder: `/Incoming`
- Trigger condition: only `.pdf` files

Immediately add **Get file content** using the trigger's file Identifier.

### Scope A - Extract

Add **AI Builder - Process invoices** and pass the file content. Use the designer's dynamic-content fields rather than manually typing internal JSON paths. Capture at least:

- Invoice ID and confidence
- Vendor Name and confidence
- Purchase Order
- Invoice Date
- Due Date
- Subtotal
- Total Tax
- Invoice Total and confidence
- Amount Due

Create a normalized duplicate key with the expression shown in `power-automate/expressions.md`.

### Scope B - Duplicate check

Use **Dataverse - List rows** against `Invoices` with Top Count = 1 and a Filter rows expression on `cyg_duplicatekey`.

If a match exists:

1. Do not run approval actions.
2. Post a Teams exception message containing supplier, invoice number, source filename and "Duplicate".
3. Email the submitter if their email is available.
4. Terminate with status **Succeeded**, because a detected duplicate is a handled business outcome rather than a technical flow failure.

The Dataverse alternate key on `cyg_duplicatekey` remains the concurrency backstop if two identical files arrive almost simultaneously.

### Scope C - Validate extraction

The required fields are Invoice ID, Vendor Name and Invoice Total. Each must be populated and the three corresponding confidence scores must meet the configured threshold.

If validation fails:

1. Create the Dataverse row with status **Needs Review**.
2. Save a human-readable Review Reason such as `Vendor confidence 0.74 is below 0.80` or `Invoice Number is missing`.
3. Notify the Finance Teams channel.
4. Notify the submitter by email.
5. End the normal approval branch.

Never replace missing extracted fields with plausible defaults.

### Scope D - Persist valid invoice

Create the Dataverse Invoice row before starting a long-running approval. Store the source file URL and all relevant extraction confidence values. Set initial status based on route:

- <= auto limit: **Approved**
- > auto limit: **Pending Approval**

### Scope E - Approval routing

#### Route 1: Auto approval

When `Invoice Total <= cyg_AutoApprovalLimit`:

- Update status = Approved
- Approved On = `utcNow()`
- Approved By = `Automation`

#### Route 2: Manager approval

When `AutoApprovalLimit < Invoice Total <= ManagerApprovalLimit`:

Use **Approvals - Start and wait for an approval**.

- Approval type: Approve/Reject - First to respond
- Assigned to: `cyg_ManagerApproverEmail`
- Title: `Invoice approval - <Invoice Number> - <Supplier>`
- Details: include amount, PO, source link and Dataverse row identifier

On Approve:

- Status = Approved
- Save responder email, comments and completion timestamp

On Reject:

- Status = Rejected
- Save responder email and comments

#### Route 3: Manager then Finance

When `Invoice Total > cyg_ManagerApprovalLimit`:

1. Run a manager **Start and wait for an approval**.
2. If manager rejects, set Rejected and stop.
3. If manager approves, run a second **Start and wait for an approval** assigned to `cyg_FinanceApproverEmail`.
4. Only after Finance approves set status Approved.

Using two explicit approval actions makes the two-stage audit trail obvious to an interviewer and avoids hiding logic in a complex expression.

### Scope F - Notifications

At the end of every handled route:

- Post a concise Teams message to the Finance team/channel.
- Send an Outlook email to the submitter when an address is known.

Notification text must use Dataverse / flow values, not AI-generated narrative.

### Scope G - Error handling

Wrap the main scopes in a Try/Catch pattern. Configure Catch with **Run after** = failed, timed out, or skipped as appropriate.

Catch actions:

1. If a Dataverse row exists, update status to **Extraction Failed** and store a short processing error.
2. Post an exception to Teams.
3. Terminate the flow as Failed so operational monitoring can detect the technical problem.

Do not include invoice file content in ordinary error messages.

---

## INV-02 - Get Invoice Status

This is a Copilot Studio agent flow.

1. Trigger: **When an agent calls the flow** with text input `invoiceNumber`.
2. Normalize the value with `trim()`.
3. Dataverse **List rows**, Top Count 5, selecting only safe response fields.
4. If zero records, respond with `found=false`.
5. Otherwise respond with invoice number, supplier, total, currency, status, review reason, approval comments and source URL.
6. Add **Respond to the agent** and keep asynchronous response Off.

No update action is present; this tool is read-only by design.

---

## INV-03 - List Review Queue

1. Trigger: **When an agent calls the flow** with optional numeric input `maxItems`.
2. Clamp the effective value to 10 or less.
3. Dataverse **List rows** where status = Needs Review, ordered oldest first.
4. Select only invoice number, supplier, total, review reason and source URL.
5. Respond to the agent with the small review list.

This flow should normally finish in a few seconds and comfortably within Copilot Studio's real-time tool limit.
