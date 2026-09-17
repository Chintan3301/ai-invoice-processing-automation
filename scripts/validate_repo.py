from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "config/business-rules.json",
    "dataverse/invoice-table.schema.json",
    "power-automate/INV-01-Process-Invoice.flow-spec.json",
    "power-automate/INV-02-Get-Invoice-Status.flow-spec.json",
    "power-automate/INV-03-List-Review-Queue.flow-spec.json",
    "power-automate/INV-04-Revalidate-Reviewed-Invoice.flow-spec.json",
    "power-apps/formulas.fx.txt",
    "copilot-studio/agent-instructions.md",
    "src/invoice_automation/api.py",
    "src/invoice_automation/service.py",
    "src/invoice_automation/extractor.py",
    "Dockerfile",
    "docs/local-reference-demo.md",
]


def main() -> None:
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    if missing:
        raise SystemExit(f"Missing required files: {missing}")

    for path in ROOT.rglob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))

    rules = json.loads((ROOT / "config/business-rules.json").read_text())
    assert rules["auto_approval_limit"] < rules["manager_approval_limit"]
    assert 0 <= rules["minimum_required_confidence"] <= 1

    print("Repository validation passed.")


if __name__ == "__main__":
    main()
