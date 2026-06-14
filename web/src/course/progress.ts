const KEY = 'rasayana.learn.v1';

export function visited(): Set<string> {
  try { return new Set(JSON.parse(localStorage.getItem(KEY) || '[]')); } catch { return new Set(); }
}

export function markVisited(slug: string): void {
  const s = visited();
  s.add(slug);
  try { localStorage.setItem(KEY, JSON.stringify([...s])); } catch { /* ignore */ }
}
