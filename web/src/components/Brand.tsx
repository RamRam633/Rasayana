import { navigate } from '../lib/router';

export function BrandMark({ size = 30 }: { size?: number }) {
  return (
    <svg className="brand-mark" width={size} height={size} viewBox="0 0 32 32" aria-hidden="true">
      <path d="M16 29C8 24 5 16.5 7 8c7 0 12 3.6 13 10.6C21 13 24.6 10.5 29 11c-1 9-6.6 14.6-13 18z" fill="#1a9d6b" />
      <path d="M16 29C11.6 22.5 10.6 16 11.6 9.6" stroke="#b8860b" strokeWidth="1.3" fill="none" strokeLinecap="round" />
      <path d="M14.2 18.6 11 16.4M17.4 14.6l2.6-1.8" stroke="#0f7d54" strokeWidth="1" fill="none" strokeLinecap="round" opacity="0.7" />
    </svg>
  );
}

export default function Brand() {
  return (
    <div className="brand" onClick={() => navigate('/')} role="link" tabIndex={0}>
      <BrandMark />
      <div>
        <div className="brand-word">Rasayana</div>
        <div className="brand-sub">by Vayu AI</div>
      </div>
    </div>
  );
}
