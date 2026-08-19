# Security policy

Do not open public issues containing credentials, tenant IDs, subscription IDs, cluster names, kubeconfig content, or exploit details. Report sensitive findings privately to the repository owner.

Production requirements:

- Microsoft Entra ID authentication and application-role authorization
- Private API ingress where possible
- Key Vault references for database secrets
- TLS-enforced PostgreSQL connectivity
- Least-privilege managed identity
- `ALLOW_REAL_UPGRADES=false` until change approval and validation gates pass
- Branch protection, dependency scanning, image scanning, and signed releases
