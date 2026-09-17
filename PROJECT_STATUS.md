# Project verification status

## Verified in this repository

- Business-rule implementation has automated tests for duplicates, missing fields, confidence threshold and all approval boundaries.
- JSON specifications and configuration files parse successfully.
- GitHub Actions workflow YAML parses successfully.
- Six synthetic PDF invoice fixtures were generated and visually rendered successfully.
- Repository has a clean Git history and no credentials are committed.

## Requires the owner's Microsoft tenant

The following cannot be truthfully marked as tenant-tested until the solution is built/imported in an environment that has Dataverse, AI Builder, Power Automate, Power Apps and Copilot Studio access:

- AI Builder extraction accuracy/confidence on the sample PDFs.
- SharePoint trigger and connection reference binding.
- Dataverse table/alternate-key creation.
- Approval delivery to real manager/finance identities.
- Teams and Outlook notification delivery.
- Canvas app publishing.
- Copilot Studio agent publishing and tool invocation.

After those tests pass, export the genuine Power Platform solution source into `solution/` and commit it to GitHub.

## Portable reference implementation

A FastAPI + SQLite reference service is included so the repository can be executed without a Microsoft tenant. It processes the synthetic PDF fixtures, applies the same validation/routing rules and simulates approval state transitions. This is test evidence only; the production implementation remains the Power Platform solution described in `docs/build-guide.md`.

Current automated result: **22 tests passing**.
