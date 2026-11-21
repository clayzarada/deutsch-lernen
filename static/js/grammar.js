// Grammar handbook: about 45 short topics (A1-B1), searchable by topic or by German word, each with tables, examples,
// common mistakes, a note for Turkish speakers and a "Try it" button that opens the matching drill.
// The text comes from the server already in the app language (app/grammar_data.py).
import { $, $$, S, api, esc, icon, store, toast, emptyState, loading, registerView, show } from './core.js';

const G = { index: null, level: store.get('grammarLevel') || '', q: '', hits: null, topic: null, current: null };

registerView('grammar', loadGrammar);

// **bold** and *italic*, as in the course lessons.
const fmt = s => esc(s).replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>').replace(/\*([^*\s][^*]*)\*/g, '<i>$1</i>');

async function loadGrammar() {
  if (!G.index) G.index = await api('/grammar');
  const want = S.grammarTopic;
  S.grammarTopic = null;
  if (want) { G.q = ''; G.hits = null; $('#gr-q').value = ''; G.level = ''; }
  renderLevels();
  renderList();
  const id = want || G.current || store.get('grammarTopic') || G.index.topics[0].id;
  await openTopic(id, { scroll: !!want });
}

function renderLevels() {
  $('#gr-levels').innerHTML = [['', 'All levels'], ...G.index.levels.map(l => [l, l])].map(([id, label]) =>
    `<button type="button" class="chip-btn ${G.level === id ? 'on' : ''}" data-level="${id}" aria-pressed="${G.level === id}">${esc(label)}</button>`).join('');
}

function topicButton(t) {
  return `<button type="button" class="gr-item ${t.id === G.current ? 'on' : ''}" data-topic="${t.id}">
    <span class="gr-lv lv-${t.level}">${t.level}</span><span class="grow">${esc(t.title)}</span></button>`;
}

function renderList() {
  const shown = G.index.topics.filter(t => !G.level || t.level === G.level);
  let html;
  if (G.hits) {
    // While searching: one list, best match first.
    const byId = Object.fromEntries(shown.map(t => [t.id, t]));
    const hits = G.hits.map(id => byId[id]).filter(Boolean);
    html = hits.length ? `<p class="muted small">${hits.length === 1 ? '1 topic' : `${hits.length} topics`}</p>${hits.map(topicButton).join('')}`
      : '<p class="muted small">Nothing found. Try a German word (wegen, dessen) or a topic (dative, Perfekt).</p>';
  } else {
    html = G.index.themes.map(th => {
      const ts = shown.filter(t => t.theme === th.id);
      return ts.length ? `<h4 class="dc-group">${esc(th.title)}</h4>${ts.map(topicButton).join('')}` : '';
    }).join('');
  }
  $('#gr-list').innerHTML = html;
}

async function openTopic(id, { scroll = false } = {}) {
  if (!G.index.topics.some(t => t.id === id)) id = G.index.topics[0].id;
  G.current = id;
  store.set('grammarTopic', id);
  $$('#gr-list .gr-item').forEach(b => b.classList.toggle('on', b.dataset.topic === id));
  const item = $('#gr-list .gr-item.on'), list = $('#gr-list');
  if (item && list.scrollHeight > list.clientHeight) list.scrollTop = item.offsetTop - list.offsetTop - list.clientHeight / 3;
  const box = $('#gr-topic');
  if (G.topic?.id !== id) {
    box.innerHTML = loading('Opening...');
    try { G.topic = await api(`/grammar/topic/${encodeURIComponent(id)}`); }
    catch (err) { box.innerHTML = emptyState('page', 'This topic could not be opened'); return toast(err.message, 'error'); }
  }
  renderTopic();
  if (scroll || matchMedia('(max-width: 860px)').matches) box.scrollIntoView({ block: 'start', behavior: 'smooth' });
}

