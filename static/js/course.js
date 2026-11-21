// The built-in course, A1 to B1: the lessons grouped by level, each lesson as four steps (words, dialogue, grammar,
// quiz), and a level test at the end of each level.
import { $, S, api, esc, icon, md, busy, toast, loading, registerView, show, refreshNav, isActive } from './core.js';

const STEPS = [['words', 'Words'], ['dialogue', 'Dialogue'], ['grammar', 'Grammar'], ['quiz', 'Quiz']];
const C = { overview: null, lesson: null, test: null, step: 'words', qi: 0, results: [], answered: null, english: false,
  startedAt: 0, open: new Set() };

registerView('course', loadCourse);

async function loadCourse() {
  if (S.courseLesson) { const id = S.courseLesson; S.courseLesson = null; return openLesson(id); }
  if (C.lesson || C.test) return C.test ? renderTest() : renderLesson();
  if (!C.overview) $('#course-box').innerHTML = loading('Opening the course...');
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

// ---------- the list, one section per level ----------
function levelHtml(lv, o) {
  const mine = o.lessons.filter(l => l.level === lv.level);
  const t = lv.test;
  const open = C.open.has(lv.level) || mine.some(l => l.id === o.next) || (!o.next && lv === o.levels[0]);
  const testNote = t.passed ? 'Level test passed' : t.best != null ? `Level test: best ${t.best}/${t.total}` : 'Level test not taken yet';
  return `<details class="course-level" data-level="${lv.level}" ${open ? 'open' : ''}>
    <summary><span class="level-badge">${lv.level}</span>
      <span class="grow"><b>${lv.level}: ${lv.done} of ${lv.total} lessons</b><small class="${t.passed ? 'level-passed' : ''}">${t.passed ? icon('check') : ''}<span>${testNote}</span></small></span>
      <span class="meter-bar level-meter" aria-hidden="true"><span style="width:${(100 * lv.done) / lv.total}%"></span></span></summary>
    <ol class="lesson-list">${mine.map(l => `
      <li class="lesson-row ${l.done ? 'done' : ''} ${l.id === o.next ? 'next' : ''}" data-lesson="${l.id}">
        <span class="lesson-num">${l.done ? icon('check') : l.ln}</span>
        <span class="grow"><b>${esc(l.title)}</b><small>${l.unit ? `<span class="lesson-unit">${esc(l.unit)}</span> · ` : ''}<span>${esc(l.subtitle)}</span></small></span>
        ${l.best != null ? `<span class="muted small">Best: ${l.best}/${l.total}</span>` : `<span class="muted small">${l.words} words</span>`}
        <button class="${l.id === o.next ? '' : 'ghost'} small">${l.done ? 'Review' : l.id === o.next ? 'Start' : 'Open'}</button>
      </li>`).join('')}
      <li class="lesson-row test-row ${t.passed ? 'done' : ''}" data-test="${lv.level}">
        <span class="lesson-num">${icon(t.passed ? 'check' : 'target')}</span>
        <span class="grow"><b>${lv.level} test</b><small>Words and grammar from all ${lv.level} lessons. ${Math.round(lv.pass * 100)}% passes the level.</small></span>
        ${t.best != null ? `<span class="muted small">Best: ${t.best}/${t.total}</span>` : ''}
        <button class="${lv.done === lv.total && !t.passed ? '' : 'ghost'} small">${t.tries ? 'Take it again' : 'Take the test'}</button>
      </li></ol></details>`;
}

function renderList() {
  const o = C.overview;
  const span = o.levels.length > 1 ? `${o.levels[0].level}–${o.levels[o.levels.length - 1].level}` : o.levels[0].level;
  $('#course-box').innerHTML = `
    <header class="page-head"><div><p class="eyebrow">Course · ${span}</p><h1>Deutsch von Anfang an</h1></div>
      <div class="course-progress"><div class="meter-bar"><span style="width:${(100 * o.done) / o.total}%"></span></div><span class="muted small">${o.done} of ${o.total} lessons done</span></div></header>
    ${o.levels.map(lv => levelHtml(lv, o)).join('')}
    <p class="muted small center">Each lesson takes about 10 minutes: new words, a short dialogue, one grammar point and a quiz. Open any lesson you like; the next one is marked.</p>`;
  for (const d of document.querySelectorAll('#course-box details.course-level')) {
    d.addEventListener('toggle', () => { if (d.open) C.open.add(d.dataset.level); else C.open.delete(d.dataset.level); });
  }
}

$('#course-box').addEventListener('click', e => {
  const s = e.target.closest('[data-say]');
  if (s) return say(s.dataset.say);
  const row = e.target.closest('[data-lesson]');
  if (row) return openLesson(row.dataset.lesson).catch(err => toast(err.message, 'error'));
  const tr = e.target.closest('[data-test]');
  if (tr) return openTest(tr.dataset.test).catch(err => toast(err.message, 'error'));
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
  C.test = null;
  Object.assign(C, { step: 'words', english: false, startedAt: Date.now() });
  renderLesson();
}

// ---------- a lesson ----------
function shell(inner, foot) {
  if (C.test) return testShell(inner, foot);
  const l = C.lesson, at = STEPS.findIndex(s => s[0] === C.step);
  return `<div class="lesson">
    <div class="lesson-top"><button class="link-btn" data-act="back">${icon('left')}All lessons</button>
      <span class="muted small">${l.level} · Lesson ${l.ln} of ${l.level_count}</span></div>
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

// ---------- the level test (same questions and screen as a lesson quiz) ----------
async function openTest(level) {
  $('#course-box').innerHTML = loading('Putting the test together...');
  C.test = await api(`/levels/${level}/test`);
  C.lesson = null;
  Object.assign(C, { step: 'quiz', startedAt: Date.now() });
  startQuiz();
  renderTest();
}

function testShell(inner, foot) {
  const t = C.test;
  return `<div class="lesson">
    <div class="lesson-top"><button class="link-btn" data-act="back">${icon('left')}All lessons</button>
      <span class="muted small">${t.level} test</span></div>
    <h1>${t.level} test</h1><p class="muted">Words and grammar from the ${t.lessons} ${t.level} lessons. You need ${Math.round(t.pass * 100)}% to pass the level.</p>
    <div class="lesson-body">${inner}</div>
    ${foot ? `<div class="lesson-foot">${foot}</div>` : ''}</div>`;
}

function renderTest() {
  if (C.step === 'quiz') renderQuiz(); else renderTestDone();
  $('#course-box').scrollIntoView({ block: 'start' });
}

function renderTestDone() {
  const t = C.test, r = C.result;
  const pct = Math.round((100 * r.right) / r.total);
  const lv = r.overview.levels.find(x => x.level === t.level);
  const next = r.overview.levels[r.overview.levels.indexOf(lv) + 1];
  $('#course-box').innerHTML = `<div class="lesson done-screen ${r.passed ? 'passed' : 'failed'}">
    <div class="done-mark">${icon(r.passed ? 'check' : 'undo')}</div>
    <h1>${r.passed ? 'Sehr gut!' : 'Noch nicht ganz'}</h1>
    <p class="done-score"><b>${r.right}</b> of ${r.total} right (${pct}%)</p>
    <p class="muted">${r.passed ? `You passed the ${t.level} test.` : `You need ${Math.round(t.pass * 100)}% to pass. Go back to the lessons where you were unsure and try again whenever you like.`}</p>
    <div class="row wrap center-row">
      ${r.passed && next ? `<button data-act="open-level" data-level="${next.level}">Go on to ${next.level}${icon('right')}</button>` : ''}
      <button data-act="test-retry" class="ghost">${icon('undo')}<span>${r.passed ? 'Take it again' : 'Try again'}</span></button>
      <button data-act="back" class="link-btn">All lessons</button>
    </div></div>`;
}

// ---------- the quiz (a lesson's or a level test's) ----------
const norm = s => s.toLowerCase().replace(/[.!?,;:"„“”']/g, '').replace(/\s+/g, ' ').trim();
const current = () => C.test || C.lesson;

function startQuiz() { Object.assign(C, { qi: 0, results: [], answered: null }); }

function renderQuiz() {
  const quiz = current().quiz, q = quiz[C.qi], a = C.answered;
  const gap = a ? `<span class="dc-gap filled ${a.right ? 'right' : 'wrong'}">${esc(q.answers[0])}</span>` : '<span class="dc-gap"></span>';
  const prompt = esc(q.prompt).replace('___', gap);
  $('#course-box').innerHTML = shell(`
    <div class="quiz-bar"><div class="meter-bar"><span style="width:${(100 * C.qi) / quiz.length}%"></span></div><span class="muted small">${C.qi + 1} of ${quiz.length}</span></div>
    <div class="quiz-card ${a ? (a.right ? 'right' : 'wrong') : ''}">
      <p class="muted">${esc(q.cue)}</p>
      <p class="quiz-prompt">${prompt}</p>
      ${q.kind === 'choice'
        ? `<div class="quiz-choices">${q.choices.map((c, i) => `<button class="ghost ${a ? (c === q.answers[0] ? 'right' : c === a.given ? 'wrong' : '') : ''}" data-choice="${esc(c)}" ${a ? 'disabled' : ''}><kbd>${i + 1}</kbd>${esc(c)}</button>`).join('')}</div>`
        : `<input id="quiz-input" class="dc-input" autocomplete="off" spellcheck="false" placeholder="Your answer" aria-label="Your answer" value="${a ? esc(a.given) : ''}" ${a ? 'readonly' : ''}>`}
      ${a ? `<p class="quiz-result">${a.right ? `${icon('check')}Richtig!` : `${icon('x')}The answer is <b>${esc(q.answers[0])}</b>`}</p>` : ''}
    </div>`,
    a ? `<button data-act="q-next">${C.qi + 1 < quiz.length ? 'Next' : 'Finish'}${icon('right')}</button>`
      : (q.kind === 'text' ? `<button data-act="q-check">Check</button>` : ''));
  $('#quiz-input')?.focus();
}

function answer(given) {
  if (C.step !== 'quiz' || C.answered) return;
  const q = current().quiz[C.qi];
  const right = q.answers.some(x => norm(x) === norm(given));
  C.answered = { given, right };
  C.results.push(right);
  renderQuiz();
  $('[data-act="q-next"]')?.focus();
}

async function finishQuiz() {
  const seconds = Math.min(1800, Math.round((Date.now() - C.startedAt) / 1000));
  if (isActive()) api('/activity', { method: 'POST', body: { kind: 'practice', seconds } }).catch(() => {});
  const url = C.test ? `/levels/${C.test.level}/test/complete` : `/lessons/${C.lesson.id}/complete`;
  C.result = await api(url, { method: 'POST', body: { results: C.results } });
  C.overview = C.result.overview;
  C.step = 'done';
  if (C.test) renderTest(); else renderLesson();
  refreshNav();
}

function renderDone() {
  const l = C.lesson, r = C.result;
  const pct = Math.round((100 * r.right) / r.total);
  const lv = r.overview.levels.find(x => x.level === l.level);
  const levelDone = r.passed && lv && lv.done === lv.total && !lv.test.passed;
  $('#course-box').innerHTML = `<div class="lesson done-screen ${r.passed ? 'passed' : 'failed'}">
    <div class="done-mark">${icon(r.passed ? 'check' : 'undo')}</div>
    <h1>${r.passed ? 'Sehr gut!' : 'Fast geschafft'}</h1>
    <p class="done-score"><b>${r.right}</b> of ${r.total} right (${pct}%)</p>
    <p class="muted">${r.passed ? `Lesson ${l.ln} of ${l.level} is done.` : `You need ${Math.round(l.pass * 100)}% to finish the lesson. Look through the grammar again and have another go.`}</p>
    ${levelDone ? `<p class="muted">That was the last ${l.level} lesson. The ${l.level} test checks the whole level.</p>` : ''}
    <div class="row wrap center-row">
      ${l.cards_left ? `<button data-act="cards" class="${r.passed ? '' : 'ghost'}">${icon('cards')}<span>Add ${l.cards_left} words to my flashcards</span></button>` : ''}
      ${levelDone ? `<button data-act="level-test" data-level="${l.level}" class="${l.cards_left ? 'ghost' : ''}">Take the ${l.level} test${icon('right')}</button>` : ''}
      ${r.passed && l.next && !levelDone ? `<button data-act="next-lesson" class="${l.cards_left ? 'ghost' : ''}">Next lesson${icon('right')}</button>` : ''}
      <button data-act="retry" class="ghost">${icon('undo')}<span>${r.passed ? 'Do the quiz again' : 'Try again'}</span></button>
      <button data-act="back" class="link-btn">All lessons</button>
    </div></div>`;
}

async function act(name, btn) {
  const l = C.lesson;
  if (name === 'back') { C.lesson = null; C.test = null; C.overview = await api('/lessons'); return renderList(); }
  if (name === 'next') {
    C.step = STEPS[STEPS.findIndex(s => s[0] === C.step) + 1][0];
    if (C.step === 'quiz') startQuiz();
    return renderLesson();
  }
  if (name === 'q-check') { const v = $('#quiz-input').value.trim(); if (v) answer(v); return; }
  if (name === 'q-next') {
    if (C.qi + 1 < current().quiz.length) { C.qi++; C.answered = null; return renderQuiz(); }
    return busy(btn, '', finishQuiz);
  }
  if (name === 'retry') return openLesson(l.id).then(() => { C.step = 'quiz'; startQuiz(); renderLesson(); });
  if (name === 'next-lesson') return openLesson(l.next);
  if (name === 'level-test') return openTest(btn.dataset.level);
  if (name === 'test-retry') return openTest(C.test.level);
  if (name === 'open-level') {
    C.test = null; C.lesson = null; C.open.add(btn.dataset.level);
    C.overview = await api('/lessons');
    return renderList();
  }
  if (name === 'cards') return busy(btn, 'Adding...', async () => {
    const r = await api(`/lessons/${l.id}/cards`, { method: 'POST' });
    toast(`Added ${r.added} cards. They show up in Flashcards, a few new ones a day.`);
    l.cards_left = 0;
    refreshNav();
    renderDone();
  });
}

document.addEventListener('keydown', e => {
  if (S.view !== 'course' || C.step !== 'quiz' || !current()) return;
  if (e.target.closest?.('summary')) return;
  const q = current().quiz[C.qi];
  if (e.key === 'Enter') {
    e.preventDefault();
    if (C.answered) $('[data-act="q-next"]')?.click();
    else if (q.kind === 'text') $('[data-act="q-check"]')?.click();
  } else if (!C.answered && q.kind === 'choice' && /^[1-4]$/.test(e.key) && q.choices[+e.key - 1]) answer(q.choices[+e.key - 1]);
});

export function openCourseLesson(id) { S.courseLesson = id; show('course'); }
