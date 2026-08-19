# Validation results

Validated in the artifact-generation environment:

- Backend Python compilation: passed
- Backend unit tests: 16 passed
- Repository structural/static verifier: passed
- ZIP integrity: performed during packaging

Not executable in this environment:

- Frontend npm install/build
- Docker image builds
- Azure CLI / Bicep validation
- Live PostgreSQL/LangGraph checkpoint integration
- Entra token validation against a real tenant
- AKS discovery or upgrades

These are mandatory CI/Azure validation gates before enabling `ALLOW_REAL_UPGRADES=true`.
