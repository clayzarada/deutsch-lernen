// Declensions section: a guided journey across "planets" (one per stage of the course) with a lesson, charts,
// a drill, a reading, flashcards and a checkpoint each, plus free practice (smart drill, sprints, tables).
import { $, $$, S, api, esc, icon, store, toast, busy, registerView, refreshNav, isActive } from './core.js';

const CASE_SHORT = { nom: 'Nominativ', akk: 'Akkusativ', dat: 'Dativ', gen: 'Genitiv' };
const INSTRUCTION = {
  def: 'Type the article', dies: 'Type the word with its ending', ein: 'Type the word with its ending', poss: 'Type the possessive with its ending',
  adjw: 'Type the adjective ending', adjm: 'Type the adjective ending', adjs: 'Type the adjective ending',
  pers: 'Type the pronoun', refl: 'Type the reflexive pronoun', rel: 'Type the relative pronoun', wer: 'Type the question word',
  trig: 'Which case?', gender: 'Which article?', plural: 'Type the plural', noun: 'Type the noun with its ending',
  combo: 'Type the whole phrase in this case', sent: 'Type the missing phrase in the right case',
};
const SPRINT_SECONDS = 60;

function saved(key, fallback) {
  try { return JSON.parse(store.get(key)) ?? fallback; } catch { return fallback; }
}

const V = { tab: store.get('declTab') === 'free' ? 'free' : 'journey', state: null };
const keyTable = {};
const heat = key => { const b = V.state?.boxes[key]; return b ? `h${b.box}` : ''; };
const caseBadge = c => c ? `<span class="case-badge c-${c}">${CASE_SHORT[c]}</span>` : '';
const fmt = s => esc(s).replace(/\*\*([^*]+)\*\*/g, '<b class="end">$1</b>').replace(/\*([^*\s][^*]*)\*/g, '<i>$1</i>');
const norm = s => (s || '').trim().toLowerCase().replace(/ä/g, 'ae').replace(/ö/g, 'oe').replace(/ü/g, 'ue').replace(/ß/g, 'ss')
  .replace(/\s+/g, ' ').replace(/^[-–— ]+/, '').replace(/[.,!? ]+$/, '');

registerView('decl', loadDecl);

async function loadDecl() {
  if (S.declTab) { V.tab = S.declTab; S.declTab = null; }
  if (S.declKeys) { D.keys = S.declKeys; S.declKeys = null; D.sub = 'drill'; stopSprint(); free.q = null; }
  $$('#dv-tabs button').forEach(b => b.classList.toggle('active', b.dataset.dv === V.tab));
  $('#dv-journey').classList.toggle('hidden', V.tab !== 'journey');
  $('#dv-free').classList.toggle('hidden', V.tab !== 'free');
  store.set('declTab', V.tab);
  await refreshState();
  if (V.tab === 'free') loadFree(); else loadJourney();
}

$('#dv-tabs').addEventListener('click', e => {
  const b = e.target.closest('[data-dv]');
  if (!b) return;
  stopSprint();
  V.tab = b.dataset.dv;
  loadDecl().catch(err => toast(err.message, 'error'));
});

async function refreshState() {
  V.state = await api('/decl/state');
  for (const t of V.state.tables) for (const r of t.rows) for (const c of r.cells) if (c.key && !keyTable[c.key]) keyTable[c.key] = t;
}
const tableById = id => V.state.tables.find(t => t.id === id);

// ================= shared pieces =================
// A grid for one declension table. rows / cols limit what is shown; input turns the cells into answer boxes.
function gridHtml(t, { rows = null, cols = null, mark = [], heatOn = false, input = false, vals = {}, checked = null } = {}) {
  const marks = new Set(mark);
  const showCol = ci => !cols || cols.includes(ci);
  const showRow = r => !rows || !r.case || rows.includes(r.case);
  return `<table class="dc-grid" data-table="${t.id}"><caption>${esc(t.title)}</caption><thead><tr><th></th>${t.cols.map((c, ci) => showCol(ci) ? `<th>${esc(c)}</th>` : '').join('')}</tr></thead>
    <tbody>${t.rows.map((r, ri) => !showRow(r) ? '' : `<tr><th class="${r.case ? 'cl-' + r.case : ''}">${esc(r.label)}</th>${r.cells.map((c, ci) => {
      if (!showCol(ci)) return '';
      if (!c.form) return '<td class="none">–</td>';
      const pos = `${ri}:${ci}`;
      if (input && c.key) {
        const res = checked?.[pos];
        return `<td class="${res ? (res.correct ? 'right' : 'wrong') : ''}"><input data-pos="${pos}" value="${esc(vals[pos] ?? '')}" autocomplete="off" spellcheck="false" aria-label="${esc(r.label)} ${esc(t.cols[ci])}">${res && !res.correct ? `<small>${esc(res.form)}</small>` : ''}</td>`;
      }
      return `<td class="${heatOn && c.key ? heat(c.key) : ''} ${marks.has(c.key) ? 'mark' : ''} ${input ? 'given' : ''}">${esc(c.form)}</td>`;
    }).join('')}</tr>`).join('')}</tbody></table>`;
}

// Enter moves down a column, then to the top of the next one, then to the Check button.
function gridEnter(e, scope, checkBtn) {
  const inp = e.target.closest?.('input[data-pos]');
  if (!inp || e.key !== 'Enter') return;
  e.preventDefault();
  const all = $$('input[data-pos]', scope);
  const next = all[all.indexOf(inp) + 1];
  const table = inp.closest('table');
  const [r, c] = inp.dataset.pos.split(':').map(Number);
  const below = $$('input[data-pos]', table).find(i => { const [rr, cc] = i.dataset.pos.split(':').map(Number); return cc === c && rr > r; });
  (below || next || checkBtn)?.focus();
}

const GENDER_LETTER = { m: ['M', 'der', 'masculine'], f: ['F', 'die', 'feminine'], n: ['N', 'das', 'neuter'], pl: ['P', 'pl', 'plural'] };
function genderHint(q) {
  if (!q.gender || ['gender', 'plural'].includes(q.family)) return '';
  const [letter, tone, word] = GENDER_LETTER[q.gender];
  return `<button class="dc-ghint g-${tone}" data-ghint title="Show the gender (Alt+G)" aria-label="Show the gender">
    <span class="q">?</span><span class="a">${letter}</span><span class="a full">${word}</span></button>`;
}

