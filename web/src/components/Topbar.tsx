import Brand from './Brand';
import { navigate, routeParts } from '../lib/router';

const LIB = new Set(['library', 'conditions', 'condition', 'molecules', 'molecule',
  'targets', 'target', 'families', 'family', 'plants', 'plant', 'sources']);

export default function Topbar({ route, onAsk }: { route: string; onAsk: () => void }) {
  const seg = routeParts(route)[0] || 'home';
  return (
    <header className="topbar">
      <Brand />
      <nav className="topnav">
        <a className={seg === 'home' ? 'on' : ''} onClick={() => navigate('/')}>Home</a>
        <a className={seg === 'learn' ? 'on' : ''} onClick={() => navigate('/learn')}>Learn</a>
        <a className={LIB.has(seg) ? 'on' : ''} onClick={() => navigate('/library')}>Library</a>
        <a className={`hide-sm ${seg === 'explore' ? 'on' : ''}`} onClick={() => navigate('/explore')}>Explore</a>
        <a className={`hide-sm ${seg === 'about' ? 'on' : ''}`} onClick={() => navigate('/about')}>About</a>
        <button className="btn primary sm" onClick={onAsk} style={{ marginLeft: '0.4rem' }}>✦ Ask</button>
      </nav>
    </header>
  );
}
