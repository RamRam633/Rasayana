import BrowseList from '../components/BrowseList';
import { api, type FamilyRow } from '../lib/api';
import type { Column } from '../components/DataTable';

const columns: Column<FamilyRow>[] = [
  { key: 'family', header: 'Botanical family', render: (r) => r.family, sortValue: (r) => r.family.toLowerCase(), width: '65%' },
  { key: 'plants', header: 'Plants', render: (r) => <span className="dt-num">{r.plants.toLocaleString()}</span>, sortValue: (r) => r.plants, align: 'right' },
];

export default function Families() {
  return (
    <BrowseList
      kicker="Library · Browse"
      title="Botanical families"
      lede="400 plant families. Click a family to browse its species."
      crumbs={[{ label: 'Library', to: '/library' }, { label: 'Families' }]}
      fetchPage={(q, p) => api.families(q, p)}
      columns={columns}
      rowTo={(r) => `/family/${encodeURIComponent(r.family)}`}
      searchPlaceholder="Filter families — Asteraceae, Lamiaceae…"
    />
  );
}
