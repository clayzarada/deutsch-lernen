// Progress page: honest measurement instead of streaks. Words known, an estimated level per skill with the reason
// behind it, the weekly study goal, and the optional monthly level check (rule-based, no AI, works offline).
// Every sentence is one text node, so the Turkish dictionary can translate it whole.
import { $, S, api, esc, icon, toast, loading, registerView, refreshNav, weekGoalText } from './core.js';

registerView('progress', loadProgress);

const SKILL_NAME = { vocab: 'Vocabulary', grammar: 'Grammar', writing: 'Writing', reading: 'Reading' };
const SECTION_NAME = { vocab: 'Vocabulary', case: 'Cases and articles', verb: 'Verb forms' };
const AREA_NAME = {
  articles_nom_akk: 'Articles: nominative and accusative', pronouns_akk: 'Pronouns: accusative', present: 'Present tense',
  articles_dat: 'Articles: dative', pronouns_dat: 'Pronouns: dative and reflexive', prepositions: 'Prepositions and their cases',
  perfekt: 'Perfekt', separable: 'Separable verbs', adjectives: 'Adjective endings', relative: 'Relative pronouns and wer/wen/wem',
  praeteritum: 'Präteritum', future_konj2: 'Futur I and Konjunktiv II', genitive: 'Genitive', plusq_fut2: 'Plusquamperfekt and Futur II',
};
const DAY = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

