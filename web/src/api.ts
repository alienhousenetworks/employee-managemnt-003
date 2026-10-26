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
