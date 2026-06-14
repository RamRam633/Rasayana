export function SectionHead({ kicker, title }: { kicker: string; title: string }) {
  return (
    <div className="sec-head">
      <span className="kick">{kicker}</span>
      <h2>{title}</h2>
    </div>
  );
}

export function Disclaimer() {
  return (
    <div className="disclaimer">
      <span className="d-ico">⚕</span>
      <p>
        <b>Not medical advice.</b> Rasayana organizes traditional and research claims about
        plants and molecules — each tagged with its evidence level and source. It is a reference
        for study, not a substitute for a qualified practitioner.
      </p>
    </div>
  );
}

export function Loading({ label = 'Loading' }: { label?: string }) {
  return (
    <div className="row" style={{ gap: '0.6rem', color: 'var(--faint)', padding: '2.5rem 0' }}>
      <span className="spin" />
      <span className="mono" style={{ fontSize: '0.8rem' }}>{label}…</span>
    </div>
  );
}

export function EvidenceBadge({ evidence }: { evidence: string }) {
  return <span className={`ev ${evidence}`}>{evidence}</span>;
}
