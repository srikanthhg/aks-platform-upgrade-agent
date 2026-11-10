# Build the backend image first, then pass the exact same tag here.
# This keeps Python dependencies, Azure CLI, kubectl and kubelogin identical
# between the API and worker images.
ARG BACKEND_IMAGE=srikanthhg/aks-upgrade-agent-backend:latest
FROM ${BACKEND_IMAGE}

WORKDIR /app

# The backend image contains the existing worker implementation at /app/worker.py.
COPY --chown=appuser:appuser worker/main.py /app/worker/main.py

# The inherited backend health check targets the FastAPI /health endpoint.
# A background worker does not expose HTTP, so disable that check.
HEALTHCHECK NONE

USER appuser
CMD ["python", "/app/worker/main.py"]
