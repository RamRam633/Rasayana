import { useEffect, useRef } from 'react';

// A living "molecular constellation": drifting nodes (plant ↔ molecule ↔ target)
// linked when near, in herb / essence / mind colors, on warm paper. The cursor
// gently gathers nearby nodes; a click sends a gold ripple. Pure 2D canvas.
const COLORS = ['#1a9d6b', '#1a9d6b', '#1a9d6b', '#28b67e', '#b8860b', '#6d3bd4'];
const TAU = Math.PI * 2;

export default function HeroCanvas() {
  const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const canvas = ref.current!;
    const ctx = canvas.getContext('2d')!;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    let w = 0, h = 0, raf = 0;
    const mouse = { x: -999, y: -999, active: false };
    let ripples: { x: number; y: number; t: number }[] = [];
    type N = { x: number; y: number; vx: number; vy: number; r: number; c: string };
    let nodes: N[] = [];

    const resize = () => {
      const rect = canvas.getBoundingClientRect();
      w = rect.width; h = rect.height;
      canvas.width = w * dpr; canvas.height = h * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const count = Math.max(26, Math.min(78, Math.floor((w * h) / 14000)));
      nodes = Array.from({ length: count }, () => ({
        x: Math.random() * w, y: Math.random() * h,
        vx: (Math.random() - 0.5) * 0.18, vy: (Math.random() - 0.5) * 0.18,
        r: 1.2 + Math.random() * 2.2, c: COLORS[Math.floor(Math.random() * COLORS.length)],
      }));
    };
    const onMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      mouse.x = e.clientX - rect.left; mouse.y = e.clientY - rect.top;
      mouse.active = mouse.x >= 0 && mouse.y >= 0 && mouse.x <= w && mouse.y <= h;
    };
    const onClick = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      const x = e.clientX - rect.left, y = e.clientY - rect.top;
      if (x >= 0 && y >= 0 && x <= w && y <= h) ripples.push({ x, y, t: 0 });
    };
    const frame = () => {
      ctx.clearRect(0, 0, w, h);
      for (const n of nodes) {
        n.x += n.vx; n.y += n.vy;
        if (n.x < 0 || n.x > w) n.vx *= -1;
        if (n.y < 0 || n.y > h) n.vy *= -1;
        if (mouse.active) {
          const dx = mouse.x - n.x, dy = mouse.y - n.y, d = Math.hypot(dx, dy);
          if (d < 150 && d > 0.1) { const f = ((150 - d) / 150) * 0.04; n.vx += (dx / d) * f; n.vy += (dy / d) * f; }
        }
        n.vx *= 0.995; n.vy *= 0.995;
      }
      for (let i = 0; i < nodes.length; i++) {
        for (let k = i + 1; k < nodes.length; k++) {
          const a = nodes[i], b = nodes[k];
          const d = Math.hypot(a.x - b.x, a.y - b.y);
          if (d < 120) {
            ctx.strokeStyle = `rgba(26,157,107,${(1 - d / 120) * 0.16})`;
            ctx.lineWidth = 0.7;
            ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
          }
        }
      }
      for (const n of nodes) {
        ctx.fillStyle = n.c; ctx.globalAlpha = 0.55;
        ctx.beginPath(); ctx.arc(n.x, n.y, n.r, 0, TAU); ctx.fill();
      }
      ctx.globalAlpha = 1;
      ripples = ripples.filter((r) => r.t < 1);
      for (const r of ripples) {
        r.t += 0.02;
        ctx.strokeStyle = `rgba(184,134,11,${(1 - r.t) * 0.4})`;
        ctx.lineWidth = 1.5;
        ctx.beginPath(); ctx.arc(r.x, r.y, r.t * 180, 0, TAU); ctx.stroke();
      }
      raf = requestAnimationFrame(frame);
    };

    resize();
    frame();
    if (reduced) cancelAnimationFrame(raf);
    const ro = new ResizeObserver(resize); ro.observe(canvas);
    window.addEventListener('mousemove', onMove);
    window.addEventListener('click', onClick);
    return () => {
      cancelAnimationFrame(raf); ro.disconnect();
      window.removeEventListener('mousemove', onMove);
      window.removeEventListener('click', onClick);
    };
  }, []);
  return <canvas ref={ref} className="hero-canvas" aria-hidden="true" />;
}
