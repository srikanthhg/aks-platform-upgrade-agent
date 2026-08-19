# Azure Container Apps deployment

This release deploys three Container Apps: API, worker, and UI. PostgreSQL stores LangGraph checkpoints, the durable work queue, cluster locks and audit events. Key Vault stores the PostgreSQL connection string. A user-assigned managed identity authenticates to Key Vault and Azure Resource Manager.

Keep `allowRealUpgrades=false` until dry-run validation succeeds. Build backend and frontend images in ACR, configure Entra API/SPA registrations, grant least-privilege AKS and Key Vault access to the managed identity, edit `infra/main.parameters.example.json`, and deploy with `az deployment group create --template-file infra/main.bicep`.

Validate login, dry run, approval/rejection, worker restart recovery, audit rows, reports, PostgreSQL backups, and one disposable-cluster real upgrade before production use.
