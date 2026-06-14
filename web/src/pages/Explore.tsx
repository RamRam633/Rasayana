import { useEffect, useState } from 'react';
import { api, type PlantLite } from '../lib/api';
import SearchBox from '../components/SearchBox';
import PlantCard from '../components/PlantCard';
import { SectionHead, Loading } from '../components/ui';

export default function Explore() {
  const [featured, setFeatured] = useState<PlantLite[]>([]);
  useEffect(() => { api.featured().then(setFeatured).catch(() => {}); }, []);

  return (
    <div className="page fade-in">
      <div className="eyebrow">Explore</div>
      <h1 style={{ margin: '0.4rem 0 0.3rem' }}>Browse the materia medica</h1>
      <p className="lede" style={{ marginBottom: '1.5rem' }}>
        Search by scientific name, vernacular name, or family. Open any plant to see its
        phytochemistry, traditional uses, and molecular targets.
      </p>
      <SearchBox autoFocus />
      <SectionHead kicker="Start with" title="Well-studied plants" />
      {featured.length === 0 ? <Loading /> : (
        <div className="card-grid">{featured.map((p) => <PlantCard key={p.id} p={p} />)}</div>
      )}
    </div>
  );
}
