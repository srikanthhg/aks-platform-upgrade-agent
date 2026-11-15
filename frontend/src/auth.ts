import { Configuration, PublicClientApplication } from '@azure/msal-browser';

const runtimeConfig = window.__APP_CONFIG__;
const tenantId = runtimeConfig?.tenantId ?? import.meta.env.VITE_ENTRA_TENANT_ID;
const clientId = runtimeConfig?.clientId ?? import.meta.env.VITE_ENTRA_CLIENT_ID;
export const apiScope = runtimeConfig?.apiScope ?? import.meta.env.VITE_API_SCOPE;

if (!tenantId || !clientId || !apiScope) {
  throw new Error(
    'Missing frontend configuration. Set ENTRA_TENANT_ID, ENTRA_CLIENT_ID and API_SCOPE in the Azure Container App environment.',
  );
}

export const msalConfig: Configuration = {
  auth: {
    clientId,
    authority: `https://login.microsoftonline.com/${tenantId}`,
    redirectUri: window.location.origin,
    postLogoutRedirectUri: window.location.origin,
  },
  cache: {
    cacheLocation: 'sessionStorage',
  },
};

export const msalInstance = new PublicClientApplication(msalConfig);
