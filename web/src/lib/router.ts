import { useEffect, useState } from 'react';

export function useHashRoute(): string {
  const [hash, setHash] = useState(() => window.location.hash.slice(1) || '/');
  useEffect(() => {
    const on = () => { setHash(window.location.hash.slice(1) || '/'); window.scrollTo(0, 0); };
    window.addEventListener('hashchange', on);
    return () => window.removeEventListener('hashchange', on);
  }, []);
  return hash;
}

export function navigate(to: string): void {
  if (window.location.hash.slice(1) === to) window.scrollTo(0, 0);
  else window.location.hash = to;
}

export function routeParts(hash: string): string[] {
  return hash.replace(/^\//, '').split('/').filter(Boolean);
}
