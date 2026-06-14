import { Widget, KeyIdea } from '../Callout';
import PlantTargetFlow from '../widgets/PlantTargetFlow';
import { navigate } from '../../lib/router';

export default function L5Target() {
  return (
    <div className="lesson-prose">
      <p className="lede">Modern pharmacology asks one question of any drug: which protein does it bind? Rasayana can answer that for plant molecules, turning a traditional remedy into a mechanism.</p>

      <h2><span className="s">§</span> From remedy to mechanism</h2>
      <p>A protein <em>target</em> is the molecular switch a compound flips, an enzyme it blocks, a receptor it activates. Map a plant's molecules to their targets and you have a hypothesis for <em>how</em> it might work, and a place where modern evidence either backs the old use or doesn't.</p>

      <Widget title="Plant → molecule → target" kind="live · interactive">
        <PlantTargetFlow />
      </Widget>

      <p>Turmeric → curcumin → <strong>COX-2</strong> and <strong>5-lipoxygenase</strong>, the very inflammation enzymes that modern anti-inflammatories target. Ashwagandha → withaferin A → stress, immune, and cancer-related proteins. The traditional label "anti-inflammatory" or "rejuvenative" suddenly has a molecular address.</p>

      <KeyIdea>
        <p>This is the bridge, and the live frontier of drug discovery from plants. Explore it in the <a className="elink" onClick={() => navigate('/targets')}>targets</a> library: pick a protein and see every plant molecule known to act on it.</p>
      </KeyIdea>
    </div>
  );
}
