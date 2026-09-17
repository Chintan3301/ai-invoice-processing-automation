# Security notes

- Never commit Power Platform client secrets, user passwords, SharePoint credentials, connection IDs containing secrets, or real invoice documents.
- Use GitHub Actions secrets for service-principal credentials.
- Use environment variables / deployment settings for environment-specific URLs, approver identities and Teams IDs.
- Use least-privilege Dataverse roles for the Canvas app and Copilot Studio users.
- Treat invoice documents as confidential business data. Synthetic fixtures in this repository contain no real personal or supplier banking information.
- Keep the Copilot toolset read-only unless a later version has a separately reviewed approval design with explicit authorization controls.
