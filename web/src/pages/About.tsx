import { useEffect, useState } from 'react';
import { api, type SourceRow } from '../lib/api';
import { Disclaimer } from '../components/ui';

export default function About() {
  const [sources, setSources] = useState<SourceRow[]>([]);
  useEffect(() => { api.sources().then(setSources).catch(() => {}); }, []);

  return (
    <div className="page fade-in" style={{ maxWidth: '840px' }}>
      <div className="eyebrow">रसायन · About</div>
      <h1 style={{ margin: '0.4rem 0 0.6rem' }}>Where herb, molecule, and healing converge.</h1>
      <p className="lede">
        <b>Rasayana</b> — the Ayurvedic science of essence and rejuvenation — is a knowledge hub for
        Indian traditional medicine. It ingests open scientific sources, resolves them to canonical
        identities, and weaves them into one provenance-first graph you can browse and ask in plain
        language.
      </p>
      <p>
        It is a sibling to <a href="https://worldsheet.vayuai.ai" target="_blank" rel="noreferrer">Worldsheet</a> and
        Amplitude — built on the same principle that deep knowledge deserves a beautiful, honest,
        interactive interface. Every assertion is traceable to a source and tagged with its level of
        evidence, so tradition and modern pharmacology can sit side by side without being confused
        for one another.
      </p>

      <h2 style={{ marginTop: '2rem' }}>Sources</h2>
      <p style={{ marginBottom: '0.9rem' }}>
        Open, citable, and license-checked. TKDL is deliberately excluded — it is access-restricted
        to patent offices.
      </p>
      <div className="grid" style={{ gridTemplateColumns: '1fr', gap: '0.6rem' }}>
        {sources.map((s) => (
          <div className="kpanel" key={s.short_code} style={{ padding: '0.9rem 1.1rem' }}>
            <div className="spread">
              <b style={{ fontFamily: 'var(--display)' }}>{s.name}</b>
              <span className="chip">{s.is_redistributable ? 'open' : 'restricted'}</span>
            </div>
            <p style={{ fontSize: '0.84rem', margin: '0.3rem 0 0' }}>
              {s.license || ''}
              {s.url ? <> · <a href={s.url} target="_blank" rel="noreferrer">{s.url.replace(/^https?:\/\//, '')}</a></> : null}
            </p>
          </div>
        ))}
      </div>

      <Disclaimer />
      <p className="faint" style={{ fontSize: '0.8rem', marginTop: '1.5rem' }}>
        Rasayana · a Vayu AI knowledge hub. Plant names, molecules, and links are drawn from public
        scientific databases; the AI layer runs on a free multi-provider fallback chain.
      </p>
    </div>
  );
}
