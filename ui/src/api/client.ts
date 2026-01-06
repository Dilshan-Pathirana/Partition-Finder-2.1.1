import type {
  FolderBrowseResponse,
  FolderPreviewRequest,
  FolderPreviewResponse,
  JobRequest,
  JobResultsResponse,
  JobStatusResponse,
  JobSubmitResponse,
  StopJobResponse,
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

export async function stopJob(jobId: string): Promise<StopJobResponse> {
  return http<StopJobResponse>(`/jobs/${encodeURIComponent(jobId)}/stop`, { method: 'POST' })
}

export function jobLogWebSocketUrl(jobId: string): string {
  const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'

  // Development: Vite dev server proxies only HTTP. For WebSocket, connect directly to the API.
  // Production: UI + API are served from one port, so use same-origin /api.
  if (import.meta.env.DEV) {
    // Use the current hostname to avoid localhost/IPv6 resolution issues on Windows.
    let host = window.location.hostname || '127.0.0.1'
    if (host === 'localhost') host = '127.0.0.1'
    return `${proto}://${host}:8000/jobs/${encodeURIComponent(jobId)}/stream`
  }

  return `${proto}://${window.location.host}${API_PREFIX}/jobs/${encodeURIComponent(jobId)}/stream`
}

export async function previewFolder(req: FolderPreviewRequest): Promise<FolderPreviewResponse> {
  return http<FolderPreviewResponse>('/folders/preview', {
    method: 'POST',
    body: JSON.stringify(req),
  })
}

export async function browseFolder(): Promise<FolderBrowseResponse> {
  return http<FolderBrowseResponse>('/folders/browse')
}
