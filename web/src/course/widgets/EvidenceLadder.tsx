const RUNGS = [
  { tag: 'clinical', color: 'var(--herb-deep)', bg: 'rgba(26,157,107,0.14)', desc: 'Tested in humans in controlled trials, the strongest tier, still rare for whole plants.' },
  { tag: 'preclinical', color: 'var(--violet)', bg: 'rgba(109,59,212,0.12)', desc: 'Lab or computational evidence: a molecule binds a target in vitro. Promising, not proof in people.' },
  { tag: 'ethnobotanical', color: 'var(--gold-soft)', bg: 'rgba(184,134,11,0.14)', desc: 'Use documented by a community and catalogued by ethnographers (e.g. Dr. Duke).' },
  { tag: 'traditional', color: 'var(--gold-soft)', bg: 'rgba(184,134,11,0.14)', desc: 'Recorded in classical texts or long folk practice, cultural knowledge, not a clinical claim.' },
];

export default function EvidenceLadder() {
  return (
    <div className="ladder">
      {RUNGS.map((r) => (
        <div className="rung" key={r.tag}>
          <span className="r-tag" style={{ background: r.bg, color: r.color }}>{r.tag}</span>
          <span className="r-desc">{r.desc}</span>
        </div>
      ))}
    </div>
  );
}
