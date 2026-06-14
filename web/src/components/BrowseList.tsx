import { useEffect, useRef, useState, type ReactNode } from 'react';
import { DataTable, Pagination, type Column } from './DataTable';
import { Breadcrumbs } from './nav';
import { navigate } from '../lib/router';
import type { Page } from '../lib/api';

export default function BrowseList<T>({ kicker, title, lede, fetchPage, columns, rowTo, searchPlaceholder, crumbs, controls }: {
  kicker: string;
  title: string;
  lede?: string;
  fetchPage: (q: string, page: number) => Promise<Page<T>>;
  columns: Column<T>[];
  rowTo: (r: T) => string;
  searchPlaceholder?: string;
  crumbs?: { label: string; to?: string }[];
  controls?: ReactNode;
}) {
  const [q, setQ] = useState('');
  const [page, setPage] = useState(1);
  const [data, setData] = useState<Page<T> | null>(null);
  const [loading, setLoading] = useState(true);
  const fp = useRef(fetchPage); fp.current = fetchPage;

  useEffect(() => { setPage(1); }, [q]);
  useEffect(() => {
    setLoading(true);
    let live = true;
    const t = setTimeout(() => {
      fp.current(q, page)
        .then((d) => { if (live) { setData(d); setLoading(false); } })
        .catch(() => { if (live) setLoading(false); });
    }, q ? 220 : 0);
    return () => { live = false; clearTimeout(t); };
  }, [q, page]);

  return (
    <div className="page fade-in">
      {crumbs && <Breadcrumbs items={crumbs} />}
      <div className="eyebrow">{kicker}</div>
      <h1 style={{ margin: '0.3rem 0 0.3rem' }}>{title}</h1>
      {lede && <p className="lede" style={{ marginBottom: '1.2rem' }}>{lede}</p>}
      {controls}
      <div className="dt-toolbar">
        <input type="search" placeholder={searchPlaceholder || 'Filter…'} value={q} onChange={(e) => setQ(e.target.value)} />
        {data && <span className="dt-count mono">{data.total.toLocaleString()} total</span>}
      </div>
      <DataTable columns={columns} rows={data?.items || []} onRowClick={(r) => navigate(rowTo(r))}
        empty={loading ? 'Loading…' : 'No matches.'} />
      {data && <Pagination page={data.page} total={data.total} pageSize={data.page_size} onPage={setPage} />}
    </div>
  );
}
