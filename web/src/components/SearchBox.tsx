import { useEffect, useRef, useState } from 'react';
import { api, type PlantLite } from '../lib/api';
import { navigate } from '../lib/router';

export default function SearchBox({ autoFocus, placeholder }: { autoFocus?: boolean; placeholder?: string }) {
  const [q, setQ] = useState('');
  const [res, setRes] = useState<PlantLite[]>([]);
  const [open, setOpen] = useState(false);
  const t = useRef<number>();

  useEffect(() => {
    if (!q.trim()) { setRes([]); setOpen(false); return; }
    window.clearTimeout(t.current);
    t.current = window.setTimeout(async () => {
      try { setRes(await api.search(q)); setOpen(true); } catch { /* ignore */ }
    }, 170);
  }, [q]);

  return (
    <div className="search">
      <span className="ico">⌕</span>
      <input
        type="search"
        value={q}
        placeholder={placeholder || 'Search 9,000+ plants — Withania, tulsi, turmeric…'}
        autoFocus={autoFocus}
        onChange={(e) => setQ(e.target.value)}
        onFocus={() => res.length > 0 && setOpen(true)}
      />
      {open && res.length > 0 && (
        <div className="search-results">
          {res.slice(0, 12).map((p) => (
            <div className="search-row" key={p.id} onClick={() => { navigate(`/plant/${p.id}`); setOpen(false); }}>
              <span className="nm">{p.accepted_name}</span>
              <span className="fam">{p.family || ''}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
