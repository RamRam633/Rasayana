import { useState } from 'react';

const RASA = [
  { name: 'Madhura', en: 'Sweet', color: '#1a9d6b', el: 'Earth + Water', effect: 'Builds & nourishes · calms Vata & Pitta, raises Kapha', ex: 'Licorice · Shatavari · dates · ghee' },
  { name: 'Amla', en: 'Sour', color: '#a87514', el: 'Earth + Fire', effect: 'Kindles digestion · calms Vata, raises Pitta & Kapha', ex: 'Amla · lemon · tamarind' },
  { name: 'Lavana', en: 'Salty', color: '#c2581f', el: 'Water + Fire', effect: 'Softens & moistens · calms Vata, raises Pitta & Kapha', ex: 'Rock salt' },
  { name: 'Katu', en: 'Pungent', color: '#bd3478', el: 'Fire + Air', effect: 'Heats & stimulates · reduces Kapha, raises Pitta & Vata', ex: 'Ginger · pepper · Trikatu' },
  { name: 'Tikta', en: 'Bitter', color: '#0e8fa8', el: 'Air + Ether', effect: 'Cools & detoxifies · reduces Pitta & Kapha, raises Vata', ex: 'Neem · turmeric · Guduchi' },
  { name: 'Kashaya', en: 'Astringent', color: '#6d3bd4', el: 'Air + Earth', effect: 'Dries & tones · reduces Pitta & Kapha, raises Vata', ex: 'Pomegranate · Haritaki' },
];

const slice = (i: number) => {
  const a0 = ((i * 60 - 90) * Math.PI) / 180, a1 = (((i + 1) * 60 - 90) * Math.PI) / 180, r = 118;
  const x0 = 140 + r * Math.cos(a0), y0 = 140 + r * Math.sin(a0), x1 = 140 + r * Math.cos(a1), y1 = 140 + r * Math.sin(a1);
  return `M140,140 L${x0.toFixed(1)},${y0.toFixed(1)} A${r},${r} 0 0 1 ${x1.toFixed(1)},${y1.toFixed(1)} Z`;
};
const labelPos = (i: number) => {
  const a = (((i + 0.5) * 60 - 90) * Math.PI) / 180, r = 80;
  return { x: 140 + r * Math.cos(a), y: 140 + r * Math.sin(a) };
};

export default function RasaWheel() {
  const [sel, setSel] = useState(0);
  const d = RASA[sel];
  return (
    <div className="rasa-wrap">
      <svg viewBox="0 0 280 280" width="100%" style={{ maxWidth: 280 }} role="img" aria-label="The six tastes wheel">
        {RASA.map((r, i) => {
          const lp = labelPos(i);
          return (
            <g key={i} className="rasa-seg" onClick={() => setSel(i)}>
              <path d={slice(i)} fill={r.color} fillOpacity={sel === i ? 0.95 : 0.62} stroke="#fffdf8" strokeWidth={2} />
              <text x={lp.x} y={lp.y} textAnchor="middle" dominantBaseline="middle" fontSize="11" fontWeight="600" fill="#fffdf8" style={{ pointerEvents: 'none', fontFamily: 'var(--mono)' }}>{r.en}</text>
            </g>
          );
        })}
        <circle cx={140} cy={140} r={29} fill="#fffdf8" stroke="rgba(42,37,32,0.16)" />
        <text x={140} y={140} textAnchor="middle" dominantBaseline="middle" fontSize="9" fill="#9a9082" style={{ fontFamily: 'var(--mono)', letterSpacing: '0.1em' }}>RASA</text>
      </svg>
      <div className="rasa-detail">
        <h4 style={{ color: d.color }}>{d.name} <span className="faint" style={{ fontWeight: 400 }}>· {d.en}</span></h4>
        <div className="rd-meta">{d.el}</div>
        <p>{d.effect}.</p>
        <p className="faint" style={{ fontSize: '0.86rem' }}><strong style={{ color: 'var(--ink)' }}>Plants:</strong> {d.ex}</p>
      </div>
    </div>
  );
}
