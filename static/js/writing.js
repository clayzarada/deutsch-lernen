// Writing desk: pick an exam-style task (or the plan's writing task, or your own topic), write, and get it
// marked like the Goethe writing paper. Corrections go to the Mistake Book.
import { $, $$, S, api, esc, icon, busy, toast, store, registerView, refreshNav, isActive, confirmDialog } from './core.js';

const W = { tasks: [], history: [], task: null, view: 'write', piece: null, started: 0, seconds: 0, timer: null, level: null };
const LEVELS = ['B1', 'B2', 'C1'];
const draftKey = t => 'writing-draft:' + (t?.id || t?.title || 'own');

registerView('writing', loadWriting);

async function loadWriting() {
  const r = await api('/writing');
  W.tasks = r.tasks;
  W.history = r.history;
  W.level ||= LEVELS.includes(S.settings.level) ? S.settings.level : S.settings.level < 'B1' ? 'B1' : 'C1';
  if (S.writingTask) { openTask(S.writingTask); S.writingTask = null; }
  else if (!W.task) openTask(W.tasks.find(t => t.level === W.level) || W.tasks[0]);
  renderSide();
  if (W.view === 'write') renderEditor(); else renderResult();
}

function renderSide() {
  const plan = S.plan?.blocks?.find(b => b.kind === 'writing' && b.status !== 'done');
  $('#w-side').innerHTML = `
    <div class="panel"><h2>Choose a task</h2>
      ${plan ? `<button class="w-task plan" data-plan>${icon('today')}<span class="grow"><b>From today's plan</b><small>${esc(plan.title)}</small></span></button>` : ''}
      <div class="tabs w-levels">${LEVELS.map(l => `<button data-level="${l}" class="${W.level === l ? 'active' : ''}">${l}</button>`).join('')}</div>
      ${W.tasks.filter(t => t.level === W.level).map(t => `<button class="w-task ${W.task?.id === t.id ? 'on' : ''}" data-task="${t.id}">
        <span class="grow"><b>${esc(t.title)}</b><small>${esc(t.kind)} · about ${t.words} words</small></span></button>`).join('')}
      <button class="w-task ${W.task?.id === 'own' ? 'on' : ''}" data-own>${icon('edit')}<span class="grow"><b>My own topic</b><small>Write about anything</small></span></button>
      ${S.settings.has_key ? `<div class="w-new"><input id="w-topic" placeholder="Topic for a new task (optional)"><button class="ghost small" id="w-gen">${icon('sparkles')}New task</button></div>` : ''}
    </div>
    <div class="panel"><h2>Your writing</h2>${W.history.length ? W.history.map(h => `
      <button class="w-hist ${W.piece?.id === h.id ? 'on' : ''}" data-piece="${h.id}"><span class="grow"><b>${esc(h.title)}</b>
        <small>${new Date(h.created_at).toLocaleDateString(undefined, { day: 'numeric', month: 'short' })} · ${h.level} · ${h.words} words</small></span>
        <span class="w-score ${h.score >= 60 ? 'ok' : ''}">${h.score}</span></button>`).join('') : '<p class="muted small">Nothing yet. Your marked texts will appear here.</p>'}</div>`;
}

function openTask(t) {
  W.task = t;
  W.view = 'write';
  W.piece = null;
  W.seconds = 0;
}

function taskHtml(t) {
  if (t.id === 'own') return `<div class="w-taskbox"><p class="eyebrow">Free writing</p><h2>My own topic</h2>
    <input id="w-own-title" placeholder="What are you writing about? (optional)" value="${esc(t.title === 'My own topic' ? '' : t.title)}"></div>`;
  return `<div class="w-taskbox"><p class="eyebrow">${esc(t.level || '')} ${esc(t.kind || 'Task')}${t.minutes ? ` · ${t.minutes} min in the exam` : ''}</p>
    <h2>${esc(t.title)}</h2><p>${esc(t.task)}</p>
    ${t.points?.length ? `<ul>${t.points.map(p => `<li>${esc(p)}</li>`).join('')}</ul>` : ''}</div>`;
}

function renderEditor() {
  const t = W.task;
  const draft = store.get(draftKey(t)) || '';
  $('#w-main').innerHTML = `${taskHtml(t)}
    <div class="w-editor">
      <textarea id="w-text" spellcheck="false" placeholder="Schreiben Sie hier...">${esc(draft)}</textarea>
      <div class="w-foot"><span id="w-count" class="w-count"></span><span id="w-time" class="muted small"></span><span class="grow"></span>
        <span class="muted small">Your draft is saved as you type.</span>
        <button id="w-check">${icon('check')}Check my writing</button></div>
    </div>`;
  updateCount();
  $('#w-text').focus();
}

function updateCount() {
  const text = $('#w-text')?.value || '';
  const n = (text.match(/[\wÄÖÜäöüß'-]+/g) || []).length;
  const target = W.task?.words;
  const el = $('#w-count');
  if (!el) return;
  el.innerHTML = `<b>${n}</b> word${n === 1 ? '' : 's'}${target ? ` of about ${target}` : ''}`;
  el.classList.toggle('ok', !!target && n >= target * .9 && n <= target * 1.3);
  el.classList.toggle('over', !!target && n > target * 1.3);
}

$('#w-main').addEventListener('input', e => {
  if (e.target.id !== 'w-text') return;
  store.set(draftKey(W.task), e.target.value);
  if (!W.started) W.started = Date.now();
  updateCount();
});
$('#w-main').addEventListener('keydown', e => {
  if (e.target.id === 'w-text' && e.key === 'Enter' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); $('#w-check')?.click(); }
});

// Writing time: counts toward today's study minutes and is shown under the text.
setInterval(() => {
  if (S.view !== 'writing' || W.view !== 'write' || !isActive()) return;
  W.seconds += 15;
  const m = Math.round(W.seconds / 60);
  if ($('#w-time')) $('#w-time').textContent = m ? `· ${m} min` : '';
  api('/activity', { method: 'POST', body: { kind: 'writing', seconds: 15 } }).catch(() => {});
}, 15000);

async function check(btn) {
  const text = $('#w-text').value;
  const t = { ...W.task };
  if (t.id === 'own') t.title = $('#w-own-title').value.trim() || 'My own topic';
  await busy(btn, 'Marking...', async () => {
    const r = await api('/writing/check', { method: 'POST', body: {
      text, seconds: W.seconds, task_id: t.id === 'own' || t.id?.startsWith('plan') || t.id === 'ai' ? null : t.id,
      title: t.title, kind: t.kind, task: t.task, points: t.points, words: t.words, level: t.level || S.settings.level } });
    store.set(draftKey(W.task), '');
    W.piece = r; W.view = 'result';
    W.history = (await api('/writing')).history;
    renderSide(); renderResult();
    if (r.new_mistakes) toast(`${r.new_mistakes} correction${r.new_mistakes === 1 ? '' : 's'} saved to your Mistake Book`);
    refreshNav();
  });
}

// The learner's text with each correction marked, in order of appearance.
function markedText(text, corrections) {
  const spans = [];
  corrections.forEach((c, i) => {
    let from = 0, at;
    while ((at = text.indexOf(c.original, from)) >= 0) {
      if (!spans.some(s => at < s.end && at + c.original.length > s.start)) { spans.push({ start: at, end: at + c.original.length, i }); break; }
      from = at + 1;
    }
  });
  spans.sort((a, b) => a.start - b.start);
  let out = '', pos = 0;
  for (const s of spans) {
    out += esc(text.slice(pos, s.start)) + `<mark class="w-err cat-${corrections[s.i].category}" data-corr="${s.i}">${esc(text.slice(s.start, s.end))}<sup>${s.i + 1}</sup></mark>`;
    pos = s.end;
  }
  return out + esc(text.slice(pos));
}

function renderResult() {
  const p = W.piece, r = p.result;
  $('#w-main').innerHTML = `${taskHtml({ ...p.task, id: p.task.task_id || 'done', title: p.title, level: p.level })}
    <div class="w-result">
      <div class="w-scores">
        <div class="w-overall ${r.passes ? 'pass' : ''}"><b>${r.overall}</b><span>/ 100</span><small>${r.passes ? `Would pass ${esc(p.level)}` : `Not a pass at ${esc(p.level)} yet`}</small></div>
        <div class="w-crit">${r.criteria.map(c => `<div><span>${esc(c.name)}</span><span class="meter"><span class="meter-bar ${c.score <= 2 ? 'bad' : c.score === 3 ? 'mid' : ''}"><span style="width:${c.score * 20}%"></span></span><b>${c.score}/5</b></span><small>${esc(c.comment)}</small></div>`).join('')}</div>
      </div>
      <p class="w-verdict">${esc(r.verdict)}</p>
      <h3>Your text <span class="muted small">${p.words} words · click a marked part to see why</span></h3>
      <div class="w-text-out">${markedText(p.text, r.corrections)}</div>
      ${r.corrections.length ? `<ol class="w-corr">${r.corrections.map((c, i) => `<li data-corr-item="${i}"><span class="wrong">${esc(c.original)}</span>${icon('right')}<span class="right">${esc(c.corrected)}</span>
        <small>${esc(c.explanation)}${c.topic ? ` · <i>${esc(c.topic)}</i>` : ''}</small></li>`).join('')}</ol>` : '<p class="muted">No mistakes found. Sehr gut!</p>'}
      ${r.tips?.length ? `<div class="ls-tip">${icon('sparkles')}<div><b>Next time</b><ul>${r.tips.map(t => `<li>${esc(t)}</li>`).join('')}</ul></div></div>` : ''}
      <details class="w-improved"><summary>Improved version</summary><p>${esc(r.improved).replace(/\n/g, '<br>')}</p></details>
      <div class="row dj-end-row"><button id="w-again">${icon('edit')}Write this task again</button>
        <button class="ghost" id="w-new">Choose another task</button><button class="icon-btn danger-hover" id="w-del" title="Delete this text">${icon('trash')}</button></div>
    </div>`;
}

$('#w-main').addEventListener('click', async e => {
  const t = e.target;
  if (t.closest('#w-check')) return check(t.closest('#w-check'));
  const mark = t.closest('[data-corr]');
  if (mark) {
    const li = $(`[data-corr-item="${mark.dataset.corr}"]`);
    $$('.w-corr li.lit').forEach(x => x.classList.remove('lit'));
    li?.classList.add('lit');
    li?.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    return;
  }
  if (t.closest('#w-again')) {
    const p = W.piece;
    openTask(W.tasks.find(x => x.id === p.task_id) || { ...p.task, id: p.task.task_id || 'again', title: p.title, level: p.level });
    renderSide(); return renderEditor();
  }
  if (t.closest('#w-new')) { W.view = 'write'; W.piece = null; renderSide(); return renderEditor(); }
  if (t.closest('#w-del')) {
    if (!await confirmDialog('Delete this text?', 'Its corrections stay in your Mistake Book.', { ok: 'Delete', danger: true })) return;
    await api(`/writing/${W.piece.id}`, { method: 'DELETE' });
    W.piece = null; W.view = 'write';
    return loadWriting();
  }
});

$('#w-side').addEventListener('click', async e => {
  const t = e.target;
  const lvl = t.closest('[data-level]');
  if (lvl) { W.level = lvl.dataset.level; return renderSide(); }
  const task = t.closest('[data-task]');
  if (task) { openTask(W.tasks.find(x => x.id === task.dataset.task)); renderSide(); return renderEditor(); }
  if (t.closest('[data-own]')) { openTask({ id: 'own', title: 'My own topic' }); renderSide(); return renderEditor(); }
  if (t.closest('[data-plan]')) {
    const b = S.plan.blocks.find(x => x.kind === 'writing' && x.status !== 'done');
    openTask({ id: 'plan-' + S.plan.id, title: b.title, kind: 'From your plan', task: b.instructions, level: S.settings.level });
    renderSide(); return renderEditor();
  }
  const piece = t.closest('[data-piece]');
  if (piece) {
    W.piece = await api(`/writing/${piece.dataset.piece}`);
    W.view = 'result';
    renderSide(); return renderResult();
  }
  if (t.closest('#w-gen')) {
    return busy(t.closest('#w-gen'), 'Writing a task...', async () => {
      const r = await api('/writing/task', { method: 'POST', body: { level: W.level, topic: $('#w-topic').value } });
      openTask({ ...r, id: 'ai', level: W.level });
      renderSide(); renderEditor();
    });
  }
});
