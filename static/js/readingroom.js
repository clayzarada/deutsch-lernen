// Reading room: short texts at your level, LingQ-style. Every word is shaded by how well you know it (from the
// shared known-words record); click a word to look it up, mark it, or make a flashcard. The computer's own voice
// can read the text aloud sentence by sentence. Your own texts and AI stories live here too.
import { aiTag } from './aitag.js';
import { $, $$, S, api, esc, icon, busy, toast, store, registerView, isActive, confirmDialog, promptDialog, hearButton, loading, emptyState, refreshNav } from './core.js';
import { dictEntryHtml } from './reader.js';

const NEW = 0, SEEN = 1, LEARNING = 2, KNOWN = 3, IGNORED = -1;
const SWEET = [90, 98];  // the "sweet spot": enough known words to read with ease, a few new ones to learn
const SPEEDS = [0.6, 0.8, 1, 1.2];
const R = { data: null, filter: store.get('rr-filter') || 'all', text: null, sents: [], st: new Map(), word: null, seconds: 0 };

// Home's "good next read" card opens a text directly (S.readingOpen).
registerView('reading', () => {
  const want = S.readingOpen;
  S.readingOpen = null;
  if (want) return openText(want);
  return R.text ? null : loadLibrary();
});

// The page heading belongs to the library; an open text has its own title and a back button.
const pageHead = on => $('#view-reading > .page-head')?.classList.toggle('hidden', !on);

// ---------- library ----------
async function loadLibrary() {
  R.text = null;
  pageHead(true);
  stopSpeech();
  $('#rr-box').innerHTML = loading('Opening the reading room...');
  R.data = await api('/readingroom');
  renderLibrary();
}

const summary = t => (S.settings?.ui_language === 'tr' ? t.summary_tr : t.summary_en) || '';
const isSweet = t => t.known_pct >= SWEET[0] && t.known_pct <= SWEET[1];
const meterTone = p => (p >= SWEET[0] ? '' : p >= 80 ? 'mid' : 'bad');

function cardHtml(t) {
  const own = t.source !== 'library';
  return `<article class="rr-card ${isSweet(t) ? 'sweet' : ''}" data-open="${esc(t.key)}">
    <div class="rr-card-top">
      ${t.level ? `<span class="chip rr-level lv-${esc(t.level)}">${esc(t.level)}</span>` : ''}
      ${t.genre ? `<span class="chip">${esc(t.genre)}</span>` : ''}${t.topic && !own ? `<span class="chip">${esc(t.topic)}</span>` : ''}
      ${t.source === 'ai' ? aiTag() : own ? '<span class="chip">Your text</span>' : ''}
      ${isSweet(t) ? `<span class="pill ok">${icon('target')}Good next read</span>` : ''}
      <span class="grow"></span>
      ${t.finished ? `<span class="rr-done" title="Finished">${icon('check')}${t.finished > 1 ? `<span>${t.finished}×</span>` : ''}</span>` : ''}
    </div>
    <button type="button" class="rr-title" data-no-i18n>${esc(t.title)}</button>
    ${summary(t) ? `<p class="small muted rr-sum">${esc(summary(t))}</p>` : ''}
    <div class="meter"><div class="meter-bar ${meterTone(t.known_pct)}"><span style="width:${t.known_pct}%"></span></div><span>You know ${t.known_pct}% of the words</span></div>
    <div class="row rr-card-foot"><small class="muted grow">${t.words} words · about ${t.minutes} min</small>
      ${own ? `<button type="button" class="icon-btn" data-rename="${esc(t.key)}" title="Rename">${icon('edit')}</button>
        <button type="button" class="icon-btn danger-hover" data-delete="${esc(t.key)}" title="Delete">${icon('trash')}</button>` : ''}</div>
  </article>`;
}

const FILTERS = [['all', 'All'], ['A1', 'A1'], ['A2', 'A2'], ['B1', 'B1'], ['mine', 'Your texts'], ['done', 'Finished']];

function filtered() {
  const f = R.filter, all = R.data.texts;
  if (f === 'mine') return all.filter(t => t.source !== 'library');
  if (f === 'done') return all.filter(t => t.finished);
  if (f === 'all') return all;
  return all.filter(t => t.level === f);
}

