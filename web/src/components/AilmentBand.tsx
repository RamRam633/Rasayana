import { useEffect, useState } from 'react';
import { api, type Ailment } from '../lib/api';
import { navigate } from '../lib/router';

const EMOJI: Record<string, string> = {
  Fever: '🤒', Cough: '😮‍💨', Diarrhoea: '💧', Dysentery: '🚱', Rheumatism: '🦴',
  Wounds: '🩹', Inflammation: '🔥', Asthma: '🫁', Jaundice: '🟡', Diabetes: '🩸',
  'Vitality / tonic': '✨', Headache: '🤕',
};

export default function AilmentBand() {
  const [a, setA] = useState<Ailment[]>([]);
  useEffect(() => { api.commonAilments().then(setA).catch(() => {}); }, []);
  if (!a.length) return null;
  return (
    <div className="ailment-band">
      {a.map((x) => (
        <button className="ailment" key={x.id} onClick={() => navigate(`/condition/${x.id}`)}>
          <span className="ai-emoji">{EMOJI[x.label] || '🌿'}</span>
          <span className="ai-label">{x.label}</span>
          <span className="ai-count">{x.plants.toLocaleString()} plants</span>
        </button>
      ))}
    </div>
  );
}
