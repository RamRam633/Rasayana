// Display helpers.

export const isInchiKey = (s?: string | null): boolean =>
  !!s && /^[A-Z]{14}-[A-Z]{8,10}-[A-Z]$/.test(s);

/** CMAUP sometimes leaves a compound's name blank (falls back to its key). */
export const prettyChem = (name?: string | null): string => {
  if (!name || isInchiKey(name)) return 'Unnamed compound';
  return name;
};

export const fmtNum = (n: number): string => n.toLocaleString('en-US');

export const fmtCompact = (n: number): string => {
  if (n >= 1e6) return (n / 1e6).toFixed(2).replace(/\.?0+$/, '') + 'M';
  if (n >= 1e3) return (n / 1e3).toFixed(n >= 1e4 ? 0 : 1).replace(/\.0$/, '') + 'k';
  return String(n);
};

export const titleCase = (s: string): string => s.replace(/\b\w/g, (c) => c.toUpperCase());

/** Group plant uses into traditional vs. researched (computational/preclinical). */
export const isTraditional = (ev: string): boolean =>
  ev === 'traditional' || ev === 'ethnobotanical' || ev === 'clinical';
