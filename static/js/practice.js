// Practice page: generate exercise sets per chapter, answer them, get them graded.
import { $, $$, S, api, esc, icon, busy, loading, emptyState, confirmDialog, toast, loadBooks, chapterOptions, registerView, isActive, store } from './core.js';

const TYPE_LABEL = {
  fill_blank: 'Fill the gap', multiple_choice: 'Multiple choice', translate_to_german: 'Translate into German',
  translate_to_native: 'Translate', conjugation: 'Conjugation', word_order: 'Word order', short_answer: 'Short answer',
};

registerView('practice', loadPractice);

// ---------- tabs: AI practice sets / gap-fills from the book ----------
let ptab = store.get('practiceTab') === 'gaps' ? 'gaps' : 'sets';
function showPtab() {
  $$('#p-tabs button').forEach(b => b.classList.toggle('active', b.dataset.ptab === ptab));
  $('#ptab-sets').classList.toggle('hidden', ptab !== 'sets');
  $('#ptab-gaps').classList.toggle('hidden', ptab !== 'gaps');
}
$('#p-tabs').addEventListener('click', e => {
  const b = e.target.closest('[data-ptab]');
  if (!b) return;
  ptab = b.dataset.ptab;
  store.set('practiceTab', ptab);
  loadPractice();
});

async function loadPractice() {
  if (S.practiceTabWant) { ptab = S.practiceTabWant; S.practiceTabWant = null; store.set('practiceTab', ptab); }
  showPtab();
  if (ptab === 'gaps') return loadGaps();
  await loadBooks();
  $('#p-chapter').innerHTML = chapterOptions(S.practiceChapter) || '<option value="">Import a book first</option>';
  $('#p-generate').disabled = !S.books.length;
  await loadSets();
  // Coming from the plan or the reader: open an unfinished set for that chapter, if there is one.
  let open = S.currentSet?.id;
  if (S.practiceChapter) {
    open = S.sets.find(x => x.chapter_id === S.practiceChapter && x.answered < x.total)?.id;
    S.practiceChapter = null;
  }
  if (open) await openSet(open);
  else if (!S.currentSet) {
    $('#p-set').innerHTML = emptyState('practice', 'Pick a chapter and generate a set',
      'Claude writes fresh exercises that match the chapter\'s vocabulary and grammar, then grades your answers with explanations.');
  }
}

async function loadSets() {
  S.sets = await api('/exercise_sets');
  $('#p-sets').innerHTML = S.sets.length ? S.sets.map(s => {
    const pct = s.total ? Math.round((100 * (s.answered || 0)) / s.total) : 0;
    return `<div class="set-item ${S.currentSet?.id === s.id ? 'active' : ''}" data-id="${s.id}">
      <div class="grow"><div class="set-title">${esc(s.title)}</div>
        <div class="meter"><div class="meter-bar"><span style="width:${pct}%"></span></div>
        <span>${s.answered || 0}/${s.total}${s.answered ? ` · ${Math.round((100 * s.correct) / s.answered)}%` : ''}</span></div></div>
      <button class="icon-btn danger-hover" data-del="${s.id}" title="Delete set">${icon('trash')}</button></div>`;
  }).join('') : '<p class="muted small">No sets yet.</p>';
}

$('#p-sets').addEventListener('click', async e => {
  const del = e.target.closest('[data-del]');
  if (del) {
    if (!await confirmDialog('Delete this practice set?', 'Your answers in it are removed too.', { ok: 'Delete', danger: true })) return;
    await api(`/exercise_sets/${del.dataset.del}`, { method: 'DELETE' });
    if (S.currentSet?.id === +del.dataset.del) S.currentSet = null;
    return loadPractice();
  }
  const item = e.target.closest('.set-item');
  if (item) openSet(+item.dataset.id);
});

$('#p-generate').addEventListener('click', e => {
  const id = +$('#p-chapter').value;
  if (!id) return toast('Pick a chapter first', 'error');
  const before = $('#p-set').innerHTML;
  $('#p-set').innerHTML = loading('Writing new exercises for this chapter. This takes 20-60 seconds...');
  busy(e.currentTarget, 'Writing exercises...', async () => {
    try {
      renderSet(await api(`/chapters/${id}/exercises`, { method: 'POST', body: { count: +$('#p-count').value, focus: $('#p-focus').value } }));
      loadSets();
    } catch (err) { $('#p-set').innerHTML = before; throw err; }
  });
});

