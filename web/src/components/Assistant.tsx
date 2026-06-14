import { useEffect, useRef, useState } from 'react';
import { Markdown } from '../lib/markdown';
import { streamChat, type ChatEvent } from '../lib/api';

interface Msg { role: 'user' | 'assistant'; content: string; provider?: string; sql?: string; rowCount?: number; }

const SUGGESTIONS = [
  'Which plants contain curcumin?',
  'What protein targets does withaferin A act on?',
  'How many plants are in the family Solanaceae?',
  'List phytochemicals found in Zingiber officinale.',
  'Which plants are used for inflammation?',
];

export default function Assistant({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const bodyRef = useRef<HTMLDivElement>(null);
  const taRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => { if (open) taRef.current?.focus(); }, [open]);
  useEffect(() => { bodyRef.current?.scrollTo({ top: bodyRef.current.scrollHeight, behavior: 'smooth' }); }, [messages, busy]);

  const send = async (q: string) => {
    const question = q.trim();
    if (!question || busy) return;
    setMessages((m) => [...m, { role: 'user', content: question }, { role: 'assistant', content: '' }]);
    setInput('');
    setBusy(true);
    let acc = '', provider: string | undefined, sql: string | undefined, rowCount: number | undefined;
    const upd = () => setMessages((m) => { const c = [...m]; c[c.length - 1] = { role: 'assistant', content: acc, provider, sql, rowCount }; return c; });
    try {
      await streamChat(question, (e: ChatEvent) => {
        if (e.type === 'meta') provider = e.provider;
        else if (e.type === 'sql') { sql = e.sql; rowCount = e.row_count; upd(); }
        else if (e.type === 'delta' && e.text) { acc += e.text; upd(); }
        else if (e.type === 'error') { acc = acc || `⚠️ ${e.message || 'Unavailable.'}`; upd(); }
      });
    } catch (err) { acc = acc || `⚠️ ${String(err)}`; upd(); }
    setBusy(false);
  };

  return (
    <>
      <div className={`asst-overlay${open ? ' open' : ''}`} onClick={onClose} />
      <aside className={`asst-panel${open ? ' open' : ''}`} aria-hidden={!open}>
        <div className="asst-header">
          <div className="asst-title">
            <b>✦ Ask Rasayana</b>
            <small>natural language over the knowledge graph</small>
          </div>
          <button className="asst-x" onClick={onClose} aria-label="Close">×</button>
        </div>
        <div className="asst-body scrolly" ref={bodyRef}>
          {messages.length === 0 && (
            <div className="muted" style={{ fontSize: '0.92rem' }}>
              <p style={{ marginTop: 0 }}>
                Ask about plants, phytochemicals, protein targets, or therapeutic uses. I write the
                query, run it read-only against the graph, and answer from the data — citing sources.
                This is research information, not medical advice.
              </p>
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`asst-msg ${m.role}`}>
              {m.role === 'assistant'
                ? (m.content ? <Markdown source={m.content} /> : <span className="typing"><i /><i /><i /></span>)
                : m.content}
              {m.role === 'assistant' && m.sql && (
                <details className="asst-sql">
                  <summary>{typeof m.rowCount === 'number' ? `${m.rowCount} row(s) · show SQL` : 'show SQL'}</summary>
                  <pre>{m.sql}</pre>
                </details>
              )}
              {m.role === 'assistant' && m.provider && m.content && <div className="asst-prov">answered via {m.provider}</div>}
            </div>
          ))}
        </div>
        <div className="asst-foot">
          {messages.length === 0 && (
            <div className="asst-suggest">
              {SUGGESTIONS.map((s) => <button key={s} className="asst-sug" onClick={() => send(s)}>{s}</button>)}
            </div>
          )}
          <div className="asst-inputrow">
            <textarea
              ref={taRef} className="asst-input" rows={1} placeholder="Ask the knowledge graph…"
              value={input} onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(input); } }}
            />
            <button className="btn primary" disabled={busy || !input.trim()} onClick={() => send(input)}>{busy ? '…' : 'Send'}</button>
          </div>
        </div>
      </aside>
    </>
  );
}
