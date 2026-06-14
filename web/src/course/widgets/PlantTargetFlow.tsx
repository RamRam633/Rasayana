import { useEffect, useState } from 'react';
import { api } from '../../lib/api';
import { isInchiKey } from '../../lib/format';
import { navigate } from '../../lib/router';

const PLANTS = [
  { n: 'Curcuma longa', l: 'Turmeric' },
  { n: 'Withania somnifera', l: 'Ashwagandha' },
  { n: 'Zingiber officinale', l: 'Ginger' },
  { n: 'Ocimum tenuiflorum', l: 'Tulsi' },
];

interface Chem { id: string; preferred_name: string | null; inchikey: string | null }
interface Tgt { gene_symbol: string | null; protein_name: string | null }

export default function PlantTargetFlow() {
  const [pi, setPi] = useState(0);
  const [pid, setPid] = useState('');
  const [chems, setChems] = useState<Chem[]>([]);
  const [mi, setMi] = useState(0);
  const [targets, setTargets] = useState<Tgt[]>([]);

  useEffect(() => {
    let live = true;
    (async () => {
      try {
        const r = await api.search(PLANTS[pi].n);
        const id = r[0]?.id;
        if (!id || !live) return;
        setPid(id);
        const d = await api.plant(id);
        const named = d.phytochemicals.filter((c) => c.preferred_name && !isInchiKey(c.preferred_name)).slice(0, 8);
        if (live) { setChems(named); setMi(0); }
      } catch { /* ignore */ }
    })();
    return () => { live = false; };
  }, [pi]);

  useEffect(() => {
    let live = true;
    const c = chems[mi];
    if (!c) { setTargets([]); return; }
    (async () => {
      try { const d = await api.chemical(c.id); if (live) setTargets(d.targets.slice(0, 8)); } catch { /* ignore */ }
    })();
    return () => { live = false; };
  }, [chems, mi]);

  return (
    <div>
      <div className="ptf-picker">
        {PLANTS.map((p, i) => <span key={p.n} className={`facet ${pi === i ? 'on' : ''}`} onClick={() => setPi(i)}>{p.l}</span>)}
      </div>
      <div className="ptf-cols">
        <div className="ptf-col">
          <h5>Plant</h5>
          <div className="ptf-node" style={{ borderColor: 'var(--herb)', fontFamily: 'var(--display)', fontStyle: 'italic' }}
            onClick={() => pid && navigate(`/plant/${pid}`)}>{PLANTS[pi].n}</div>
        </div>
        <div className="ptf-col">
          <h5>Molecule — pick one</h5>
          {chems.length === 0 ? <div className="faint" style={{ fontSize: '0.8rem' }}>loading…</div>
            : chems.map((c, i) => (
              <div key={c.id} className="ptf-node mol"
                style={i === mi ? { borderColor: 'var(--herb)', background: 'color-mix(in srgb,var(--herb) 8%,var(--panel-2))' } : undefined}
                onClick={() => setMi(i)}>{c.preferred_name}</div>
            ))}
        </div>
        <div className="ptf-col">
          <h5>Acts on — proteins</h5>
          {targets.length === 0 ? <div className="faint" style={{ fontSize: '0.8rem' }}>{chems.length ? 'no mapped targets' : ''}</div>
            : targets.map((t, i) => (
              <div key={i} className="ptf-node tgt">{t.gene_symbol} <span className="faint" style={{ fontFamily: 'var(--sans)' }}>{t.protein_name}</span></div>
            ))}
        </div>
      </div>
      <p className="faint" style={{ fontSize: '0.82rem', marginTop: '0.8rem' }}>
        Live from the knowledge graph — choose a plant, then a molecule, to see the proteins it acts on. Click the plant to open its full page.
      </p>
    </div>
  );
}
