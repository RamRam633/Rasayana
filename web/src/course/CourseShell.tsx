import { useEffect } from 'react';
import { LESSONS, lessonBySlug } from './registry';
import { markVisited, visited } from './progress';
import { navigate } from '../lib/router';

export default function CourseShell({ slug }: { slug: string }) {
  const lesson = lessonBySlug(slug);
  useEffect(() => { if (lesson) { markVisited(lesson.slug); window.scrollTo(0, 0); } }, [slug, lesson]);

  if (!lesson) return <div className="page"><p>Lesson not found. <a onClick={() => navigate('/learn')}>Back to the course</a></p></div>;

  const seen = visited();
  const idx = LESSONS.findIndex((l) => l.slug === slug);
  const prev = LESSONS[idx - 1];
  const next = LESSONS[idx + 1];
  const Body = lesson.Component;
  const pct = Math.round(((idx + 1) / LESSONS.length) * 100);

  return (
    <div className="course-shell">
      <aside className="course-rail scrolly">
        <div className="cr-title" onClick={() => navigate('/learn')}>रसायन · Learn</div>
        {LESSONS.map((l) => (
          <div key={l.slug} className={`cr-link ${l.slug === slug ? 'on' : ''}`} onClick={() => navigate(`/learn/${l.slug}`)}>
            <span className="cr-num">{l.num}</span>
            <span style={{ flex: 1, minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{l.title}</span>
            {seen.has(l.slug) && l.slug !== slug && <span className="cr-check">✓</span>}
          </div>
        ))}
      </aside>
      <div className="course-content fade-in" key={slug}>
        <div className="course-progress"><div className="bar" style={{ width: `${pct}%` }} /></div>
        <div className="lesson-kicker">Lesson {lesson.num} · {lesson.kicker}</div>
        <h1 style={{ margin: '0 0 0.4rem' }}>{lesson.title}</h1>
        <Body />
        <div className="lesson-nav">
          {prev
            ? <button onClick={() => navigate(`/learn/${prev.slug}`)}><span className="ln-dir">← Previous</span><span className="ln-title">{prev.title}</span></button>
            : <span />}
          {next
            ? <button className="next" onClick={() => navigate(`/learn/${next.slug}`)}><span className="ln-dir">Next →</span><span className="ln-title">{next.title}</span></button>
            : <button className="next" onClick={() => navigate('/library')}><span className="ln-dir">Finish →</span><span className="ln-title">Explore the library</span></button>}
        </div>
      </div>
    </div>
  );
}
