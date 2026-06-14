import { useState, type ReactNode } from 'react';

export interface Column<T> {
  key: string;
  header: string;
  render: (row: T) => ReactNode;
  sortValue?: (row: T) => string | number;
  width?: string;
  align?: 'right';
}

export function DataTable<T>({ columns, rows, onRowClick, empty }: {
  columns: Column<T>[]; rows: T[]; onRowClick?: (r: T) => void; empty?: string;
}) {
  const [sort, setSort] = useState<{ key: string; dir: 1 | -1 } | null>(null);
  let view = rows;
  if (sort) {
    const col = columns.find((c) => c.key === sort.key);
    if (col?.sortValue) {
      view = [...rows].sort((a, b) => {
        const av = col.sortValue!(a), bv = col.sortValue!(b);
        return (av < bv ? -1 : av > bv ? 1 : 0) * sort.dir;
      });
    }
  }
  const onSort = (key: string) =>
    setSort((s) => (s && s.key === key ? { key, dir: s.dir === 1 ? -1 : 1 } : { key, dir: 1 }));

  return (
    <div className="dtable-wrap scrolly">
      <table className="dtable">
        <thead>
          <tr>
            {columns.map((c) => (
              <th key={c.key} style={{ width: c.width, textAlign: c.align }}
                  className={c.sortValue ? 'sortable' : ''}
                  onClick={() => c.sortValue && onSort(c.key)}>
                {c.header}{sort?.key === c.key ? (sort.dir === 1 ? ' ▲' : ' ▼') : ''}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {view.length === 0 ? (
            <tr><td className="dt-empty" colSpan={columns.length}>{empty || 'No rows.'}</td></tr>
          ) : view.map((r, i) => (
            <tr key={i} className={onRowClick ? 'click' : ''} onClick={() => onRowClick?.(r)}>
              {columns.map((c) => <td key={c.key} style={{ textAlign: c.align }}>{c.render(r)}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function Pagination({ page, total, pageSize, onPage }: {
  page: number; total: number; pageSize: number; onPage: (p: number) => void;
}) {
  const pages = Math.ceil(total / pageSize);
  if (pages <= 1) return null;
  return (
    <div className="pager">
      <button className="btn sm" disabled={page <= 1} onClick={() => onPage(page - 1)}>← Prev</button>
      <span className="pager-info">
        {((page - 1) * pageSize + 1).toLocaleString()}–{Math.min(page * pageSize, total).toLocaleString()} of {total.toLocaleString()}
      </span>
      <button className="btn sm" disabled={page >= pages} onClick={() => onPage(page + 1)}>Next →</button>
    </div>
  );
}
