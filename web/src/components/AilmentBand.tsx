import { useEffect, useState } from 'react';
import { api, type Ailment } from '../lib/api';
import { navigate } from '../lib/router';
import { ailmentIcon } from './icons';

export default function AilmentBand() {
  const [a, setA] = useState<Ailment[]>([]);
  useEffect(() => { api.commonAilments().then(setA).catch(() => {}); }, []);
  if (!a.length) return null;
  return (
    <div className="ailment-band">
      {a.map((x) => {
        const Ico = ailmentIcon(x.label);
        return (
          <button className="ailment" key={x.id} onClick={() => navigate(`/condition/${x.id}`)}>
            <span className="ai-ico"><Ico size={20} strokeWidth={1.5} /></span>
            <span className="ai-label">{x.label}</span>
            <span className="ai-count">{x.plants.toLocaleString()} plants</span>
          </button>
        );
      })}
    </div>
  );
}
