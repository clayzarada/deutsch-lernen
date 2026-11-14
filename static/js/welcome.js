// The welcome flow: four questions on first start (level, how you learn, daily goal, starter cards), no API key
// and no textbook needed. Settings has a button to run it again.
import { $, S, api, esc, icon, toast, show, refreshNav } from './core.js';
import { openCourseLesson } from './course.js';

const LEVELS = [
  ['new', 'A1', "I'm new to German", 'Start from the very first words.'],
  ['basics', 'A1', 'I know a few basics', 'Greetings, some words, simple sentences.'],
  ['some', 'A2', 'I can get by in simple conversations', 'Shopping, directions, talking about myself.'],
  ['more', 'B1', "I'm intermediate or higher", 'I want grammar practice and tools for my own material.'],
];
const WAYS = [
  ['course', 'With the built-in course', 'Short lessons with words, dialogues, grammar and quizzes. Nothing else needed.'],
  ['book', 'With my own textbook', 'Import a PDF to read it, do its exercises and practice from it inside the app.'],
  ['both', 'Both', 'The course, plus my own book.'],
];
const GOALS = [[10, 'Easy', '10 minutes a day'], [20, 'Steady', '20 minutes a day'], [30, 'Serious', '30 minutes a day'], [45, 'Intense', '45 minutes a day']];
const PACKS = [
  ['phrases', 'Everyday phrases', '55 cards: greetings, thanks, at the café'],
  ['verbs', 'Core verbs', '158 cards, each with its forms'],
  ['nouns-1', 'Most common nouns', '300 cards with der, die, das and plurals'],
  ['adjectives', 'Core adjectives', '88 cards'],
];

const W = { step: 0, level: 'new', way: 'course', goal: 20, packs: new Set(['phrases']) };

export function startWelcome() {
  Object.assign(W, { step: 0, level: 'new', way: 'course', goal: 20, packs: new Set(['phrases']) });
  $('#welcome').classList.remove('hidden');
  render();
}

const option = (group, value, title, text, on) =>
  `<button type="button" class="w-option ${on ? 'on' : ''}" data-w="${group}" data-value="${value}"><span class="w-radio">${on ? icon('check') : ''}</span><span><b>${esc(title)}</b><small>${esc(text)}</small></span></button>`;

function render() {
  const steps = [
    () => `<div class="w-hero"><span class="flag big"><i></i><i></i><i></i></span><h1>Willkommen!</h1>
        <p>Deutsch lernen helps you learn German a little every day: lessons, flashcards, grammar drills and your own textbook, in one place.</p>
        <p class="muted">Four quick questions set it up for you. It takes under a minute.</p></div>`,
    () => `<h2>How much German do you know?</h2><div class="w-options">${LEVELS.map(([v, , t, d]) => option('level', v, t, d, W.level === v)).join('')}</div>`,
    () => `<h2>How would you like to learn?</h2><div class="w-options">${WAYS.map(([v, t, d]) => option('way', v, t, d, W.way === v)).join('')}</div>`,
    () => `<h2>Pick a daily goal</h2><p class="muted">A small goal you keep beats a big one you skip. You can change it any time.</p>
        <div class="w-options two">${GOALS.map(([v, t, d]) => option('goal', v, t, d, W.goal === v)).join('')}</div>`,
    () => `<h2>Start with some flashcards?</h2><p class="muted">Pick any you like. New cards come in a few at a time, and there are more packs under Flashcards.</p>
        <div class="w-options">${PACKS.map(([v, t, d]) => option('pack', v, t, d, W.packs.has(v))).join('')}</div>`,
  ];
  const last = W.step === steps.length - 1;
  $('#welcome').innerHTML = `<div class="w-card">
    <div class="w-dots">${steps.map((_, i) => `<i class="${i === W.step ? 'on' : i < W.step ? 'past' : ''}"></i>`).join('')}</div>
    <div class="w-body">${steps[W.step]()}</div>
    <div class="w-foot">
      ${W.step ? `<button type="button" class="ghost" data-w-act="back">${icon('left')}Back</button>` : `<button type="button" class="link-btn" data-w-act="skip">Skip setup</button>`}
      <span class="grow"></span>
      <button type="button" data-w-act="${last ? 'finish' : 'next'}">${W.step === 0 ? "Let's go" : last ? 'Start learning' : 'Next'}${icon('right')}</button>
    </div></div>`;
}

async function finish(skip) {
  const level = LEVELS.find(l => l[0] === W.level)[1];
  const body = skip ? {} : { level, daily_minutes: W.goal, use_course: W.way === 'book' ? '0' : '1', packs: [...W.packs] };
  let r;
  try { r = await api('/welcome', { method: 'POST', body }); } catch (err) { return toast(err.message, 'error'); }
  S.settings = r.settings;
  $('#welcome').classList.add('hidden');
  $('#welcome').innerHTML = '';
  refreshNav();
  if (skip) return show('today');
  if (r.added) toast(`Added ${r.added} flashcards to get you started.`);
  if (W.way === 'book') return show('library');
  if (W.level === 'new' || W.level === 'basics') return openCourseLesson('hallo');
  show('course');
}

$('#welcome').addEventListener('click', e => {
  const o = e.target.closest('[data-w]');
  if (o) {
    const v = o.dataset.value;
    if (o.dataset.w === 'pack') W.packs.has(v) ? W.packs.delete(v) : W.packs.add(v);
    else if (o.dataset.w === 'goal') W.goal = +v;
    else {
      W[o.dataset.w] = v;
      // sensible starter cards for the level: phrases for beginners, verbs and nouns for the rest
      if (o.dataset.w === 'level') W.packs = new Set(v === 'new' || v === 'basics' ? ['phrases'] : ['verbs', 'nouns-1']);
      if (o.dataset.w === 'level' && v === 'more') W.way = 'book';
    }
    return render();
  }
  const a = e.target.closest('[data-w-act]')?.dataset.wAct;
  if (a === 'next') { W.step++; render(); }
  else if (a === 'back') { W.step--; render(); }
  else if (a === 'skip') finish(true);
  else if (a === 'finish') finish(false);
});
