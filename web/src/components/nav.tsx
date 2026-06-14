import type { ReactNode } from 'react';
import { navigate } from '../lib/router';

export function EntityLink({ to, children, kind }: { to: string; children: ReactNode; kind?: string }) {
  return (
    <a className={`elink ${kind || ''}`} onClick={(e) => { e.stopPropagation(); navigate(to); }}>
      {children}
    </a>
  );
}

export function SourcePill({ code }: { code: string }) {
  return (
    <span className="src-pill" onClick={(e) => { e.stopPropagation(); navigate('/sources'); }} style={{ cursor: 'pointer' }}>
      <span className="dot" />{code}
    </span>
  );
}

export function Sources({ codes }: { codes: string }) {
  const list = (codes || '').split(',').filter(Boolean);
  return <span className="row" style={{ gap: '0.3rem', flexWrap: 'wrap' }}>{list.map((c) => <SourcePill key={c} code={c} />)}</span>;
}

export function Breadcrumbs({ items }: { items: { label: string; to?: string }[] }) {
  return (
    <div className="crumbs">
      {items.map((it, i) => (
        <span key={i}>
          {i > 0 && <span className="sep">/</span>}
          {it.to ? <a onClick={() => navigate(it.to!)}>{it.label}</a> : <span>{it.label}</span>}
        </span>
      ))}
    </div>
  );
}
