# AKS Platform Upgrade Agent

An AI-assisted platform engineering application for discovering, validating, reviewing, approving, and upgrading Azure Kubernetes Service (AKS) clusters. The backend uses **Azure OpenAI** for contextual operational risk analysis and recommendations, while **LangGraph** orchestrates the workflow and deterministic tools perform cluster discovery, validation, and upgrades.

> **Safety default:** real AKS upgrades are disabled. Keep `ALLOW_REAL_UPGRADES=false` until the complete dry-run and disposable-cluster validation gates pass. The LLM is advisory only; it cannot approve or execute upgrades.

## Architecture

```text
Browser (React + Microsoft Entra ID)
        │
        ▼
FastAPI API ──► PostgreSQL job queue / audit / checkpoints
        │
        ▼
Dedicated LangGraph worker
        │
        ├── Azure CLI + kubectl ──► AKS discovery and deterministic health checks
        │
        ├── Azure OpenAI ──► Risk analysis, recommendations, missing-information questions
        │
        ├── Human approval gate (required for validation warnings)
        │
        └── Deterministic upgrade + post-upgrade validation + report
```

## What makes this AI-assisted?

- The workflow sends real discovered AKS facts—Kubernetes versions, available upgrades, node pools, validation results, and dry-run intent—to an Azure OpenAI chat deployment.
- The model returns structured operational analysis: summary, risks, recommendations, and questions about missing information.
- The AI analysis is saved into LangGraph state and included in the workflow reports and approval context.
- The application remains safe if Azure OpenAI is unavailable: the AI result is marked `UNAVAILABLE`, while deterministic validation and the configured approval gates remain authoritative.
- The model does not run arbitrary shell commands, change cluster state, bypass validation, or approve its own recommendations.

## Repository layout

```text
.
├── backend/          FastAPI API, Azure OpenAI advisor, LangGraph workflow, worker, tests
├── frontend/         React + TypeScript + MSAL UI
├── infra/            Azure Container Apps Bicep
├── scripts/          Azure preflight and API smoke checks
├── docs/             Architecture, deployment, operations, validation
└── .github/          CI, container build, security and contribution files
```

## Configure Azure OpenAI

1. Create or use an Azure AI Foundry / Azure OpenAI resource.
2. Deploy a chat-capable model (for example, a supported GPT deployment) and note the **deployment name**. Use the deployment name, not merely the model family name.
3. Configure these backend environment variables in the API/worker Container Apps environment:

```dotenv
AI_ADVISOR_ENABLED=true
AZURE_OPENAI_ENDPOINT=https://<resource-name>.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=<chat-deployment-name>
AZURE_OPENAI_API_VERSION=2024-10-21
```

4. Prefer managed identity in Azure. Grant the Container Apps workload identity the required Azure AI inference permissions for the resource. The code uses `DefaultAzureCredential` when `AZURE_OPENAI_API_KEY` is not set.
5. For local development only, you may set `AZURE_OPENAI_API_KEY` to a key stored in your local untracked `.env`. Never commit keys or place them in frontend `VITE_*` variables.
6. Restart/redeploy the backend and worker with the new configuration. AI analysis runs after deterministic pre-upgrade validation; inspect the workflow report for `ai_advisor.status` (`COMPLETED`, `DISABLED`, or `UNAVAILABLE`).

When the endpoint or deployment is not configured, the advisor reports `DISABLED`; it does not pretend an LLM call occurred. Set `AI_ADVISOR_ENABLED=false` to disable the advisor intentionally.

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

For local API-key authentication, use the development key configured in `docker-compose.yml`. Configure Azure OpenAI in `backend/.env` to activate model analysis.

## Verify

```bash
make test
make compile
make verify
```

CI builds both Docker images and validates Bicep when Azure CLI is available. Run the full test suite before merging this branch.

## Deployment

Follow [docs/azure-container-apps.md](docs/azure-container-apps.md). Production deployment requires Azure Database for PostgreSQL Flexible Server, Azure Container Registry, Azure Container Apps, a user-assigned managed identity, Key Vault for secrets, Microsoft Entra API and SPA registrations, AKS permissions for the worker identity, and Azure OpenAI access for the backend/worker identity.

## Production status

This repository is a deployment-ready candidate, not proof that your Azure environment is production validated. Complete [docs/production-validation.md](docs/production-validation.md) against a disposable AKS cluster before enabling real upgrades.
