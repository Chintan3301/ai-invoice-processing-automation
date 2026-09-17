# Power Automate expressions

These expressions are intended to be pasted into the corresponding actions in the flow designer. Replace action names if Power Automate changes the generated internal name.

## File trigger condition

```text
@endsWith(toLower(triggerOutputs()?['body/{FilenameWithExtension}']), '.pdf')
```

## Validation order

Check required fields and their confidence values **before** duplicate detection. A missing or low-confidence invoice number must go to **Needs Review** instead of being used as a duplicate key.

## Normalized duplicate key

Only build/use this key after the required fields pass validation. Use the AI Builder dynamic values for Vendor Name and Invoice ID inside the same expression:

```text
concat(
  toLower(trim(coalesce(<VendorName>, ''))),
  '|',
  toLower(trim(coalesce(<InvoiceId>, '')))
)
```

## Escape a text value before inserting it into an OData filter

```text
replace(outputs('Compose_Duplicate_Key'),'''','''''')
```

Then use the Dataverse **Filter rows** value:

```text
cyg_duplicatekey eq '<escaped duplicate key>'
```

## Duplicate exists

```text
greater(length(outputs('List_matching_invoices')?['body/value']), 0)
```

## Required values present

```text
and(
  not(empty(<InvoiceId>)),
  not(empty(<VendorName>)),
  not(empty(<InvoiceTotalNumber>))
)
```

## Required confidence threshold met

```text
and(
  greaterOrEquals(float(coalesce(<InvoiceIdConfidence>, 0)), float(<MinimumConfidence>)),
  greaterOrEquals(float(coalesce(<VendorNameConfidence>, 0)), float(<MinimumConfidence>)),
  greaterOrEquals(float(coalesce(<InvoiceTotalConfidence>, 0)), float(<MinimumConfidence>))
)
```

## Approval routing

Auto-approve:

```text
lessOrEquals(float(<InvoiceTotalNumber>), float(<AutoApprovalLimit>))
```

Manager approval only:

```text
and(
  greater(float(<InvoiceTotalNumber>), float(<AutoApprovalLimit>)),
  lessOrEquals(float(<InvoiceTotalNumber>), float(<ManagerApprovalLimit>))
)
```

Manager then Finance:

```text
greater(float(<InvoiceTotalNumber>), float(<ManagerApprovalLimit>))
```

## Notes on accuracy

Do not default a missing invoice number, supplier, or total to a believable value. Missing or low-confidence required data must go to **Needs Review**. This prevents the automation from silently approving a bad extraction.

## Revalidated invoice duplicate filter

For `INV-04`, exclude the current Dataverse row from the duplicate lookup. In the designer, build the OData filter using the current row ID from the trigger, for example conceptually:

```text
cyg_duplicatekey eq '<escaped duplicate key>' and cyg_invoiceid ne <current row id>
```

Use the designer's dynamic row-id value rather than hard-coding a GUID.
