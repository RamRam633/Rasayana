import { KeyIdea, Widget } from '../Callout';
import DoshaExplorer from '../widgets/DoshaExplorer';

export default function L2Doshas() {
  return (
    <div className="lesson-prose">
      <p className="lede">Ayurveda builds the whole body — and every plant — from five elements, organised into three working forces. Grasp these three and most of the system follows.</p>

      <h2><span className="s">§</span> Five elements, three doshas</h2>
      <p>The <em>pancha mahabhuta</em> — ether, air, fire, water, earth — combine into three <em>doshas</em>, the functional energies of the body:</p>
      <ul>
        <li><strong>Vata</strong> (air + ether) — movement: breath, circulation, nerve impulse, thought.</li>
        <li><strong>Pitta</strong> (fire + water) — transformation: digestion, metabolism, body heat.</li>
        <li><strong>Kapha</strong> (earth + water) — structure: tissue, lubrication, immunity, calm.</li>
      </ul>
      <p>Everyone carries all three; your particular ratio is your <em>prakriti</em>, your constitution. Illness, in this view, is a dosha pushed out of its natural range — and the remedy is whatever carries the opposite qualities.</p>

      <Widget title="Find your dominant dosha" kind="interactive">
        <DoshaExplorer />
      </Widget>

      <KeyIdea>
        <p>This is why <strong>opposites heal</strong>: a cold, dry, anxious (Vata) state is met with warm, oily, grounding food and herbs; a hot, inflamed (Pitta) state with cooling, calming ones. The next lesson — the six tastes — is the practical tool for choosing which.</p>
      </KeyIdea>
    </div>
  );
}
