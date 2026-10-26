const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';
export type Organization = { id: string; name: string; role: string; department: string };
export type CurrentUser = { id: string; username: string; email: string; organizations: Organization[] };
export async function apiGet<T>(path: string, token: string, organizationId?: string): Promise<T> {
  const headers: Record<string,string> = { Authorization: `Bearer ${token}`, Accept: 'application/json' };
  if (organizationId) headers['X-Organization-ID'] = organizationId;
  const response = await fetch(`${API_BASE}${path}`, { headers });
  if (!response.ok) throw new Error(response.status === 403 ? 'You do not have permission to access this resource.' : `API request failed (${response.status})`);
  return response.json() as Promise<T>;
}

export async function apiPost<T>(path: string, body: unknown, token?: string, organizationId?: string): Promise<T> {
  const headers: Record<string,string> = { 'Content-Type': 'application/json', Accept: 'application/json' };
  if (token) headers.Authorization = `Bearer ${token}`;
  if (organizationId) headers['X-Organization-ID'] = organizationId;
  const response = await fetch(`${API_BASE}${path}`, { method: 'POST', headers, body: JSON.stringify(body) });
  if (!response.ok) { const data = await response.json().catch(() => ({})); throw new Error(data.detail ?? `API request failed (${response.status})`); }
  return response.json() as Promise<T>;
}
