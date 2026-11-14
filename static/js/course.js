// The built-in beginner course: a list of lessons, and each lesson as four steps (words, dialogue, grammar, quiz).
import { $, $$, S, api, esc, icon, md, busy, toast, loading, registerView, show, refreshNav, isActive } from './core.js';

const STEPS = [['words', 'Words'], ['dialogue', 'Dialogue'], ['grammar', 'Grammar'], ['quiz', 'Quiz']];
const C = { overview: null, lesson: null, step: 'words', qi: 0, results: [], answered: null, english: false, startedAt: 0 };

registerView('course', loadCourse);

async function loadCourse() {
  if (S.courseLesson) { const id = S.courseLesson; S.courseLesson = null; return openLesson(id); }
  if (C.lesson) return renderLesson();
  C.overview = await api('/lessons');
  renderList();
}

// ---------- speaking (the computer's own German voice; quietly does nothing without one) ----------
function germanVoice() {
  const vs = window.speechSynthesis?.getVoices() || [];
  return vs.find(v => v.lang === 'de-DE') || vs.find(v => v.lang?.startsWith('de'));
}
function say(text) {
  if (!window.speechSynthesis) return;
  const u = new SpeechSynthesisUtterance(text.replace(/…|\.\.\./g, ' '));
  u.lang = 'de-DE';
  const v = germanVoice();
  if (v) u.voice = v;
  u.rate = 0.9;
  speechSynthesis.cancel();
  speechSynthesis.speak(u);
}
const canSpeak = () => !!window.speechSynthesis;
const hear = text => canSpeak() ? `<button class="icon-btn hear" data-say="${esc(text)}" title="Hear it">${icon('volume')}</button>` : '';

// ---------- the list ----------
function renderList() {
  const o = C.overview;
  $('#course-box').innerHTML = `
    <header class="page-head"><div><p class="eyebrow">Beginner course · A1</p><h1>Deutsch von Anfang an</h1></div>
      <div class="course-progress"><div class="meter-bar"><span style="width:${(100 * o.done) / o.total}%"></span></div><span class="muted small">${o.done} of ${o.total} lessons done</span></div></header>
    <ol class="lesson-list">${o.lessons.map(l => `
      <li class="lesson-row ${l.done ? 'done' : ''} ${l.id === o.next ? 'next' : ''}" data-lesson="${l.id}">
        <span class="lesson-num">${l.done ? icon('check') : l.n}</span>
        <span class="grow"><b>${esc(l.title)}</b><small>${esc(l.subtitle)}</small></span>
        ${l.best != null ? `<span class="muted small">Best: ${l.best}/${l.total}</span>` : `<span class="muted small">${l.words} words</span>`}
        <button class="${l.id === o.next ? '' : 'ghost'} small">${l.done ? 'Review' : l.id === o.next ? 'Start' : 'Open'}</button>
      </li>`).join('')}</ol>
    <p class="muted small center">Each lesson takes about 10 minutes: new words, a short dialogue, one grammar point and a quiz. More lessons are on the way.</p>`;
}

$('#course-box').addEventListener('click', e => {
  const s = e.target.closest('[data-say]');
  if (s) return say(s.dataset.say);
  const row = e.target.closest('[data-lesson]');
  if (row) return openLesson(row.dataset.lesson).catch(err => toast(err.message, 'error'));
  const a = e.target.closest('[data-act]');
  if (a) return act(a.dataset.act, a);
  const st = e.target.closest('[data-step]');
  if (st) { C.step = st.dataset.step; if (C.step === 'quiz') startQuiz(); return renderLesson(); }
  const ch = e.target.closest('[data-choice]');
  if (ch) return answer(ch.dataset.choice);
});

async function openLesson(id) {
  $('#course-box').innerHTML = loading('Opening the lesson...');
  C.lesson = await api(`/lessons/${id}`);
  Object.assign(C, { step: 'words', english: false, startedAt: Date.now() });
  renderLesson();
}