async function openSet(id) {
  try { renderSet(await api(`/exercise_sets/${id}`)); loadSets(); }
  catch (err) { S.currentSet = null; toast(err.message, 'error'); }
}

function exerciseInput(e) {
  const val = e.user_answer || '';
  if (e.type === 'multiple_choice') {
    return `<div class="opts">${e.options.map(o => `<label class="opt-btn"><input type="radio" name="ex${e.id}" value="${esc(o)}" ${o === val ? 'checked' : ''}><span>${esc(o)}</span></label>`).join('')}</div>`;
  }
  if (['translate_to_german', 'translate_to_native', 'short_answer'].includes(e.type)) {
    return `<textarea rows="2" data-ans="${e.id}" placeholder="Your answer">${esc(val)}</textarea>`;
  }
  return `<input type="text" data-ans="${e.id}" value="${esc(val)}" autocomplete="off" spellcheck="false" placeholder="Your answer">`;
}

function feedbackHtml(e) {
  if (e.correct === null) return '';
  return `<div class="fb">${icon(e.correct ? 'check' : 'x')}<div><b>${e.correct ? 'Richtig!' : 'Not quite.'}</b> ${esc(e.feedback === 'Richtig!' ? '' : e.feedback)}
    ${e.correct ? '' : `<details><summary>Show answer</summary><b>${esc(e.answer)}</b><p class="muted">${esc(e.explanation)}</p></details>`}</div></div>`;
}

