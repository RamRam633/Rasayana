import { useState } from 'react';
import BrowseList from '../components/BrowseList';
import { api, type ConditionRow } from '../lib/api';
import type { Column } from '../components/DataTable';

export default function Conditions() {
  const [trad, setTrad] = useState(true);
  const columns: Column<ConditionRow>[] = [
    { key: 'label', header: 'Condition / use', render: (r) => r.preferred_label, sortValue: (r) => r.preferred_label.toLowerCase(), width: '50%' },
    { key: 'icd', header: 'ICD-11', render: (r) => <span className="dt-mono faint">{r.icd11_code || '—'}</span> },
    { key: 'plants', header: 'Plants', render: (r) => <span className="dt-num">{r.plants.toLocaleString()}</span>, sortValue: (r) => r.plants, align: 'right', width: '120px' },
  ];
  return (
    <BrowseList
      key={trad ? 't' : 'a'}
      kicker="Library · Browse"
      title="Conditions &amp; uses"
      lede="What plants are used for. Don't know what to ask? Start here — pick a condition to see the plants linked to it."
      crumbs={[{ label: 'Library', to: '/library' }, { label: 'Conditions' }]}
      fetchPage={(q, p) => api.conditions(q, trad, p)}
      columns={columns}
      rowTo={(r) => `/condition/${r.id}`}
      searchPlaceholder="Filter conditions — fever, cough, diabetes…"
      controls={
        <div className="facets">
          <span className={`facet ${trad ? 'on' : ''}`} onClick={() => setTrad(true)}>Traditional uses</span>
          <span className={`facet ${!trad ? 'on' : ''}`} onClick={() => setTrad(false)}>All (incl. researched)</span>
        </div>
      }
    />
  );
}
