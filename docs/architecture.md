# Architecture

## Components

- **Frontend:** React, TypeScript, Material UI, MSAL.
- **API:** FastAPI. Authenticates operators and enqueues work.
- **Worker:** Claims PostgreSQL jobs and executes LangGraph workflows.
- **PostgreSQL:** Durable queue, checkpoints, cluster locks, audit events, reports.
- **Azure tools:** Azure CLI, kubectl, and kubelogin run with argument arrays and timeouts.

## Safety model

1. A workflow acquires a cluster-specific distributed lock.
2. Discovery confirms the cluster and supported target versions.
3. Validation evaluates nodes, pods, PDBs, storage, events, and system workloads.
4. Warnings pause for an authorized operator decision.
5. Real commands require both request `dry_run=false` and server `ALLOW_REAL_UPGRADES=true`.
6. Control plane is upgraded before node pools.
7. Validation runs after each disruptive stage.
8. Every decision and result is written to PostgreSQL audit storage.