function renderSet(s, drafts = {}) {
  S.currentSet = s;
  const answered = s.exercises.filter(e => e.correct !== null);
  const right = answered.filter(e => e.correct === 1).length;
  const wrong = answered.length - right;
  const finished = answered.length === s.exercises.length;
  $('#p-set').innerHTML = `
    <div class="set-head">
      <div><h2>${esc(s.title)}</h2>
        <div class="meter"><div class="meter-bar"><span style="width:${(100 * answered.length) / s.exercises.length}%"></span></div>
        <span>${answered.length}/${s.exercises.length} answered · ${right} right</span></div></div>
      <div class="row"><button data-check>${icon('check')}<span>Check answers</span></button>
        <button id="p-reset" class="ghost">${icon('undo')}Start over</button></div>
    </div>
    ${finished ? '' : '<p class="muted small set-hint"><kbd>Enter</kbd> checks the question you\'re on and moves to the next. For longer answers use <kbd>Ctrl</kbd>+<kbd>Enter</kbd>.</p>'}
    ${finished ? `<div class="result ${wrong ? '' : 'perfect'}"><b>${right}/${s.exercises.length}</b> ${wrong ? `correct. Try the ${wrong} you missed again?` : 'Perfekt! Every answer right.'}
      ${wrong ? `<button id="p-retry" class="small">${icon('undo')}Retry wrong ones</button>` : ''}</div>` : ''}
    ${s.exercises.map((e, i) => `
      <div class="ex ${e.correct === 1 ? 'right' : e.correct === 0 ? 'wrong' : ''}" data-id="${e.id}">
        <div class="ex-head"><span class="num">${i + 1}</span><span class="ex-type">${TYPE_LABEL[e.type] || esc(e.type)}</span><span class="chip">${esc(e.topic)}</span></div>
        ${e.instructions ? `<div class="ex-instr">${esc(e.instructions)}</div>` : ''}
        <div class="ex-prompt">${esc(e.prompt)}</div>
        ${exerciseInput(e)}
        ${feedbackHtml(e)}
      </div>`).join('')}
    ${finished ? '' : `<button data-check class="wide">${icon('check')}Check answers</button>`}`;

  const pset = $('#p-set');
  // Answers typed but not checked yet are put back after every redraw.
  const open = new Set(s.exercises.filter(e => e.correct === null).map(e => String(e.id)));
  for (const [id, v] of Object.entries(drafts)) {
    if (!open.has(id) || !v) continue;
    const field = $(`[data-ans="${id}"]`, pset);
    if (field) field.value = v;
    else $$(`input[name="ex${id}"]`, pset).forEach(r => { r.checked = r.value === v; });
  }
  const collect = () => {
    const a = {};
    $$('[data-ans]', pset).forEach(i => { a[i.dataset.ans] = i.value; });
    $$('.opts input:checked', pset).forEach(i => { a[i.name.slice(2)] = i.value; });
    return a;
  };
  // Check the given answers: one question (Enter) or everything (the Check button).
  const check = async (answers, exEl) => {
    const all = collect();
    exEl?.classList.add('checking');
    try {
      const checked = await api(`/exercise_sets/${s.id}/check`, { method: 'POST', body: { answers } });
      renderSet(checked, all);
      loadSets();
      if (checked.new_mistakes) toast(`${checked.new_mistakes} mistake${checked.new_mistakes === 1 ? '' : 's'} saved to your Mistake Book`);
    } catch (err) { exEl?.classList.remove('checking'); toast(err.message, 'error'); }
  };
  $$('[data-check]', pset).forEach(b => b.addEventListener('click', () => busy(b, 'Checking...', async () => {
    const answers = collect();
    if (!Object.values(answers).some(v => v.trim())) return toast('Answer at least one question first', 'error');
    await check(answers);
  })));
  $$('.opts input', pset).forEach(r => r.addEventListener('change', () => check({ [r.name.slice(2)]: r.value }, r.closest('.ex'))));
  $$('textarea[data-ans]', pset).forEach(t => t.addEventListener('keydown', ev => {
    if (ev.key === 'Enter' && (ev.ctrlKey || ev.metaKey) && t.value.trim()) { ev.preventDefault(); check({ [t.dataset.ans]: t.value }, t.closest('.ex')); }
  }));
  $('#p-reset').addEventListener('click', async () => { renderSet(await api(`/exercise_sets/${s.id}/reset`, { method: 'POST' })); loadSets(); });
  $('#p-retry')?.addEventListener('click', async () => { renderSet(await api(`/exercise_sets/${s.id}/reset?wrong_only=true`, { method: 'POST' })); loadSets(); });
  // Put the cursor in the first question still to answer (after checking, or "Retry wrong ones").
  if (!finished && S.view === 'practice') $$('[data-ans]', $('#p-set')).find(i => !i.value.trim() && open.has(i.dataset.ans))?.focus();
  $$('input[data-ans]', $('#p-set')).forEach((inp, i, all) => inp.addEventListener('keydown', ev => {
    if (ev.key !== 'Enter') return;
    ev.preventDefault();
    if (inp.value.trim()) check({ [inp.dataset.ans]: inp.value }, inp.closest('.ex'));
    else (all[i + 1] || $('[data-check]', pset)).focus();
  }));
}

// ---------- gap-fills from the book (offline dictionary, no AI) ----------
const G = { kind: store.get('gapKind') || 'mixed', sheet: null, checked: false };
const gnorm = s => (s || '').trim().toLowerCase().replace(/[.,!?;:]+$/, '');

async function loadGaps() {
  await loadBooks();
  const keep = S.gapChapterWant || $('#g-chapter').value || store.get('gapChapter') || '';
  S.gapChapterWant = null;
  $('#g-chapter').innerHTML = chapterOptions(keep) || '<option value="">Import a book first</option>';
  $$('#g-kinds [data-kind]').forEach(b => b.classList.toggle('on', b.dataset.kind === G.kind));
  if (!G.sheet) {
    $('#g-sheet').innerHTML = emptyState('practice', 'Practice with your own book',
      'Pick a chapter and press New sheet. You get real sentences from it with an article, an adjective ending or a verb form to fill in. Marked instantly, as often as you like.');
  }
}

$('#g-kinds').addEventListener('click', e => {
  const b = e.target.closest('[data-kind]');
  if (!b) return;
  G.kind = b.dataset.kind;
  store.set('gapKind', G.kind);
  $$('#g-kinds [data-kind]').forEach(x => x.classList.toggle('on', x === b));
  if ($('#g-chapter').value) newSheet();
});
$('#g-chapter').addEventListener('change', () => { store.set('gapChapter', $('#g-chapter').value); newSheet(); });
$('#g-new').addEventListener('click', () => newSheet());

