import { useEffect, useState } from 'react';
import { api, type RefRow } from '../lib/api';
import { Breadcrumbs } from '../components/nav';
import { Disclaimer, Loading } from '../components/ui';

export default function Sources() {
  const [rows, setRows] = useState<RefRow[] | null>(null);
  useEffect(() => { api.references().then(setRows).catch(() => {}); }, []);

  return (
    <div className="page fade-in" style={{ maxWidth: '860px' }}>
      <Breadcrumbs items={[{ label: 'Library', to: '/library' }, { label: 'Sources' }]} />
      <div className="eyebrow">References</div>
      <h1 style={{ margin: '0.3rem 0 0.5rem' }}>Sources &amp; references</h1>
      <p className="lede" style={{ marginBottom: '1.2rem' }}>
        Every assertion in Rasayana is traceable to one of these open, citable databases. TKDL is
        deliberately excluded, it is access-restricted to patent offices.
      </p>
      {!rows ? <Loading /> : (
        <div className="grid" style={{ gridTemplateColumns: '1fr', gap: '0.6rem' }}>
          {rows.map((r) => (
            <div className="kpanel" key={r.short_code} style={{ padding: '1rem 1.2rem' }}>
              <div className="spread">
                <div><b style={{ fontFamily: 'var(--display)', fontSize: '1.05rem' }}>{r.name}</b> <span className="chip" style={{ marginLeft: '0.4rem' }}>{r.short_code}</span></div>
                <span className="chip">{r.is_redistributable ? 'open' : 'restricted'}</span>
              </div>
              <p style={{ fontSize: '0.84rem', margin: '0.4rem 0 0' }}>
                {r.edges > 0 && <span className="dt-num" style={{ marginRight: '0.6rem' }}>{r.edges.toLocaleString()} links</span>}
                {r.license || ''}
                {r.url ? <> · <a href={r.url} target="_blank" rel="noreferrer">{r.url.replace(/^https?:\/\//, '')}</a></> : null}
              </p>
            </div>
          ))}
        </div>
      )}
      <Disclaimer />
    </div>
  );
}
