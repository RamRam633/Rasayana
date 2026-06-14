import BrowseList from '../components/BrowseList';
import { api, type MoleculeRow } from '../lib/api';
import type { Column } from '../components/DataTable';

const columns: Column<MoleculeRow>[] = [
  { key: 'name', header: 'Molecule', render: (r) => r.preferred_name, sortValue: (r) => (r.preferred_name || '').toLowerCase(), width: '38%' },
  { key: 'inchikey', header: 'InChIKey', render: (r) => <span className="dt-mono faint">{r.inchikey || '—'}</span> },
  { key: 'cid', header: 'PubChem', render: (r) => r.pubchem_cid ? <span className="dt-mono">{r.pubchem_cid}</span> : <span className="faint">—</span>, align: 'right' },
  { key: 'formula', header: 'Formula', render: (r) => <span className="dt-mono">{r.molecular_formula || '—'}</span> },
];

export default function Molecules() {
  return (
    <BrowseList
      kicker="Library · Browse"
      title="Molecules"
      lede="43,000+ named phytochemicals. Click one to see which plants carry it and which proteins it acts on."
      crumbs={[{ label: 'Library', to: '/library' }, { label: 'Molecules' }]}
      fetchPage={(q, p) => api.molecules(q, p)}
      columns={columns}
      rowTo={(r) => `/molecule/${r.id}`}
      searchPlaceholder="Filter molecules — curcumin, quercetin, withaferin…"
    />
  );
}
