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
export interface UseRow { preferred_label: string; category: string; icd11_code: string | null; evidence: string; sources: string; }
export interface TargetRow { gene_symbol: string | null; protein_name: string | null; via_chemicals: number; }
export interface PlantDetail {
  id: string; accepted_name: string; genus: string | null; family: string | null;
  resolution_confidence: number | null; is_curated: boolean;
  names: NameRow[]; phytochemicals: ChemRow[]; uses: UseRow[]; targets: TargetRow[];
  chem_count: number; use_count: number; target_count: number;
}
export interface SourceRow { short_code: string; name: string; url?: string; license?: string; is_redistributable?: boolean; provides?: string[]; phase?: string | number; }

export const api = {
  stats: () => fetch('/api/stats').then(j) as Promise<Stats>,
  featured: () => fetch('/api/featured').then(j) as Promise<PlantLite[]>,
  search: (q: string) => fetch(`/api/plants?q=${encodeURIComponent(q)}&limit=36`).then(j) as Promise<PlantLite[]>,
  plant: (id: string) => fetch(`/api/plants/${id}/detail`).then(j) as Promise<PlantDetail>,
  sources: () => fetch('/api/sources').then(j) as Promise<SourceRow[]>,
};

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
