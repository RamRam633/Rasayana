// Typed client for the Rasayana FastAPI knowledge graph (proxied at /api).

const j = (r: Response) => {
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
  return r.json();
};

export interface Stats {
  plants: number; phytochemicals: number; phytochemicals_keyed: number;
  targets: number; therapeutic_uses: number; sources: number; edges: number;
}
export interface PlantLite {
  id: string; accepted_name: string; family: string | null;
  also_known_as?: (string | null)[]; chems?: number;
}
export interface NameRow { name: string; name_kind: string; language_code: string | null; transliteration: string | null; }
export interface ChemRow { id: string; preferred_name: string | null; inchikey: string | null; pubchem_cid: number | null; evidence: string; }
export interface UseRow { id: string; preferred_label: string; category: string; icd11_code: string | null; evidence: string; sources: string; }
export interface TargetRow { id: string; gene_symbol: string | null; protein_name: string | null; via_chemicals: number; }
export interface PlantDetail {
  id: string; accepted_name: string; genus: string | null; family: string | null;
  resolution_confidence: number | null; is_curated: boolean;
  names: NameRow[]; phytochemicals: ChemRow[]; uses: UseRow[]; targets: TargetRow[];
  chem_count: number; use_count: number; target_count: number;
  related: { id: string; accepted_name: string; family: string | null; chems: number }[];
}
export interface SourceRow { short_code: string; name: string; url?: string; license?: string; is_redistributable?: boolean; provides?: string[]; phase?: string | number; }

export const api = {
  stats: () => fetch('/api/stats').then(j) as Promise<Stats>,
  featured: () => fetch('/api/featured').then(j) as Promise<PlantLite[]>,
  search: (q: string) => fetch(`/api/plants?q=${encodeURIComponent(q)}&limit=36`).then(j) as Promise<PlantLite[]>,
  plant: (id: string) => fetch(`/api/plants/${id}/detail`).then(j) as Promise<PlantDetail>,
  sources: () => fetch('/api/sources').then(j) as Promise<SourceRow[]>,

  conditions: (q = '', traditional = true, page = 1) =>
    fetch(`/api/conditions?q=${encodeURIComponent(q)}&traditional=${traditional}&page=${page}`).then(j) as Promise<Page<ConditionRow>>,
  condition: (id: string) => fetch(`/api/conditions/${id}`).then(j) as Promise<ConditionDetail>,
  families: (q = '', page = 1) =>
    fetch(`/api/families?q=${encodeURIComponent(q)}&page=${page}`).then(j) as Promise<Page<FamilyRow>>,
  family: (name: string, page = 1) =>
    fetch(`/api/families/${encodeURIComponent(name)}?page=${page}`).then(j) as Promise<FamilyDetail>,
  molecules: (q = '', page = 1) =>
    fetch(`/api/molecules?q=${encodeURIComponent(q)}&page=${page}`).then(j) as Promise<Page<MoleculeRow>>,
  chemical: (id: string) => fetch(`/api/chemicals/${id}`).then(j) as Promise<ChemicalDetail>,
  targets: (q = '', page = 1) =>
    fetch(`/api/targets?q=${encodeURIComponent(q)}&page=${page}`).then(j) as Promise<Page<TargetListRow>>,
  target: (id: string) => fetch(`/api/targets/${id}`).then(j) as Promise<TargetDetail>,
  plantIndex: (q = '', family = '', letter = '', page = 1) =>
    fetch(`/api/plant-index?q=${encodeURIComponent(q)}&family=${encodeURIComponent(family)}&letter=${encodeURIComponent(letter)}&page=${page}`).then(j) as Promise<Page<PlantIndexRow>>,
  searchAll: (q: string) => fetch(`/api/search-all?q=${encodeURIComponent(q)}`).then(j) as Promise<SearchAll>,
  references: () => fetch('/api/references').then(j) as Promise<RefRow[]>,
  commonAilments: () => fetch('/api/common-ailments').then(j) as Promise<Ailment[]>,
  plantOverview: (id: string) => fetch(`/api/plants/${id}/overview`).then(j) as Promise<Overview>,
};

export interface Ailment { label: string; id: string; matched: string; plants: number; }
export interface Overview { found: boolean; title?: string; extract?: string; thumbnail?: string | null; url?: string | null; }

// ── library browse types ─────────────────────────────────────────────────
export interface Page<T> { items: T[]; total: number; page: number; page_size: number; }
export interface ConditionRow { id: string; preferred_label: string; category: string; icd11_code: string | null; plants: number; }
export interface ConditionDetail {
  id: string; preferred_label: string; category: string; icd11_code: string | null;
  plants: { id: string; accepted_name: string; family: string | null; evidence: string; sources: string }[];
  plant_count: number;
}
export interface FamilyRow { family: string; plants: number; }
export interface PlantIndexRow { id: string; accepted_name: string; family: string | null; chems: number; }
export interface FamilyDetail { family: string; items: PlantIndexRow[]; total: number; page: number; page_size: number; }
export interface MoleculeRow { id: string; preferred_name: string | null; inchikey: string | null; pubchem_cid: number | null; chembl_id: string | null; molecular_formula: string | null; }
export interface ChemicalDetail {
  id: string; preferred_name: string | null; inchikey: string | null; pubchem_cid: number | null;
  chembl_id: string | null; smiles: string | null; molecular_formula: string | null; molecular_weight: number | null;
  plants: { id: string; accepted_name: string; family: string | null }[];
  targets: { gene_symbol: string | null; protein_name: string | null; activity_type: string | null; activity_value: string | null; activity_unit: string | null }[];
}
export interface TargetListRow { id: string; gene_symbol: string | null; protein_name: string | null; uniprot_id: string | null; target_class: string | null; chems: number; }
export interface TargetDetail {
  id: string; gene_symbol: string | null; protein_name: string | null; uniprot_id: string | null;
  chembl_id: string | null; target_class: string | null;
  chemicals: { id: string; preferred_name: string | null; inchikey: string | null; activity_type: string | null; activity_value: string | null; activity_unit: string | null }[];
  plants: { id: string; accepted_name: string; family: string | null }[];
  chem_count: number;
}
export interface RefRow { short_code: string; name: string; url: string | null; license: string | null; is_redistributable: boolean; edges: number; }
export interface SearchHit { id: string; label: string | null; sub: string | null; }
export interface SearchAll { plants: SearchHit[]; molecules: SearchHit[]; conditions: SearchHit[]; targets: SearchHit[]; }

export interface ChatEvent {
  type: 'meta' | 'sql' | 'delta' | 'done' | 'error';
  provider?: string; text?: string; sql?: string; rows?: any[]; row_count?: number; message?: string;
}

export async function streamChat(question: string, onEvent: (e: ChatEvent) => void): Promise<void> {
  const res = await fetch('/api/chat', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  });
  if (!res.body) { onEvent({ type: 'error', message: 'No response stream.' }); return; }
  const reader = res.body.getReader();
  const dec = new TextDecoder();
  let buf = '';
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    let i;
    while ((i = buf.indexOf('\n\n')) >= 0) {
      const frame = buf.slice(0, i); buf = buf.slice(i + 2);
      const line = frame.split('\n').find((l) => l.startsWith('data:'));
      if (!line) continue;
      try { onEvent(JSON.parse(line.slice(5).trim())); } catch { /* skip */ }
    }
  }
}
