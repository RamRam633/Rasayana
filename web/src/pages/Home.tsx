import { useEffect, useState } from 'react';
import { api, type Stats, type PlantLite } from '../lib/api';
import HeroCanvas from '../components/HeroCanvas';
import StatStrip from '../components/StatStrip';
import SearchBox from '../components/SearchBox';
import PlantCard from '../components/PlantCard';
import { SectionHead, Disclaimer, Loading } from '../components/ui';
import AilmentBand from '../components/AilmentBand';
import { navigate } from '../lib/router';

export default function Home({ onAsk }: { onAsk: () => void }) {
  const [stats, setStats] = useState<Stats | null>(null);
  const [featured, setFeatured] = useState<PlantLite[]>([]);
  useEffect(() => {
    api.stats().then(setStats).catch(() => {});
    api.featured().then(setFeatured).catch(() => {});
  }, []);

  return (
    <div className="fade-in">
      <section className="hero">
        <HeroCanvas />
        <div className="hero-inner">
          <div className="eyebrow">रसायन · the science of essence</div>
          <h1>The living atlas of <span className="grad">Indian medicine</span>.</h1>
          <p className="lede">
            Thousands of medicinal plants, their phytochemistry, and the molecular targets they
            touch — drawn from Ayurveda, Unani, Siddha and beyond — unified into one queryable
            knowledge graph. Every claim carries its source.
          </p>
          <div className="hero-cta">
            <button className="btn primary" onClick={() => navigate('/learn')}>Take the course →</button>
            <button className="btn gold" onClick={() => navigate('/library')}>Browse the library</button>
            <button className="btn violet" onClick={onAsk}>✦ Ask</button>
          </div>
          {stats && <StatStrip stats={stats} />}
        </div>
      </section>

      <div className="page" style={{ paddingTop: 0 }}>
        <SectionHead kicker="Not sure what to ask?" title="Browse by ailment" />
        <AilmentBand />

        <SectionHead kicker="Or search" title="Find anything" />
        <SearchBox />

        <SectionHead kicker="Notable plants" title="Featured materia medica" />
        {featured.length === 0 ? <Loading label="Gathering plants" /> : (
          <div className="card-grid">{featured.map((p) => <PlantCard key={p.id} p={p} />)}</div>
        )}

        <SectionHead kicker="What this is" title="From leaf to molecule to mechanism" />
        <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(236px,1fr))' }}>
          <div className="kpanel"><h3>🌿 Plants</h3><p style={{ fontSize: '0.9rem' }}>Resolved botanical names, families, and vernacular names — the substances of traditional practice.</p></div>
          <div className="kpanel"><h3>⚛ Phytochemicals</h3><p style={{ fontSize: '0.9rem' }}>Tens of thousands of constituents with canonical InChIKey identity, linked to the plants that carry them.</p></div>
          <div className="kpanel"><h3>🎯 Targets</h3><p style={{ fontSize: '0.9rem' }}>The proteins those molecules act on, with binding values — bridging tradition and modern pharmacology.</p></div>
          <div className="kpanel"><h3>✦ Ask anything</h3><p style={{ fontSize: '0.9rem' }}>A natural-language layer writes read-only SQL over the graph and answers from the data, citing sources.</p></div>
        </div>

        <Disclaimer />
      </div>
    </div>
  );
}
