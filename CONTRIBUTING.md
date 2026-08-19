# Contributing

1. Create a branch from `main`.
2. Keep real upgrades disabled in local and CI environments.
3. Add or update tests for every behavior change.
4. Run `make test compile verify` and `make frontend-build`.
5. Never commit credentials, kubeconfig files, access tokens, or database URLs.
6. Use pull requests; require CI and one reviewer before merge.

Commit messages should describe the operational outcome, for example:
`feat(validation): block upgrades when system pods are unhealthy`.
