FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates gnupg unzip \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://aka.ms/InstallAzureCLIDeb | bash \
    && az version

ARG KUBECTL_MINOR=v1.32
RUN curl -fsSL "https://pkgs.k8s.io/core:/stable:/${KUBECTL_MINOR}/deb/Release.key" \
      | gpg --dearmor -o /usr/share/keyrings/kubernetes-apt-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/${KUBECTL_MINOR}/deb/ /" \
      > /etc/apt/sources.list.d/kubernetes.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends kubectl \
    && kubectl version --client=true \
    && rm -rf /var/lib/apt/lists/*

ARG KUBELOGIN_VERSION=v0.2.20
ARG KUBELOGIN_SHA256=2e92450a929dd2aec4da818b40dd4fda97aaeae2d6cd9c1074cc1371210f4ab9
RUN curl -fsSL "https://github.com/Azure/kubelogin/releases/download/${KUBELOGIN_VERSION}/kubelogin-linux-amd64.zip" \
      -o /tmp/kubelogin.zip \
    && echo "${KUBELOGIN_SHA256}  /tmp/kubelogin.zip" | sha256sum -c - \
    && unzip -q /tmp/kubelogin.zip -d /tmp/kubelogin \
    && install -m 0755 /tmp/kubelogin/bin/linux_amd64/kubelogin /usr/local/bin/kubelogin \
    && kubelogin --version \
    && rm -rf /tmp/kubelogin /tmp/kubelogin.zip

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .
RUN mkdir -p /app/data /app/logs /app/reports \
    && useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
