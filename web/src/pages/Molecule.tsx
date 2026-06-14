import { useEffect, useState } from 'react';
import { api, type ChemicalDetail } from '../lib/api';
import { DataTable, type Column } from '../components/DataTable';
import { Breadcrumbs } from '../components/nav';
import { Loading } from '../components/ui';
import { navigate } from '../lib/router';
import { prettyChem } from '../lib/format';

export default function Molecule({ id }: { id: string }) {
  const [d, setD] = useState<ChemicalDetail | null>(null);
  const [err, setErr] = useState(false);
  useEffect(() => { setD(null); setErr(false); api.chemical(id).then(setD).catch(() => setErr(true)); }, [id]);

  if (err) return <div className="page"><p>Molecule not found. <a onClick={() => navigate('/molecules')}>Back</a></p></div>;
  if (!d) return <div className="page"><Loading /></div>;

  const name = prettyChem(d.preferred_name);
  const act = (r: { activity_type: string | null; activity_value: string | null; activity_unit: string | null }) =>
    [r.activity_type, r.activity_value, r.activity_unit].filter(Boolean).join(' ') || ', ';
  const plantCols: Column<ChemicalDetail['plants'][number]>[] = [
    { key: 'p', header: 'Plant', render: (r) => <span className="dt-sci">{r.accepted_name}</span>, sortValue: (r) => r.accepted_name.toLowerCase(), width: '55%' },
    { key: 'f', header: 'Family', render: (r) => r.family || ', ' },
  ];
  const tgtCols: Column<ChemicalDetail['targets'][number]>[] = [
    { key: 'g', header: 'Gene', render: (r) => <span className="dt-mono" style={{ color: 'var(--violet)', fontWeight: 600 }}>{r.gene_symbol || ', '}</span>, width: '120px' },
    { key: 'pr', header: 'Protein', render: (r) => r.protein_name || ', ' },
    { key: 'a', header: 'Activity', render: (r) => <span className="dt-mono faint">{act(r)}</span> },
  ];

  return (
    <div className="page fade-in">
      <Breadcrumbs items={[{ label: 'Library', to: '/library' }, { label: 'Molecules', to: '/molecules' }, { label: name }]} />
      <div className="detail-head"><h1 style={{ margin: '0.2rem 0' }}>{name}</h1></div>
      <div className="idchips">
        {d.inchikey && <span className="idchip"><b>InChIKey</b>{d.inchikey}</span>}
        {d.molecular_formula && <span className="idchip"><b>formula</b>{d.molecular_formula}</span>}
        {d.molecular_weight != null && <span className="idchip"><b>MW</b>{Math.round(d.molecular_weight * 100) / 100}</span>}
        {d.pubchem_cid && <span className="idchip"><b>PubChem</b><a href={`https://pubchem.ncbi.nlm.nih.gov/compound/${d.pubchem_cid}`} target="_blank" rel="noreferrer">{d.pubchem_cid} ↗</a></span>}
        {d.chembl_id && <span className="idchip"><b>ChEMBL</b><a href={`https://www.ebi.ac.uk/chembl/compound_report_card/${d.chembl_id}/`} target="_blank" rel="noreferrer">{d.chembl_id} ↗</a></span>}
      </div>
      <div className="sec-head"><span className="kick">contained in</span><h2>Plants ({d.plants.length}{d.plants.length >= 40 ? '+' : ''})</h2></div>
      <DataTable columns={plantCols} rows={d.plants} onRowClick={(r) => navigate(`/plant/${r.id}`)} empty="No plants recorded." />
      <div className="sec-head"><span className="kick">acts on</span><h2>Targets ({d.targets.length}{d.targets.length >= 40 ? '+' : ''})</h2></div>
      <DataTable columns={tgtCols} rows={d.targets} empty="No mapped molecular targets." />
    </div>
  );
}
