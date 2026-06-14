// Central icon vocabulary for Rasayana.
// Line icons (lucide), one consistent stroke weight, tinted with theme tokens.
// Keep every glyph classy and on-brand: no colourful emoji anywhere in the UI.
import {
  Thermometer, Wind, Droplets, Waves, Bone, Bandage, Flame, Stethoscope,
  Sun, Activity, Sparkles, Leaf, Atom, Target, Network, BookOpen,
  Info, ArrowUpRight, Search, Compass, GraduationCap, Pill,
  type LucideIcon,
} from 'lucide-react';

export type { LucideIcon };

// Re-exports used across the app, so callers import from one place.
export {
  Sparkles, Leaf, Atom, Target, Network, BookOpen, Stethoscope,
  Info, ArrowUpRight, Search, Compass, GraduationCap, Pill, Flame,
};

// Ailment -> glyph. Distinct, calm, evocative; never alarming.
const AILMENT: Record<string, LucideIcon> = {
  Fever: Thermometer,
  Cough: Wind,
  Diarrhoea: Droplets,
  Dysentery: Waves,
  Rheumatism: Bone,
  Wounds: Bandage,
  Inflammation: Flame,
  Asthma: Stethoscope,
  Jaundice: Sun,
  Diabetes: Activity,
  'Vitality / tonic': Sparkles,
};

export const ailmentIcon = (name: string): LucideIcon => AILMENT[name] ?? Leaf;

// The library's six doors, in order.
export const DOOR_ICON: Record<string, LucideIcon> = {
  '/conditions': Stethoscope,
  '/plants': Leaf,
  '/molecules': Atom,
  '/targets': Target,
  '/families': Network,
  '/sources': BookOpen,
};
