# Personal Microsoft Tenant Setup

This project is intended to be deployed in a Microsoft tenant that you personally control, not in an employer or university tenant.

## Recommended setup

Use this ownership chain:

Personal Microsoft account -> personally owned Microsoft Entra tenant -> native `*.onmicrosoft.com` work account -> Power Apps Developer Plan -> Developer Power Platform environment -> Dataverse / Power Automate / Power Apps / Copilot Studio.

A normal Outlook.com/Hotmail consumer account is useful as the owner/sign-up identity, but the Power Apps Developer Plan itself expects a work account. Microsoft currently recommends creating a dedicated test tenant first when you do not already have a work account.

## Step 1 - Create or identify your Microsoft Entra tenant

Microsoft's current manual route requires an Azure account with an active subscription.

1. Sign in to the Microsoft Entra admin center: `https://entra.microsoft.com/`.
2. Check the account menu in the upper-right corner to see whether you already have a tenant.
3. If you do not have a suitable tenant, create a new **Microsoft Entra ID workforce tenant**.
4. Use an organisation name that you personally control, for example `Chintan AI Lab`.
5. Choose an initial domain such as `chintanailab.onmicrosoft.com`.
6. Use your real country/region. The initial `onmicrosoft.com` domain cannot later be renamed or deleted, so choose it carefully.

Alternative Microsoft-supported routes are a qualifying Microsoft 365 Developer Program sandbox, a Microsoft 365 trial, or a paid Microsoft 365 business plan.

## Step 2 - Create a native work account inside the tenant

After the tenant exists:

1. In Microsoft Entra admin center, go to **Entra ID -> Users -> New user -> Create new user**.
2. Create a cloud-only account such as `chintan@chintanailab.onmicrosoft.com`.
3. Save the temporary password.
4. Assign the account the administrator permissions needed to manage your own development tenant. For a one-person lab, Global Administrator is the simplest bootstrap option; after setup, reduce privileges where practical.
5. Sign out of the personal Microsoft account and sign in once with the new `onmicrosoft.com` account to complete the initial password change.

Do not put the password, tenant secret, client secret, connection string, or recovery codes in this GitHub repository.

## Step 3 - Sign up for the Power Apps Developer Plan

1. While signed in as the new work account, open the Power Apps Developer Plan sign-up page: `https://aka.ms/PowerAppsDevPlan`.
2. Complete the sign-up.
3. Open `https://make.powerapps.com/`.
4. Use the environment picker in the upper-right and select your new **Developer** environment, normally named after your account.
5. Confirm that Dataverse is available.

Microsoft states that the Developer Plan is for development/testing and provides Power Apps, Power Automate, and Dataverse development capabilities. It is not a production environment.

## Step 4 - Verify the environment before building this project

Record these values privately (do not commit secrets):

- Tenant name
- Tenant ID
- Work account UPN, for example `chintan@...onmicrosoft.com`
- Power Platform environment name
- Environment URL
- Region

Then confirm you can open:

- Power Apps: `https://make.powerapps.com/`
- Power Automate: `https://make.powerautomate.com/`
- Power Platform admin center: `https://admin.powerplatform.microsoft.com/`
- Copilot Studio: `https://copilotstudio.microsoft.com/`

## Step 5 - Licensing reality for this portfolio project

### Power Apps / Power Automate / Dataverse

The Developer Plan is appropriate for building and testing the app, flows, tables and solution components in a personal developer environment.

### AI Builder invoice extraction

The project uses AI Builder invoice processing. Microsoft discontinued AI Builder trials. Running AI Builder inside an app, flow or agent consumes AI Builder credits or Copilot Credits depending on the environment/licensing state.

This means the repository can be built and most of the workflow can be tested for free, but **real runtime invoice extraction through AI Builder may require available capacity/credits**. Keep the included local PDF reference extractor as a zero-cost development/test fallback until capacity is available.

Do not claim live AI Builder processing on your CV until you have actually executed the invoice model successfully in the Microsoft environment.

### Copilot Studio

A Copilot Studio trial currently allows creating and testing an agent in the test chat panel, but Microsoft states that the trial does not permit publishing the agent. For a portfolio demonstration, a tested agent inside Copilot Studio is still useful; publishing requires the appropriate tenant licence/capacity.

## Step 6 - Target project build order

After the tenant and Developer environment are ready, build the Microsoft solution in this order:

1. Create solution `AI Invoice Processing Automation`.
2. Create Dataverse Invoice table and choice values from `dataverse/`.
3. Add environment variables and connection references.
4. Create SharePoint `Invoices` library with `Incoming`, `Processed`, and `Exceptions` folders if SharePoint is available in the tenant.
5. Build `INV-01 - Process Invoice` from `power-automate/INV-01-Process-Invoice.flow-spec.json`.
6. Build `INV-04 - Revalidate Reviewed Invoice` so Power Apps cannot bypass server-side validation.
7. Build the invoice-review Canvas app from `power-apps/`.
8. Build Copilot Studio status/review tools from `copilot-studio/`.
9. Add Teams/email notifications if the tenant has those services.
10. Test with all synthetic invoices in `test-data/invoices/`.
11. Export the genuine unmanaged solution from the tenant.
12. Unpack/export the solution into `solution/` and commit those real generated artifacts to GitHub.

## Definition of done

The Microsoft deployment is considered genuinely complete only when these scenarios work in the tenant:

- `01-auto-approve.pdf` -> valid low-value invoice -> auto-approved.
- `02-manager-approval.pdf` -> manager approval required.
- `03-high-value.pdf` -> manager approval then finance approval.
- Duplicate pair -> second invoice rejected/flagged as duplicate.
- Missing invoice-number fixture -> Needs Review -> corrected in Power Apps -> revalidated through Power Automate.
- Copilot Studio test chat retrieves invoice status and review queue without being allowed to approve or pay an invoice.

## Security rules

- Use only synthetic invoices for the public portfolio repository.
- Never commit bank details, access tokens, client secrets, tenant secrets or production data.
- Keep the Copilot agent read-only for status/review queries.
- Keep approval/payment authority inside server-side Power Automate logic, never directly in Power Apps or Copilot Studio.