let data = null;
const L = i => (i == null ? null : data?.levels?.[i] || ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'][i]);
const fmtDate = d => new Date(d + 'T12:00').toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' });

async function loadProgress() {
  if (!data) $('#lv-body').innerHTML = loading('Adding up your progress...');
  data = await api('/level');
  render();
}

function render() {
  const d = data;
  $('#lv-body').innerHTML = `
    ${verdictPanel(d)}
    <div class="lv-grid">${d.skills.map(skillCard).join('')}</div>
    <div class="lv-two">
      ${wordsPanel(d.known)}
      ${weekPanel(d.week)}
    </div>
    ${checkPanel(d)}`;
}

// ---------- the overall picture ----------
function verdictPanel(d) {
  const v = d.verdict;
  const lines = [];
  if (v.ready != null) {
    lines.push(`<p class="lv-ready">${icon('check')}<span>${`The evidence says you're ready for ${L(v.ready)}.`}</span></p>`);
    lines.push(`<p><button class="ghost small" data-lv-set="${L(v.ready)}">${`Set my level to ${L(v.ready)}`}</button></p>`);
  }
  if (v.weakest) {
    const s = d.skills.find(x => x.skill === v.weakest);
    lines.push(`<p><span>What's holding you back most:</span> <b>${SKILL_NAME[v.weakest]}</b></p>`);
    const m = moveUp(s);
    if (m) lines.push(`<p class="muted small">${m}</p>`);
  }
  if (v.rated < 2) lines.push(`<p class="muted">${'Not enough evidence yet for an overall picture. It fills in as you study, or take the level check below.'}</p>`);
  const set = d.setting != null ? `<p class="muted small">${`Your level setting: ${L(d.setting)}`}</p>` : '';
  return `<div class="panel lv-verdict"><h2>Where you stand</h2>${lines.join('')}${set}</div>`;
}

// ---------- one card per skill ----------
function levelChip(s) {
  if (!s.enough) return '<span class="lv-chip none">Not enough data yet</span>';
  if (s.level == null) return '<span class="lv-chip low">Below A1</span>';
  return `<span class="lv-chip">${L(s.level)}</span>`;
}

function why(s) {
  if (s.skill === 'vocab') {
    if (!s.enough) return 'Not enough data yet: fewer than 30 words known or being learned. Flashcards, lessons and reading add words here.';
    if (s.source === 'check') return `From your level check on ${fmtDate(s.check_date)}.`;
    const b = s.bands[Math.max(0, (s.level ?? 0))] || s.bands[0];
    return `${b.known} known and ${b.learning} being learned of the ${b.top} most common German words (${b.pct}%).`;
  }
  if (s.skill === 'grammar') {
    if (!s.enough) return `Not enough data yet: fewer than 30 declension and verb answers in the last ${s.days} days.`;
    if (s.source === 'check') return `From your level check on ${fmtDate(s.check_date)}.`;
    return `Based on ${s.answers} declension and verb answers in the last ${s.days} days. An area counts as solid at 80% right over 10 or more answers.`;
  }
  if (s.skill === 'writing') {
    if (!s.enough) return 'No texts yet. Texts you write on the Writing page (marked by AI) are counted here.';
    if (s.passed === 1) return `${s.passed} of ${s.texts} texts passed at its level (marked by AI). One text is a first sign, not proof.`;
    return `${s.passed} of ${s.texts} texts passed at their level (marked by AI).`;
  }
  if (s.skill === 'reading') {
    if (s.source === 'texts') return `${s.comfortable} of ${s.texts} texts read with 90% or more of the words known.`;
    if (!s.enough) return 'Not enough data yet: reading is estimated from your vocabulary for now.';
    return 'Estimated from your vocabulary: comfortable reading is mostly a matter of knowing the words.';
  }
  return '';
}

function moveUp(s) {
  if (s.skill === 'vocab' && s.next) return `To reach ${L(s.next.level)}: about ${s.next.words} more of the ${s.next.top} most common words.`;
  if (s.skill === 'vocab') return 'You know most of the common words. Reading widely moves you further.';
  if (s.skill === 'grammar') {
    if (!s.next) return 'The drills go up to B2. Writing and reading take it further.';
    return `To reach ${L(s.next.level)}: make these areas solid in Declensions and Verbs.`;
  }
  if (s.skill === 'writing') {
    const nxt = s.level == null ? 0 : s.level + 1;
    return nxt < 6 ? `To reach ${L(nxt)}: pass two texts at ${L(nxt)} on the Writing page.` : '';
  }
  if (s.skill === 'reading') return s.source === 'texts' ? 'Read texts a level higher until 90% of their words feel familiar.' : 'Grows with your vocabulary.';
  return '';
}

function skillCard(s) {
  let extra = '';
  if (s.skill === 'grammar') {
    if (s.next?.areas?.length) extra += `<div class="lv-areas">${s.next.areas.map(a => `<span class="chip">${esc(AREA_NAME[a] || a)}</span>`).join('')}</div>`;
    extra += caseBars(s.cases);
  }
  if (s.skill === 'vocab' && s.bands) {
    extra += `<div class="lv-bands">${s.bands.map(b => `<div class="lv-band" title="${b.known} + ${b.learning}"><span>${`Top ${b.top}`}</span>
      <i class="lv-meter"><i style="width:${b.pct}%"></i></i><small>${b.pct}%</small></div>`).join('')}</div>`;
  }
  return `<div class="panel lv-skill"><div class="lv-skill-head"><h3>${SKILL_NAME[s.skill]}</h3>${levelChip(s)}</div>
    <p class="small">${esc(why(s))}</p><p class="muted small">${esc(moveUp(s))}</p>${extra}</div>`;
}

function caseBars(cases) {
  if (!cases?.some(c => c.n)) return '<p class="muted small">Accuracy per case appears once you practice declensions.</p>';
  return `<div class="lv-cases" role="list" aria-label="Accuracy per case">${cases.map(c => `
    <div class="lv-case" role="listitem"><span>${esc(c.name)}</span>
      <i class="lv-meter ${c.pct == null ? '' : c.pct >= 80 ? 'ok' : c.pct >= 60 ? 'mid' : 'bad'}"><i style="width:${c.pct || 0}%"></i></i>
      <small>${c.pct == null ? '–' : c.pct + '%'}</small><small class="muted">${c.n ? `${c.n} answers` : ''}</small></div>`).join('')}</div>`;
}

// ---------- words you know ----------
function lineChart(hist) {
  if (!hist || hist.length < 2) return '<p class="muted small">The graph fills in day by day.</p>';
  const W = 520, H = 150, P = 28;
  const max = Math.max(5, ...hist.map(h => h.known));
  const x = i => P + (i * (W - 2 * P)) / (hist.length - 1);
  const y = v => H - P + 6 - (v * (H - P - 4)) / max;
  const pts = hist.map((h, i) => `${x(i).toFixed(1)},${y(h.known).toFixed(1)}`).join(' ');
  const last = hist[hist.length - 1];
  return `<svg class="lv-line" viewBox="0 0 ${W} ${H}" role="img" aria-label="${`Known words over time: ${last.known} now`}">
    <line x1="${P}" y1="${y(0)}" x2="${W - P}" y2="${y(0)}" class="axis"/>
    <line x1="${P}" y1="${y(max)}" x2="${W - P}" y2="${y(max)}" class="grid"/>
    <text x="${P - 4}" y="${y(max) + 4}" text-anchor="end">${max}</text><text x="${P - 4}" y="${y(0) + 4}" text-anchor="end">0</text>
    <polyline points="${pts}" class="known"/>
    <circle cx="${x(hist.length - 1)}" cy="${y(last.known)}" r="3.5" class="known-dot"/>
    <text x="${P}" y="${H - 4}">${fmtDate(hist[0].date)}</text><text x="${W - P}" y="${H - 4}" text-anchor="end">${fmtDate(last.date)}</text>
  </svg>`;
}

function wordsPanel(k) {
  return `<div class="panel"><h2>Words you know</h2>
    <div class="lv-nums"><div><b>${k.known}</b><span>known</span></div><div><b>${k.learning}</b><span>being learned</span></div></div>
    ${lineChart(k.history)}
    <p class="muted small">A word counts as known when its flashcard has reached a 21-day interval, or when you mark it known yourself.</p></div>`;
}

// ---------- this week ----------
function weekDots(w) {
  return `<div class="lv-days">${w.studied.map((on, i) => `<span class="lv-day ${on ? 'on' : ''} ${i === w.today_index ? 'today' : ''}" title="${DAY[i]}">${DAY[i]}</span>`).join('')}</div>`;
}

function weekPanel(w) {
  return `<div class="panel"><h2>Weekly goal</h2>
    <p class="lv-week-text">${weekGoalText(w)}</p>
    ${weekDots(w)}
    <p class="muted small">${w.met ? 'Goal reached for this week. Anything more is a bonus.' : 'Rest days are part of learning. Missing a day never resets anything.'}</p>
    <p class="small"><a href="#" data-go="settings">Change the weekly goal in Settings</a></p></div>`;
}

// ---------- the monthly level check ----------
function resultLine(r) {
  const part = v => (v == null ? 'Below A1' : L(v));
  return `<span class="chip">Vocabulary <b>${part(r.vocab)}</b></span><span class="chip">Cases <b>${part(r.case)}</b></span><span class="chip">Verbs <b>${part(r.verb)}</b></span>`;
}

function checkPanel(d) {
  const offer = d.check_due
    ? `<p>${d.days_since_check == null ? 'Want to see where you are? The level check takes about 10 minutes. It is optional and uses no AI.' : `Your last level check was ${d.days_since_check} days ago. Take a new one if you like: about 10 minutes, no AI.`}</p>`
    : `<p class="muted small">${d.days_since_check === 0 ? 'Your last check was today. A new one makes most sense after about a month.'
      : `Last check ${d.days_since_check} days ago. A new one makes most sense after about a month.`}</p>`;
  const hist = d.checks.length ? `<table class="lv-hist"><thead><tr><th>Date</th><th>Overall</th><th>Parts</th><th>Right</th></tr></thead><tbody>
    ${d.checks.map(c => `<tr><td>${fmtDate(c.date)}</td><td><b>${c.overall == null ? 'Below A1' : L(c.overall)}</b></td><td>${resultLine(c)}</td><td>${c.right}/${c.total}</td></tr>`).join('')}</tbody></table>` : '';
  return `<div class="panel lv-check-panel"><div class="panel-head"><div><h2>Level check</h2>
    <p class="muted small">Words, cases and verb forms. The questions get harder when you're right and easier when you're not.</p></div>
    <button id="lv-start" class="${d.check_due ? '' : 'ghost'}">${icon('target')}<span>Start the level check</span></button></div>
    ${offer}${hist}</div>`;
}

// The check runs in its own panel above the page.
const C = { id: null, q: null, answered: false };

async function startCheck() {
  const r = await api('/level/check/start', { method: 'POST' });
  Object.assign(C, { id: r.id, q: r.question, answered: false });
  $('#lv-body').classList.add('hidden');
  $('#lv-check').classList.remove('hidden');
  drawQuestion();
  $('#view-progress').scrollIntoView({ block: 'start' });
}

function drawQuestion() {
  const q = C.q;
  const head = `<div class="lv-q-head"><span class="muted small">${`Question ${q.n} of ${q.total}`}</span><span class="chip">${SECTION_NAME[q.section]}</span>
    <button class="link-btn" id="lv-quit">Stop the check</button></div><i class="lv-meter lv-q-meter"><i style="width:${(100 * (q.n - 1)) / q.total}%"></i></i>`;
  let body;
  if (q.kind === 'choice') {
    body = `<p class="muted small">What does this word mean?</p><p class="lv-q-prompt" data-no-i18n lang="de">${esc(q.prompt)}</p>
      <div class="lv-choices">${q.choices.map((c, i) => `<button class="ghost" data-lv-choice="${i}" data-no-i18n>${esc(c)}</button>`).join('')}</div>`;
  } else {
    const hint = q.section === 'verb' ? `Write the verb form in the ${q.tense}.` : 'Fill the gap with the words below, in the right form.';
    body = `<p class="muted small">${esc(hint)}</p>
      <p class="lv-q-prompt" data-no-i18n lang="de">${esc(q.prompt)}</p>
      ${q.cue ? `<p class="lv-q-cue">${esc(q.cue)}</p>` : ''}
      <form id="lv-form" class="row"><label class="grow lv-answer"><input id="lv-answer" autocomplete="off" autocapitalize="off" spellcheck="false" lang="de" aria-label="Your answer"></label>
      <button type="submit">Check</button></form>`;
  }
  $('#lv-check').innerHTML = `<div class="panel lv-q">${head}${body}<div id="lv-feedback" aria-live="polite"></div></div>`;
  $('#lv-answer')?.focus();
  ($('[data-lv-choice]') && !$('#lv-answer')) && $('[data-lv-choice]').focus();
}

async function submit(answer) {
  if (C.answered) return;
  C.answered = true;
  try {
    const r = await api('/level/check/answer', { method: 'POST', body: { id: C.id, answer } });
    $$lock();
    const fb = r.correct
      ? `<p class="lv-right">${icon('check')}<span>Right.</span></p>`
      : `<p class="lv-wrong">${icon('x')}<span>Not quite. The answer:</span></p><p class="lv-q-cue" data-no-i18n lang="de">${esc(r.full)}</p>${r.why ? `<p class="muted small">${esc(r.why)}</p>` : ''}`;
    const next = r.next ? '<button id="lv-next">Next</button>' : '<button id="lv-done">See the result</button>';
    $('#lv-feedback').innerHTML = fb + `<p>${next}</p>`;
    ($('#lv-next') || $('#lv-done')).focus();
    C.pending = r;
  } catch (e) {
    C.answered = false;
    toast(e.message, 'error');
  }
}

function $$lock() {
  document.querySelectorAll('#lv-check [data-lv-choice], #lv-answer, #lv-form button').forEach(b => { b.disabled = true; });
}

function showResult(r) {
  const res = r.result;
  const over = res.overall == null ? 'Below A1' : L(res.overall);
  const setting = S.settings.level;
  const suggest = res.overall != null && L(res.overall) !== setting
    ? `<p>${`Your level setting is ${setting}. This check suggests ${L(res.overall)}.`}</p><p class="row"><button data-lv-set="${L(res.overall)}">${`Set my level to ${L(res.overall)}`}</button><button class="ghost" id="lv-back">Keep ${esc(setting)}</button></p>`
    : '<p class="row"><button id="lv-back">Back to Progress</button></p>';
  $('#lv-check').innerHTML = `<div class="panel lv-q"><h2>Your result</h2>
    <p class="lv-big">${over}</p><p>${resultLine(res)}</p>
    <p class="muted small">${`${res.right} of ${res.total} right. One check is a snapshot, not a verdict: it is one of several signs on this page.`}</p>
    ${suggest}</div>`;
}

function closeCheck() {
  Object.assign(C, { id: null, q: null, answered: false, pending: null });
  $('#lv-check').classList.add('hidden');
  $('#lv-check').innerHTML = '';
  $('#lv-body').classList.remove('hidden');
  loadProgress().catch(e => toast(e.message, 'error'));
}

async function setLevel(level) {
  S.settings = await api('/settings', { method: 'PUT', body: { level } });
  toast(`Level set to ${level}`);
  closeCheck();
}

document.addEventListener('click', e => {
  const t = e.target.closest('button, a');
  if (!t || !t.closest('#view-progress')) return;
  if (t.id === 'lv-start') startCheck().catch(err => toast(err.message, 'error'));
  else if (t.dataset.lvChoice != null) submit(C.q.choices[+t.dataset.lvChoice]);
  else if (t.id === 'lv-next') { Object.assign(C, { q: C.pending.next, answered: false }); drawQuestion(); }
  else if (t.id === 'lv-done') { showResult(C.pending); refreshNav(); }
  else if (t.id === 'lv-back' || t.id === 'lv-quit') closeCheck();
  else if (t.dataset.lvSet) setLevel(t.dataset.lvSet).catch(err => toast(err.message, 'error'));
});
document.addEventListener('submit', e => {
  if (e.target.id !== 'lv-form') return;
  e.preventDefault();
  const v = $('#lv-answer').value.trim();
  if (v) submit(v);
});

// ---------- Home: a small summary that links here ----------
async function homeSummary() {
  const box = $('#today-progress');
  if (!box) return;
  try {
    const b = await api('/level/brief');
    box.innerHTML = `<a href="#" class="panel lv-home" data-go="progress">
      <h2>${icon('progress')}<span>Progress</span></h2>
      <div class="lv-nums"><div><b>${b.known}</b><span>words known</span></div><div><b>${b.learning}</b><span>being learned</span></div></div>
      <p class="small">${weekGoalText(b.week)}</p>${weekDots(b.week)}</a>`;
  } catch { box.innerHTML = ''; }
}

// ---------- Settings: the weekly goal (saved as soon as it changes) ----------
document.addEventListener('viewchange', e => {
  if (e.detail === 'today') homeSummary();
  if (e.detail === 'settings' && $('#s-week-goal')) $('#s-week-goal').value = String(S.settings?.week_goal || 5);
});
$('#s-week-goal')?.addEventListener('change', async e => {
  try {
    S.settings = await api('/settings', { method: 'PUT', body: { week_goal: e.target.value } });
    refreshNav();
  } catch (err) { toast(err.message, 'error'); }
});
