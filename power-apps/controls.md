# Canvas app - Invoice Review

Create a tablet Canvas app inside the same solution and add the Dataverse **Invoices** table.

## Screens

### 1. Review Queue
- `txtSearch`: search box.
- `ddStatus`: optional status filter.
- `galInvoices`: gallery showing invoice number, supplier, total, status and created date.
- Use status chips only as a visual aid; do not hide validation problems.

### 2. Invoice Detail
- `frmInvoice`: Edit form bound to `galInvoices.Selected`.
- Editable fields: Invoice Number, Supplier Name, Purchase Order, Invoice Date, Due Date, Subtotal, Tax, Invoice Total, Amount Due.
- Read-only fields: Status, confidence values, source filename, source URL, submitted by.
- Buttons: Save, Mark Ready, Reject, Open Source PDF.

### 3. Dashboard (optional)
- Count of Needs Review, Pending Approval, Approved and Rejected records.
- Keep it simple; the app is primarily a reviewer work queue.

Use the formulas in `formulas.fx.txt`. Formula names may need to be adjusted to the display names created in your environment.
