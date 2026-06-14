import BrowseList from '../components/BrowseList';
import { api, type TargetListRow } from '../lib/api';
import type { Column } from '../components/DataTable';

const columns: Column<TargetListRow>[] = [
  { key: 'gene', header: 'Gene', render: (r) => <span className="dt-mono" style={{ color: 'var(--violet)', fontWeight: 600 }}>{r.gene_symbol || '—'}</span>, sortValue: (r) => (r.gene_symbol || '').toLowerCase(), width: '130px' },
  { key: 'protein', header: 'Protein', render: (r) => r.protein_name || '—', width: '46%' },
  { key: 'class', header: 'Class', render: (r) => <span className="faint">{r.target_class || '—'}</span> },
  { key: 'chems', header: 'Molecules', render: (r) => <span className="dt-num">{r.chems.toLocaleString()}</span>, sortValue: (r) => r.chems, align: 'right' },
];

export default function Targets() {
  return (
    <BrowseList
      kicker="Library · Browse"
      title="Protein targets"
      lede="The proteins plant molecules act on — reverse pharmacology. Click a target to see its molecules and the plants that reach it."
      crumbs={[{ label: 'Library', to: '/library' }, { label: 'Targets' }]}
      fetchPage={(q, p) => api.targets(q, p)}
      columns={columns}
      rowTo={(r) => `/target/${r.id}`}
      searchPlaceholder="Filter targets — COX-2, CYP3A4, tau…"
    />
  );
}
