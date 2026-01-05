import type {
  JobRequest,
  JobResultsResponse,
  JobStatusResponse,
  JobSubmitResponse,
} from './types'

const API_PREFIX = '/api'

async function http<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_PREFIX}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
  })

  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`
    try {
      const body = (await res.json()) as { detail?: string }
      if (body.detail) detail = body.detail
    } catch {
      // ignore
    }
    throw new Error(detail)
  }

  return (await res.json()) as T
}

export async function submitJob(req: JobRequest): Promise<JobSubmitResponse> {
  return http<JobSubmitResponse>('/jobs', {
    method: 'POST',
    body: JSON.stringify(req),
  })
}

export async function listJobs(limit = 50): Promise<JobStatusResponse[]> {
  const qs = new URLSearchParams({ limit: String(limit) })
  return http<JobStatusResponse[]>(`/jobs?${qs.toString()}`)
}

export async function getJobStatus(jobId: string): Promise<JobStatusResponse> {
  return http<JobStatusResponse>(`/jobs/${encodeURIComponent(jobId)}/status`)
}

export async function getJobResults(jobId: string): Promise<JobResultsResponse> {
  return http<JobResultsResponse>(`/jobs/${encodeURIComponent(jobId)}/results`)
}

export async function deleteJob(jobId: string): Promise<void> {
  await http(`/jobs/${encodeURIComponent(jobId)}`, { method: 'DELETE' })
}

export function jobLogWebSocketUrl(jobId: string): string {
  const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
  // Vite dev server proxies only HTTP. For WebSocket, we connect directly to the API.
  return `${proto}://localhost:8000/jobs/${encodeURIComponent(jobId)}/stream`
}