function blockHtml(b) {
  if (b.kind === 'p') return `<p>${fmt(b.text)}</p>`;
  if (b.kind === 'rule') return `<div class="ls-rule">${fmt(b.text)}</div>`;
  if (b.kind === 'tip') return `<div class="ls-tip">${icon('sparkles')}<div>${fmt(b.text)}</div></div>`;
  if (b.kind === 'table') {
    return `<div class="gr-table-wrap"><table class="gr-table">${b.caption ? `<caption>${esc(b.caption)}</caption>` : ''}
      <thead><tr>${b.cols.map(c => `<th scope="col">${esc(c)}</th>`).join('')}</tr></thead>
      <tbody>${b.rows.map(r => `<tr>${r.map((c, i) => i === 0 ? `<th scope="row">${esc(c)}</th>` : `<td>${esc(c)}</td>`).join('')}</tr>`).join('')}</tbody>
    </table></div>`;
  }
  return '';
}

function renderTopic() {
  const t = G.topic;
  const all = G.index.topics, i = all.findIndex(x => x.id === t.id);
  const prev = all[i - 1], next = all[i + 1];
  const theme = G.index.themes.find(th => th.id === t.theme)?.title || '';
  $('#gr-topic').innerHTML = `<article class="panel gr-topic" aria-labelledby="gr-title">
    <div class="gr-meta"><span class="gr-lv lv-${t.level}">${t.level}</span><span class="chip">${esc(theme)}</span></div>
    <h2 id="gr-title">${esc(t.title)}</h2>
    <p class="gr-summary">${fmt(t.summary)}</p>
    ${t.try ? `<div class="gr-try"><button type="button" data-try>${icon('target')}<span>Try it</span></button><span class="muted small">Practise this in the app's free drills.</span></div>` : ''}
    <div class="gr-body">${t.body.map(blockHtml).join('')}</div>
    <h3>Examples</h3>
    <div class="ls-ex">${t.examples.map(e => `<div><span lang="de">${fmt(e.de)}</span><small>${esc(e.tr)}</small></div>`).join('')}</div>
    <h3>Common mistakes</h3>
    <ul class="gr-mistakes">${t.mistakes.map(m => `<li><div class="gr-pair"><span class="gr-wrong" lang="de"><span aria-hidden="true">❌</span> ${esc(m.wrong)}</span>
      <span class="gr-arrow" aria-hidden="true">→</span><span class="gr-right" lang="de"><span aria-hidden="true">✅</span> ${esc(m.right)}</span></div>
      <small>${esc(m.why)}</small></li>`).join('')}</ul>
    <aside class="gr-tr" lang="tr"><h3>For Turkish speakers</h3><p>${esc(t.note)}</p></aside>
    <nav class="gr-nav" aria-label="Other topics">
      ${prev ? `<button type="button" class="ghost" data-topic="${prev.id}">${icon('left')}<span>${esc(prev.title)}</span></button>` : '<span></span>'}
      ${next ? `<button type="button" class="ghost" data-topic="${next.id}"><span>${esc(next.title)}</span>${icon('right')}</button>` : ''}
    </nav>
  </article>`;
}

// "Try it": the drill pages pick this up when they load (see loadDecl in declensions.js).
function tryIt(spec) {
  S[spec.view + 'Want'] = spec;
  show(spec.view);
}

$('#gr-levels').addEventListener('click', e => {
  const b = e.target.closest('[data-level]');
  if (!b) return;
  G.level = b.dataset.level;
  store.set('grammarLevel', G.level);
  renderLevels();
  renderList();
});

document.addEventListener('click', e => {
  if (S.view !== 'grammar') return;
  const t = e.target.closest('#view-grammar [data-topic]');
  if (t) return openTopic(t.dataset.topic, { scroll: !!t.closest('.gr-nav') });
  if (e.target.closest('#gr-topic [data-try]') && G.topic?.try) tryIt(G.topic.try);
});

let searchTimer = null;
$('#gr-q').addEventListener('input', () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(async () => {
    const q = $('#gr-q').value.trim();
    G.q = q;
    try { G.hits = q ? (await api('/grammar/search?q=' + encodeURIComponent(q))).ids : null; }
    catch (err) { return toast(err.message, 'error'); }
    if (G.q === q) renderList();
  }, 150);
});
$('#gr-q').addEventListener('keydown', e => {
  if (e.key !== 'Enter') return;
  e.preventDefault();
  const first = $('#gr-list .gr-item');
  if (first) openTopic(first.dataset.topic, { scroll: true });
});
