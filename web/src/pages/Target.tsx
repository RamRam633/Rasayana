import { useEffect, useState } from 'react';
import { api, type TargetDetail } from '../lib/api';
import { DataTable, type Column } from '../components/DataTable';
import { Breadcrumbs } from '../components/nav';
import { Loading } from '../components/ui';
import { navigate } from '../lib/router';
import { prettyChem } from '../lib/format';

export default function Target({ id }: { id: string }) {
  const [d, setD] = useState<TargetDetail | null>(null);
  const [err, setErr] = useState(false);
  useEffect(() => { setD(null); setErr(false); api.target(id).then(setD).catch(() => setErr(true)); }, [id]);

  if (err) return <div className="page"><p>Target not found. <a onClick={() => navigate('/targets')}>Back</a></p></div>;
  if (!d) return <div className="page"><Loading /></div>;

  const chemCols: Column<TargetDetail['chemicals'][number]>[] = [
    { key: 'm', header: 'Molecule', render: (r) => prettyChem(r.preferred_name), sortValue: (r) => (r.preferred_name || '').toLowerCase(), width: '40%' },
    { key: 'k', header: 'InChIKey', render: (r) => <span className="dt-mono faint">{r.inchikey || '—'}</span> },
    { key: 'a', header: 'Activity', render: (r) => <span className="dt-mono faint">{[r.activity_type, r.activity_value, r.activity_unit].filter(Boolean).join(' ') || '—'}</span> },
  ];
  const plantCols: Column<TargetDetail['plants'][number]>[] = [
    { key: 'p', header: 'Plant', render: (r) => <span className="dt-sci">{r.accepted_name}</span>, sortValue: (r) => r.accepted_name.toLowerCase(), width: '55%' },
    { key: 'f', header: 'Family', render: (r) => r.family || '—' },
  ];

  return (
    <div className="page fade-in">
      <Breadcrumbs items={[{ label: 'Library', to: '/library' }, { label: 'Targets', to: '/targets' }, { label: d.gene_symbol || 'Target' }]} />
      <div className="detail-head">
        <h1 style={{ margin: '0.2rem 0', color: 'var(--violet)' }}>{d.gene_symbol || '—'}</h1>
        {d.protein_name && <div className="fam">{d.protein_name}</div>}
      </div>
      <div className="idchips">
        {d.target_class && <span className="idchip"><b>class</b>{d.target_class}</span>}
        {d.uniprot_id && <span className="idchip"><b>UniProt</b><a href={`https://www.uniprot.org/uniprotkb/${d.uniprot_id}/entry`} target="_blank" rel="noreferrer">{d.uniprot_id} ↗</a></span>}
        {d.chembl_id && <span className="idchip"><b>ChEMBL</b><a href={`https://www.ebi.ac.uk/chembl/target_report_card/${d.chembl_id}/`} target="_blank" rel="noreferrer">{d.chembl_id} ↗</a></span>}
        <span className="idchip"><b>molecules</b>{d.chem_count.toLocaleString()}</span>
      </div>
      <div className="sec-head"><span className="kick">hit by</span><h2>Molecules ({d.chem_count.toLocaleString()})</h2></div>
      <DataTable columns={chemCols} rows={d.chemicals} onRowClick={(r) => navigate(`/molecule/${r.id}`)} />
      <div className="sec-head"><span className="kick">reached through them</span><h2>Plants ({d.plants.length}{d.plants.length >= 80 ? '+' : ''})</h2></div>
      <DataTable columns={plantCols} rows={d.plants} onRowClick={(r) => navigate(`/plant/${r.id}`)} />
    </div>
  );
}
