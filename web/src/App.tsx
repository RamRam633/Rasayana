import { useState } from 'react';
import { useHashRoute, routeParts, navigate } from './lib/router';
import Topbar from './components/Topbar';
import Assistant from './components/Assistant';
import Home from './pages/Home';
import Explore from './pages/Explore';
import PlantDetail from './pages/PlantDetail';
import About from './pages/About';

export default function App() {
  const route = useHashRoute();
  const [asstOpen, setAsstOpen] = useState(false);
  const parts = routeParts(route);

  let page;
  if (parts[0] === 'plant' && parts[1]) page = <PlantDetail id={parts[1]} key={parts[1]} />;
  else if (parts[0] === 'explore') page = <Explore />;
  else if (parts[0] === 'about') page = <About />;
  else page = <Home onAsk={() => setAsstOpen(true)} />;

  return (
    <div className="app">
      <Topbar route={route} onAsk={() => setAsstOpen(true)} />
      <main className="main">{page}</main>
      <footer className="foot">
        <span className="by">रसायन · Rasayana — a <b>Vayu AI</b> knowledge hub</span>
        <div className="foot-links">
          <a onClick={() => navigate('/explore')}>Explore</a>
          <a onClick={() => navigate('/about')}>About</a>
          <a href="https://vayuai.ai" target="_blank" rel="noreferrer">vayuai.ai</a>
        </div>
      </footer>
      <button className="asst-fab" onClick={() => setAsstOpen(true)}>✦ Ask Rasayana</button>
      <Assistant open={asstOpen} onClose={() => setAsstOpen(false)} />
    </div>
  );
}
