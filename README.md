# AKS Platform Upgrade Agent

A production-oriented reference implementation for safely discovering, validating, approving, and upgrading Azure Kubernetes Service clusters. It includes a React UI, FastAPI API, durable PostgreSQL-backed job queue and LangGraph checkpoints, a dedicated worker, Microsoft Entra ID authorization, Docker packaging, GitHub Actions, and Azure Container Apps Bicep deployment.

> **Safety default:** real AKS upgrades are disabled. Keep `ALLOW_REAL_UPGRADES=false` until the complete dry-run and disposable-cluster validation gates pass.

## Repository layout

```text
.
├── backend/          FastAPI API, LangGraph agent, worker, tests
├── frontend/         React + TypeScript + MSAL UI
├── infra/            Azure Container Apps Bicep
├── scripts/          Azure preflight and API smoke checks
├── docs/             Architecture, deployment, operations, validation
└── .github/          CI, container build, security and contribution files
```

## Architecture

```text
Browser (React + MSAL)
        │
        ▼
FastAPI (2–5 replicas)
        │
        ▼
PostgreSQL
  ├─ workflow job queue
  ├─ LangGraph checkpoints
  ├─ distributed cluster locks
  ├─ audit events
  └─ reports
        │
        ▼
Dedicated worker
        │
        ▼
Azure CLI + kubectl + AKS
```

## Local development

Prerequisites: Python 3.12, Node.js 22, Docker Compose, Azure CLI, kubectl, and optionally kubelogin.

```bash
cp backend/.env.example backend/.env
docker compose up --build
```

Services:

- UI: http://localhost:5173
- API: http://localhost:8000
- API docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432

For local API-key authentication, the compose file uses `local-development-key`.

## Verify

```bash
make test
make compile
make verify
```

The CI workflow additionally builds both Docker images and validates Bicep when Azure CLI is available.

## Deployment

Follow [docs/azure-container-apps.md](docs/azure-container-apps.md). Production deployment requires:

- Azure Database for PostgreSQL Flexible Server
- Azure Container Registry
- Azure Container Apps environment
- User-assigned managed identity
- Key Vault secret containing `DATABASE_URL`
- Microsoft Entra API and SPA app registrations
- AKS permissions for the worker identity

## Production status

This repository is a deployment-ready **candidate**, not proof that your specific Azure environment is production validated. Complete [docs/production-validation.md](docs/production-validation.md) against a disposable AKS cluster before enabling real upgrades.

## Extending the platform

The backend is intentionally separated so future resource modules—Argo CD, Helm release validation, Terraform/Bicep review, and Azure resource maintenance—can reuse authentication, approvals, queueing, audit, UI, and deployment foundations.
