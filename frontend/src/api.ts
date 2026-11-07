import { InteractionRequiredAuthError } from '@azure/msal-browser';
import { msalInstance, apiScope } from './auth';
import type { AuditEvent, StartPayload, WorkflowResponse } from './types';

const configuredBase = import.meta.env.VITE_API_BASE_URL as string | undefined;
if (!configuredBase) {
  throw new Error('VITE_API_BASE_URL is missing from the frontend build configuration.');
}
const base = configuredBase.replace(/\/$/, '');

async function token(): Promise<string> {
  const account = msalInstance.getActiveAccount() ?? msalInstance.getAllAccounts()[0];
  if (!account) throw new Error('No signed-in Entra account found. Sign out and sign in again.');

  try {
    const result = await msalInstance.acquireTokenSilent({ account, scopes: [apiScope] });
    return result.accessToken;
  } catch (error) {
    if (error instanceof InteractionRequiredAuthError) {
      const result = await msalInstance.acquireTokenPopup({ account, scopes: [apiScope] });
      return result.accessToken;
    }
    throw error;
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const accessToken = await token();
  const response = await fetch(`${base}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${accessToken}`,
      ...init.headers,
    },
  });
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`API request failed (${response.status}): ${body || response.statusText}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  start: (payload: StartPayload) => request<WorkflowResponse>('/api/v1/workflows', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),
  get: (id: string) => request<WorkflowResponse>(`/api/v1/workflows/${id}`),
  decide: (id: string, approved: boolean, comment: string) =>
    request<WorkflowResponse>(`/api/v1/workflows/${id}/${approved ? 'approve' : 'reject'}`, {
      method: 'POST',
      body: JSON.stringify({ comment }),
    }),
  audit: (limit = 50) => request<{ items: AuditEvent[] }>(`/api/v1/audit?limit=${limit}`),
};
