# Background worker image

The worker runs as a separate Azure Container App from the FastAPI API. It
consumes jobs from the existing PostgreSQL `workflow_jobs` queue and executes
the existing LangGraph workflow.

## Image design

The worker image is layered on the backend image rather than installing a
second copy of Python dependencies and Azure tooling. This keeps the API and
worker runtime dependencies aligned. The worker entry point delegates to
`backend/worker.py`; queue and workflow logic are not duplicated.

## Build and push

Build and push the backend image first. Then build the worker image using the
**same backend image tag**:

```bash
docker build \
  -f worker/Dockerfile \
  --build-arg BACKEND_IMAGE=srikanthhg/aks-upgrade-agent-backend:<tag> \
  -t srikanthhg/aks-upgrade-agent-worker:<tag> \
  .

docker push srikanthhg/aks-upgrade-agent-worker:<tag>
```

Replace `<tag>` with the exact tag of the backend image deployed to the API
Container App. Run these commands from the repository root.

## Azure Container App configuration

Create a separate Container App for the worker with:

- The worker image built above.
- The same Container Apps environment as the backend API.
- No ingress.
- The same PostgreSQL `DATABASE_URL` secret/reference used by the backend.
- The same Azure managed identity and required Azure configuration used by
  the backend worker operations.
- Minimum replicas: `1`; maximum replicas: `1` initially.
- No HTTP health probe. The worker is a long-running background process and
  does not expose an HTTP endpoint.

The image starts with `python /app/worker/main.py`. Do not override the
container command unless you intentionally want to replace this entry point.

## Important

The worker only processes jobs after it can connect to PostgreSQL. If no AKS
cluster exists for a submitted request, the worker will still consume the job,
but the discovery step will fail for that cluster. A demo/no-cluster workflow
would be a separate application feature.
