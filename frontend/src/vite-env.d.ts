/// <reference types="vite/client" />

interface Window {
  __APP_CONFIG__?: {
    tenantId: string;
    clientId: string;
    apiScope: string;
  };
}
