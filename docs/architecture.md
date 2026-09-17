# Architecture

```mermaid
flowchart LR
    U[Finance user / supplier] -->|Uploads PDF| SP[SharePoint Incoming folder]
    SP --> PA[Power Automate: Process Invoice]
    PA --> AI[AI Builder: Invoice processing]
    AI --> VAL{Validate + duplicate check}
    VAL -->|Duplicate / low confidence / missing data| DV[(Dataverse Invoices)]
    VAL -->|Valid| ROUTE{Approval routing}
    ROUTE -->|<= £500| AUTO[Auto approve]
    ROUTE -->|£500.01 - £5,000| MGR[Manager approval]
    ROUTE -->|> £5,000| MGR2[Manager] --> FIN[Finance approval]
    AUTO --> DV
    MGR --> DV
    FIN --> DV
    DV --> APP[Power Apps Review UI]
    DV --> AGENT[Copilot Studio Agent]
    PA --> TEAMS[Teams notification]
    PA --> EMAIL[Email notification]
```

## Design choices

- **SharePoint** stores source documents; **Dataverse** stores structured workflow state.
- **AI Builder** extracts invoice values and confidence scores. Low confidence does not silently pass.
- Duplicate identity is the normalized `supplier_name|invoice_number`, backed by a Dataverse alternate key.
- Approval thresholds are environment configuration, not hard-coded business logic.
- The Copilot agent is read-only. It can retrieve status and review queues but cannot approve or pay an invoice.

## Manual-review re-entry

Power Apps never assigns `Pending Approval` directly. A reviewer corrects the extracted fields and sets `Ready for Validation`. `INV-04 - Revalidate Reviewed Invoice` then performs required-field checks, duplicate detection and approval routing in Power Automate. This prevents client-side bypass of finance controls.
