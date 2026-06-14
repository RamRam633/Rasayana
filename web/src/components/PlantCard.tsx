import type { PlantLite } from '../lib/api';
import { navigate } from '../lib/router';

export default function PlantCard({ p }: { p: PlantLite }) {
  return (
    <button className="pcard" onClick={() => navigate(`/plant/${p.id}`)}>
      <span className="pc-name">{p.accepted_name}</span>
      <span className="pc-fam">{p.family || ', '}</span>
      {typeof p.chems === 'number' && (
        <span className="pc-meta"><span><b>{p.chems.toLocaleString()}</b> phytochemicals</span></span>
      )}
    </button>
  );
}
