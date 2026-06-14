import Brand from './Brand';
import { navigate, routeParts } from '../lib/router';

export default function Topbar({ route, onAsk }: { route: string; onAsk: () => void }) {
  const seg = routeParts(route)[0] || 'home';
  const link = (to: string, label: string, key: string) => (
    <a className={seg === key ? 'on' : ''} onClick={() => navigate(to)}>{label}</a>
  );
  return (
    <header className="topbar">
      <Brand />
      <nav className="topnav">
        <a className={seg === 'home' ? 'on' : ''} onClick={() => navigate('/')}>Home</a>
        {link('/explore', 'Explore', 'explore')}
        {link('/about', 'About', 'about')}
        <button className="btn primary sm" onClick={onAsk} style={{ marginLeft: '0.4rem' }}>✦ Ask</button>
      </nav>
    </header>
  );
}