// ---------- a lesson ----------
function shell(inner, foot) {
  const l = C.lesson, at = STEPS.findIndex(s => s[0] === C.step);
  return `<div class="lesson">
    <div class="lesson-top"><button class="link-btn" data-act="back">${icon('left')}All lessons</button>
      <span class="muted small">Lesson ${l.n} of ${l.count}</span></div>
    <h1>${esc(l.title)}</h1><p class="muted">${esc(l.subtitle)}</p>
    <div class="lesson-steps">${STEPS.map(([k, label], i) => `<button data-step="${k}" class="${k === C.step ? 'active' : ''} ${i < at ? 'past' : ''}"><i>${i + 1}</i>${label}</button>`).join('')}</div>
    <div class="lesson-body">${inner}</div>
    ${foot ? `<div class="lesson-foot">${foot}</div>` : ''}</div>`;
}
const nextBtn = (label = 'Next') => `<button data-act="next">${label}${icon('right')}</button>`;

function renderLesson() {
  const l = C.lesson, box = $('#course-box');
  if (C.step === 'words') {
    box.innerHTML = shell(`<div class="word-grid">${l.words.map(w => `<div class="word-card"><div><b>${w.article ? `<span class="art-${w.article}">${w.article}</span> ${esc(w.word)}` : esc(w.de)}</b><span>${esc(w.en)}</span></div>${hear(w.de)}</div>`).join('')}</div>
      <p class="muted small">Say each word aloud. Nouns come with der, die or das: learn them as one piece.</p>`, nextBtn());
  } else if (C.step === 'dialogue') {
    box.innerHTML = shell(`<div class="dialogue ${C.english ? 'show-en' : ''}">${l.dialogue.map(d => `<div class="line"><span class="who">${esc(d.who)}</span><div class="grow"><p>${esc(d.de)}</p><p class="en muted small">${esc(d.en)}</p></div>${hear(d.de)}</div>`).join('')}</div>
      <label class="check"><input type="checkbox" id="dlg-en" ${C.english ? 'checked' : ''}> Show the English</label>
      <p class="muted small">Read it once without the English and see how much you understand. Then read it aloud.</p>`, nextBtn());
    $('#dlg-en').addEventListener('change', e => { C.english = e.target.checked; $('.dialogue').classList.toggle('show-en', C.english); });
  } else if (C.step === 'grammar') {
    box.innerHTML = shell(`<div class="grammar"><h2>${esc(l.grammar.title)}</h2>${md(l.grammar.text)}
      <ul class="examples">${l.grammar.examples.map(x => `<li><span><b>${esc(x.de)}</b><small class="muted">${esc(x.en)}</small></span>${hear(x.de)}</li>`).join('')}</ul></div>`, nextBtn('Start the quiz'));
  } else if (C.step === 'quiz') renderQuiz();
  else renderDone();
  box.scrollIntoView({ block: 'start' });
}

