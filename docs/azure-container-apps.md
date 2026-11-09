# Azure Container Apps deployment

This release deploys three Container Apps: API, worker, and UI. PostgreSQL stores LangGraph checkpoints, the durable work queue, cluster locks and audit events. Key Vault stores the PostgreSQL connection string. A user-assigned managed identity authenticates to Key Vault, Azure Resource Manager, and Azure OpenAI.

Keep `allowRealUpgrades=false` until dry-run validation succeeds. Build backend and frontend images in ACR, configure Entra API/SPA registrations, grant least-privilege AKS and Key Vault access to the managed identity, edit `infra/main.parameters.example.json`, and deploy with `az deployment group create --template-file infra/main.bicep --parameters @infra/main.parameters.example.json`.

## Azure OpenAI (GPT-4.1-class)

1. Create an Azure OpenAI / Azure AI Foundry resource in a region and subscription with GPT-4.1 model availability and quota.
2. Deploy a chat model from the GPT-4.1 family. The deployment name is an arbitrary resource-level name; set that exact name in `azureOpenAIDeployment` (example: `gpt-41-aks-advisor`). The code selects the deployment by this name; it does not hard-code a model ID.
3. Set `azureOpenAIEndpoint` to the resource endpoint and keep `azureOpenAIApiVersion` on a version supported by your resource/deployment.
4. Grant the user-assigned identity attached to both the API and worker the **Cognitive Services OpenAI User** role on the Azure OpenAI resource. Use the resource scope, not subscription-wide scope. Example:

   ```bash
   az role assignment create \\
     --assignee-object-id <managed-identity-principal-id> \\
     --assignee-principal-type ServicePrincipal \\
     --role 'Cognitive Services OpenAI User' \\
     --scope <azure-openai-resource-id>
   ```

   No API key is needed in ACA; the backend uses `DefaultAzureCredential` and managed identity.
5. Set `aiAdvisorEnabled=true`. Both API and worker receive the endpoint, deployment, API version, and enable flag. The worker executes the LangGraph model call. Verify `/diagnostics` and the workflow's `ai_advisor.status` after deployment.

The model has three bounded, read-only tools over facts already gathered by deterministic discovery: available upgrade facts, node pool facts, and validation facts. It cannot invoke Azure CLI, kubectl, shell commands, or write operations. Tool calls are capped. Its risk analysis, recommendations, and proposed checks are advisory and cannot alter deterministic validation outcomes.

## Approval safety

- A clean dry run may proceed without an approval pause. Validation warnings require operator review.
- **Every real upgrade requires an authenticated Entra operator approval**, including when validation is PASS.
- The approval is bound to a SHA-256 hash of the cluster identity, current/target Kubernetes versions, dry-run mode, max surge, node pool list, and validation status/warnings. A changed plan invalidates the approval. Approvals expire after `approvalTtlMinutes` (default 30 minutes).
- The upgrade executor independently enforces approval, approver identity, matching plan hash, validation status, and `ALLOW_REAL_UPGRADES=true`. The model cannot approve or execute.
- Keep `allowRealUpgrades=false` until the full disposable-cluster validation process is complete.

Validate login, dry run, approval/rejection, plan-change rejection, worker restart recovery, audit rows, reports, PostgreSQL backups, and one disposable-cluster real upgrade before production use.