function renderLibrary() {
  const d = R.data;
  const sweet = d.texts.filter(t => isSweet(t) && !t.finished).sort((a, b) => b.known_pct - a.known_pct).slice(0, 3);
  const list = filtered();
  const levels = d.ai_levels.map(l => `<option ${l === (d.ai_levels.includes(S.settings.level) ? S.settings.level : 'A2') ? 'selected' : ''}>${l}</option>`).join('');
  $('#rr-box').innerHTML = `
    <div class="split rr-split">
      <div class="side-col">
        <div class="panel">
          <h2>How it works</h2>
          <p class="muted small">You learn most from texts where you already know 90 to 98% of the words: easy enough to enjoy, with a few new words to pick up.</p>
          <p class="muted small">New words are highlighted. Click a word to look it up and mark it as known, learning or ignored. Your choices update every text's numbers.</p>
          <p class="small rr-total">${d.finished_total ? `You have finished ${d.finished_total} texts.` : 'Nothing finished yet.'}</p>
        </div>
        <details class="panel rr-add" id="rr-add">
          <summary><h2>Add your own text</h2></summary>
          <p class="muted small">Paste a German text or import a .txt file. It stays on this computer.</p>
          <label>Title<input id="rr-add-title" maxlength="120" placeholder="Optional"></label>
          <label>Level<select id="rr-add-level"><option value="">Not set</option>${d.ai_levels.map(l => `<option>${l}</option>`).join('')}</select></label>
          <label>Text<textarea id="rr-add-text" rows="8" maxlength="${d.max_chars}" lang="de" placeholder="Paste your text here"></textarea></label>
          <div class="row wrap"><small id="rr-add-count" class="muted grow"></small>
            <label class="button ghost-link rr-file">${icon('upload')}<span>Import .txt</span><input id="rr-add-file" type="file" accept=".txt,text/plain" hidden></label>
            <button type="button" id="rr-add-save">${icon('plus')}Save</button></div>
        </details>
        ${S.settings.has_key ? `<div class="panel rr-story">
          <h2>${icon('sparkles')}Write me a story</h2>
          <p class="muted small">The AI writes a short story at your level, mostly from words you know or are learning, with a few new ones. It is saved with your texts and labeled AI-written.</p>
          <label>Topic<input id="rr-story-topic" maxlength="200" placeholder="e.g. a day at the lake, a job interview"></label>
          <label>Level<select id="rr-story-level">${levels}</select></label>
          <button type="button" id="rr-story-go" class="wide">${icon('sparkles')}Write me a story</button>
        </div>` : `<p class="muted small rr-ai-note">${icon('sparkles')}<span>With AI turned on (Plus or your own Claude API key), the reading room can also write stories for you from the words you know.</span></p>`}
        ${d.recent.length ? `<div class="panel"><h2>Recently finished</h2>${d.recent.map(r => `
          <button type="button" class="rr-recent" data-open="${esc(r.text_key)}"><span class="grow" data-no-i18n>${esc(r.title)}</span>
            <small class="muted">${new Date(r.ts).toLocaleDateString(undefined, { day: 'numeric', month: 'short' })}</small></button>`).join('')}</div>` : ''}
      </div>
      <div class="main-col">
        ${sweet.length ? `<section class="rr-next"><h2>${icon('target')}Good next reads</h2>
          <p class="muted small">You know 90 to 98% of the words in these.</p>
          <div class="rr-grid">${sweet.map(cardHtml).join('')}</div></section>` : ''}
        <div class="row wrap rr-filters"><div class="tabs" role="tablist">${FILTERS.map(([k, l]) =>
          `<button type="button" data-filter="${k}" class="${R.filter === k ? 'active' : ''}">${l}</button>`).join('')}</div></div>
        ${list.length ? `<div class="rr-grid">${list.map(cardHtml).join('')}</div>`
          : emptyState('book', R.filter === 'done' ? 'Nothing finished yet' : 'No texts here yet',
            R.filter === 'mine' ? 'Add your own text on the left.' : '')}
      </div>
    </div>`;
  updateCount();
}

function updateCount() {
  const el = $('#rr-add-count');
  if (el) el.textContent = `${$('#rr-add-text').value.length.toLocaleString()} / ${R.data.max_chars.toLocaleString()} characters`;
}

