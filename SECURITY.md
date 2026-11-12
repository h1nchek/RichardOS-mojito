# Security policy

## Reporting a vulnerability

Do not publish credentials, signing keys, private firmware dumps, or exploitable vulnerability details in a public issue.

For a security-sensitive report, contact the repository owner privately through the contact method listed on their GitHub profile. Include:

- the affected file, component, or commit;
- the impact and conditions required to reproduce the issue;
- a minimal proof or relevant log with secrets removed.

If private contact is unavailable, open a public issue containing only a high-level description and ask for a private reporting channel. Do not attach passwords, access tokens, runner registration tokens, private keys, or personal data.

## Build infrastructure

- Use a dedicated, trusted self-hosted runner for Android builds.
- Do not run untrusted pull-request code on a runner that has access to secrets or other sensitive systems.
- Treat downloaded source archives, prebuilts, and build artifacts as untrusted until inspected.
- Never store signing keys or long-lived credentials in the repository.
