export interface Charset {
  subset: string
  range: string
  length?: number
}

export interface BestSchemeHeader {
  schemeName?: string
  lnl?: number
  aic?: number
  aicc?: number
  bic?: number
  parameters?: number
  sites?: number
  subsets?: number
}

export interface SubsetModel {
  subset: string
  model: string
}

function parseRangeLength(range: string): number | undefined {
  // Handles simple ranges like "1-407" and comma-separated ranges.
  // This is intentionally minimal; it supports the most common PartitionFinder outputs.
  const parts = range
    .replace(/;/g, '')
    .split(',')
    .map((p) => p.trim())
    .filter(Boolean)

  let total = 0
  let any = false

  for (const p of parts) {
    const m = /^([0-9]+)\s*-\s*([0-9]+)$/.exec(p)
    if (m) {
      const a = Number(m[1])
      const b = Number(m[2])
      if (Number.isFinite(a) && Number.isFinite(b) && b >= a) {
        total += b - a + 1
        any = true
      }
      continue
    }
    // Odd-searches can emit explicit site lists: "1 2 5 10" etc.
    const nums = p
      .split(/\s+/)
      .map((x) => Number(x))
      .filter((n) => Number.isFinite(n))
    if (nums.length > 0) {
      total += nums.length
      any = true
    }
  }

  return any ? total : undefined
}

export function extractNexusSetsBlock(bestSchemeTxt: string): string | null {
  const start = bestSchemeTxt.indexOf('begin sets;')
  if (start === -1) return null
  const end = bestSchemeTxt.indexOf('end;', start)
  if (end === -1) return null
  return bestSchemeTxt.slice(start, end + 'end;'.length)
}

export function parseBestSchemeHeader(bestSchemeTxt: string): BestSchemeHeader {
  const header: BestSchemeHeader = {}

  function findNumber(label: string): number | undefined {
    const re = new RegExp(`^\\s*${label}\\s*:?\\s*(.+?)\\s*$`, 'im')
    const m = re.exec(bestSchemeTxt)
    if (!m) return undefined
    const n = Number(m[1])
    return Number.isFinite(n) ? n : undefined
  }

  const nameMatch = /^\s*Scheme Name\s*:?\s*(.+?)\s*$/im.exec(bestSchemeTxt)
  if (nameMatch) header.schemeName = nameMatch[1]

  header.lnl = findNumber('Scheme lnL')
  header.aic = findNumber('Scheme AIC')
  header.aicc = findNumber('Scheme AICc')
  header.bic = findNumber('Scheme BIC')
  header.parameters = findNumber('Number of params')
  header.sites = findNumber('Number of sites')
  header.subsets = findNumber('Number of subsets')

  return header
}

export function parseSubsetModelsFromIQtree(bestSchemeTxt: string): SubsetModel[] {
  // We use the IQtree section because it encodes the model for each subset:
  // charpartition PartitionFinder = GTR+G:Subset1, HKY+I:Subset2;
  const m = /^\s*charpartition\s+PartitionFinder\s*=\s*(.+?)\s*;\s*$/im.exec(bestSchemeTxt)
  if (!m) return []
  const rhs = m[1]
  const entries = rhs
    .split(',')
    .map((e) => e.trim())
    .filter(Boolean)

  const out: SubsetModel[] = []
  for (const e of entries) {
    const parts = e.split(':').map((p) => p.trim())
    if (parts.length !== 2) continue
    const [model, subset] = parts
    if (!model || !subset) continue
    out.push({ model, subset })
  }
  return out
}

export function parseCharsetsFromNexusBlock(block: string): Charset[] {
  const lines = block.split(/\r?\n/)
  const charsets: Charset[] = []

  for (const line of lines) {
    const m = /^\s*charset\s+(Subset\S+)\s*=\s*(.+?);\s*$/i.exec(line)
    if (!m) continue
    const subset = m[1]
    const range = m[2]
    charsets.push({ subset, range, length: parseRangeLength(range) })
  }

  return charsets
}

export interface SchemeRow {
  name: string
  sites: number
  lnl: number
  parameters: number
  subsets: number
  aic: number
  aicc: number
  bic: number
}

export function parseSchemeDataCsv(csv: string): SchemeRow[] {
  const lines = csv.split(/\r?\n/).filter((l) => l.trim().length > 0)
  if (lines.length < 2) return []

  // Expect: name,sites,lnL,parameters,subsets,aic,aicc,bic
  const rows: SchemeRow[] = []
  for (const line of lines.slice(1)) {
    const parts = line.split(',')
    if (parts.length < 8) continue
    const [name, sites, lnl, parameters, subsets, aic, aicc, bic] = parts
    rows.push({
      name,
      sites: Number(sites),
      lnl: Number(lnl),
      parameters: Number(parameters),
      subsets: Number(subsets),
      aic: Number(aic),
      aicc: Number(aicc),
      bic: Number(bic),
    })
  }

  return rows.filter((r) => Number.isFinite(r.aic) && Number.isFinite(r.bic))
}

export function downloadText(filename: string, content: string): void {
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}
