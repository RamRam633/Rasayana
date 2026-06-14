import { useEffect, useState } from 'react';
import { api, type ConditionDetail } from '../lib/api';
import { DataTable, type Column } from '../components/DataTable';
import { Breadcrumbs, Sources } from '../components/nav';
import { Loading, Disclaimer, EvidenceBadge } from '../components/ui';
import { navigate } from '../lib/router';

type Row = ConditionDetail['plants'][number];

export default function Condition({ id }: { id: string }) {
  const [d, setD] = useState<ConditionDetail | null>(null);
  const [err, setErr] = useState(false);
  useEffect(() => { setD(null); setErr(false); api.condition(id).then(setD).catch(() => setErr(true)); }, [id]);

  if (err) return <div className="page"><p>Condition not found. <a onClick={() => navigate('/conditions')}>Back</a></p></div>;
  if (!d) return <div className="page"><Loading /></div>;

  const columns: Column<Row>[] = [
    { key: 'plant', header: 'Plant', render: (r) => <span className="dt-sci">{r.accepted_name}</span>, sortValue: (r) => r.accepted_name.toLowerCase(), width: '42%' },
    { key: 'family', header: 'Family', render: (r) => r.family || ', ' },
    { key: 'evidence', header: 'Evidence', render: (r) => <EvidenceBadge evidence={r.evidence} />, sortValue: (r) => r.evidence },
    { key: 'src', header: 'Source', render: (r) => <Sources codes={r.sources} /> },
  ];

  return (
    <div className="page fade-in">
      <Breadcrumbs items={[{ label: 'Library', to: '/library' }, { label: 'Conditions', to: '/conditions' }, { label: d.preferred_label }]} />
      <div className="detail-head">
        <h1 style={{ margin: '0.2rem 0' }}>{d.preferred_label}</h1>
        <div className="idchips">
          {d.icd11_code && <span className="idchip"><b>ICD-11</b>{d.icd11_code}</span>}
          <span className="idchip"><b>category</b>{d.category}</span>
          <span className="idchip"><b>plants</b>{d.plant_count.toLocaleString()}</span>
        </div>
      </div>
      <p className="muted" style={{ maxWidth: '70ch' }}>Plants linked to this condition, traditional/ethnobotanical evidence first. Click any plant to follow the thread.</p>
      <DataTable columns={columns} rows={d.plants} onRowClick={(r) => navigate(`/plant/${r.id}`)} />
      <Disclaimer />
    </div>
  );
}
