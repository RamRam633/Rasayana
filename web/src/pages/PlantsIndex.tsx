import BrowseList from '../components/BrowseList';
import { api, type PlantIndexRow } from '../lib/api';
import type { Column } from '../components/DataTable';

const columns: Column<PlantIndexRow>[] = [
  { key: 'name', header: 'Plant', render: (r) => <span className="dt-sci">{r.accepted_name}</span>, sortValue: (r) => r.accepted_name.toLowerCase(), width: '45%' },
  { key: 'family', header: 'Family', render: (r) => r.family || ', ' },
  { key: 'chems', header: 'Phytochemicals', render: (r) => <span className="dt-num">{r.chems.toLocaleString()}</span>, sortValue: (r) => r.chems, align: 'right' },
];

export default function PlantsIndex() {
  return (
    <BrowseList
      kicker="Library · Browse"
      title="All plants"
      lede="The full materia medica, 9,291 species. Filter by name, or open one to see its phytochemistry and uses."
      crumbs={[{ label: 'Library', to: '/library' }, { label: 'Plants' }]}
      fetchPage={(q, p) => api.plantIndex(q, '', '', p)}
      columns={columns}
      rowTo={(r) => `/plant/${r.id}`}
      searchPlaceholder="Filter plants, Withania, Curcuma…"
    />
  );
}
