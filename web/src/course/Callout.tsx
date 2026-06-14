import type { ReactNode } from 'react';

export function KeyIdea({ label = 'Key idea', children }: { label?: string; children: ReactNode }) {
  return (
    <div className="key-idea">
      <div className="ki-label">{label}</div>
      {children}
    </div>
  );
}

export function Caution({ children }: { children: ReactNode }) {
  return (
    <div className="caution">
      <span className="c-ico">⚠</span>
      <p>{children}</p>
    </div>
  );
}

export function Widget({ title, kind, children }: { title: string; kind?: string; children: ReactNode }) {
  return (
    <div className="widget">
      <div className="widget-bar">
        <span className="widget-dot" />
        <span className="widget-title">{title}</span>
        {kind && <span className="widget-kind">{kind}</span>}
      </div>
      <div className="widget-body">{children}</div>
    </div>
  );
}
