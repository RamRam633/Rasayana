import { Widget, KeyIdea } from '../Callout';
import RasaWheel from '../widgets/RasaWheel';

export default function L3Rasa() {
  return (
    <div className="lesson-prose">
      <p className="lede">In Ayurveda, taste isn't just flavour, it's a plant's first medicine. The six tastes (<em>shad rasa</em>) each carry elements and act predictably on the doshas.</p>

      <h2><span className="s">§</span> The six tastes (rasa)</h2>
      <p>Every plant has one or more dominant tastes, and each taste pushes the doshas up or down. Click a slice to explore, this is how a practitioner reasons about a herb before any chemistry enters the picture.</p>

      <Widget title="The six tastes" kind="interactive">
        <RasaWheel />
      </Widget>

      <h2><span className="s">§</span> Beyond taste: virya, vipaka, prabhava</h2>
      <p>Three further axes complete a plant's Ayurvedic pharmacology:</p>
      <ul>
        <li><strong>Virya</strong>, potency: is it heating (<em>ushna</em>) or cooling (<em>shita</em>)?</li>
        <li><strong>Vipaka</strong>, the post-digestive effect, after the body has transformed it.</li>
        <li><strong>Prabhava</strong>, a specific action the taste-logic can't predict: a plant's "special power".</li>
      </ul>

      <KeyIdea>
        <p>Remarkably, this taste-and-quality logic often <strong>tracks the chemistry</strong>. Bitter, cooling herbs (neem, turmeric) turn out to be rich in anti-inflammatory polyphenols; pungent, heating ones (ginger, pepper) in stimulating alkaloids. Tradition reached the conclusion centuries before the molecule had a name.</p>
      </KeyIdea>
    </div>
  );
}
