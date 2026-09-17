from __future__ import annotations

from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "test-data" / "invoices"
OUT.mkdir(parents=True, exist_ok=True)

INVOICES = [
    ("01-auto-approve.pdf", "Northwind Office Ltd", "INV-1001", "PO-4401", 350.00, 70.00, 420.00),
    ("02-manager-approval.pdf", "Contoso Facilities Ltd", "INV-1002", "PO-4402", 1000.00, 200.00, 1200.00),
    ("03-high-value.pdf", "Fabrikam Technology Ltd", "INV-1003", "PO-4403", 6250.00, 1250.00, 7500.00),
    ("04-duplicate-original.pdf", "Adventure Works Services", "INV-1004", "PO-4404", 250.00, 50.00, 300.00),
    ("05-duplicate-copy.pdf", "Adventure Works Services", "INV-1004", "PO-4404", 250.00, 50.00, 300.00),
    ("06-missing-invoice-number.pdf", "Tailspin Supplies Ltd", None, "PO-4405", 700.00, 140.00, 840.00),
]


def money(value: float) -> str:
    return f"GBP {value:,.2f}"


def draw_invoice(path: Path, supplier: str, number: str | None, po: str, subtotal: float, tax: float, total: float) -> None:
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    c.setTitle(number or "Invoice")

    c.setFont("Helvetica-Bold", 22)
    c.drawString(25 * mm, height - 28 * mm, "INVOICE")
    c.setFont("Helvetica-Bold", 13)
    c.drawString(25 * mm, height - 42 * mm, supplier)
    c.setFont("Helvetica", 10)
    c.drawString(25 * mm, height - 49 * mm, "14 Example Business Park")
    c.drawString(25 * mm, height - 55 * mm, "Manchester, M1 1AA, United Kingdom")

    y = height - 75 * mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(25 * mm, y, "Invoice Number")
    c.drawString(75 * mm, y, "Purchase Order")
    c.drawString(125 * mm, y, "Invoice Date")
    c.drawString(165 * mm, y, "Due Date")
    c.setFont("Helvetica", 10)
    c.drawString(25 * mm, y - 7 * mm, number or "")
    c.drawString(75 * mm, y - 7 * mm, po)
    c.drawString(125 * mm, y - 7 * mm, "17 Sep 2026")
    c.drawString(165 * mm, y - 7 * mm, "17 Oct 2026")

    y -= 30 * mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(25 * mm, y, "Description")
    c.drawRightString(145 * mm, y, "Net")
    c.drawRightString(170 * mm, y, "VAT")
    c.drawRightString(200 * mm, y, "Total")
    c.line(25 * mm, y - 2 * mm, 200 * mm, y - 2 * mm)

    c.setFont("Helvetica", 10)
    c.drawString(25 * mm, y - 10 * mm, "Professional services / supplied goods")
    c.drawRightString(145 * mm, y - 10 * mm, money(subtotal))
    c.drawRightString(170 * mm, y - 10 * mm, money(tax))
    c.drawRightString(200 * mm, y - 10 * mm, money(total))

    y -= 35 * mm
    c.setFont("Helvetica", 10)
    c.drawRightString(175 * mm, y, "Subtotal")
    c.drawRightString(200 * mm, y, money(subtotal))
    c.drawRightString(175 * mm, y - 7 * mm, "Total Tax")
    c.drawRightString(200 * mm, y - 7 * mm, money(tax))
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(175 * mm, y - 16 * mm, "Invoice Total")
    c.drawRightString(200 * mm, y - 16 * mm, money(total))
    c.drawRightString(175 * mm, y - 25 * mm, "Amount Due")
    c.drawRightString(200 * mm, y - 25 * mm, money(total))

    c.setFont("Helvetica", 8)
    c.drawString(25 * mm, 20 * mm, "Synthetic test invoice - no real supplier, bank details or payment instruction.")
    c.save()


def main() -> None:
    for args in INVOICES:
        filename, *rest = args
        draw_invoice(OUT / filename, *rest)
    print(f"Generated {len(INVOICES)} synthetic invoices in {OUT}")


if __name__ == "__main__":
    main()
