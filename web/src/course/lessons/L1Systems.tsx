import { KeyIdea } from '../Callout';
import { navigate } from '../../lib/router';

export default function L1Systems() {
  return (
    <div className="lesson-prose">
      <p className="lede">India is home to not one but several living systems of medicine, each a different way of reading the body, yet sharing one instinct: that health is <em>balance</em>, and that the natural world is a pharmacy.</p>

      <h2><span className="s">§</span> The AYUSH family</h2>
      <p><strong>Ayurveda</strong>, the oldest, roughly three thousand years, reads the body through three <em>doshas</em> (Vata, Pitta, Kapha) built from five elements. Treatment restores balance with diet, lifestyle, and plant formulations.</p>
      <p><strong>Unani</strong>, Greco-Arabic medicine, descended from Hippocrates and Galen and refined across the Islamic world, works through four humours: blood, phlegm, yellow bile, and black bile. It reached India in the medieval period.</p>
      <p><strong>Siddha</strong>, the Tamil tradition of the <em>siddhars</em>, parallels Ayurveda's framework but leans heavily on mineral and metallic preparations (the alchemy of <em>rasa shastra</em>).</p>
      <p><strong>Sowa Rigpa</strong>, Tibetan medicine, blends Ayurvedic, Chinese, and Greco-Arab streams, and is practised across the Himalaya.</p>
      <p><strong>Yoga &amp; Naturopathy</strong>, not pharmacology but the disciplines of breath, movement, and natural living that the others assume as a foundation.</p>

      <KeyIdea>
        <p>These are <strong>systems of correspondence</strong>. A plant isn't merely "a remedy", it carries qualities (hot or cold, heavy or light, a taste) that act on the body's own qualities. Rasayana lets you follow those plants all the way down to the molecules and proteins that modern science can name.</p>
      </KeyIdea>

      <p>Throughout this short course the working framework is Ayurveda's, the most documented, but the same plants recur across all five systems. Whenever you meet one, you can open its full page in the <a className="elink" onClick={() => navigate('/library')}>library</a>.</p>
    </div>
  );
}
