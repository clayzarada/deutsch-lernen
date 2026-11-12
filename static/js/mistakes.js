// Mistake Book: every wrong answer collected in one place, grouped by topic, with drills and flashcards.
import { $, $$, S, api, esc, icon, busy, toast, emptyState, registerView, show, confirmDialog, refreshNav, isActive } from './core.js';

const SOURCE_LABEL = { practice: 'Practice set', page: 'Textbook page', speaking: 'Speaking', writing: 'Writing' };
const M = { status: 'open', topic: null, selected: new Set(), data: null };

registerView('mistakes', loadMistakes);

// Going over your mistakes is study time too.
setInterval(() => {
  if (S.view === 'mistakes' && isActive()) api('/activity', { method: 'POST', body: { kind: 'practice', seconds: 15 } }).catch(() => {});
}, 15000);

async function loadMistakes() {
  if (S.mistakeTopic !== undefined) { M.topic = S.mistakeTopic; S.mistakeTopic = undefined; M.status = 'open'; }
  $$('#mk-status button').forEach(b => b.classList.toggle('active', b.dataset.status === M.status));
  const params = new URLSearchParams({ status: M.status });
  if (M.topic !== null) params.set('topic', M.topic);
  M.data = await api('/mistakes?' + params);
  // New mistakes are linked to declension skills in the background (one small Claude call per 40 mistakes).
  if (M.data.unlinked && S.settings?.has_key && !M.linking) {
    M.linking = true;
    api('/mistakes/link', { method: 'POST' }).then(r => { M.linking = false; if (r.linked && S.view === 'mistakes') loadMistakes(); })
      .catch(() => { M.linking = false; });
  }
  M.selected = new Set([...M.selected].filter(id => M.data.mistakes.some(m => m.id === id)));
  render();
}

function render() {
  const { mistakes, topics, counts } = M.data;
  const total = topics.reduce((a, t) => a + t.n, 0);
  $('#mk-topics').innerHTML = topics.length
    ? [`<button class="topic-btn ${M.topic === null ? 'active' : ''}" data-topic="">All topics<b>${total}</b></button>`]
      .concat(topics.map(t => `<button class="topic-btn ${M.topic === t.topic ? 'active' : ''}" data-topic="${esc(t.topic)}" data-has="1">
        ${esc(t.topic || 'Other')}<b>${t.n}</b></button>`)).join('')
    : '<p class="muted small">Nothing here yet.</p>';

  const sel = M.selected.size;
  const selLinked = mistakes.some(m => M.selected.has(m.id) && m.skills?.length);
  const learned = M.status === 'learned';
  $('#mk-bar').innerHTML = mistakes.length ? `
    <label class="check"><input type="checkbox" id="mk-all" ${sel && sel === mistakes.length ? 'checked' : ''}> ${sel ? `${sel} selected` : 'Select all'}</label>
    <span class="grow muted small">${counts.open || 0} to learn · ${counts.learned || 0} learned</span>
    ${learned ? '' : `<button data-act="free" ${selLinked ? '' : 'disabled'} title="Free drills from the declension engine, no AI needed">${icon('rocket')}Free drill</button>
      <button class="ghost" data-act="drill" ${sel ? '' : 'disabled'}>${icon('sparkles')}AI drill</button>
      <button class="ghost" data-act="cards" ${sel ? '' : 'disabled'}>${icon('cards')}Make flashcards</button>`}
    <button class="ghost" data-act="${learned ? 'reopen' : 'learned'}" ${sel ? '' : 'disabled'}>${icon(learned ? 'undo' : 'check')}${learned ? 'Back to "to learn"' : 'Mark learned'}</button>
    <button class="icon-btn danger-hover" data-act="delete" title="Delete selected" ${sel ? '' : 'disabled'}>${icon('trash')}</button>` : '';

  const linked = mistakes.filter(m => m.skills?.length);
  const banner = !learned && linked.length ? `<div class="mk-free">${icon('rocket')}<div class="grow"><b>${linked.length} of these mistake${linked.length === 1 ? ' is' : 's are'} about cases and endings.</b>
      <small>Drill them for free in the declension trainer. Each one is marked learned once you get it right on ${M.data.learned_days} separate days.</small></div>
      <button data-free-all>Drill all ${linked.length}</button></div>` : '';
  $('#mk-list').innerHTML = mistakes.length ? banner + mistakes.map(m => `
    <label class="mk-item ${M.selected.has(m.id) ? 'selected' : ''}">
      <input type="checkbox" data-id="${m.id}" ${M.selected.has(m.id) ? 'checked' : ''}>
      <div class="grow">
        ${questionHtml(m)}
        <div class="mk-line"><span class="wrong">${esc(m.wrong)}</span>${icon('right')}<span class="right">${esc(m.correct)}</span></div>
        ${m.explanation ? `<p class="small">${esc(m.explanation)}</p>` : ''}
        <p class="muted small">${m.context ? esc(m.context) + ' · ' : ''}${SOURCE_LABEL[m.source] || esc(m.source)} · ${new Date(m.last_seen || m.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}</p>
      </div>
      <div class="mk-tags">${m.topic ? `<span class="chip">${esc(m.topic)}</span>` : ''}
        ${m.times > 1 ? `<span class="st due">${m.times}× made</span>` : ''}
        ${m.card_id ? `<span class="st later">${icon('cards')}card</span>` : ''}
        ${m.skills?.length && !learned ? `<span class="st new" title="Right on ${m.drill_days} of ${M.data.learned_days} days in the free drill">${icon('rocket')}${m.drill_days}/${M.data.learned_days} days</span>` : ''}
        ${m.learned_by === 'drill' && learned ? `<span class="st later">${icon('rocket')}learned in drills</span>` : ''}</div>
    </label>`).join('')
    : emptyState('mistake', learned ? 'Nothing marked as learned yet' : 'No mistakes to learn',
      learned ? '' : 'Mistakes from practice sets and checked textbook pages show up here automatically.');
}