async function saveOwn(btn) {
  const text = $('#rr-add-text').value;
  if (!text.trim()) return toast('Paste or import a text first.', 'error');
  await busy(btn, 'Saving...', async () => {
    const t = await api('/readingroom/texts', { method: 'POST', body: { title: $('#rr-add-title').value, level: $('#rr-add-level').value, text } });
    toast('Text saved');
    openText(t.key);
  });
}

async function writeStory(btn) {
  await busy(btn, 'Writing your story...', async () => {
    const t = await api('/readingroom/story', { method: 'POST', body: { topic: $('#rr-story-topic').value, level: $('#rr-story-level').value } });
    refreshNav();
    openText(t.key);
  });
}

$('#rr-box').addEventListener('click', async e => {
  const f = e.target.closest('[data-filter]');
  if (f) { R.filter = f.dataset.filter; store.set('rr-filter', R.filter); return renderLibrary(); }
  const rn = e.target.closest('[data-rename]');
  if (rn) {
    const t = R.data.texts.find(x => x.key === rn.dataset.rename);
    const title = await promptDialog('Rename this text', t.title);
    if (!title) return;
    try { await api('/readingroom/texts/' + t.key, { method: 'PUT', body: { title } }); t.title = title; renderLibrary(); }
    catch (err) { toast(err.message, 'error'); }
    return;
  }
  const del = e.target.closest('[data-delete]');
  if (del) {
    const t = R.data.texts.find(x => x.key === del.dataset.delete);
    if (!await confirmDialog('Delete this text?', 'It is removed from your reading room. Words you marked stay marked.', { ok: 'Delete', danger: true })) return;
    try { await api('/readingroom/texts/' + t.key, { method: 'DELETE' }); await loadLibrary(); toast('Text deleted'); }
    catch (err) { toast(err.message, 'error'); }
    return;
  }
  if (e.target.closest('#rr-add-save')) return saveOwn(e.target.closest('button'));
  if (e.target.closest('#rr-story-go')) return writeStory(e.target.closest('button'));
  const back = e.target.closest('[data-rr-back]');
  if (back) return loadLibrary();
  const open = e.target.closest('[data-open]');
  if (open && !e.target.closest('label, input, select, textarea')) openText(open.dataset.open);
});
$('#rr-box').addEventListener('input', e => { if (e.target.id === 'rr-add-text') updateCount(); });
$('#rr-box').addEventListener('change', e => {
  if (e.target.id !== 'rr-add-file') return;
  const file = e.target.files[0];
  e.target.value = '';
  if (!file) return;
  if (file.size > R.data.max_chars * 4) return toast('This file is too big. Import a text under 20,000 characters.', 'error');
  const rd = new FileReader();
  rd.onload = () => {
    let text = String(rd.result || '');
    if (text.length > R.data.max_chars) { text = text.slice(0, R.data.max_chars); toast('Only the first 20,000 characters were kept.', 'error'); }
    $('#rr-add-text').value = text;
    if (!$('#rr-add-title').value) $('#rr-add-title').value = file.name.replace(/\.txt$/i, '');
    updateCount();
  };
  rd.readAsText(file, 'utf-8');
});

// ---------- reader ----------
async function openText(key) {
  stopSpeech();
  R.word = null;
  R.seconds = 0;
  $('#rr-box').innerHTML = loading('Opening the text...');
  const t = await api('/readingroom/texts/' + encodeURIComponent(key)).catch(err => { toast(err.message, 'error'); return null; });
  if (!t) return loadLibrary();
  const r = await api('/known/text', { method: 'POST', body: { text: t.text, saw: false } });
  R.text = t;
  R.st = new Map();
  for (const p of r.tokens) if (p.lemma) R.st.set(p.lemma, p.s);
  R.sents = [];
  pageHead(false);
  renderReader(r.tokens);
  // Record the visit (new words become "seen") without changing the shading you see now, so the words that
  // were new when you opened the text stay highlighted while you read it.
  api('/known/text', { method: 'POST', body: { text: t.text, saw: true } }).catch(() => {});
  $('main').scrollTop = 0;  // the page scrolls inside <main>, not the window
}

