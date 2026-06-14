import { useEffect, useState } from 'react';
import { api, type FamilyDetail } from '../lib/api';
import { DataTable, Pagination, type Column } from '../components/DataTable';
import { Breadcrumbs } from '../components/nav';
import { Loading } from '../components/ui';
import { navigate } from '../lib/router';

export default function Family({ name }: { name: string }) {
  const [page, setPage] = useState(1);
  const [d, setD] = useState<FamilyDetail | null>(null);
  useEffect(() => { setD(null); api.family(name, page).then(setD).catch(() => {}); }, [name, page]);

  const columns: Column<FamilyDetail['items'][number]>[] = [
    { key: 'p', header: 'Plant', render: (r) => <span className="dt-sci">{r.accepted_name}</span>, sortValue: (r) => r.accepted_name.toLowerCase(), width: '55%' },
    { key: 'c', header: 'Phytochemicals', render: (r) => <span className="dt-num">{r.chems.toLocaleString()}</span>, sortValue: (r) => r.chems, align: 'right' },
  ];

  return (
    <div className="page fade-in">
      <Breadcrumbs items={[{ label: 'Library', to: '/library' }, { label: 'Families', to: '/families' }, { label: name }]} />
      <div className="eyebrow">Botanical family</div>
      <h1 style={{ margin: '0.2rem 0 0.6rem' }}>{name}</h1>
      {!d ? <Loading /> : (
        <>
          <p className="muted">{d.total.toLocaleString()} species in this family.</p>
          <DataTable columns={columns} rows={d.items} onRowClick={(r) => navigate(`/plant/${r.id}`)} />
          <Pagination page={d.page} total={d.total} pageSize={d.page_size} onPage={setPage} />
        </>
      )}
    </div>
  );
}
