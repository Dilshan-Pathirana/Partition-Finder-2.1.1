export interface ConfigState {
  datatype: 'DNA' | 'protein' | 'morphology'
  modelsPreset: string
  criterion: 'aic' | 'aicc' | 'bic'
  search: string
  branchlengths: 'linked' | 'unlinked'
  cpus: number
}

export const defaultConfigState: ConfigState = {
  datatype: 'DNA',
  modelsPreset: 'all',
  criterion: 'aicc',
  search: 'greedy',
  branchlengths: 'linked',
  cpus: 1,
}
