param location string = resourceGroup().location
param environmentName string
param apiAppName string
param workerAppName string
param uiAppName string
param backendImage string
param uiImage string
param managedIdentityName string
@secure()
param databaseSecretUri string
param entraTenantId string
param entraAudience string
param apiMinReplicas int = 2
param apiMaxReplicas int = 5
param uiMinReplicas int = 2
param uiMaxReplicas int = 5
param externalApiIngress bool = true
param applicationInsightsConnectionString string = ''
param allowRealUpgrades bool = false
param approvalTtlMinutes int = 30
param aiAdvisorEnabled bool = true
@description('Azure OpenAI resource endpoint, for example https://resource.openai.azure.com/')
param azureOpenAIEndpoint string = ''
@description('Azure OpenAI deployment name. Deploy a GPT-4.1-class chat model in Azure AI Foundry.')
param azureOpenAIDeployment string = ''
param azureOpenAIApiVersion string = '2024-10-21'
resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {name: managedIdentityName}
resource env 'Microsoft.App/managedEnvironments@2024-03-01' existing = {name: environmentName}
resource ui 'Microsoft.App/containerApps@2024-03-01' = {name:uiAppName location:location properties:{managedEnvironmentId:env.id configuration:{activeRevisionsMode:'Single' ingress:{external:true targetPort:8080 transport:'auto' allowInsecure:false}} template:{containers:[{name:'ui' image:uiImage resources:{cpu:json('0.5') memory:'1Gi'}}] scale:{minReplicas:uiMinReplicas maxReplicas:uiMaxReplicas}}}}
resource api 'Microsoft.App/containerApps@2024-03-01' = {name:apiAppName location:location identity:{type:'UserAssigned' userAssignedIdentities:{'${identity.id}':{}}} properties:{managedEnvironmentId:env.id configuration:{activeRevisionsMode:'Single' ingress:{external:externalApiIngress targetPort:8000 transport:'auto' allowInsecure:false} secrets:[{name:'database-url' keyVaultUrl:databaseSecretUri identity:identity.id}]} template:{containers:[{name:'api' image:backendImage env:[{name:'APP_ENVIRONMENT' value:'production'},{name:'AUTH_MODE' value:'entra_id'},{name:'ENTRA_TENANT_ID' value:entraTenantId},{name:'ENTRA_AUDIENCE' value:entraAudience},{name:'DATABASE_URL' secretRef:'database-url'},{name:'AZURE_AUTH_MODE' value:'managed_identity'},{name:'AZURE_MANAGED_IDENTITY_CLIENT_ID' value:identity.properties.clientId},{name:'ALLOW_REAL_UPGRADES' value:string(allowRealUpgrades)},{name:'APPROVAL_TTL_MINUTES' value:string(approvalTtlMinutes)},{name:'AI_ADVISOR_ENABLED' value:string(aiAdvisorEnabled)},{name:'AZURE_OPENAI_ENDPOINT' value:azureOpenAIEndpoint},{name:'AZURE_OPENAI_DEPLOYMENT' value:azureOpenAIDeployment},{name:'AZURE_OPENAI_API_VERSION' value:azureOpenAIApiVersion}] resources:{cpu:json('1.0') memory:'2Gi'}}] scale:{minReplicas:apiMinReplicas maxReplicas:apiMaxReplicas}}}}
resource worker 'Microsoft.App/containerApps@2024-03-01' = {name:workerAppName location:location identity:{type:'UserAssigned' userAssignedIdentities:{'${identity.id}':{}}} properties:{managedEnvironmentId:env.id configuration:{activeRevisionsMode:'Single' secrets:[{name:'database-url' keyVaultUrl:databaseSecretUri identity:identity.id}]} template:{containers:[{name:'worker' image:backendImage command:['python','worker.py'] env:[{name:'APP_ENVIRONMENT' value:'production'},{name:'AUTH_MODE' value:'entra_id'},{name:'ENTRA_TENANT_ID' value:entraTenantId},{name:'ENTRA_AUDIENCE' value:entraAudience},{name:'DATABASE_URL' secretRef:'database-url'},{name:'AZURE_AUTH_MODE' value:'managed_identity'},{name:'AZURE_MANAGED_IDENTITY_CLIENT_ID' value:identity.properties.clientId},{name:'ALLOW_REAL_UPGRADES' value:string(allowRealUpgrades)},{name:'APPROVAL_TTL_MINUTES' value:string(approvalTtlMinutes)},{name:'AI_ADVISOR_ENABLED' value:string(aiAdvisorEnabled)},{name:'AZURE_OPENAI_ENDPOINT' value:azureOpenAIEndpoint},{name:'AZURE_OPENAI_DEPLOYMENT' value:azureOpenAIDeployment},{name:'AZURE_OPENAI_API_VERSION' value:azureOpenAIApiVersion}] resources:{cpu:json('2.0') memory:'4Gi'}}] scale:{minReplicas:1 maxReplicas:1}}}}
output apiUrl string='https://${api.properties.configuration.ingress.fqdn}'
output uiUrl string='https://${ui.properties.configuration.ingress.fqdn}'
