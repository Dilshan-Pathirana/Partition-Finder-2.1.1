export type JobState = 'queued' | 'running' | 'succeeded' | 'failed'

export interface JobSubmitResponse {
  id: string
}

export interface JobStatusResponse {
  id: string
  state: JobState
  created_at: string
  updated_at: string
  datatype?: string
  input_folder?: string
  exit_code?: number | null
  error?: string | null
}

export interface StopJobResponse {
  status: string
  job_id: string
}

export interface JobResultsResponse {
  id: string
  state: JobState
  best_scheme_txt?: string | null
  scheme_data_csv?: string | null
  analysis_path?: string | null
}

export interface JobRequest {
  folder: string
  datatype: 'DNA' | 'protein' | 'morphology'
  cpus?: number
  args: string[]
  copy_input: boolean
  overrides: Record<string, string>
}

export interface DataBlock {
  name: string
  range: string
  length?: number | null
}

export interface FolderPreviewRequest {
  folder: string
}

export interface FolderPreviewResponse {
  folder: string
  cfg_file: string
  alignment?: string | null
  data_blocks: DataBlock[]
}
