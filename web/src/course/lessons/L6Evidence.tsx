import { Widget, Caution, KeyIdea } from '../Callout';
import EvidenceLadder from '../widgets/EvidenceLadder';
import { navigate } from '../../lib/router';

export default function L6Evidence() {
  return (
    <div className="lesson-prose">
      <p className="lede">A knowledge graph that mixes 3,000-year-old folk use with last year's lab assay is powerful, and dangerous if you read every line the same way. The final skill is telling them apart.</p>

      <h2><span className="s">§</span> The ladder of evidence</h2>
      <p>Rasayana tags every claim with <em>how it is known</em>. The rungs are not equal:</p>

      <Widget title="Levels of evidence" kind="reference">
        <EvidenceLadder />
      </Widget>

      <p>A plant "used for fever" in an ethnobotanical record is a piece of cultural memory, valuable, but not a clinical result. A molecule that "binds a target" in a preclinical study is a promising lead, not a proven cure. Hold each claim at its true weight.</p>

      <Caution>
        Traditional use is <strong>not</strong> a safety guarantee. Many classical plants are potent or outright toxic, <em>Aconitum</em>, <em>Nerium</em>, and others appear in folk records yet can harm or kill at the wrong dose. Nothing in Rasayana is medical advice; never self-treat, and consult a qualified practitioner.
      </Caution>

      <KeyIdea>
        <p>Used well, this is the best of both worlds: tradition proposes, evidence disposes. You now hold the whole toolkit, systems, doshas, tastes, molecules, targets, and evidence. Go <a className="elink" onClick={() => navigate('/library')}>wander the library</a>, and read every plant with open eyes.</p>
      </KeyIdea>
    </div>
  );
}
