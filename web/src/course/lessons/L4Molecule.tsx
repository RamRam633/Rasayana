import HeroCanvas from '../../components/HeroCanvas';
import { Widget, KeyIdea } from '../Callout';
import { navigate } from '../../lib/router';

export default function L4Molecule() {
  return (
    <div className="lesson-prose">
      <p className="lede">Open a medicinal plant and you find a chemistry lab. A single species can make hundreds of distinct compounds, its <em>phytochemicals</em>, and these are what actually act on the body.</p>

      <h2><span className="s">§</span> A plant is a chemical factory</h2>
      <p>Plants can't run, so they defend and signal with chemistry. The very molecules built to deter insects, fight microbes, or attract pollinators are what make a plant medicinal. They fall into a few great families:</p>
      <ul>
        <li><strong>Alkaloids</strong>, nitrogen-rich and often potent (caffeine, morphine, piperine, berberine).</li>
        <li><strong>Terpenes &amp; terpenoids</strong>, aromatic oils and resins (the scent of tulsi, the bitterness of neem's azadirachtin).</li>
        <li><strong>Polyphenols &amp; flavonoids</strong>, antioxidants and pigments (curcumin, quercetin, the tannins of triphala).</li>
      </ul>

      <Widget title="A plant's molecular cloud" kind="visual">
        <div style={{ position: 'relative', height: 240, borderRadius: 'var(--r)', overflow: 'hidden', border: '1px solid var(--line-soft)' }}>
          <HeroCanvas />
        </div>
      </Widget>

      <KeyIdea>
        <p><strong>Curcuma longa</strong> (turmeric) carries <em>curcumin</em>, one polyphenol among <a className="elink" onClick={() => navigate('/molecules')}>tens of thousands</a> in the graph. A plant's effect is rarely one molecule, though: it's the whole <em>orchestra</em>, which is exactly why whole-plant tradition and single-molecule pharmacology sometimes disagree.</p>
      </KeyIdea>

      <p>Rasayana gives every named molecule its own page, its structure identifiers, the plants that carry it, and the proteins it touches. That last link is where tradition meets modern medicine, and it's the next lesson.</p>
    </div>
  );
}
