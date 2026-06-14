import { useState } from 'react';
import { useHashRoute, routeParts, navigate } from './lib/router';
import Topbar from './components/Topbar';
import Assistant from './components/Assistant';
import Home from './pages/Home';
import Explore from './pages/Explore';
import About from './pages/About';
import Library from './pages/Library';
import Conditions from './pages/Conditions';
import Condition from './pages/Condition';
import Molecules from './pages/Molecules';
import Molecule from './pages/Molecule';
import Targets from './pages/Targets';
import Target from './pages/Target';
import Families from './pages/Families';
import Family from './pages/Family';
import PlantsIndex from './pages/PlantsIndex';
import PlantDetail from './pages/PlantDetail';
import Sources from './pages/Sources';
import CourseHome from './course/CourseHome';
import CourseShell from './course/CourseShell';
import { Sparkles } from 'lucide-react';

export default function App() {
  const route = useHashRoute();
  const [asstOpen, setAsstOpen] = useState(false);
  const p = routeParts(route);
  const id = p[1] ? decodeURIComponent(p[1]) : '';

  let page;
  switch (p[0]) {
    case 'library': page = <Library />; break;
    case 'conditions': page = <Conditions />; break;
    case 'condition': page = <Condition id={id} key={id} />; break;
    case 'molecules': page = <Molecules />; break;
    case 'molecule': page = <Molecule id={id} key={id} />; break;
    case 'targets': page = <Targets />; break;
    case 'target': page = <Target id={id} key={id} />; break;
    case 'families': page = <Families />; break;
    case 'family': page = <Family name={id} key={id} />; break;
    case 'plants': page = <PlantsIndex />; break;
    case 'plant': page = id ? <PlantDetail id={id} key={id} /> : <PlantsIndex />; break;
    case 'sources': page = <Sources />; break;
    case 'learn': page = id ? <CourseShell slug={id} key={id} /> : <CourseHome />; break;
    case 'explore': page = <Explore />; break;
    case 'about': page = <About />; break;
    default: page = <Home onAsk={() => setAsstOpen(true)} />;
  }

  return (
    <div className="app">
      <Topbar route={route} onAsk={() => setAsstOpen(true)} />
      <main className="main">{page}</main>
      <footer className="foot">
        <span className="by">रसायन · Rasayana, a <b>Vayu AI</b> knowledge hub</span>
        <div className="foot-links">
          <a onClick={() => navigate('/library')}>Library</a>
          <a onClick={() => navigate('/sources')}>Sources</a>
          <a onClick={() => navigate('/about')}>About</a>
          <a href="https://vayuai.ai" target="_blank" rel="noreferrer">vayuai.ai</a>
        </div>
      </footer>
      <button className="asst-fab" onClick={() => setAsstOpen(true)}><Sparkles size={16} strokeWidth={2} /> Ask Rasayana</button>
      <Assistant open={asstOpen} onClose={() => setAsstOpen(false)} />
    </div>
  );
}
