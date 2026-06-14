import { useEffect, useState } from 'react';
import { api, type PlantDetail as PD } from '../lib/api';
import { Loading, Disclaimer, EvidenceBadge } from '../components/ui';
import { isInchiKey, isTraditional } from '../lib/format';
import { navigate } from '../lib/router';

export default function PlantDetail({ id }: { id: string }) {
  const [d, setD] = useState<PD | null>(null);
  const [err, setErr] = useState(false);
  useEffect(() => {
    setD(null); setErr(false);
    api.plant(id).then(setD).catch(() => setErr(true));
  }, [id]);

  if (err) return <div className="page"><p>Plant not found. <a onClick={() => navigate('/explore')}>Back to explore</a></p></div>;
  if (!d) return <div className="page"><Loading label="Loading plant" /></div>;

  const vernacular = d.names.filter((n) => n.name_kind !== 'scientific_accepted');
  const tradUses = d.uses.filter((u) => isTraditional(u.evidence));
  const researchUses = d.uses.filter((u) => !isTraditional(u.evidence));
  const namedChems = d.phytochemicals.filter((c) => !!c.preferred_name && !isInchiKey(c.preferred_name));

  return (
    <div className="page fade-in">
      <div className="eyebrow"><a onClick={() => navigate('/explore')}>Explore</a> &nbsp;/&nbsp; Plant</div>
      <div className="detail-head">
        <div className="sci">{d.accepted_name}</div>
        {d.family && <div className="fam">{d.family}{d.genus ? ` · ${d.genus}` : ''}</div>}
        {vernacular.length > 0 && (
          <div className="names-row">
            {vernacular.slice(0, 12).map((n, i) => (
              <span className="name-pill" key={i}>
                <span className="nv">{n.transliteration || n.name}</span>
                <span className="nk">{n.name_kind.replace(/_/g, ' ')}</span>
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="metric-row">
        <div className="metric"><span className="mv">{d.chem_count.toLocaleString()}</span><span className="ml">phytochemicals</span></div>
        <div className="metric"><span className="mv">{d.use_count.toLocaleString()}</span><span className="ml">therapeutic uses</span></div>
        <div className="metric"><span className="mv">{d.target_count}</span><span className="ml">protein targets</span></div>
      </div>

      <div className="detail-grid">
        <div className="kpanel">
          <h3>Phytochemistry</h3>
          <div className="kp-sub">named constituents · green edge = canonical InChIKey</div>
          <div className="tag-flow">
            {namedChems.slice(0, 48).map((c) => (
              <span key={c.id} className={`tag chem ${c.inchikey ? 'keyed' : ''}`} title={c.inchikey || ''}>
                {c.preferred_name}
              </span>
            ))}
            {d.chem_count > namedChems.length && (
              <span className="tag faint">+{(d.chem_count - namedChems.length).toLocaleString()} more compounds</span>
            )}
          </div>
        </div>

        <div className="kpanel">
          <h3>Molecular targets</h3>
          <div className="kp-sub">proteins acted on by this plant's chemicals · CMAUP</div>
          {d.targets.length === 0
            ? <p className="faint" style={{ fontSize: '0.86rem' }}>No mapped targets yet.</p>
            : d.targets.map((t, i) => (
                <div className="tgt-row" key={i}>
                  <span className="gene">{t.gene_symbol || '—'}</span>
                  <span className="prot">{t.protein_name || ''}</span>
                  <span className="via">{t.via_chemicals}×</span>
                </div>
              ))}
        </div>
      </div>

      <div className="detail-grid" style={{ marginTop: '1.2rem' }}>
        <div className="kpanel">
          <h3>Traditional uses</h3>
          <div className="kp-sub">ethnobotanical / classical · Duke</div>
          {tradUses.length === 0
            ? <p className="faint" style={{ fontSize: '0.86rem' }}>None recorded in the current sources.</p>
            : tradUses.slice(0, 28).map((u, i) => (
                <div className="use-row" key={i}>
                  <span className="ul">{u.preferred_label}</span>
                  <EvidenceBadge evidence={u.evidence} />
                </div>
              ))}
        </div>
        <div className="kpanel">
          <h3>Researched associations</h3>
          <div className="kp-sub">computational / preclinical · ICD-11 · CMAUP</div>
          {researchUses.length === 0
            ? <p className="faint" style={{ fontSize: '0.86rem' }}>None.</p>
            : researchUses.slice(0, 28).map((u, i) => (
                <div className="use-row" key={i}>
                  <span className="ul">{u.preferred_label}</span>
                  {u.icd11_code && <span className="icd">{u.icd11_code}</span>}
                  <EvidenceBadge evidence={u.evidence} />
                </div>
              ))}
        </div>
      </div>

      <Disclaimer />
    </div>
  );
}
