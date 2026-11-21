// Pages that only work with AI explain that up front, instead of offering a form that fails after a click.
import { $, S, api, esc, icon } from './core.js';

const PAGES = {
  coach: 'The coach is an AI feature: it reads your progress and answers your questions.',
  listening: 'Listening episodes are written by AI from your chapters, then read aloud using a free Google Gemini key.',
  practice: 'AI practice sets are written by AI. The Gap-fills tab is free and works without it.',
};
let salesOpen = null;
let movedPractice = false;

async function plusLine() {
  if (salesOpen === null) {
    try { salesOpen = !!(await api('/account')).sales_open; } catch { salesOpen = false; }
  }
  return salesOpen ? 'Get <b>Plus</b> under Settings &rarr; Account &amp; Plus, or add your own Claude API key.'
    : '<b>Plus</b> (coming soon) will include it with nothing to set up. Until then you can add your own Claude API key.';
}

async function update(view) {
  const section = $(`#view-${view}`);
  if (!section) return;
  section.querySelector('.needs-ai')?.remove();
  const off = !S.settings?.has_key;
  section.classList.toggle('no-ai', off);
  if (!off || !PAGES[view]) return;
  if (view === 'practice' && !movedPractice) {  // open on the free tab the first time
    movedPractice = true;
    document.querySelector('[data-ptab="gaps"]')?.click();
  }
  const box = document.createElement('div');
  box.className = 'panel needs-ai';
  box.innerHTML = `<span class="needs-ai-icon">${icon('sparkles')}</span>
    <div class="grow"><b>This needs AI</b><p class="small">${esc(PAGES[view])} ${await plusLine()}</p></div>
    <button type="button" class="ghost small" data-go="settings">Open Settings</button>`;
  section.querySelector('.page-head')?.after(box);
}

document.addEventListener('viewchange', e => { if (PAGES[e.detail]) update(e.detail); });
