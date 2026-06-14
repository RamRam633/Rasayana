import type { Stats } from '../lib/api';
import { fmtCompact } from '../lib/format';

export default function StatStrip({ stats }: { stats: Stats }) {
  const items = [
    { n: stats.plants, l: 'medicinal plants' },
    { n: stats.phytochemicals, l: 'phytochemicals' },
    { n: stats.targets, l: 'protein targets' },
    { n: stats.therapeutic_uses, l: 'therapeutic uses' },
    { n: stats.edges, l: 'sourced links' },
  ];
  return (
    <div className="stats">
      {items.map((it) => (
        <div className="stat" key={it.l}>
          <span className="num">{fmtCompact(it.n)}</span>
          <span className="lbl">{it.l}</span>
        </div>
      ))}
    </div>
  );
}
