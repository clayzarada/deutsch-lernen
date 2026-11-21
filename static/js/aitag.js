// The "AI-written" label. Everything Claude writes for the learner (practice sets, AI flashcards, listening
// scripts, coach answers, writing feedback, explanations, look-ups, daily plans) carries this one small tag, so
// it's always clear what was written by people and checked by rules, and what may contain AI mistakes.
// Built-in lessons, packs, drills and the offline dictionary are never tagged.
import { icon } from './core.js';

export const AI_TIP = 'Written by AI. It may contain mistakes.';

/** The tag as HTML, to put next to a heading or at the start of an AI-written block. */
export function aiTag(cls = '') {
  return `<span class="ai-tag ${cls}" title="${AI_TIP}">${icon('sparkles')}<span>AI-written</span></span>`;
}

/** Cards made by AI carry the tag "ai" (see app/main.py). */
export function isAiCard(c) {
  try { return JSON.parse(c.tags || '[]').includes('ai'); } catch { return false; }
}
