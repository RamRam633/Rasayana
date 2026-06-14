import type { ComponentType } from 'react';
import L1 from './lessons/L1Systems';
import L2 from './lessons/L2Doshas';
import L3 from './lessons/L3Rasa';
import L4 from './lessons/L4Molecule';
import L5 from './lessons/L5Target';
import L6 from './lessons/L6Evidence';

export interface Lesson {
  slug: string; num: number; title: string; kicker: string; summary: string; Component: ComponentType;
}

export const LESSONS: Lesson[] = [
  { slug: 'systems', num: 1, title: 'The Five Systems', kicker: 'Foundations',
    summary: 'Ayurveda, Unani, Siddha, Sowa Rigpa, Yoga, five living traditions, one idea: health is balance.', Component: L1 },
  { slug: 'doshas', num: 2, title: 'Doshas & Elements', kicker: 'The framework',
    summary: 'Five elements, three doshas, and why opposites heal. Find your constitution.', Component: L2 },
  { slug: 'tastes', num: 3, title: 'The Six Tastes', kicker: 'The framework',
    summary: 'How taste becomes medicine: the rasa wheel, plus virya, vipaka and prabhava.', Component: L3 },
  { slug: 'molecule', num: 4, title: 'Plant to Molecule', kicker: 'The chemistry',
    summary: 'A plant is a chemical factory, alkaloids, terpenes, polyphenols.', Component: L4 },
  { slug: 'target', num: 5, title: 'Tradition meets Pharmacology', kicker: 'The chemistry',
    summary: 'Plant → molecule → protein target, live from the graph. A remedy becomes a mechanism.', Component: L5 },
  { slug: 'evidence', num: 6, title: 'Reading the Evidence', kicker: 'The discipline',
    summary: 'Tradition vs preclinical vs clinical, and the safety every healer needs.', Component: L6 },
];

export const lessonBySlug = (slug: string) => LESSONS.find((l) => l.slug === slug);
