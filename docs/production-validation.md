# Production validation gates

Run repository/unit checks, container builds, local PostgreSQL/API smoke tests, read-only Azure/AKS preflight, Container Apps dry runs, and finally one disposable AKS real upgrade. Only enable `ALLOW_REAL_UPGRADES=true` after all prior gates pass. Validate control-plane-before-nodepool ordering, post-upgrade health, audit, reports, restart recovery, private networking, PostgreSQL HA/backups, Key Vault rotation, alerting, and change approval.
