# Operations runbook

Before every upgrade confirm the change window, backup/restore readiness, Azure-supported target version, PDB disruption capacity, surge capacity, recent warning events, and kube-system health. Start with dry run and review the pre-upgrade report.

Do not automatically retry destructive commands without understanding failures. Preserve workflow ID and audit records. Enable PostgreSQL HA, TLS, backups, point-in-time restore, private networking, monitoring, and tested recovery procedures.