// One question at a time: ask, grade on the server, show feedback, move on. Used by free practice and by
// every drill and checkpoint on the journey.
//   url: API base · params(): extra request fields · stats(): HTML for the card's top right · above(): HTML over the card
//   delay(res): ms before moving on by itself (null = wait for Enter) · onResult(res, q): return 'stop' to end · onDone()
let activeRunner = null;
function makeRunner(box, o) {
  const R = { q: null, next: null, phase: 'idle', result: null, given: '', recent: [], timer: null, t0: 0, finished: false, box };
  const body = extra => ({ ...o.params?.(), recent: R.recent.slice(-4), ...extra });
  R.start = async () => {
    clearTimeout(R.timer);
    Object.assign(R, { recent: [], q: null, finished: false, phase: 'idle' });
    activeRunner = R;
    R.ask(await api(o.url + '/next', { method: 'POST', body: body() }));
  };
  R.ask = q => {
    Object.assign(R, { q, next: null, result: null, phase: 'ask', t0: performance.now() });
    R.render();
    $('.dc-input', box)?.focus();
  };
  R.stop = () => { clearTimeout(R.timer); R.phase = 'idle'; if (activeRunner === R) activeRunner = null; };
  R.render = () => {
    const q = R.q, r = R.result;
    if (!q) { box.innerHTML = '<div class="dc-card"></div>'; return; }
    const answered = R.phase === 'feedback';
    const fill = answered ? (q.family.startsWith('adj') ? q.answers[0] : q.display) : null;
    const gap = fill ? `<span class="dc-gap filled ${r.correct ? 'right' : 'wrong'}">${esc(fill)}</span>` : '<span class="dc-gap"></span>';
    box.innerHTML = `${o.above?.() || ''}
      <div class="dc-card ${answered ? (r.correct ? 'right' : 'wrong') : ''}">
        <div class="dc-top"><span class="chip">${esc(q.label)}</span>${!q.hide_case || answered ? caseBadge(q.case) : ''}<span class="grow"></span>${o.stats?.() || ''}${genderHint(q)}</div>
        <p class="dc-instr">${INSTRUCTION[q.family]}</p>
        ${q.cue ? `<p class="dc-cue">${esc(q.cue)}</p>` : ''}
        <p class="dc-prompt ${q.family === 'gender' ? 'big' : ''}">${esc(q.prompt).replace('___', gap)}</p>
        ${q.kind === 'choice' ? choicesHtml(q, r, R.given) : `<input class="dc-input" autocomplete="off" spellcheck="false" placeholder="Your answer" ${answered ? 'readonly' : ''} value="${answered ? esc(R.given) : ''}">`}
        ${answered ? feedbackHtml(q, r, R.given, o.delay?.(r) == null) : `<div class="dc-hint"><span class="muted small">${q.kind === 'choice' ? q.choices.map((_, i) => `<kbd>${i + 1}</kbd>`).join(' ') + ' to answer' : '<kbd>Enter</kbd> to check'}</span><button class="link-btn" data-skip>I don't know</button></div>`}
      </div>`;
    o.afterRender?.();
  };
  R.submit = async value => {
    if (R.phase !== 'ask') return;
    R.phase = 'waiting';
    const q = R.q;
    const ms = Math.round(performance.now() - R.t0);
    R.given = value;
    R.recent.push(q.key);
    let res;
    try {
      res = await api(o.url + '/answer', { method: 'POST', body: body({ question: q, answer: value, ms }) });
    } catch (err) { R.phase = 'ask'; return toast(err.message, 'error'); }
    if (R.phase !== 'waiting') return; // stopped while the answer was being saved (e.g. the sprint clock ran out)
    Object.assign(R, { result: res, next: res.next, phase: 'feedback' });
    if (V.state) V.state.today.answered++;
    R.finished = o.onResult?.(res, q) === 'stop';
    R.render();
    clearTimeout(R.timer);
    const wait = o.delay ? o.delay(res) : (res.correct ? 650 : null);
    if (wait != null) R.timer = setTimeout(R.advance, wait);
  };
  R.advance = () => {
    if (R.phase !== 'feedback') return;
    clearTimeout(R.timer);
    if (R.finished) { R.stop(); return o.onDone?.(); }
    if (R.next) R.ask(R.next);
  };
  R.key = e => {
    if (e.altKey && e.code === 'KeyG') { e.preventDefault(); $('[data-ghint]', box)?.classList.toggle('shown'); return; }
    if (e.key === 'Enter') {
      if (e.target.closest?.('button, select, a') && !e.target.closest('.dc-card')) return;
      e.preventDefault();
      if (R.phase === 'feedback') R.advance();
      else if (R.phase === 'ask' && R.q?.kind === 'text') {
        const v = $('.dc-input', box).value.trim();
        if (v) R.submit(v);
      }
    } else if (R.phase === 'ask' && R.q?.kind === 'choice' && /^[1-4]$/.test(e.key)) {
      const c = R.q.choices[+e.key - 1];
      if (c) R.submit(c);
    }
  };
  box.addEventListener('pointerdown', e => { if (e.target.closest('[data-ghint]')) e.preventDefault(); }); // keep the cursor in the answer box
  box.addEventListener('click', e => {
    if (activeRunner !== R) return;
    if (e.target.closest('[data-ghint]')) return e.target.closest('[data-ghint]').classList.toggle('shown');
    const c = e.target.closest('[data-choice]');
    if (c) return R.submit(c.dataset.choice);
    if (e.target.closest('[data-skip]')) R.submit('');
  });
  return R;
}

function choicesHtml(q, r, given) {
  return `<div class="dc-choices">${q.choices.map((c, i) => {
    let cls = '';
    if (r) { if (c === q.display) cls = 'right'; else if (c === given) cls = 'wrong'; }
    return `<button class="dc-choice ${q.family === 'gender' ? `g-${c}` : ''} ${cls}" data-choice="${esc(c)}" ${r ? 'disabled' : ''}><kbd>${i + 1}</kbd>${esc(c)}</button>`;
  }).join('')}</div>`;
}

function feedbackHtml(q, r, given, waits) {
  if (r.correct) {
    return `<div class="dc-fb right">${icon('check')}<div><b>Richtig!</b> ${esc(q.full)}${r.fast ? ` <span class="dc-fast" title="Fast enough to count toward mastery">${icon('flame')}fast</span>` : ''}</div></div>`;
  }
  const keys = (r.wrong_parts.length ? r.wrong_parts : q.parts.map(p => p.key)).filter(k => keyTable[k]);
  const seen = new Set();
  const charts = keys.filter(k => { const t = keyTable[k].id; if (seen.has(t)) return false; seen.add(t); return true; }).slice(0, 2)
    .map(k => `<div class="dc-mini">${gridHtml(keyTable[k], { mark: keys })}</div>`).join('');
  return `<div class="dc-fb wrong">${icon('x')}<div>
      <p class="dc-answer">${esc(q.full)}</p>
      ${given ? `<p class="muted small">You wrote: ${esc(given)}</p>` : ''}
      <p class="small">${esc(q.why)}</p></div></div>
    ${charts ? `<div class="dc-charts">${charts}</div>` : ''}
    ${waits ? '<div class="dc-hint"><span class="muted small"><kbd>Enter</kbd> for the next one. This comes back soon.</span></div>' : ''}`;
}

document.addEventListener('keydown', e => {
  if (S.view !== 'decl' || e.repeat || $('dialog[open]')) return;
  if (activeRunner && activeRunner.box.isConnected && activeRunner.box.offsetParent !== null) return activeRunner.key(e);
  if (V.tab === 'journey' && J.screen === 'step' && J.step === 'cards') cardsKey(e);
});

// ================= the journey =================
const J = { data: null, screen: 'map', stage: null, step: null, detail: {}, session: null };
const POS = [[110, 125], [330, 95], [550, 135], [770, 100], [890, 320], [670, 350], [450, 315], [230, 355], [110, 560], [410, 590], [740, 555]];
const STEP_ICON = { learn: 'reader', chart: 'grid', drill: 'target', reading: 'page', cards: 'cards', checkpoint: 'rocket' };
const jbox = $('#dv-journey');

async function loadJourney() {
  J.data = await api('/decl/journey');
  if (J.screen === 'map' || !J.stage) return renderMap();
  if (J.screen === 'stage') return renderStage();
  // A step in progress keeps its screen (e.g. when coming back from another page).
  if (!jbox.childElementCount) renderStage();
}

const stageOf = id => J.data.stages.find(s => s.id === id);
const stageIdx = id => J.data.stages.findIndex(s => s.id === id);

// The green alien kitty in its saucer, drawn around (0, 0).
export function kittySvg() {
  return `<g class="kitty-bob">
    <ellipse cx="0" cy="27" rx="13" ry="3.5" fill="#7df9ff" opacity=".35" class="kitty-glow"/>
    <path d="M-18 9 A18 21 0 0 1 18 9 Z" fill="rgba(170,225,255,.22)" stroke="rgba(255,255,255,.55)" stroke-width="1.2"/>
    <g stroke="#3faa4a" stroke-width="1.6" stroke-linecap="round"><path d="M-4 -11 L-8 -21"/><path d="M4 -11 L8 -21"/></g>
    <circle cx="-8" cy="-22" r="2.4" fill="#c8ff7a"/><circle cx="8" cy="-22" r="2.4" fill="#c8ff7a"/>
    <path d="M-11 -4 L-10 -16 L-2 -9 Z" fill="#62d66a"/><path d="M11 -4 L10 -16 L2 -9 Z" fill="#62d66a"/>
    <path d="M-9.4 -7 L-9 -13 L-5 -9.5 Z" fill="#f7a8c4"/><path d="M9.4 -7 L9 -13 L5 -9.5 Z" fill="#f7a8c4"/>
    <circle cx="0" cy="0" r="11.5" fill="#62d66a"/>
    <ellipse cx="-4.6" cy="-1" rx="2.9" ry="3.8" fill="#0d1320"/><ellipse cx="4.6" cy="-1" rx="2.9" ry="3.8" fill="#0d1320"/>
    <circle cx="-5.4" cy="-2.4" r="1" fill="#fff"/><circle cx="3.8" cy="-2.4" r="1" fill="#fff"/>
    <path d="M-1.4 3.4 L1.4 3.4 L0 5 Z" fill="#f7a8c4"/>
    <path d="M0 5 Q-2 7.6 -4 6 M0 5 Q2 7.6 4 6" fill="none" stroke="#1d5a2a" stroke-width="1" stroke-linecap="round"/>
    <g stroke="#d9ffe0" stroke-width=".7" stroke-linecap="round" opacity=".8"><path d="M-7 3 L-14 2"/><path d="M-7 4.6 L-13.6 6"/><path d="M7 3 L14 2"/><path d="M7 4.6 L13.6 6"/></g>
    <ellipse cx="0" cy="14" rx="31" ry="8.5" fill="#aeb6d6"/><ellipse cx="0" cy="12.6" rx="31" ry="7" fill="#d5daee"/>
    <ellipse cx="0" cy="19" rx="17" ry="4.6" fill="#7a83a8"/>
    ${[-22, -11, 0, 11, 22].map((x, i) => `<circle cx="${x}" cy="${14.5 - Math.abs(x) / 16}" r="1.9" class="kitty-light" style="animation-delay:${i * .18}s"/>`).join('')}
  </g>`;
}

function smoothPath(pts) {
  let d = `M${pts[0][0]} ${pts[0][1]}`;
  for (let i = 0; i < pts.length - 1; i++) {
    const p0 = pts[i - 1] || pts[i], p1 = pts[i], p2 = pts[i + 1], p3 = pts[i + 2] || p2;
    d += ` C${p1[0] + (p2[0] - p0[0]) / 6} ${p1[1] + (p2[1] - p0[1]) / 6} ${p2[0] - (p3[0] - p1[0]) / 6} ${p2[1] - (p3[1] - p1[1]) / 6} ${p2[0]} ${p2[1]}`;
  }
  return d;
}

function starsText(n) { return '★'.repeat(n) + '☆'.repeat(3 - n); }

function planetBody(s, r) {
  if (!s.unlocked) {
    return `<circle r="${r}" fill="#262b3f" stroke="#3b4260" stroke-width="2"/>
      <g transform="translate(-9,-11) scale(.75)" fill="none" stroke="#8088a8" stroke-width="2.4" stroke-linecap="round"><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></g>`;
  }
  const ring = s.ring ? [`<ellipse rx="${r * 1.65}" ry="${r * .42}" fill="none" stroke="hsl(${s.hue} 70% 78%)" stroke-width="5" opacity=".55" transform="rotate(-18)"/>`,
    `<path d="M${-r * 1.65} 0 A${r * 1.65} ${r * .42} 0 0 0 ${r * 1.65} 0" fill="none" stroke="hsl(${s.hue} 75% 84%)" stroke-width="5" opacity=".9" transform="rotate(-18)"/>`] : ['', ''];
  let surface = `<ellipse cx="${-r * .3}" cy="${r * .35}" rx="${r * .28}" ry="${r * .18}" fill="#000" opacity=".13"/><circle cx="${r * .38}" cy="${-r * .1}" r="${r * .15}" fill="#000" opacity=".12"/><circle cx="${-r * .05}" cy="${-r * .5}" r="${r * .1}" fill="#fff" opacity=".18"/>`;
  if (s.nebula) surface = `<ellipse cx="0" cy="${-r * .25}" rx="${r * .9}" ry="${r * .16}" fill="#fff" opacity=".2"/><ellipse cx="0" cy="${r * .15}" rx="${r * .98}" ry="${r * .14}" fill="#000" opacity=".14"/><ellipse cx="0" cy="${r * .52}" rx="${r * .8}" ry="${r * .12}" fill="#fff" opacity=".16"/>`;
  if (s.home) surface = `<path d="M${-r * .7} ${-r * .2} q${r * .3} ${-r * .5} ${r * .7} ${-r * .3} q${r * .2} ${r * .3} ${-r * .1} ${r * .5} q${-r * .4} ${r * .3} ${-r * .6} ${-r * .2}z" fill="#3fbf6a" opacity=".9"/><path d="M${r * .1} ${r * .3} q${r * .4} ${-r * .2} ${r * .6} ${r * .1} q${-r * .1} ${r * .4} ${-r * .5} ${r * .3}z" fill="#3fbf6a" opacity=".9"/><ellipse cx="${-r * .2}" cy="${r * .6}" rx="${r * .5}" ry="${r * .1}" fill="#fff" opacity=".35"/>`;
  return `${ring[0]}<circle r="${r}" fill="url(#pg-${s.id})"/><g clip-path="url(#pc-${s.id})">${surface}</g>${ring[1]}
    ${s.complete ? `<g transform="translate(${r * .72},${-r * .72})"><circle r="10" fill="#22c55e" stroke="#0b1020" stroke-width="2"/><path d="M-4.5 0 L-1.2 3.4 L4.8 -3.2" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></g>` : ''}`;
}

function renderMap() {
  J.screen = 'map';
  activeRunner = null;
  const d = J.data, cur = stageIdx(d.current);
  const curStage = d.stages[cur];
  const nextStep = curStage.steps.find(x => !x.done);
  // deterministic star field
  let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  const stars = Array.from({ length: 130 }, () => { const x = rnd() * 1000, y = rnd() * 700, r = rnd() * 1.3 + .3; return `<circle cx="${x.toFixed(0)}" cy="${y.toFixed(0)}" r="${r.toFixed(1)}" class="${rnd() < .18 ? 'tw' : ''}" style="animation-delay:${(rnd() * 4).toFixed(1)}s" opacity="${(rnd() * .6 + .25).toFixed(2)}"/>`; }).join('');
  const defs = d.stages.map((s, i) => { const r = s.home ? 46 : 34; return `<radialGradient id="pg-${s.id}" cx=".34" cy=".3" r=".8"><stop offset="0" stop-color="hsl(${s.hue} ${s.home ? 70 : 85}% ${s.home ? 62 : 74}%)"/><stop offset="1" stop-color="hsl(${s.hue} 62% ${s.home ? 30 : 34}%)"/></radialGradient><clipPath id="pc-${s.id}"><circle r="${r}"/></clipPath>`; }).join('');
  const planets = d.stages.map((s, i) => {
    const [x, y] = POS[i], r = s.home ? 46 : 34;
    return `<g class="pl ${s.unlocked ? '' : 'locked'} ${i === cur && !d.finished ? 'current' : ''}" data-stage="${s.id}" transform="translate(${x},${y})" tabindex="0" role="button" aria-label="${esc(s.title)}${s.unlocked ? '' : ' (locked)'}">
      ${i === cur && !d.finished ? `<circle r="${r + 11}" class="pl-halo"/>` : ''}
      <g class="pl-body">${planetBody(s, r)}</g>
      <text y="${r + 24}" class="pl-title">${esc(s.title)}</text><text y="${r + 41}" class="pl-name">${esc(s.planet)}</text>
      ${s.unlocked ? `<text y="${r + 59}" class="pl-stars s${s.stars}">${starsText(s.stars)}</text>` : ''}</g>`;
  }).join('');
  const kpos = i => { const [x, y] = POS[i], r = d.stages[i].home ? 46 : 34; return [x, y - r - 36]; };
  const lastIdx = Math.min(+store.get('declKitty') || 0, cur);
  const [kx, ky] = kpos(lastIdx);
  jbox.innerHTML = `
    <div class="dj-mission">
      <svg class="dj-avatar" viewBox="-34 -27 68 60">${kittySvg()}</svg>
      <div class="grow"><b>${d.finished ? 'Mission complete! Every planet is yours.' : `Next stop: ${esc(curStage.title)}`}</b>
        <p class="muted small">${d.finished ? 'Keep your skills solid with free practice, and collect the last stars.' : `${esc(curStage.blurb)} ${nextStep ? `Up next: ${nextStep.label.toLowerCase()}.` : ''}`}</p></div>
      <span class="dj-stars" title="Stars: 1 for the checkpoint, 2 for every step, 3 for keeping the skills solid over time">★ ${d.stars}<small>/${d.max_stars}</small></span>
      <button data-go-stage="${curStage.id}">${icon('rocket')}${d.finished ? 'Visit home' : curStage.steps.some(x => x.done) ? 'Continue' : 'Land here'}</button>
    </div>
    <div class="dj-map"><svg viewBox="0 0 1000 700" role="img" aria-label="Map of the declension planets">
      <defs>${defs}<radialGradient id="neb1" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#7c3aed" stop-opacity=".35"/><stop offset="1" stop-color="#7c3aed" stop-opacity="0"/></radialGradient>
        <radialGradient id="neb2" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#0ea5e9" stop-opacity=".22"/><stop offset="1" stop-color="#0ea5e9" stop-opacity="0"/></radialGradient></defs>
      <ellipse cx="840" cy="250" rx="300" ry="200" fill="url(#neb1)"/><ellipse cx="220" cy="480" rx="340" ry="230" fill="url(#neb2)"/>
      <g fill="#fff">${stars}</g>
      <path d="${smoothPath(POS)}" class="dj-path"/>
      ${cur > 0 || d.finished ? `<path d="${smoothPath(POS.slice(0, cur + 1))}" class="dj-path done"/>` : ''}
      ${planets}
      <g id="dj-kitty" class="dj-kitty" style="transform: translate(${kx}px, ${ky}px)">${kittySvg()}</g>
    </svg></div>`;
  if (lastIdx !== cur) {
    const [nx, ny] = kpos(cur);
    setTimeout(() => { const k = $('#dj-kitty'); if (k) { k.classList.add('flying'); k.style.transform = `translate(${nx}px, ${ny}px)`; } }, 350);
  }
  store.set('declKitty', String(cur));
}

function openStage(id) {
  const s = stageOf(id);
  if (!s.unlocked) {
    const prev = J.data.stages[stageIdx(id) - 1];
    return toast(`Locked. Pass the checkpoint on ${prev.title} first.`, 'error');
  }
  J.stage = id;
  renderStage();
}

function miniPlanet(s, size = 84) {
  return `<svg viewBox="-70 -60 140 120" width="${size * 1.17}" height="${size}" class="dj-mini-planet"><defs><radialGradient id="pg-${s.id}" cx=".34" cy=".3" r=".8"><stop offset="0" stop-color="hsl(${s.hue} 85% 74%)"/><stop offset="1" stop-color="hsl(${s.hue} 62% 34%)"/></radialGradient><clipPath id="pc-${s.id}"><circle r="40"/></clipPath></defs>${planetBody({ ...s, complete: false, unlocked: true }, 40)}</svg>`;
}

function renderStage() {
  J.screen = 'stage';
  activeRunner = null;
  const s = stageOf(J.stage);
  const doneSteps = s.steps.filter(x => x.done).length;
  jbox.innerHTML = `
    <button class="link-btn dj-back" data-map>${icon('left')}Back to the map</button>
    <div class="dj-stage-head">
      ${miniPlanet(s)}
      <div class="grow"><p class="eyebrow">${esc(s.planet)}</p><h2>${esc(s.title)}</h2><p class="muted">${esc(s.blurb)}</p>
        <div class="meter"><div class="meter-bar"><span style="width:${(100 * s.skills.solid) / Math.max(1, s.skills.total)}%"></span></div><span>${s.skills.solid}/${s.skills.total} skills solid</span></div></div>
      <div class="dj-stage-stars"><span class="pl-stars s${s.stars}">${starsText(s.stars)}</span><small class="muted">${s.complete ? 'Planet complete' : `${doneSteps} of ${s.steps.length} steps`}</small></div>
    </div>
    <div class="dj-steps">${s.steps.map((x, i) => {
      const cp = x.id === 'checkpoint';
      const best = x.best != null && ['drill', 'checkpoint', 'reading'].includes(x.id) ? `best ${x.best}${x.id === 'drill' ? `/${J.data.drill.size}` : cp ? `/${s.checkpoint.size}` : ''}` : '';
      const text = cp ? `${s.checkpoint.size} mixed questions. Get ${s.checkpoint.need} right to ${s.complete ? 'pass' : 'unlock the next planet'}.` : x.id === 'cards' ? `Flip through ${s.cards} key rules.` : x.text;
      return `<button class="dj-step ${x.done ? 'done' : ''} ${cp ? 'checkpoint' : ''}" data-step="${x.id}">
        <span class="dj-step-icon">${icon(x.done ? 'check' : STEP_ICON[x.id])}</span>
        <span class="grow"><b>${i + 1}. ${x.label}</b><small>${text}</small></span>
        <span class="dj-step-meta">${best ? `<small>${best}</small>` : ''}<span class="chip">${x.done ? 'Again' : 'Start'}${icon('right')}</span></span></button>`;
    }).join('')}</div>
    ${s.complete ? '' : `<p class="muted small center dj-testout">${icon('sparkles')}Already know this? Go straight to the <b>checkpoint</b> to test out and unlock the next planet.</p>`}`;
}

jbox.addEventListener('click', e => {
  if (e.target.closest('[data-map]')) { J.session?.runner?.stop(); J.screen = 'map'; return loadJourney(); }
  if (e.target.closest('[data-stage-back]')) { J.session?.runner?.stop(); J.screen = 'stage'; return loadJourney(); }
  const go = e.target.closest('[data-go-stage]');
  if (go) return openStage(go.dataset.goStage);
  const pl = e.target.closest('.pl[data-stage]');
  if (pl) return openStage(pl.dataset.stage);
  const st = e.target.closest('[data-step]');
  if (st) return openStep(st.dataset.step).catch(err => toast(err.message, 'error'));
  stepClick(e);
});
jbox.addEventListener('keydown', e => {
  const pl = e.target.closest?.('.pl[data-stage]');
  if (pl && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); e.stopPropagation(); openStage(pl.dataset.stage); }
  gridEnter(e, jbox, $('#dj-chart-check'));
  const gap = e.target.closest?.('input[data-gap]');
  if (gap && e.key === 'Enter') { e.preventDefault(); const all = $$('input[data-gap]', jbox); (all[all.indexOf(gap) + 1] || $('#dj-read-check'))?.focus(); }
});

async function getDetail(id) { return J.detail[id] ||= await api(`/decl/stage/${id}`); }

function stepShell(label, inner, { narrow = false } = {}) {
  const s = stageOf(J.stage);
  jbox.innerHTML = `<div class="dj-step-head"><button class="link-btn" data-stage-back>${icon('left')}${esc(s.title)}</button><span class="chip">${icon(STEP_ICON[J.step])}${label}</span></div>
    <div class="dj-step-body ${narrow ? 'narrow' : ''}" id="dj-body">${inner}</div>`;
}

async function openStep(step) {
  J.step = step; J.screen = 'step';
  const d = await getDetail(J.stage);
  ({ learn: showLesson, chart: showChart, drill: () => showSession('drill'), checkpoint: () => showSession('checkpoint'), reading: () => showReading(d.reading, false), cards: showCards })[step](d);
  $('main')?.scrollTo?.(0, 0); window.scrollTo(0, 0);
}

async function finishStep(score, total) {
  const r = await api(`/decl/stage/${J.stage}/complete`, { method: 'POST', body: { step: J.step, score, total } });
  J.data = r.journey;
  return r;
}

// ---------- step: briefing ----------
function showLesson(d) {
  const blocks = d.lesson.map(b => {
    const [kind, a, rows, cols] = b;
    if (kind === 'p') return `<p>${fmt(a)}</p>`;
    if (kind === 'h') return `<h3>${fmt(a)}</h3>`;
    if (kind === 'rule') return `<div class="ls-rule">${fmt(a)}</div>`;
    if (kind === 'tip') return `<div class="ls-tip">${icon('sparkles')}<div>${fmt(a)}</div></div>`;
    if (kind === 'ex') return `<div class="ls-ex">${a.map(([de, en]) => `<div><span>${fmt(de)}</span><small>${fmt(en)}</small></div>`).join('')}</div>`;
    if (kind === 'table') return `<div class="ls-table">${gridHtml(tableById(a), { rows, cols })}</div>`;
    return '';
  }).join('');
  stepShell('Briefing', `<article class="dj-lesson">${blocks}<div class="row dj-end-row"><button id="dj-lesson-done">${icon('check')}Got it</button></div></article>`, { narrow: true });
}

// ---------- step: charts ----------
const CH = { vals: {}, checked: {}, peek: false };
function showChart(d, keep = false) {
  if (!keep) Object.assign(CH, { vals: {}, checked: {}, peek: false });
  const grids = d.tables.map(t => `<div class="dj-chart">${gridHtml(tableById(t.id), { rows: t.rows, cols: t.cols, input: !CH.peek, vals: CH.vals[t.id] || {}, checked: CH.checked[t.id] })}
    ${tableById(t.id).ending && !CH.peek ? '<p class="muted small center">Type just the ending, like -en.</p>' : ''}</div>`).join('');
  const all = Object.values(CH.checked).flatMap(c => Object.values(c));
  stepShell('Charts', `<p class="muted center">${CH.peek ? 'Study the charts, then hide them and fill them in from memory.' : 'Fill in every box from memory. <kbd>Enter</kbd> moves down a column.'}</p>
    <div class="dj-charts">${grids}</div>
    <div class="row dj-end-row">${CH.peek ? '' : `<button id="dj-chart-check">${icon('check')}Check</button>`}
      <button class="ghost" id="dj-chart-peek">${CH.peek ? 'Hide and test me' : 'Let me look first'}</button>
      ${all.length ? `<span class="muted small">${all.filter(c => c.correct).length} of ${all.length} right</span>` : ''}</div>`);
  if (!CH.peek) ($$('input[data-pos]', jbox).find(i => !i.value) || null)?.focus();
}

async function checkChart(btn) {
  const d = await getDetail(J.stage);
  let total = 0, right = 0, blank = 0;
  await busy(btn, 'Checking...', async () => {
    for (const t of d.tables) {
      const answers = {};
      $$(`table[data-table="${t.id}"] input[data-pos]`, jbox).forEach(i => { answers[i.dataset.pos] = i.value; if (!i.value.trim()) blank++; });
      CH.vals[t.id] = answers;
      const { results } = await api('/decl/table', { method: 'POST', body: { table: t.id, answers } });
      CH.checked[t.id] = results;
      total += Object.keys(answers).length;
      right += Object.values(results).filter(r => r.correct).length;
    }
  });
  await refreshState();
  if (right === total) {
    await finishStep(right, total);
    return doneScreen({ title: 'Charts complete!', text: `All ${total} boxes right, from memory.` });
  }
  // keep the right answers, clear the wrong ones so they can be tried again
  for (const t of d.tables) for (const [pos, r] of Object.entries(CH.checked[t.id])) if (!r.correct) CH.vals[t.id][pos] = '';
  showChart(d, true);
  toast(blank ? `${right} of ${total} right. Fill in the rest to finish.` : `${right} of ${total} right. The correct forms are shown in green: try those boxes again.`);
}

// ---------- step: drill and checkpoint ----------
function showSession(mode) {
  const s = stageOf(J.stage);
  const size = mode === 'checkpoint' ? s.checkpoint.size : J.data.drill.size;
  const need = mode === 'checkpoint' ? s.checkpoint.need : J.data.drill.need;
  const sess = J.session = { mode, size, need, n: 0, right: 0, missed: [] };
  stepShell(mode === 'checkpoint' ? 'Checkpoint' : 'Drill', '<div id="dj-run"></div>', { narrow: true });
  sess.runner = makeRunner($('#dj-run'), {
    url: `/decl/stage/${J.stage}`,
    params: () => ({ mode }),
    stats: () => `<span class="dc-score"><b>${sess.right}</b>/${sess.n}</span>`,
    above: () => `<div class="dj-progress" title="${sess.n} of ${size}"><i style="width:${(100 * sess.n) / size}%"></i><span style="left:${(100 * need) / size}%" title="Pass mark: ${need}"></span></div>
      <p class="muted small dj-progress-label">Question ${Math.min(sess.n + (sess.runner?.phase === 'feedback' ? 0 : 1), size)} of ${size} · ${need} right to pass</p>`,
    onResult: (res, q) => { sess.n++; if (res.correct) sess.right++; else sess.missed.push(q); return sess.n >= size ? 'stop' : null; },
    onDone: () => endSession().catch(err => toast(err.message, 'error')),
  });
  sess.runner.start().catch(err => toast(err.message, 'error'));
}

async function endSession() {
  const sess = J.session;
  const r = await finishStep(sess.right, sess.n);
  refreshState().catch(() => {});
  const missed = [...new Map(sess.missed.map(q => [q.full, q])).values()].slice(0, 8);
  const missedHtml = missed.length ? `<div class="dc-missed"><h3>Worth another look</h3>${missed.map(q => `<p>${caseBadge(q.case)}<span>${esc(q.full)}</span></p>`).join('')}</div>` : '';
  const s = stageOf(J.stage);
  if (sess.mode === 'checkpoint' && r.planet_complete) {
    const next = r.next && stageOf(r.next);
    return doneScreen({ big: true, title: `${s.title} complete!`, score: `${sess.right}/${sess.n}`,
      text: next ? `The way to ${next.planet} is open. Next up: ${next.title}.` : 'That was the last planet. You have crossed the whole system. Wunderbar!',
      extra: missedHtml, primary: next ? ['Fly to the next planet', 'map'] : ['Back to the map', 'map'] });
  }
  doneScreen({ fail: !r.passed, title: r.passed ? (sess.mode === 'checkpoint' ? 'Checkpoint passed again!' : 'Drill passed!') : 'Not quite yet', score: `${sess.right}/${sess.n}`,
    text: r.passed ? 'Nice work. Speed comes with repetition.' : `You need ${sess.need} right. ${sess.mode === 'checkpoint' ? 'Try the briefing and the drill, then come back.' : 'Have another go: the ones you missed will come up again.'}`,
    extra: missedHtml, retry: true });
}

// The end-of-step screen, with the kitty.
function doneScreen({ title, text = '', score = '', extra = '', fail = false, big = false, retry = false, primary = null }) {
  activeRunner = null;
  const burst = big ? `<div class="dj-burst">${Array.from({ length: 12 }, (_, i) => `<i style="--a:${i * 30}deg; animation-delay:${(i % 4) * .08}s">★</i>`).join('')}</div>` : '';
  $('#dj-body').className = 'dj-step-body narrow';
  $('#dj-body').innerHTML = `<div class="dc-card dj-done ${fail ? 'fail' : ''} ${big ? 'big' : ''}">
    <div class="dj-done-kitty">${burst}<svg viewBox="-34 -27 68 60" width="${big ? 150 : 104}">${kittySvg()}</svg></div>
    ${score ? `<div class="dc-end-score">${score}</div>` : ''}
    <h2>${esc(title)}</h2><p class="muted">${esc(text)}</p>${extra}
    <div class="row dc-end-actions">${primary ? `<button data-done="${primary[1]}">${icon('rocket')}${primary[0]}</button>` : `<button data-done="stage">${icon('check')}Back to the planet</button>`}
      ${retry ? `<button class="ghost" data-done="retry">${icon('undo')}${fail ? 'Try again' : 'Go again'}</button>` : ''}</div></div>`;
  $('[data-done]', jbox)?.focus();
}

// ---------- step: reading ----------
const RD = { reading: null, checked: false, fresh: false };
function showReading(reading, fresh) {
  Object.assign(RD, { reading, checked: false, fresh });
  let gi = 0;
  const text = reading.segments.map(seg => {
    if (seg.t != null) return esc(seg.t);
    const i = gi++;
    return `<span class="rd-gap ${seg.hint ? 'word' : 'ending'}"><input data-gap="${i}" autocomplete="off" spellcheck="false" autocapitalize="off" placeholder="${esc(seg.hint || '')}" aria-label="gap ${i + 1}"></span>`;
  }).join('');
  const ai = S.settings?.has_key;
  stepShell('Reading', `<article class="dj-reading"><h2>${esc(reading.title)}</h2>
      <p class="muted small">Fill in each gap. Gray words in the boxes are hints; small boxes want just an ending. <kbd>Enter</kbd> jumps to the next gap.</p>
      <p class="rd-text">${text}</p>
      <div class="row dj-end-row"><button id="dj-read-check">${icon('check')}Check</button><span id="dj-read-result" class="muted small"></span></div></article>
    <div class="panel dj-fresh"><div class="grow"><b>${icon('sparkles')}Want a different text?</b><p class="muted small">${ai ? 'Claude writes a new one for this planet. Uses a little API credit.' : 'Add a Claude API key in Settings to get freshly written texts.'}</p></div>
      ${ai ? `<input id="dj-read-topic" placeholder="Topic (optional), e.g. the gym"><button class="ghost" id="dj-read-new">${icon('sparkles')}New text</button>` : ''}</div>`, { narrow: true });
  $('input[data-gap]', jbox)?.focus();
}

async function checkReading() {
  const gaps = RD.reading.segments.filter(s => s.a != null);
  const inputs = $$('input[data-gap]', jbox);
  if (RD.checked) return;
  if (inputs.every(i => !i.value.trim())) return toast('Fill in the gaps first', 'error');
  RD.checked = true;
  const items = inputs.map((inp, i) => {
    const correct = norm(inp.value) === norm(gaps[i].a);
    const wrap = inp.parentElement;
    wrap.classList.add(correct ? 'right' : 'wrong');
    inp.readOnly = true;
    if (!correct) wrap.insertAdjacentHTML('beforeend', `<b>${esc(gaps[i].a)}</b>`);
    return { key: gaps[i].key, correct };
  });
  const right = items.filter(i => i.correct).length;
  api('/decl/record', { method: 'POST', body: { items } }).catch(() => {});
  const r = await finishStep(right, items.length);
  $('#dj-read-result').innerHTML = `<b>${right} of ${items.length} right.</b> ${r.passed ? 'Reading passed!' : `You need ${Math.ceil(items.length * .8)} to pass.`}`;
  $('#dj-read-check').outerHTML = `<button data-done="stage">${icon('check')}Back to the planet</button><button class="ghost" id="dj-read-retry">${icon('undo')}Do it again</button>`;
}

// ---------- step: flashcards ----------
const FC = { queue: [], revealed: false, total: 0, added: 0 };
function showCards(d) {
  Object.assign(FC, { queue: d.cards.map((c, i) => ({ ...c, i })), revealed: false, total: d.cards.length, added: d.cards_added });
  renderCards();
}
function renderCards() {
  const c = FC.queue[0];
  if (!c) return;
  const done = FC.total - FC.queue.length;
  stepShell('Flashcards', `<div class="dj-progress"><i style="width:${(100 * done) / FC.total}%"></i></div>
    <div class="flash ${FC.revealed ? 'revealed' : ''} dj-flash"><div class="flash-type">rule · ${FC.queue.length} to go</div>
      <div class="flash-front">${esc(c.front)}</div>
      ${FC.revealed ? `<div class="flash-answer"><div class="flash-back">${esc(c.back)}</div>${c.extra ? `<div class="flash-extra">${esc(c.extra)}</div>` : ''}</div>` : ''}</div>
    <div class="flash-actions two">${FC.revealed
      ? `<button class="grade grade-1" data-fc="again"><b>Again</b><small>see it again</small></button><button class="grade grade-3" data-fc="ok"><b>Got it</b><small>next card</small></button>`
      : '<button class="reveal" data-fc="reveal">Show answer</button>'}</div>
    <p class="muted small center keys"><kbd>Space</kbd> show answer &nbsp; <kbd>1</kbd> Again &nbsp; <kbd>2</kbd> Got it</p>`, { narrow: true });
}
async function cardsAct(act) {
  if (act === 'reveal') FC.revealed = true;
  else {
    const c = FC.queue.shift();
    if (act === 'again') FC.queue.push(c);
    FC.revealed = false;
    if (!FC.queue.length) {
      await finishStep(FC.total, FC.total);
      const s = stageOf(J.stage);
      const all = FC.added >= FC.total;
      return doneScreen({ title: 'Rules reviewed!', text: all ? 'These cards are already in your Flashcards deck, so they will come back on schedule.' : 'Add them to your Flashcards deck and spaced repetition will bring them back just before you forget.',
        extra: all ? '' : `<div class="row dc-end-actions"><button class="ghost" id="dj-cards-add">${icon('plus')}Add ${FC.total - FC.added} cards to my Flashcards</button></div>` });
    }
  }
  renderCards();
}
function cardsKey(e) {
  if (e.target.closest?.('input, textarea, select') || !FC.queue.length || !$('.dj-flash')) return;
  if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); if (!FC.revealed) cardsAct('reveal'); }
  else if (FC.revealed && e.key === '1') cardsAct('again');
  else if (FC.revealed && e.key === '2') cardsAct('ok');
}

function stepClick(e) {
  const t = e.target;
  const done = t.closest('[data-done]');
  if (done) {
    const where = done.dataset.done;
    if (where === 'retry') return openStep(J.step);
    J.screen = where === 'map' ? 'map' : 'stage';
    return loadJourney();
  }
  const fc = t.closest('[data-fc]');
  if (fc) return cardsAct(fc.dataset.fc);
  if (t.closest('#dj-lesson-done')) return finishStep().then(() => { toast('Briefing done'); J.screen = 'stage'; renderStage(); });
  if (t.closest('#dj-chart-check')) return checkChart(t.closest('#dj-chart-check'));
  if (t.closest('#dj-chart-peek')) { CH.peek = !CH.peek; if (!CH.peek) CH.checked = {}; return getDetail(J.stage).then(d => showChart(d, true)); }
  if (t.closest('#dj-read-check')) return checkReading();
  if (t.closest('#dj-read-retry')) return showReading(RD.reading, RD.fresh);
  if (t.closest('#dj-read-new')) {
    const btn = t.closest('#dj-read-new');
    return busy(btn, 'Writing...', async () => showReading(await api(`/decl/stage/${J.stage}/reading`, { method: 'POST', body: { topic: $('#dj-read-topic').value } }), true));
  }
  if (t.closest('#dj-cards-add')) {
    return busy(t.closest('#dj-cards-add'), 'Adding...', async () => {
      const r = await api(`/decl/stage/${J.stage}/cards`, { method: 'POST' });
      delete J.detail[J.stage];
      toast(`Added ${r.added} cards to your Flashcards`);
      refreshNav();
      t.closest('#dj-cards-add')?.remove();
    });
  }
}

// ================= free practice =================
const D = {
  sub: 'drill', sprint: null, table: 'def', tableMode: 'test', checked: null, tableVals: {}, clock: null,
  focus: new Set(saved('declFocus', [])), cases: new Set(saved('declCases', ['nom', 'akk', 'dat', 'gen'])),
  session: { n: 0, right: 0, streak: 0 },
};
const free = makeRunner($('#dc-main'), {
  url: '/decl',
  params: () => D.keys ? { keys: D.keys } : { focus: [...D.focus], cases: [...D.cases] },
  stats: () => {
    const s = D.session;
    if (D.sprint) return `<span class="dc-score"><b>${D.sprint.score}</b> right</span>`;
    return `<span class="muted small">${s.n ? `${s.right}/${s.n} right${s.streak > 2 ? ` · ${icon('flame')}${s.streak} in a row` : ''} · ` : ''}${V.state?.today.answered || 0} today</span>`;
  },
  above: () => (D.keys ? `<div class="dc-keys">${icon('mistake')}<span class="grow">Drilling <b>${D.keys.length} skill${D.keys.length === 1 ? '' : 's'}</b> from your Mistake Book. Each mistake is marked learned after 3 days of right answers.</span><button class="link-btn" data-keys-off>Back to normal practice</button></div>` : '')
    + (D.sprint ? '<div class="dc-timer"><i id="dc-timer-bar"></i></div>' : ''),
  delay: res => D.sprint ? (res.correct ? 120 : 1400) : (res.correct ? 650 : null),
  onResult: (res, q) => {
    const s = D.session;
    s.n++;
    if (res.correct) { s.right++; s.streak++; } else s.streak = 0;
    if (res.learned?.length) toast(res.learned.length === 1 ? `Mistake learned: ${res.learned[0].correct}` : `${res.learned.length} mistakes marked learned`);
    if (D.sprint) { D.sprint.total++; if (res.correct) D.sprint.score++; else D.sprint.missed.push(q); }
    else if (s.n % 5 === 0) refreshState().then(() => { if (D.sub === 'drill' && V.tab === 'free') renderSide(); }).catch(() => {});
  },
});

function loadFree() {
  renderSide();
  renderFreeMain();
  if (D.sub === 'drill' && !D.sprint?.done) {
    if (!free.q) free.start().catch(err => toast(err.message, 'error'));
    else { activeRunner = free; if (free.phase === 'ask') $('.dc-input', free.box)?.focus(); }
  }
}

function renderSide() {
  const fams = V.state.families;
  const groups = [...new Set(fams.map(f => f.group))];
  if (D.sub === 'tables') {
    const byGroup = { Articles: ['def', 'dies', 'ein', 'kein', 'mein', 'dein', 'sein', 'ihr', 'unser', 'euer'], 'Adjective endings': ['adjw', 'adjm', 'adjs'], Pronouns: ['pers', 'refl', 'rel', 'wer'] };
    $('#dc-side').innerHTML = `<div class="panel"><h2>Tables</h2>${Object.entries(byGroup).map(([g, ids]) => `
      <h4 class="dc-group">${g}</h4><div class="dc-table-list">${ids.map(id => `<button class="chip-btn ${D.table === id ? 'on' : ''}" data-table="${id}">${esc(tableById(id).title.replace(/^Adjective /, '').replace(/^(.)/, m => m.toUpperCase()))}</button>`).join('')}</div>`).join('')}
      <h4 class="dc-group">Case triggers</h4><div class="dc-table-list"><button class="chip-btn ${D.table === 'triggers' ? 'on' : ''}" data-table="triggers">Prepositions &amp; verbs</button>
        <button class="chip-btn ${D.table === 'match' ? 'on' : ''}" data-table="match">Match the case</button></div></div>`;
    return;
  }
  const famRow = f => {
    const combo = f.group === 'Combinations';
    return `<button class="dc-fam ${D.focus.has(f.id) ? 'on' : ''}" data-fam="${f.id}"><span class="grow">${esc(f.label)}
      ${combo ? '' : `<span class="dc-meter"><i style="width:${Math.round((f.avg_box / 5) * 100)}%"></i></span>`}</span>${combo ? '' : `<small>${f.mastered}/${f.total}</small>`}</button>`;
  };
  $('#dc-side').innerHTML = `<div class="panel"><h2>What to drill</h2>
      <button class="dc-fam smart ${D.focus.size ? '' : 'on'}" data-smart>${icon('sparkles')}<span class="grow"><b>Smart mix</b><small>Your weakest and due skills from everything</small></span></button>
      ${groups.map(g => `<h4 class="dc-group">${g}</h4>${fams.filter(f => f.group === g).map(famRow).join('')}`).join('')}
    </div><div class="panel"><h2>Cases</h2><div class="dc-cases">${Object.entries(CASE_SHORT).map(([c, n]) =>
      `<button class="case-toggle c-${c} ${D.cases.has(c) ? 'on' : ''}" data-case="${c}">${n}</button>`).join('')}</div></div>`;
}

$('#dc-side').addEventListener('click', e => {
  const fam = e.target.closest('[data-fam]'), kase = e.target.closest('[data-case]'), table = e.target.closest('[data-table]');
  if (table) { Object.assign(D, { table: table.dataset.table, checked: null, tableVals: {} }); renderSide(); return renderFreeMain(); }
  if (fam || kase || e.target.closest('[data-smart]')) D.keys = null;
  if (e.target.closest('[data-smart]')) D.focus.clear();
  else if (fam) { if (D.focus.has(fam.dataset.fam)) D.focus.delete(fam.dataset.fam); else D.focus.add(fam.dataset.fam); }
  else if (kase) {
    if (D.cases.has(kase.dataset.case)) {
      if (D.cases.size === 1) return toast('Keep at least one case on', 'error');
      D.cases.delete(kase.dataset.case);
    } else D.cases.add(kase.dataset.case);
  } else return;
  store.set('declFocus', JSON.stringify([...D.focus]));
  store.set('declCases', JSON.stringify([...D.cases]));
  renderSide();
  stopSprint();
  free.start().catch(err => toast(err.message, 'error'));
});

function renderFreeMain() {
  $$('#dc-sub button').forEach(b => b.classList.toggle('active', b.dataset.sub === D.sub));
  $('#dc-sprint').classList.toggle('hidden', D.sub !== 'drill');
  if (D.sub === 'tables') { activeRunner = null; renderTable(); } else if (D.sprint?.done) renderSprintEnd(); else free.render();
}

$('#dc-sub').addEventListener('click', e => {
  const b = e.target.closest('[data-sub]');
  if (!b) return;
  stopSprint();
  D.sub = b.dataset.sub;
  loadFree();
});

// ---------- sprint ----------
$('#dc-sprint').addEventListener('click', () => { if (D.sprint && !D.sprint.done) { stopSprint(); free.start(); } else startSprint(); });

async function startSprint() {
  D.sprint = { end: Date.now() + SPRINT_SECONDS * 1000, score: 0, total: 0, missed: [] };
  $('#dc-sprint span').textContent = 'Stop sprint';
  await free.start();
  clearInterval(D.clock);
  // A plain interval keeps the clock honest even if the window isn't being drawn.
  D.clock = setInterval(() => {
    if (!D.sprint || D.sprint.done) return clearInterval(D.clock);
    const left = D.sprint.end - Date.now();
    const bar = $('#dc-timer-bar');
    if (bar) bar.style.width = Math.max(0, (100 * left) / (SPRINT_SECONDS * 1000)) + '%';
    if (left <= 0) endSprint();
  }, 100);
}

function stopSprint() {
  clearInterval(D.clock);
  if (!D.sprint) return;
  D.sprint = null;
  $('#dc-sprint span').textContent = `${SPRINT_SECONDS}-second sprint`;
}

async function endSprint() {
  clearInterval(D.clock);
  const sprint = D.sprint;
  sprint.done = true;
  free.stop();
  free.q = null;
  $('#dc-sprint span').textContent = `${SPRINT_SECONDS}-second sprint`;
  renderSprintEnd();
  sprint.saved = await api('/decl/sprint', { method: 'POST', body: { score: sprint.score } });
  if (D.sprint === sprint && D.sub === 'drill') renderSprintEnd();
  refreshState().then(() => { if (D.sub === 'drill') renderSide(); }).catch(() => {});
}

function renderSprintEnd() {
  const s = D.sprint;
  const missed = [...new Map(s.missed.map(q => [q.full, q])).values()];
  $('#dc-main').innerHTML = `<div class="dc-card dc-end">
    <p class="eyebrow">${SPRINT_SECONDS} seconds</p>
    <div class="dc-end-score">${s.score}</div>
    <p class="muted">${s.total} answered${s.total ? ` · ${Math.round((100 * s.score) / s.total)}% right` : ''}</p>
    ${s.saved?.new_best ? `<p class="dc-best">${icon('flame')}New best!</p>` : s.saved ? `<p class="muted small">Your best: ${s.saved.best}</p>` : ''}
    ${missed.length ? `<div class="dc-missed"><h3>Missed</h3>${missed.map(q => `<p>${caseBadge(q.case)}<span>${esc(q.full)}</span></p>`).join('')}</div>` : ''}
    <div class="row dc-end-actions"><button id="dc-sprint-again">${icon('undo')}Go again</button><button id="dc-sprint-close" class="ghost">Back to the drill</button></div>
  </div>`;
}

// ---------- tables ----------
const legend = () => '<div class="dc-legend"><span class="h0">Weak</span><span class="h2">Learning</span><span class="h3">Solid</span><span class="h4">Mastered</span></div>';

function renderTable() {
  const box = $('#dc-main');
  if (D.table === 'match') return renderMatch();
  if (D.table === 'triggers') {
    box.innerHTML = `<div class="dc-card dc-table-card"><div class="panel-head"><div><h2>Which case?</h2><p class="muted small">Colors show how well you know each one.</p></div>
      <button data-drill="trig" class="small">${icon('target')}Drill these</button></div>
      ${V.state.triggers.map(g => `<div class="dc-trig"><h4>${g.case ? caseBadge(g.case) : ''}${esc(g.title)}</h4><div class="dc-words">${g.items.map(i => `<span class="dc-word ${heat(i.key)}">${esc(i.word)}</span>`).join('')}</div></div>`).join('')}
      ${legend()}</div>`;
    return;
  }
  const t = tableById(D.table);
  const test = D.tableMode === 'test';
  box.innerHTML = `<div class="dc-card dc-table-card">
    <div class="panel-head"><div class="tabs dc-mode"><button data-mode="test" class="${test ? 'active' : ''}">Test me</button><button data-mode="show" class="${test ? '' : 'active'}">Show the table</button></div>
      <button data-drill="${t.family}" class="ghost small">${icon('target')}Drill this</button></div>
    ${gridHtml(t, { input: test, heatOn: !test, vals: D.tableVals, checked: D.checked })}
    ${t.note ? `<p class="muted small dc-note">${esc(t.note)}</p>` : ''}
    ${test ? `<div class="row"><button id="dc-table-check">${icon('check')}Check</button><button id="dc-table-clear" class="ghost">${D.checked ? 'Clear wrong ones' : 'Clear'}</button>
      ${D.checked ? `<span class="muted small">${Object.values(D.checked).filter(c => c.correct).length} of ${Object.keys(D.checked).length} right</span>` : `<span class="muted small">${t.ending ? 'Type just the ending, like -en. ' : ''}<kbd>Enter</kbd> moves down a column.</span>`}</div>` : legend()}
  </div>`;
  if (test) $$('input[data-pos]', box).find(i => !i.value)?.focus();
}

$('#dc-main').addEventListener('click', async e => {
  const t = e.target;
  if (t.closest('[data-keys-off]')) { D.keys = null; stopSprint(); return free.start(); }
  if (t.closest('#dc-sprint-again')) return startSprint();
  if (t.closest('#dc-sprint-close')) { stopSprint(); return free.start(); }
  const mode = t.closest('[data-mode]');
  if (mode) { Object.assign(D, { tableMode: mode.dataset.mode, checked: null, tableVals: {} }); return renderTable(); }
  const drill = t.closest('[data-drill]');
  if (drill) {
    D.focus = new Set([drill.dataset.drill]);
    store.set('declFocus', JSON.stringify([...D.focus]));
    D.sub = 'drill';
    renderSide(); renderFreeMain();
    return free.start();
  }
  if (t.closest('#dc-table-clear')) {
    const keep = {};
    if (D.checked) for (const [p, r] of Object.entries(D.checked)) if (r.correct) keep[p] = D.tableVals[p];
    Object.assign(D, { tableVals: D.checked ? keep : {}, checked: null });
    return renderTable();
  }
  if (t.closest('#dc-table-check')) {
    const answers = {};
    $$('#dc-main input[data-pos]').forEach(i => { answers[i.dataset.pos] = i.value; });
    if (!Object.values(answers).some(v => v.trim())) return toast('Fill in at least one cell first', 'error');
    try {
      const { results } = await api('/decl/table', { method: 'POST', body: { table: D.table, answers } });
      Object.assign(D, { checked: results, tableVals: answers });
      await refreshState();
      renderTable();
    } catch (err) { toast(err.message, 'error'); }
  }
});
$('#dc-main').addEventListener('keydown', e => gridEnter(e, $('#dc-main'), $('#dc-table-check')));

// ---------- match the case ----------
// Sort prepositions and verbs into the case they always take. Tap a card, then a box (or press 1-4).
const M = { kind: store.get('declMatchKind') || 'all', cards: [], placed: {}, sel: null, checked: false, loading: false };
const BINS = [
  { c: 'akk', label: 'Akkusativ' }, { c: 'dat', label: 'Dativ' }, { c: 'gen', label: 'Genitiv' },
  { c: 'two', label: 'Two-way', hint: 'wohin? Akk · wo? Dat' },
];
const binsFor = kind => kind === 'verb' ? BINS.slice(0, 2) : BINS;  // verbs only take Akkusativ or Dativ
const matchOpen = () => S.view === 'decl' && V.tab === 'free' && D.sub === 'tables' && D.table === 'match';

async function newMatchRound() {
  M.loading = true;
  try {
    const r = await api('/decl/match?kind=' + M.kind);
    Object.assign(M, { cards: r.cards, placed: {}, sel: 0, checked: false });
  } catch (err) { toast(err.message, 'error'); }
  M.loading = false;
  renderMatch();
}

function matchCard(c, i, where) {
  const res = M.checked ? (M.placed[i] === c.case ? 'right' : 'wrong') : '';
  const tip = where === 'bin' && !M.checked ? ' title="Tap to take it back"' : '';
  return `<button class="dm-card ${M.sel === i && !M.checked ? 'on' : ''} ${res}" data-mcard="${i}" ${M.checked ? 'disabled' : ''}${tip}>`
    + `<b>${esc(c.word)}</b>${c.meaning ? `<small>${esc(c.meaning)}</small>` : ''}</button>`;
}

function renderMatch() {
  if (D.table !== 'match' || D.sub !== 'tables') return;
  const box = $('#dc-main');
  if (!M.cards.length) {
    box.innerHTML = '<div class="dc-card dm"><p class="muted">Loading...</p></div>';
    if (!M.loading) newMatchRound();
    return;
  }
  const all = M.cards.map((c, i) => i);
  const left = all.filter(i => !(i in M.placed));
  const right = M.checked ? all.filter(i => M.placed[i] === M.cards[i].case).length : 0;
  const wrong = M.checked ? M.cards.filter((c, i) => M.placed[i] !== c.case) : [];
  const bins = binsFor(M.kind);
  box.innerHTML = `<div class="dc-card dm">
    <div class="panel-head"><div><h2>Match the case</h2><p class="muted small">Tap a word, then the case it always takes. Keys 1-${bins.length} work too.</p></div>
      <div class="tabs dc-mode">${[['all', 'Both'], ['prep', 'Prepositions'], ['verb', 'Verbs']].map(([k, l]) =>
        `<button data-mkind="${k}" class="${M.kind === k ? 'active' : ''}">${l}</button>`).join('')}</div></div>
    ${left.length ? `<div class="dm-tray">${left.map(i => matchCard(M.cards[i], i, 'tray')).join('')}</div>`
      : (M.checked ? '<div class="dm-gap"></div>' : '<div class="dm-tray"><p class="muted small">All sorted. Check your answers.</p></div>')}
    <div class="dm-bins">${bins.map((b, n) => `<div class="dm-bin ${b.c === 'two' ? 'c-two' : 'c-' + b.c}" data-mbin="${b.c}">
      <h4><kbd>${n + 1}</kbd><span>${b.label}</span>${b.hint ? `<small>${b.hint}</small>` : ''}</h4>
      <div class="dm-bin-cards">${all.filter(i => M.placed[i] === b.c).map(i => matchCard(M.cards[i], i, 'bin')).join('')}</div></div>`).join('')}</div>
    <div class="row dm-foot">${M.checked
      ? `<b class="dm-score">${right} of ${M.cards.length} words right</b><button id="dm-next">${icon('undo')}New round</button>`
      : `<button id="dm-check" ${left.length ? 'disabled' : ''}>${icon('check')}Check</button><span class="muted small">${M.cards.length - left.length} of ${M.cards.length} sorted</span>`}</div>
    ${wrong.length ? `<div class="dm-fix"><h4>Worth another look</h4>${wrong.map(c =>
      `<p><b>${esc(c.word)}</b> → ${c.case === 'two' ? 'Two-way' : CASE_SHORT[c.case]}. <span class="muted">${esc(c.why)}</span></p>`).join('')}</div>` : ''}
  </div>`;
}

function placeSelected(binCase) {
  if (M.checked || M.sel == null || !M.cards[M.sel] || (M.sel in M.placed)) return;
  M.placed[M.sel] = binCase;
  M.sel = M.cards.map((c, i) => i).find(i => !(i in M.placed)) ?? null;  // move on to the next unsorted card
  renderMatch();
}

async function checkMatch() {
  if (M.checked || Object.keys(M.placed).length < M.cards.length) return;
  M.checked = true;
  renderMatch();
  const items = M.cards.map((c, i) => ({ key: c.key, correct: M.placed[i] === c.case }));
  try {
    await api('/decl/record', { method: 'POST', body: { family: 'trig', items } });
    await refreshState();
  } catch { /* the result still shows; only the skill tracking missed this round */ }
}

$('#dc-main').addEventListener('click', e => {
  if (D.table !== 'match' || D.sub !== 'tables') return;
  const k = e.target.closest('[data-mkind]');
  if (k) { M.kind = k.dataset.mkind; store.set('declMatchKind', M.kind); M.cards = []; return newMatchRound(); }
  const card = e.target.closest('[data-mcard]');
  if (card && !M.checked) {
    const i = +card.dataset.mcard;
    if (i in M.placed) delete M.placed[i];  // tapped in a box: take it back out
    M.sel = i;
    return renderMatch();
  }
  const bin = e.target.closest('[data-mbin]');
  if (bin) return placeSelected(bin.dataset.mbin);
  if (e.target.closest('#dm-check')) return checkMatch();
  if (e.target.closest('#dm-next')) return newMatchRound();
});

document.addEventListener('keydown', e => {
  if (!matchOpen() || e.target.closest?.('input, textarea, select')) return;
  const bins = binsFor(M.kind);
  const n = +e.key;
  if (!M.checked && n >= 1 && n <= bins.length) { e.preventDefault(); placeSelected(bins[n - 1].c); }
  else if (e.key === 'Enter') { e.preventDefault(); if (M.checked) newMatchRound(); else checkMatch(); }
});
$('#dc-main').addEventListener('input', e => {
  const inp = e.target.closest?.('input[data-pos]');
  if (inp) D.tableVals[inp.dataset.pos] = inp.value;
});

// Time spent working here counts toward today's study minutes (not time spent just looking at the map).
setInterval(() => {
  if (S.view === 'decl' && isActive() && (V.tab === 'free' || J.screen !== 'map')) {
    api('/activity', { method: 'POST', body: { kind: 'practice', seconds: 15 } }).catch(() => {});
  }
}, 15000);
