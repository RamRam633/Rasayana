import { useEffect, useRef, useState } from 'react';
import { api, type SearchAll, type SearchHit } from '../lib/api';
import { navigate } from '../lib/router';
import { prettyChem } from '../lib/format';

const GROUPS: { key: keyof SearchAll; label: string; to: (id: string) => string; render: (h: SearchHit) => string; plain?: boolean }[] = [
  { key: 'conditions', label: 'Conditions', to: (id) => `/condition/${id}`, render: (h) => h.label || '', plain: true },
  { key: 'plants', label: 'Plants', to: (id) => `/plant/${id}`, render: (h) => h.label || '' },
  { key: 'molecules', label: 'Molecules', to: (id) => `/molecule/${id}`, render: (h) => prettyChem(h.label), plain: true },
  { key: 'targets', label: 'Targets', to: (id) => `/target/${id}`, render: (h) => h.label || '', plain: true },
];

export default function SearchBox({ autoFocus, placeholder }: { autoFocus?: boolean; placeholder?: string }) {
  const [q, setQ] = useState('');
  const [res, setRes] = useState<SearchAll | null>(null);
  const [open, setOpen] = useState(false);
  const t = useRef<number>();

  useEffect(() => {
    if (!q.trim()) { setRes(null); setOpen(false); return; }
    window.clearTimeout(t.current);
    t.current = window.setTimeout(async () => {
      try { setRes(await api.searchAll(q)); setOpen(true); } catch { /* ignore */ }
    }, 180);
  }, [q]);

  const total = res ? Object.values(res).reduce((a, v) => a + v.length, 0) : 0;
  const go = (to: string) => { navigate(to); setOpen(false); setQ(''); };

  return (
    <div className="search">
      <span className="ico">⌕</span>
      <input type="search" value={q} autoFocus={autoFocus}
        placeholder={placeholder || 'Search plants, molecules, conditions, targets…'}
        onChange={(e) => setQ(e.target.value)} onFocus={() => total > 0 && setOpen(true)} />
      {open && res && total > 0 && (
        <div className="search-results">
          {GROUPS.filter((g) => res[g.key].length > 0).map((g) => (
            <div key={g.key}>
              <div className="usearch-group">{g.label}</div>
              {res[g.key].slice(0, 5).map((h) => (
                <div className="search-row" key={h.id} onClick={() => go(g.to(h.id))}>
                  <span className="nm" style={g.plain ? { fontStyle: 'normal', fontFamily: 'var(--sans)', fontSize: '0.94rem' } : undefined}>{g.render(h)}</span>
                  <span className="fam">{h.sub || ''}</span>
                </div>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
