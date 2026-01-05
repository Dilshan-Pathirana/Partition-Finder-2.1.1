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
  args: string[]
  copy_input: boolean
  overrides: Record<string, string>
}
