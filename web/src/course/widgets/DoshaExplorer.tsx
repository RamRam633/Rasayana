import { useState } from 'react';

const DOSHAS = {
  Vata: { elements: 'Air + Ether', qualities: 'light, dry, cool, mobile, quick',
    balance: 'warmth, oil, routine, grounding, and sweet · sour · salty tastes', herbs: 'Ashwagandha · Ginger · Bala' },
  Pitta: { elements: 'Fire + Water', qualities: 'hot, sharp, intense, oily, penetrating',
    balance: 'cooling, calm, moderation, and sweet · bitter · astringent tastes', herbs: 'Amalaki · Coriander · Brahmi' },
  Kapha: { elements: 'Earth + Water', qualities: 'heavy, slow, cool, stable, moist',
    balance: 'lightness, warmth, stimulation, and pungent · bitter · astringent tastes', herbs: 'Trikatu · Guggulu · Pippali' },
} as const;

const COLOR: Record<string, string> = { Vata: 'var(--violet)', Pitta: 'var(--ember)', Kapha: 'var(--herb)' };
type Key = keyof typeof DOSHAS;

export default function DoshaExplorer() {
  const [v, setV] = useState<Record<Key, number>>({ Vata: 55, Pitta: 50, Kapha: 45 });
  const dom = (Object.keys(v) as Key[]).reduce((a, b) => (v[a] >= v[b] ? a : b));
  const d = DOSHAS[dom];
  return (
    <div>
      <p className="muted" style={{ fontSize: '0.9rem', marginTop: 0 }}>
        Drag each toward how strongly it resonates with you. Your highest is your dominant dosha (<em>prakriti</em>).
      </p>
      {(Object.keys(v) as Key[]).map((k) => (
        <div className="dosha-row" key={k}>
          <label><span>{k} <span className="faint">· {DOSHAS[k].elements}</span></span><b>{v[k]}</b></label>
          <input type="range" min={0} max={100} value={v[k]} style={{ accentColor: COLOR[k] }}
            onChange={(e) => setV((s) => ({ ...s, [k]: +e.target.value }))} />
        </div>
      ))}
      <div className="dosha-out" style={{ borderColor: `color-mix(in srgb, ${COLOR[dom]} 35%, var(--line))` }}>
        <h4 style={{ color: COLOR[dom] }}>{dom} dominant</h4>
        <p><strong>Qualities:</strong> {d.qualities}.</p>
        <p><strong>To balance:</strong> {d.balance}.</p>
        <p><strong>Classic herbs:</strong> {d.herbs}.</p>
      </div>
    </div>
  );
}