// ---------- the quiz ----------
const norm = s => s.toLowerCase().replace(/[.!?,;:"„“”']/g, '').replace(/\s+/g, ' ').trim();

function startQuiz() { Object.assign(C, { qi: 0, results: [], answered: null }); }

function renderQuiz() {
  const l = C.lesson, q = l.quiz[C.qi], a = C.answered;
  const gap = a ? `<span class="dc-gap filled ${a.right ? 'right' : 'wrong'}">${esc(q.answers[0])}</span>` : '<span class="dc-gap"></span>';
  const prompt = esc(q.prompt).replace('___', gap);
  $('#course-box').innerHTML = shell(`
    <div class="quiz-bar"><div class="meter-bar"><span style="width:${(100 * C.qi) / l.quiz.length}%"></span></div><span class="muted small">${C.qi + 1} of ${l.quiz.length}</span></div>
    <div class="quiz-card ${a ? (a.right ? 'right' : 'wrong') : ''}">
      <p class="muted">${esc(q.cue)}</p>
      <p class="quiz-prompt">${prompt}</p>
      ${q.kind === 'choice'
        ? `<div class="quiz-choices">${q.choices.map((c, i) => `<button class="ghost ${a ? (c === q.answers[0] ? 'right' : c === a.given ? 'wrong' : '') : ''}" data-choice="${esc(c)}" ${a ? 'disabled' : ''}><kbd>${i + 1}</kbd>${esc(c)}</button>`).join('')}</div>`
        : `<input id="quiz-input" class="dc-input" autocomplete="off" spellcheck="false" placeholder="Your answer" value="${a ? esc(a.given) : ''}" ${a ? 'readonly' : ''}>`}
      ${a ? `<p class="quiz-result">${a.right ? `${icon('check')}Richtig!` : `${icon('x')}The answer is <b>${esc(q.answers[0])}</b>`}</p>` : ''}
    </div>`,
    a ? `<button data-act="q-next">${C.qi + 1 < l.quiz.length ? 'Next' : 'Finish'}${icon('right')}</button>`
      : (q.kind === 'text' ? `<button data-act="q-check">Check</button>` : ''));
  $('#quiz-input')?.focus();
}

function answer(given) {
  if (C.step !== 'quiz' || C.answered) return;
  const q = C.lesson.quiz[C.qi];
  const right = q.answers.some(x => norm(x) === norm(given));
  C.answered = { given, right };
  C.results.push(right);
  renderQuiz();
  $('[data-act="q-next"]')?.focus();
}

async function finishQuiz() {
  const l = C.lesson;
  const seconds = Math.min(1200, Math.round((Date.now() - C.startedAt) / 1000));
  if (isActive()) api('/activity', { method: 'POST', body: { kind: 'practice', seconds } }).catch(() => {});
  C.result = await api(`/lessons/${l.id}/complete`, { method: 'POST', body: { results: C.results } });
  C.overview = C.result.overview;
  C.step = 'done';
  renderLesson();
  refreshNav();
}

function renderDone() {
  const l = C.lesson, r = C.result;
  const pct = Math.round((100 * r.right) / r.total);
  $('#course-box').innerHTML = `<div class="lesson done-screen ${r.passed ? 'passed' : 'failed'}">
    <div class="done-mark">${icon(r.passed ? 'check' : 'undo')}</div>
    <h1>${r.passed ? 'Sehr gut!' : 'Fast geschafft'}</h1>
    <p class="done-score"><b>${r.right}</b> of ${r.total} right (${pct}%)</p>
    <p class="muted">${r.passed ? `Lesson ${l.n} is done.` : `You need ${Math.round(l.pass * 100)}% to finish the lesson. Look through the grammar again and have another go.`}</p>
    <div class="row wrap center-row">
      ${l.cards_left ? `<button data-act="cards" class="${r.passed ? '' : 'ghost'}">${icon('cards')}<span>Add ${l.cards_left} words to my flashcards</span></button>` : ''}
      ${r.passed && l.next ? `<button data-act="next-lesson" class="${l.cards_left ? 'ghost' : ''}">Next lesson${icon('right')}</button>` : ''}
      <button data-act="retry" class="ghost">${icon('undo')}<span>${r.passed ? 'Do the quiz again' : 'Try again'}</span></button>
      <button data-act="back" class="link-btn">All lessons</button>
    </div></div>`;
}

async function act(name, btn) {
  const l = C.lesson;
  if (name === 'back') { C.lesson = null; C.overview = await api('/lessons'); return renderList(); }
  if (name === 'next') {
    C.step = STEPS[STEPS.findIndex(s => s[0] === C.step) + 1][0];
    if (C.step === 'quiz') startQuiz();
    return renderLesson();
  }
  if (name === 'q-check') { const v = $('#quiz-input').value.trim(); if (v) answer(v); return; }
  if (name === 'q-next') {
    if (C.qi + 1 < l.quiz.length) { C.qi++; C.answered = null; return renderQuiz(); }
    return busy(btn, '', finishQuiz);
  }
  if (name === 'retry') return openLesson(l.id).then(() => { C.step = 'quiz'; startQuiz(); renderLesson(); });
  if (name === 'next-lesson') return openLesson(l.next);
  if (name === 'cards') return busy(btn, 'Adding...', async () => {
    const r = await api(`/lessons/${l.id}/cards`, { method: 'POST' });
    toast(`Added ${r.added} cards. They show up in Flashcards, a few new ones a day.`);
    l.cards_left = 0;
    refreshNav();
    renderDone();
  });
}

document.addEventListener('keydown', e => {
  if (S.view !== 'course' || C.step !== 'quiz' || !C.lesson) return;
  const q = C.lesson.quiz[C.qi];
  if (e.key === 'Enter') {
    e.preventDefault();
    if (C.answered) $('[data-act="q-next"]')?.click();
    else if (q.kind === 'text') $('[data-act="q-check"]')?.click();
  } else if (!C.answered && q.kind === 'choice' && /^[1-4]$/.test(e.key) && q.choices[+e.key - 1]) answer(q.choices[+e.key - 1]);
});

export function openCourseLesson(id) { S.courseLesson = id; show('course'); }
