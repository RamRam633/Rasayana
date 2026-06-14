import { useEffect, useState } from 'react';
import { api, type Stats } from '../lib/api';
import { navigate } from '../lib/router';
import { fmtCompact } from '../lib/format';
import AilmentBand from '../components/AilmentBand';
import { SectionHead } from '../components/ui';

const doors = (s: Stats | null) => [
  { ico: '🩺', title: 'Conditions & uses', count: s ? fmtCompact(s.therapeutic_uses) : '…', desc: 'Browse every recorded use, traditional first.', to: '/conditions' },
  { ico: '🌿', title: 'Plants', count: s ? fmtCompact(s.plants) : '…', desc: 'The full materia medica — 9,000+ species, by name or family.', to: '/plants' },
  { ico: '⚛', title: 'Molecules', count: s ? fmtCompact(s.phytochemicals) : '…', desc: 'Phytochemicals with canonical identity — and what each plant carries.', to: '/molecules' },
  { ico: '🎯', title: 'Protein targets', count: s ? fmtCompact(s.targets) : '…', desc: 'The proteins those molecules act on — reverse pharmacology.', to: '/targets' },
  { ico: '🧬', title: 'Families', count: '400', desc: 'Browse the botanical taxonomy, family by family.', to: '/families' },
  { ico: '📚', title: 'Sources & references', count: s ? String(s.sources) : '…', desc: 'Every claim is sourced — see the references and what each contributed.', to: '/sources' },
];

export default function Library() {
  const [s, setS] = useState<Stats | null>(null);
  useEffect(() => { api.stats().then(setS).catch(() => {}); }, []);
  return (
    <div className="page fade-in">
      <div className="eyebrow">रसायन · The library</div>
      <h1 style={{ margin: '0.3rem 0 0.4rem' }}>Wander the <span className="grad">whole atlas</span>.</h1>
      <p className="lede">Every plant, molecule, protein target, condition, and source — browsable and cross-linked. Pick a door and follow the threads; you can always click onward.</p>

      <SectionHead kicker="Start with an ailment" title="I'm looking for…" />
      <AilmentBand />

      <SectionHead kicker="Or browse a dimension" title="The whole catalogue" />
      <div className="lib-grid">
        {doors(s).map((d) => (
          <button className="lib-card" key={d.title} onClick={() => navigate(d.to)}>
            <span className="lc-ico">{d.ico}</span>
            <span className="lc-title">{d.title}</span>
            <span className="lc-count">{d.count}</span>
            <p className="lc-desc">{d.desc}</p>
          </button>
        ))}
      </div>
    </div>
  );
}