// The original task: instruction (small, can be expanded) and the sentence with its gap.
function questionHtml(m) {
  if (!m.question) return '';
  const parts = m.question.split(/\n\n|\s+[–—]\s+/);
  const sentence = parts.length > 1 ? parts.slice(1).join('\n') : parts[0];
  const instruction = parts.length > 1 ? parts[0] : '';
  return `<div class="mk-question">${instruction ? `<span class="mk-instr" title="${esc(instruction)}">${esc(instruction)}</span>` : ''}
    <span class="mk-sentence">${esc(sentence).replace(/_{3,}/g, '<u>&nbsp;&nbsp;?&nbsp;&nbsp;</u>')}</span></div>`;
}

$('#mk-status').addEventListener('click', e => {
  const b = e.target.closest('[data-status]');
  if (!b) return;
  Object.assign(M, { status: b.dataset.status, topic: null, selected: new Set() });
  loadMistakes();
});

$('#mk-topics').addEventListener('click', e => {
  const b = e.target.closest('[data-topic]');
  if (!b) return;
  M.topic = b.dataset.has ? b.dataset.topic : null;
  M.selected = new Set();
  loadMistakes();
});

function freeDrill(ids) {
  return api('/mistakes/skills', { method: 'POST', body: { ids } }).then(r => {
    if (!r.keys.length) return toast('None of these can be drilled in the declension trainer', 'error');
    S.declKeys = r.keys;
    S.declTab = 'free';
    show('decl');
  });
}

$('#mk-list').addEventListener('click', e => {
  if (e.target.closest('[data-free-all]')) { e.preventDefault(); freeDrill(M.data.mistakes.filter(m => m.skills?.length).map(m => m.id)); }
});

$('#mk-list').addEventListener('change', e => {
  const id = +e.target.dataset.id;
  if (!id) return;
  if (e.target.checked) M.selected.add(id); else M.selected.delete(id);
  render();
});

$('#mk-bar').addEventListener('change', e => {
  if (e.target.id !== 'mk-all') return;
  M.selected = e.target.checked ? new Set(M.data.mistakes.map(m => m.id)) : new Set();
  render();
});

$('#mk-bar').addEventListener('click', async e => {
  const b = e.target.closest('[data-act]');
  if (!b || b.disabled) return;
  const ids = [...M.selected];
  const act = b.dataset.act;
  if (act === 'free') return freeDrill(ids.filter(id => M.data.mistakes.find(m => m.id === id)?.skills?.length));
  if (act === 'drill') {
    return busy(b, 'Writing a drill...', async () => {
      const r = await api('/mistakes/drill', { method: 'POST', body: { ids, count: Math.min(20, Math.max(8, ids.length * 2)) } });
      S.currentSet = { id: r.set_id };
      show('practice');
    });
  }
  if (act === 'cards') {
    return busy(b, 'Making cards...', async () => {
      const r = await api('/mistakes/cards', { method: 'POST', body: { ids } });
      toast(r.added ? `Made ${r.added} flashcard${r.added === 1 ? '' : 's'}${r.skipped ? ` (${r.skipped} already had one)` : ''}. They're in your review now.` : 'These already have flashcards');
      refreshNav();
      loadMistakes();
    });
  }
  if (act === 'delete' && !await confirmDialog(`Delete ${ids.length} mistake${ids.length === 1 ? '' : 's'}?`, 'Use "Mark learned" instead if you just want them out of the way.', { ok: 'Delete', danger: true })) return;
  const body = act === 'delete' ? { ids, delete: true } : { ids, status: act === 'reopen' ? 'open' : 'learned' };
  await api('/mistakes', { method: 'PUT', body });
  if (act === 'learned') toast(`Nice! ${ids.length} mistake${ids.length === 1 ? '' : 's'} marked as learned`);
  M.selected = new Set();
  loadMistakes();
});
