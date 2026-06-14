// Minimal, XSS-safe markdown -> React (no innerHTML). Handles bold, italic,
// inline code, links, and bullet/numbered lists. Enough for assistant answers.
import { Fragment, type ReactNode } from 'react';

function inline(text: string): ReactNode[] {
  const out: ReactNode[] = [];
  const re = /(\*\*([^*]+)\*\*|`([^`]+)`|\*([^*]+)\*|\[([^\]]+)\]\(([^)]+)\))/g;
  let last = 0;
  let key = 0;
  let m: RegExpExecArray | null;
  while ((m = re.exec(text))) {
    if (m.index > last) out.push(text.slice(last, m.index));
    if (m[2]) out.push(<strong key={key++}>{m[2]}</strong>);
    else if (m[3]) out.push(<code key={key++}>{m[3]}</code>);
    else if (m[4]) out.push(<em key={key++}>{m[4]}</em>);
    else if (m[5]) out.push(<a key={key++} href={m[6]} target="_blank" rel="noreferrer">{m[5]}</a>);
    last = re.lastIndex;
  }
  if (last < text.length) out.push(text.slice(last));
  return out;
}

export function Markdown({ source }: { source: string }) {
  const blocks = source.trim().split(/\n{2,}/);
  return (
    <div className="md">
      {blocks.map((b, bi) => {
        const lines = b.split('\n');
        const isUl = lines.length > 0 && lines.every((l) => /^\s*[-*]\s+/.test(l));
        const isOl = lines.length > 0 && lines.every((l) => /^\s*\d+\.\s+/.test(l));
        if (isUl) return <ul key={bi}>{lines.map((l, li) => <li key={li}>{inline(l.replace(/^\s*[-*]\s+/, ''))}</li>)}</ul>;
        if (isOl) return <ol key={bi}>{lines.map((l, li) => <li key={li}>{inline(l.replace(/^\s*\d+\.\s+/, ''))}</li>)}</ol>;
        return <p key={bi}>{lines.map((l, li) => <Fragment key={li}>{li > 0 && <br />}{inline(l)}</Fragment>)}</p>;
      })}
    </div>
  );
}