async function newSheet() {
  const id = +$('#g-chapter').value;
  if (!id) return toast('Pick a chapter first', 'error');
  $('#g-sheet').innerHTML = loading('Finding sentences...');
  try {
    const r = await api(`/chapters/${id}/gapfill?kind=${G.kind}&n=10`);
    Object.assign(G, { sheet: r, checked: false });
    renderSheet();
  } catch (err) { $('#g-sheet').innerHTML = ''; toast(err.message, 'error'); }
}

const KIND_NAME = { articles: 'Article', adjectives: 'Adjective ending', verbs: 'Verb form' };
function renderSheet() {
  const r = G.sheet;
  if (!r.items.length) {
    $('#g-sheet').innerHTML = emptyState('practice', 'No sentences for this',
      Object.values(r.available).some(Boolean) ? 'This chapter has none of this kind. Try Mixed or another kind.'
        : 'This chapter has no German sentences the app can use, for example when it is mostly English explanations or pictures.');
    return;
  }
  $('#g-sheet').innerHTML = `<div class="g-head"><h2>Fill in the gaps</h2><span class="muted small" id="g-score"></span></div>
    <ol class="g-list">${r.items.map((it, i) => {
      const prefix = it.gap.replace('___', '');
      return `<li class="g-item" data-i="${i}"><span class="chip">${KIND_NAME[it.kind]}</span>
        <p>${esc(it.before)}<span class="g-gap">${esc(prefix)}<input data-i="${i}" autocomplete="off" spellcheck="false" size="${Math.max(3, it.solution.length - prefix.length + 1)}"></span>${esc(it.after)}
        ${it.cue ? `<small class="g-cue">(${esc(it.cue)})</small>` : ''}</p><p class="g-fb small"></p></li>`;
    }).join('')}</ol>
    <div class="row"><button id="g-check" data-icon="check"><span>Check</span></button><button class="ghost" id="g-again" data-icon="play"><span>New sheet</span></button></div>`;
  fillIconsIn($('#g-sheet'));
  const inputs = $$('input[data-i]', $('#g-sheet'));
  inputs[0]?.focus();
  inputs.forEach((inp, i) => inp.addEventListener('keydown', ev => {
    if (ev.key !== 'Enter') return;
    ev.preventDefault();
    if (G.checked) return newSheet();
    if (inputs[i + 1]) inputs[i + 1].focus(); else checkSheet();
  }));
  $('#g-check').addEventListener('click', checkSheet);
  $('#g-again').addEventListener('click', () => newSheet());
}

function fillIconsIn(box) {
  $$('[data-icon]', box).forEach(b => { if (!b.querySelector('svg')) b.insertAdjacentHTML('afterbegin', icon(b.dataset.icon)); });
}

function checkSheet() {
  if (G.checked) return;
  G.checked = true;
  let right = 0;
  G.sheet.items.forEach((it, i) => {
    const li = $(`.g-item[data-i="${i}"]`, $('#g-sheet'));
    const inp = $('input', li);
    const given = gnorm(inp.value);
    const prefix = it.gap.replace('___', '').toLowerCase();
    const ok = !!given && it.answers.some(a => gnorm(a) === given || gnorm(a) === prefix + given);
    if (ok) right++;
    inp.readOnly = true;
    li.classList.add(ok ? 'right' : 'wrong');
    $('.g-fb', li).innerHTML = ok ? `${icon('check')} ${esc(it.solution)}` : `${icon('x')} The book says: <b>${esc(it.solution)}</b>`;
    api('/gapfill/record', { method: 'POST', body: { kind: it.kind, correct: ok } }).catch(() => {});
  });
  $('#g-score').textContent = `${right}/${G.sheet.items.length} right`;
  $('#g-check').disabled = true;
  $('#g-again').focus();
  api('/activity', { method: 'POST', body: { kind: 'practice', seconds: 30 } }).catch(() => {});
}

// Practice time counts toward today's study minutes.
setInterval(() => {
  if (S.view === 'practice' && S.currentSet && isActive()) {
    api('/activity', { method: 'POST', body: { kind: 'practice', seconds: 15 } }).catch(() => {});
  }
}, 15000);
