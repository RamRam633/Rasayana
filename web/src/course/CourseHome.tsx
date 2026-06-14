import { Check } from 'lucide-react';
import { LESSONS } from './registry';
import { visited } from './progress';
import { navigate } from '../lib/router';

export default function CourseHome() {
  const seen = visited();
  return (
    <div className="page fade-in">
      <div className="eyebrow">रसायन · Learn</div>
      <h1 style={{ margin: '0.3rem 0 0.4rem' }}>The living science of <span className="grad">Indian medicine</span>.</h1>
      <p className="lede">
        A short, interactive course, from the five traditions and the doshas, through taste and
        chemistry, to the proteins that connect a 3,000-year-old remedy to modern pharmacology.
        About twenty minutes, and every idea is playable.
      </p>
      <div className="syllabus">
        {LESSONS.map((l) => (
          <button className="syl-card" key={l.slug} onClick={() => navigate(`/learn/${l.slug}`)}>
            <span className="syl-num">
              <span>Lesson {l.num} · {l.kicker}</span>
              {seen.has(l.slug) && <span className="done"><Check size={13} strokeWidth={2.4} /></span>}
            </span>
            <h3>{l.title}</h3>
            <p>{l.summary}</p>
          </button>
        ))}
      </div>
    </div>
  );
}