// Splits the tokens into paragraphs of sentences so the read-aloud can follow along.
function buildHtml(tokens) {
  const paras = [];
  let para = [], sent = [];
  const endSent = () => {
    if (sent.length) {
      const i = R.sents.length;
      R.sents.push(sent.map(p => p.t).join(''));
      para.push(`<span class="rr-s" data-s="${i}">${sent.map(p => p.lemma
        ? `<span class="rr-w" data-l="${esc(p.lemma)}" tabindex="-1">${esc(p.t)}</span>` : esc(p.t)).join('')}</span>`);
    }
    sent = [];
  };
  const endPara = () => { endSent(); if (para.length) paras.push(`<p>${para.join('')}</p>`); para = []; };
  tokens.forEach((p, k) => {
    if (p.lemma) { sent.push(p); return; }
    let rest = p.t;
    while (rest) {
      // a sentence ends at . ! ? … (plus closing quotes) before a space or the end; "6. November" and "z. B." don't
      const m = rest.match(/[.!?…]+["“”»«‘’')]*(?=\s|$)/);
      const nl = rest.indexOf('\n');
      if (m && (nl < 0 || m.index < nl)) {
        const before = rest.slice(0, m.index), after = rest.slice(m.index + m[0].length);
        const ordinal = /\d$/.test(before) && !/^[^\S\n]*(\n|$)/.test(after);  // "am 6. November"
        const abbrev = !before && tokens[k - 1]?.lemma && tokens[k - 1].t.length === 1;  // "z. B."
        sent.push({ t: rest.slice(0, m.index + m[0].length) });
        rest = after;
        if (!ordinal && !abbrev) endSent();
        continue;
      }
      if (nl >= 0) {
        if (rest.slice(0, nl).trim()) sent.push({ t: rest.slice(0, nl) });
        endPara();
        rest = rest.slice(nl + 1).replace(/^\n+/, '');
        continue;
      }
      if (!sent.length && rest.trim()) {  // "200 Gramm" or "„Minka" starts a sentence; the space before it doesn't
        const lead = rest.match(/^\s*/)[0];
        if (lead) para.push(esc(lead));
        rest = rest.slice(lead.length);
      }
      if (sent.length || rest.trim()) sent.push({ t: rest }); else para.push(esc(rest));
      rest = '';
    }
  });
  endPara();
  return paras.join('');
}

function stats() {
  let total = 0, ok = 0;
  const fresh = new Set();
  for (const el of $$('#rr-text .rr-w')) {
    const s = R.st.get(el.dataset.l) ?? NEW;
    total++;
    if (s >= LEARNING || s === IGNORED) ok++; else fresh.add(el.dataset.l);
  }
  return { pct: total ? Math.round(100 * ok / total) : 100, fresh: [...fresh] };
}

function shade() {
  for (const el of $$('#rr-text .rr-w')) el.className = 'rr-w st' + (R.st.get(el.dataset.l) ?? NEW) + (el.classList.contains('sel') ? ' sel' : '');
  const s = stats();
  $('#rr-cov').textContent = `You know ${s.pct}% of the words`;
  $('#rr-fresh').textContent = s.fresh.length ? `${s.fresh.length} words in this text are still new to you.` : 'You know every word in this text.';
  $('#rr-mark-rest').disabled = !s.fresh.length;
}

function renderReader(tokens) {
  const t = R.text;
  $('#rr-box').innerHTML = `
    <div class="rr-head">
      <button type="button" class="ghost small" data-rr-back>${icon('left')}Reading room</button>
      <div class="grow rr-head-title">
        <p class="eyebrow">${[t.level, t.genre].filter(Boolean).map(x => `<span>${esc(x)}</span>`).join(' · ')}</p>
        <h1 data-no-i18n>${esc(t.title)}</h1>
        ${t.source === 'ai' ? `<p class="small rr-ai-label">${aiTag()}<span>It may contain mistakes, so trust the dictionary over the story if they disagree.</span></p>` : ''}
      </div>
    </div>
    <div class="rr-tools panel" id="rr-tools"></div>
    <div class="rr-layout">
      <div class="panel rr-page">
        <article id="rr-text" class="rr-text" lang="de" data-no-i18n>${buildHtml(tokens)}</article>
        <div class="rr-finish">
          <h2>Finished reading?</h2>
          <p class="muted small" id="rr-fresh"></p>
          <div class="row wrap">
            <button type="button" id="rr-done">${icon('check')}I've finished this text</button>
          </div>
          <div id="rr-after" class="hidden rr-after">
            <p><b>Mark the remaining new words as known?</b></p>
            <p class="muted small">Only do this if you understood them. You can change any word later by clicking it.</p>
            <div class="row wrap"><button type="button" id="rr-mark-rest" class="ghost">${icon('check')}Mark them as known</button>
              <button type="button" class="ghost" data-rr-back>Back to the reading room</button></div>
          </div>
          <label class="check small rr-auto"><input type="checkbox" id="rr-auto" ${store.get('rr-auto-known') === '1' ? 'checked' : ''}> When I finish a text, mark its remaining new words as known automatically</label>
        </div>
      </div>
      <aside class="rr-side">
        <div class="panel">
          <p class="small rr-cov-line"><b id="rr-cov"></b></p>
          <div class="rr-legend small"><span class="rr-w st0">new</span><span class="rr-w st1">seen</span><span class="rr-w st2">learning</span><span class="rr-w st3">known</span></div>
        </div>
        <div class="panel rr-word" id="rr-word"><p class="muted small">Click any word to look it up and mark how well you know it. With the keyboard: Tab into the text, then use the arrow keys and Enter.</p></div>
      </aside>
    </div>`;
  const first = $('#rr-text .rr-w');
  if (first) first.tabIndex = 0;
  shade();
  renderTools();
}

// ---------- word panel ----------
const sentenceOf = el => el.closest('.rr-s')?.textContent.trim() || '';
const STATUS_BTNS = [[KNOWN, 'Known', 'check'], [LEARNING, 'Learning', 'target'], [IGNORED, 'Ignore', 'x']];

function wordButtons(lemma) {
  const s = R.st.get(lemma) ?? NEW;
  return STATUS_BTNS.map(([v, label, ic]) =>
    `<button type="button" class="chip-btn ${s === v ? 'on' : ''}" data-status="${v}" aria-pressed="${s === v}">${icon(ic)}${label}</button>`).join('');
}

const cardWord = front => (front || '').replace(/^(der|die|das)\s+/i, '').split(/[,·(|]/)[0].trim().toLowerCase();

async function openWord(el) {
  $$('#rr-text .rr-w.sel').forEach(x => x.classList.remove('sel'));
  el.classList.add('sel');
  const lemma = el.dataset.l, word = el.textContent;
  R.word = { lemma, word, sentence: sentenceOf(el), entry: null };
  const box = $('#rr-word');
  box.classList.add('open');  // on narrow windows the panel opens as a sheet at the bottom
  box.innerHTML = `<div class="lk-head"><span class="lk-word" data-no-i18n>${esc(word)}</span>${hearButton(word, 'tiny')}<span class="grow"></span>
      <button type="button" class="icon-btn rr-word-close" title="Close">${icon('x')}</button></div>
    ${lemma.toLowerCase() !== word.toLowerCase() ? `<p class="muted small">Dictionary form: <b data-no-i18n>${esc(lemma)}</b></p>` : ''}
    <div class="row wrap rr-status" id="rr-status">${wordButtons(lemma)}</div>
    <div id="rr-dict">${loading('Looking it up...')}</div>
    <div class="row wrap rr-word-acts">
      <button type="button" class="ghost small" id="rr-card">${icon('cards')}Add flashcard</button>
      <button type="button" class="ghost small" id="rr-say-here">${icon('volume')}Read aloud from here</button>
    </div>`;
  let entries = [];
  try { entries = (await api('/dict?word=' + encodeURIComponent(word))).entries; } catch { /* shown below */ }
  if (R.word?.word !== word) return;
  R.word.entry = entries.find(x => !x.grammar) || null;
  $('#rr-dict').innerHTML = entries.length
    ? `<div class="lookup">${entries.map(dictEntryHtml).join('')}<p class="muted tiny">From the built-in dictionary (Wiktionary), free and offline.</p></div>`
    : `<p class="muted small">This word isn't in the built-in dictionary. Names and rare words often aren't; you can mark it as ignored.</p>`;
  if (S.settings.has_key) $('#rr-dict').insertAdjacentHTML('beforeend', `<button type="button" class="link-btn" id="rr-ai-look">${icon('sparkles')}Explain it in this sentence</button>`);
  // Is it already a flashcard? Then say so instead of offering a duplicate.
  const w = cardWord(R.word.entry?.word || lemma);
  try {
    const have = await api('/cards?q=' + encodeURIComponent(w));
    if (R.word?.word === word && have.some(c => cardWord(c.front) === w)) markCardDone();
  } catch { /* the check is only a convenience */ }
}

function markCardDone() {
  const b = $('#rr-card');
  if (b) { b.disabled = true; b.innerHTML = `${icon('check')}In your flashcards`; }
}

async function setStatus(v) {
  const { lemma } = R.word;
  try {
    const r = await api('/known/mark', { method: 'POST', body: { lemmas: [lemma], status: v } });
    for (const [k, s] of Object.entries(r.statuses)) R.st.set(k, s);
    $('#rr-status').innerHTML = wordButtons(lemma);
    shade();
  } catch (err) { toast(err.message, 'error'); }
}

async function addCard(btn) {
  const { entry, lemma, sentence } = R.word;
  const e = entry;
  const front = e ? [e.article, e.word].filter(Boolean).join(' ') + (e.pos === 'noun' && e.plural ? `, ${e.plural}` : '') : lemma;
  const back = e ? (e.short || e.meanings.slice(0, 2).join('; ')) : '';
  if (!back) return toast('No dictionary meaning to put on the card. Make it under Flashcards instead.', 'error');
  const current = R.word;
  const added = await busy(btn, 'Adding...', async () => {
    const w = cardWord(front);
    const have = await api('/cards?q=' + encodeURIComponent(w));
    if (have.some(c => cardWord(c.front) === w)) { toast('This word is already in your flashcards'); return 'had'; }
    await api('/cards', { method: 'POST', body: { front, back, extra: [e.pos === 'verb' ? e.forms_text : '', sentence].filter(Boolean).join('\n'),
      type: e.pos === 'verb' ? 'verb' : 'vocab', tags: ['reading room'] } });
    toast('Card added');
    refreshNav();
    return 'added';
  });
  if (!added || R.word !== current) return;
  markCardDone();
  // Flashcards feed the known-words record, so the word's status may have changed: refresh its shading.
  const r = await api('/known/text', { method: 'POST', body: { text: current.word } }).catch(() => null);
  const tok = r?.tokens.find(p => p.lemma === lemma);
  if (tok) { R.st.set(lemma, tok.s); shade(); if (R.word === current) $('#rr-status').innerHTML = wordButtons(lemma); }
}

async function aiLook(btn) {
  const { word, sentence } = R.word;
  await busy(btn, 'Asking the AI...', async () => {
    const r = await api('/lookup', { method: 'POST', body: { word, sentence } });
    btn.replaceWith(Object.assign(document.createElement('div'), { className: 'lookup rr-ai-look', innerHTML: `
      <p class="lk-meaning">${esc(r.meaning)}</p>
      ${r.meaning_in_context ? `<p class="small"><b>Here:</b> ${esc(r.meaning_in_context)}</p>` : ''}
      ${r.note ? `<p class="small tip">${icon('sparkles')}${esc(r.note)}</p>` : ''}` }));
  });
}

$('#rr-box').addEventListener('click', e => {
  const w = e.target.closest('#rr-text .rr-w');
  if (w) { e.preventDefault(); return openWord(w); }
  const st = e.target.closest('#rr-status [data-status]');
  if (st && R.word) return setStatus(+st.dataset.status);
  if (e.target.closest('#rr-card') && R.word) return addCard(e.target.closest('#rr-card'));
  if (e.target.closest('#rr-ai-look') && R.word) return aiLook(e.target.closest('#rr-ai-look'));
  if (e.target.closest('#rr-say-here') && R.word) {
    const s = $('#rr-text .rr-w.sel')?.closest('.rr-s');
    return startSpeech(s ? +s.dataset.s : 0);
  }
  if (e.target.closest('.rr-word-close')) { $('#rr-word').classList.remove('open'); $$('#rr-text .rr-w.sel').forEach(x => x.classList.remove('sel')); return; }
  if (e.target.closest('#rr-done')) return finish(e.target.closest('#rr-done'));
  if (e.target.closest('#rr-mark-rest')) return markRest(e.target.closest('#rr-mark-rest'));
});
$('#rr-box').addEventListener('change', e => { if (e.target.id === 'rr-auto') store.set('rr-auto-known', e.target.checked ? '1' : ''); });

// Roving focus: one tab stop for the text, arrow keys move from word to word, Enter or Space opens the word.
$('#rr-box').addEventListener('keydown', e => {
  const w = e.target.closest?.('#rr-text .rr-w');
  if (!w) return;
  if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openWord(w); return; }
  const step = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key];
  if (!step) return;
  e.preventDefault();
  const all = $$('#rr-text .rr-w');
  const next = all[all.indexOf(w) + step];
  if (next) { w.tabIndex = -1; next.tabIndex = 0; next.focus(); }
});

// ---------- finishing ----------
async function finish(btn) {
  const ok = await busy(btn, 'Saving...', async () => {
    await api('/readingroom/finished', { method: 'POST', body: { key: R.text.key, seconds: R.seconds } });
    toast('Well done! Saved as finished.');
    return true;
  });
  if (!ok) return;
  btn.innerHTML = `${icon('check')}Finished`;
  btn.classList.add('ghost');
  const fresh = stats().fresh;
  if (!fresh.length) return;
  if (store.get('rr-auto-known') === '1') return markRest($('#rr-mark-rest'));
  $('#rr-after').classList.remove('hidden');
}

async function markRest(btn) {
  const fresh = stats().fresh;
  if (!fresh.length) return;
  await busy(btn, 'Saving...', async () => {
    for (let i = 0; i < fresh.length; i += 500) {
      const r = await api('/known/mark', { method: 'POST', body: { lemmas: fresh.slice(i, i + 500), status: KNOWN } });
      for (const [k, s] of Object.entries(r.statuses)) R.st.set(k, s);
    }
    toast(`${fresh.length} words marked as known`);
  });
  shade();
  if (R.word) $('#rr-status').innerHTML = wordButtons(R.word.lemma);
}

// Reading time counts toward today's study minutes (and the plan, stats and streak), like the other pages.
// Listening to the text read aloud counts too, even without touching anything.
setInterval(() => {
  if (S.view !== 'reading' || !R.text || !(isActive() || T.playing)) return;
  R.seconds += 15;
  api('/activity', { method: 'POST', body: { kind: 'reading', seconds: 15 } }).catch(() => {});
}, 15000);

// ---------- read aloud ----------
// The computer's own German voice (free, offline) reads sentence by sentence and the current sentence is
// highlighted. With a Gemini key there is also Google's voice, which sounds more natural but needs the internet.
const T = { playing: false, idx: 0, run: 0, rate: +(store.get('rr-rate') || 1), engine: store.get('rr-engine') || 'local', audio: null, clips: new Map() };

const hasSpeech = () => !!window.speechSynthesis;
const deVoices = () => (hasSpeech() ? speechSynthesis.getVoices().filter(v => /^de(-|_|$)/i.test(v.lang)) : []);
function pickVoice() {
  const vs = deVoices(), want = store.get('rr-voice');
  return vs.find(v => v.name === want) || vs.find(v => v.localService && /de-DE/i.test(v.lang)) || vs.find(v => v.localService) || vs[0] || null;
}
if (hasSpeech()) speechSynthesis.addEventListener?.('voiceschanged', () => { if (R.text) renderTools(); });

function renderTools() {
  const box = $('#rr-tools');
  if (!box) return;
  const gemini = !!S.settings.has_gemini_key;
  if (!gemini) T.engine = 'local';
  const voices = deVoices(), local = T.engine === 'local';
  const canPlay = !local || voices.length;
  box.innerHTML = `<div class="row wrap">
      <button type="button" id="rr-play" ${canPlay ? '' : 'disabled'}>${icon(T.playing ? 'pause' : 'play')}${T.playing ? 'Pause' : 'Read aloud'}</button>
      <button type="button" class="ghost small" id="rr-restart" ${canPlay ? '' : 'disabled'} title="Start again from the beginning">${icon('undo')}From the start</button>
      <label class="rr-inline">Speed<select id="rr-rate">${SPEEDS.map(r => `<option value="${r}" ${r === T.rate ? 'selected' : ''}>${r}×</option>`).join('')}</select></label>
      ${gemini ? `<label class="rr-inline">Voice<select id="rr-engine"><option value="local" ${local ? 'selected' : ''}>Computer voice (free, offline)</option>
        <option value="gemini" ${local ? '' : 'selected'}>Google Gemini voice (online)</option></select></label>` : ''}
      ${local && voices.length > 1 ? `<label class="rr-inline">German voice<select id="rr-voice" data-no-i18n>${voices.map(v =>
        `<option ${v.name === pickVoice()?.name ? 'selected' : ''}>${esc(v.name)}</option>`).join('')}</select></label>` : ''}
    </div>
    ${local && !voices.length ? `<p class="small rr-voice-note">${icon('volume')}<span>${hasSpeech()
      ? 'No German voice is installed on this computer, so it can’t read aloud yet. On Windows: Settings → Time & language → Speech → Add voices → Deutsch (Deutschland). On a Mac: System Settings → Accessibility → Spoken Content → System voice → Manage Voices → German. Then restart the app.'
      : 'This window can’t read text aloud.'}</span>${gemini ? ' <span>You can use the Google Gemini voice instead.</span>' : ''}</p>` : ''}`;
}

function highlight(i) {
  $$('#rr-text .rr-s.speaking').forEach(x => x.classList.remove('speaking'));
  const s = $(`#rr-text .rr-s[data-s="${i}"]`);
  if (s) { s.classList.add('speaking'); s.scrollIntoView({ block: 'nearest', behavior: 'smooth' }); }
}

function startSpeech(i = T.idx) {
  stopSpeech();
  T.idx = Math.max(0, Math.min(i, R.sents.length - 1));
  T.playing = true;
  renderTools();
  speakNext(T.run);
}

function stopSpeech() {
  T.run++;
  const was = T.playing;
  T.playing = false;
  if (hasSpeech()) speechSynthesis.cancel();
  T.audio?.pause();
  if (was) renderTools();
}

function done(run) {
  if (run !== T.run) return;
  T.idx++;
  speakNext(run);
}

async function geminiClip(i) {
  if (!T.clips.has(i)) {
    T.clips.set(i, api('/speak', { method: 'POST', body: { text: R.sents[i].slice(0, 600) } })
      .then(r => r.blob()).then(b => URL.createObjectURL(b)).catch(err => { T.clips.delete(i); throw err; }));
  }
  return T.clips.get(i);
}

async function speakNext(run) {
  if (run !== T.run) return;
  while (T.idx < R.sents.length && !/[A-Za-zÄÖÜäöüß]/.test(R.sents[T.idx])) T.idx++;
  if (T.idx >= R.sents.length) { T.idx = 0; stopSpeech(); $$('#rr-text .rr-s.speaking').forEach(x => x.classList.remove('speaking')); return; }
  highlight(T.idx);
  const text = R.sents[T.idx];
  if (T.engine === 'gemini') {
    try {
      const url = await geminiClip(T.idx);
      if (T.idx + 1 < R.sents.length) geminiClip(T.idx + 1).catch(() => {});
      if (run !== T.run) return;
      T.audio = new Audio(url);
      T.audio.playbackRate = T.rate;
      T.audio.onended = () => done(run);
      await T.audio.play();
    } catch (err) { toast(err.message, 'error'); stopSpeech(); }
    return;
  }
  const u = new SpeechSynthesisUtterance(text.replace(/…/g, ' '));
  u.lang = 'de-DE';
  const v = pickVoice();
  if (v) { u.voice = v; u.lang = v.lang; }
  u.rate = T.rate;
  u.onend = () => done(run);
  u.onerror = e => { if (run === T.run && e.error !== 'interrupted' && e.error !== 'canceled') { toast('The voice stopped: ' + e.error, 'error'); stopSpeech(); } };
  speechSynthesis.speak(u);
}

$('#rr-box').addEventListener('click', e => {
  if (e.target.closest('#rr-play')) return T.playing ? stopSpeech() : startSpeech(T.idx);
  if (e.target.closest('#rr-restart')) return startSpeech(0);
});
$('#rr-box').addEventListener('change', e => {
  const id = e.target.id;
  if (id === 'rr-rate') { T.rate = +e.target.value; store.set('rr-rate', T.rate); if (T.playing) startSpeech(T.idx); }
  if (id === 'rr-engine') { T.engine = e.target.value; store.set('rr-engine', T.engine); if (T.playing) startSpeech(T.idx); else renderTools(); }
  if (id === 'rr-voice') { store.set('rr-voice', e.target.value); if (T.playing) startSpeech(T.idx); }
});
document.addEventListener('viewchange', e => { if (e.detail !== 'reading') stopSpeech(); });
