// Flashcards page: spaced-repetition review, browsing/editing/generating cards, Anki export.
import {
  $, $$, S, api, esc, icon, busy, toast, emptyState, loadBooks, chapterOptions, scopeParams, queryString,
  registerView, cardEditor, setBadge, confirmDialog, hearButton, refreshNav,
} from './core.js';

const GRADES = [['Again', 1], ['Hard', 2], ['Good', 3], ['Easy', 4]];

registerView('cards', loadCards);

async function loadCards() {
  await loadBooks();
  cardTab(S.cardTab || 'review');
}

function cardTab(tab) {
  S.cardTab = tab;
  $$('[data-tab]').forEach(b => b.classList.toggle('active', b.dataset.tab === tab));
  $$('#view-cards .tab').forEach(t => t.classList.toggle('hidden', t.id !== 'tab-' + tab));
  if (tab === 'review') loadReview();
  if (tab === 'browse') loadBrowse();
  if (tab === 'anki') $('#anki-scope').innerHTML = chapterOptions(S.cardScope || '', { all: true });
}
$$('[data-tab]').forEach(b => b.addEventListener('click', () => cardTab(b.dataset.tab)));

// ---------- review ----------
// Normal mode follows the spaced-repetition schedule. "Practice" mode shows any cards now and
// doesn't change when they come back.
const R = { queue: [], counts: null, scope: null, ahead: false, extraNew: 0, revealed: false, typed: '', shownAt: 0, done: 0, undo: null };
const TRICKY = 4; // missed this many times: the card probably needs rewording

// "in 25 min", "in 13 h", "tomorrow 9:58 PM", "in 3 days"
export function whenText(iso) {
  const d = new Date(iso), mins = (d - Date.now()) / 60000;
  if (mins <= 0) return 'now';
  if (mins < 60) return `in ${Math.round(mins)} min`;
  if (mins < 18 * 60) return `in ${Math.round(mins / 60)} h`;
  const days = Math.round((new Date(d).setHours(0, 0, 0, 0) - new Date().setHours(0, 0, 0, 0)) / 864e5);
  const time = d.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' });
  return days <= 1 ? `tomorrow ${time}` : `in ${days} days`;
}

export function startReview(scope = '', { ahead = false } = {}) {
  Object.assign(S, { reviewScope: scope, cardTab: 'review' });
  R.ahead = ahead;
  R.extraNew = 0;
  cardTab('review');
}

async function loadReview() {
  $('#rv-scope').innerHTML = chapterOptions(S.reviewScope || '', { all: true });
  const params = { ...scopeParams(S.reviewScope || ''), extra_new: R.extraNew || '', ahead: R.ahead || '' };
  const r = await api('/review/queue?' + queryString(params));
  Object.assign(R, { queue: r.cards, counts: r.counts, scope: r.scope, revealed: false, typed: '', done: 0, undo: null });
  loadStats();
  if (R.ahead) R.queue.sort(() => Math.random() - 0.5);
  renderReview();
}

$('#rv-scope').addEventListener('change', e => { S.reviewScope = e.target.value; R.extraNew = 0; loadReview(); });

function renderMode() {
  $('#rv-mode').innerHTML = R.ahead
    ? `<span class="pill-note">${icon('sparkles')}Practice mode: your answers here don't change when cards come back</span><button class="link-btn" id="rv-exit">Back to scheduled review</button>`
    : '';
  $('#rv-exit')?.addEventListener('click', () => { R.ahead = false; loadReview(); });
  $('#rv-keys').innerHTML = '<kbd>Space</kbd> show answer &nbsp; <kbd>Alt</kbd>+<kbd>H</kbd> hint &nbsp; ' + (R.ahead
    ? '<kbd>1</kbd> Again &nbsp; <kbd>2</kbd> Got it'
    : '<kbd>1</kbd> Again &nbsp; <kbd>2</kbd> Hard &nbsp; <kbd>3</kbd> Good &nbsp; <kbd>4</kbd> Easy');
  $('#rv-keys').classList.toggle('hidden', !R.queue.length);
}

function emptyReview() {
  const s = R.scope, k = R.counts;
  const waitingNew = R.ahead ? 0 : s.new;
  let title, text = '', buttons = '';
  if (!s.total) {
    title = 'No cards here yet';
    text = 'Make some under <b>Browse &amp; create</b> (pick a chapter and press Generate), or turn words into cards from the Reader.';
    buttons = '<button data-goto="browse">Make cards</button>';
  } else {
    title = R.done ? `Session complete: ${R.done} card${R.done === 1 ? '' : 's'} reviewed` : 'All caught up for now';
    const parts = [];
    if (waitingNew) {
      parts.push(`You've reached today's limit of ${S.settings.new_cards_per_day} new cards. <b>${waitingNew}</b> more new card${waitingNew === 1 ? ' is' : 's are'} waiting. (You can change the limit in Settings.)`);
      buttons += `<button data-more>${icon('plus')}Learn 10 more new cards now</button>`;
    }
    if (s.later) {
      parts.push(`<b>${s.later}</b> card${s.later === 1 ? '' : 's'} will come back for review. The next one is due <b>${whenText(s.next_due)}</b>.`);
    }
    parts.push('<span class="muted">Cards disappear after you grade them and return just before you\'d forget them. That\'s how spaced repetition works.</span>');
    text = parts.map(p => `<p>${p}</p>`).join('');
    buttons += `<button class="${waitingNew ? 'ghost' : ''}" data-ahead>${icon('cards')}Practice all ${s.total} cards now</button>`;
  }
  return `<div class="flash done-card">${icon(s.total ? 'check' : 'cards')}<div class="flash-front">${title}</div>${text}
    <div class="row wrap center-row">${buttons}</div></div>`;
}

function renderReview() {
  const c = R.queue[0], k = R.counts;
  setBadge('cards', k.due + k.new_available);
  renderMode();
  const box = $('#review-box');
  if (!c) {
    box.innerHTML = emptyReview();
    $('[data-more]', box)?.addEventListener('click', () => { R.extraNew += 10; loadReview(); });
    $('[data-ahead]', box)?.addEventListener('click', () => { R.ahead = true; loadReview(); });
    $('[data-goto]', box)?.addEventListener('click', () => cardTab('browse'));
    if (R.undo) box.insertAdjacentHTML('beforeend', undoHtml());
    $('#rv-undo')?.addEventListener('click', undoGrade);
    if (R.done) loadStats();
    return;
  }
  if (!R.revealed) R.shownAt = Date.now();
  const left = R.queue.length;
  // Typed answers may use ae, oe, ue and ss for ä, ö, ü and ß.
  const norm = s => s.toLowerCase().replace(/ä/g, 'ae').replace(/ö/g, 'oe').replace(/ü/g, 'ue').replace(/ß/g, 'ss').replace(/[^\p{L}\p{N} ]/gu, '').replace(/\s+/g, ' ').trim();
  const typedOk = R.typed && norm(c.back).includes(norm(R.typed));
  const grades = R.ahead
    ? [['Again', 1, 'see it again'], ['Got it', 3, 'next card']]
    : GRADES.map(([l, g]) => [l, g, c.previews?.[g] || '']);
  box.innerHTML = `
    <div class="review-top"><span>${left} left in this session</span><span class="muted">${R.ahead ? 'practice' : `${k.due} due · ${k.new_available} new today`}</span></div>
    <div class="session-bar"><span style="width:${(100 * R.done) / (R.done + left)}%"></span></div>
    <div class="flash ${R.revealed ? 'revealed' : ''}">
      <div class="flash-type">${esc(c.type)}${c.due ? '' : ' · new'}${c.lapses >= TRICKY ? ` · <span class="tricky" title="Consider rewording it or adding a hint (Browse & create → edit)">tricky: missed ${c.lapses} times</span>` : ''}</div>
      ${frontHtml(c)}
      ${!R.revealed && hintTopics(c).length ? `<button class="flash-hint" id="rv-hint" title="Show which grammar point this card is about (Alt+H)">${icon('sparkles')}<span class="q">Hint</span><span class="a">${hintTopics(c).map(esc).join(' · ')}</span></button>` : ''}
      ${R.revealed ? `<div class="flash-answer"><div class="flash-back">${esc(c.back)}</div>
        ${c.extra ? `<div class="flash-extra">${esc(c.extra)}</div>` : ''}
        ${R.typed ? `<div class="typed ${typedOk ? 'ok' : 'bad'}">${icon(typedOk ? 'check' : 'x')}You typed: ${esc(R.typed)}</div>` : ''}</div>`
      : '<input id="typed" placeholder="Type your answer (optional), then Enter" autocomplete="off" spellcheck="false">'}
    </div>
    <div class="flash-actions ${R.ahead ? 'two' : ''}">${R.revealed
      ? grades.map(([l, g, sub]) => `<button class="grade grade-${g}" data-grade="${g}"><b>${l}</b><small>${sub}</small></button>`).join('')
      : `<button id="reveal" class="reveal">Show answer</button>`}</div>${R.undo ? undoHtml() : ''}`;
  $('#rv-undo')?.addEventListener('click', undoGrade);
  $('#reveal')?.addEventListener('click', reveal);
  $('#rv-hint')?.addEventListener('pointerdown', e => e.preventDefault()); // keep the cursor in the answer box
  $('#rv-hint')?.addEventListener('click', toggleHint);
  const typed = $('#typed');
  typed?.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); R.typed = typed.value.trim(); reveal(); } });
  // Ready to type the next answer straight away, so a whole session works without the mouse.
  if (typed && S.view === 'cards') typed.focus();
  $$('[data-grade]', box).forEach(b => b.addEventListener('click', () => grade(+b.dataset.grade)));
}

// Mistake cards hold "instruction\n\nsentence": show the instruction small and the sentence as the card.
function frontHtml(c) {
  const split = c.type === 'fix' ? c.front.indexOf('\n\n') : -1;
  if (split > 0) {
    return `<div class="flash-task">${esc(c.front.slice(0, split))}</div><div class="flash-front fix">${esc(c.front.slice(split + 2))}</div>`;
  }
  return `<div class="flash-front">${esc(c.front)}${!['cloze', 'fix'].includes(c.type) ? hearButton(c.front.split(',')[0]) : ''}</div>`;
}

function reveal() { R.revealed = true; renderReview(); }

// The grammar point a card practices, from its tags (e.g. "Possessives in the dative"), hidden until asked for.
const NOT_HINTS = new Set(['mistake-book', 'grammar', 'declension', 'verbs', 'vocab', 'vocabulary']);
function hintTopics(c) {
  if (!['fix', 'cloze', 'rule'].includes(c.type)) return [];
  let tags = [];
  try { tags = JSON.parse(c.tags || '[]'); } catch { /* old cards without tags */ }
  return tags.filter(t => t && !NOT_HINTS.has(t.toLowerCase()) && !t.startsWith('decl:'));
}
function toggleHint() { $('#rv-hint')?.classList.toggle('shown'); }

async function grade(g) {
  const c = R.queue.shift();
  if (!c) return;
  const seconds = Math.round((Date.now() - R.shownAt) / 1000);
  R.revealed = false;
  R.typed = '';
  if (R.ahead) { // practice: no scheduling, but the time still counts toward today's study minutes
    if (g === 1) R.queue.push(c); else R.done++;
    R.undo = { card: c, again: g === 1 };
    api('/activity', { method: 'POST', body: { kind: 'flashcards', seconds: Math.min(seconds, 90) } }).catch(() => {});
    return renderReview();
  }
  try {
    const r = await api(`/review/${c.id}`, { method: 'POST', body: { grade: g, seconds } });
    R.counts = r.counts;
    if (g === 1) R.queue.push(r.card); // see it again this session
    else R.done++;
    R.undo = { card: c, again: g === 1, server: r.undo };
  } catch (err) { toast(err.message, 'error'); R.queue.unshift(c); }
  renderReview();
}

const undoHtml = () => '<p class="center rv-undo"><button class="link-btn" id="rv-undo">' + icon('undo') + 'Undo last grade <kbd>Ctrl</kbd>+<kbd>Z</kbd></button></p>';

// Take back the last grade: the card returns to the front with its old schedule.
async function undoGrade() {
  const u = R.undo;
  if (!u) return;
  R.undo = null;
  try {
    let card = u.card;
    if (u.server) {
      const r = await api('/review-undo', { method: 'POST', body: u.server });
      card = r.card;
      R.counts = r.counts;
    }
    if (u.again) {
      const i = R.queue.map(x => x.id).lastIndexOf(card.id);
      if (i >= 0) R.queue.splice(i, 1);
    } else R.done = Math.max(0, R.done - 1);
    R.queue.unshift(card);
    Object.assign(R, { revealed: false, typed: '' });
    toast('Grade undone');
  } catch (err) { toast(err.message, 'error'); }
  renderReview();
}

async function loadStats() {
  let st;
  try { st = await api('/review/stats'); } catch { return; }
  const max = Math.max(1, ...st.forecast.map(f => f.due));
  const d = st.deck;
  if (!d.total) { $('#rv-stats').innerHTML = ''; return; }
  $('#rv-stats').innerHTML = `<div class="panel rv-stats">
    <div class="rv-forecast"><h2>Coming up</h2><p class="muted small">Reviews due over the next two weeks</p>
      <div class="bars mini">${st.forecast.map((f, i) => {
        const day = new Date(f.date + 'T12:00');
        return `<div class="bar ${i === 0 ? 'today' : ''}" title="${f.due} due ${i === 0 ? 'today' : 'on ' + day.toLocaleDateString(undefined, { weekday: 'long', day: 'numeric', month: 'short' })}">
          <em>${f.due || ''}</em><div class="bar-track"><span style="height:${f.due ? Math.max(6, (100 * f.due) / max) : 0}%"></span></div><small>${i === 0 ? 'now' : day.toLocaleDateString(undefined, { weekday: 'narrow' })}</small></div>`;
      }).join('')}</div></div>
    <div class="rv-facts">
      <div><b>${st.retention == null ? '–' : st.retention + '%'}</b><span>remembered</span><small>${st.retention == null ? 'needs a few more reviews' : 'reviews in the last 30 days'}</small></div>
      <div><b>${d.total}</b><span>cards</span><small>${d.learning} learning · ${d.mature} well known · ${d.new} new</small></div>
      ${d.tricky ? `<button class="rv-tricky" id="rv-tricky"><b>${d.tricky}</b><span>tricky card${d.tricky === 1 ? '' : 's'}</span><small>missed ${st.tricky_lapses}+ times · take a look</small></button>` : ''}
    </div></div>`;
  $('#rv-tricky')?.addEventListener('click', () => { S.cardFilter = 'tricky'; S.cardScope = ''; cardTab('browse'); });
}

document.addEventListener('keydown', e => {
  if (S.view !== 'cards' || S.cardTab !== 'review') return;
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'z' && R.undo && !(e.target.closest('input, textarea') && e.target.value)) {
    e.preventDefault();
    return undoGrade();
  }
  if (e.altKey && e.code === 'KeyH' && !R.revealed) { e.preventDefault(); return toggleHint(); }
  if (e.target.closest('input, textarea, select')) return;
  if (e.key === ' ') {
    e.preventDefault(); // stop Space from also pressing a focused button
    if (!R.revealed && R.queue.length) reveal();
  } else if (R.revealed && R.ahead && ['1', '2'].includes(e.key)) grade(e.key === '1' ? 1 : 3);
  else if (R.revealed && !R.ahead && ['1', '2', '3', '4'].includes(e.key)) grade(+e.key);
});

// ---------- browse & create ----------
async function loadBrowse() {
  $('#cb-scope').innerHTML = chapterOptions(S.cardScope || '', { all: true });
  if (!$('#cb-new').childElementCount) {
    $('#cb-new').append(cardEditor({}, {
      context: () => scopeParams($('#cb-scope').value),
      onSaved: ed => { $$('input, textarea', ed).forEach(i => { i.value = ''; }); $('.ce-front', ed).focus(); loadCardList(); },
    }));
  }
  await loadCardList();
}

function cardStatus(c) {
  if (!c.due) return { cls: 'new', text: 'New' };
  if (new Date(c.due) <= Date.now()) return { cls: 'due', text: 'Due now' };
  return { cls: 'later', text: 'Back ' + whenText(c.due) };
}

async function loadCardList(justAdded = 0) {
  const scope = $('#cb-scope').value;
  const params = { ...scopeParams(scope), q: $('#cb-search').value.trim() };
  let cards = await api('/cards?' + queryString(params));
  const tricky = S.cardFilter === 'tricky';
  if (tricky) cards = cards.filter(c => c.lapses >= TRICKY);
  S.cardList = cards;
  const scopeName = $('#cb-scope').selectedOptions[0]?.textContent || 'All cards';
  const counts = { new: 0, due: 0, later: 0 };
  cards.forEach(c => counts[cardStatus(c).cls]++);
  const ready = counts.new + counts.due;
  const bar = `<div class="review-cta ${justAdded ? 'fresh' : ''}">
      <div class="grow">${justAdded ? `<b>${icon('check')}Added ${justAdded} cards.</b> ` : ''}
        <span>${cards.length} card${cards.length === 1 ? '' : 's'} in ${esc(scopeName)}:
        <span class="st new">${counts.new} new</span> <span class="st due">${counts.due} due now</span> <span class="st later">${counts.later} scheduled later</span></span></div>
      ${ready ? `<button data-review>${icon('play')}Review ${ready === 1 ? 'it' : 'these'} now</button>` : ''}
      <button class="ghost" data-practice>${icon('cards')}Practice all</button></div>`;
  const filterNote = tricky ? `<p class="pill-note filter-note">${icon('target')}Showing only tricky cards: ones you've missed ${TRICKY} or more times. Rewording them or adding a hint usually helps more than repeating them.<button class="link-btn" data-clear-filter>Show all cards</button></p>` : '';
  $('#cb-list').innerHTML = cards.length ? filterNote + bar + `<div class="card-list">${cards.map(cardRow).join('')}</div>`
    : tricky ? filterNote + emptyState('check', 'No tricky cards', '') : emptyState('cards', 'No cards here yet', 'Pick a chapter above and press <b>Generate cards</b>, or add one by hand.');
  $('[data-clear-filter]', $('#cb-list'))?.addEventListener('click', () => { S.cardFilter = null; loadCardList(); });
  $('[data-review]', $('#cb-list'))?.addEventListener('click', () => startReview(scope));
  $('[data-practice]', $('#cb-list'))?.addEventListener('click', () => startReview(scope, { ahead: true }));
}

function cardRow(c) {
  const st = cardStatus(c);
  return `<div class="card-row" data-id="${c.id}">
    <div class="cr-front">${esc(c.front)}</div><div class="cr-back">${esc(c.back)}${c.extra ? `<small>${esc(c.extra)}</small>` : ''}</div>
    <div class="cr-meta"><span class="chip">${esc(c.type)}</span><span class="st ${st.cls}">${st.text}</span>${c.lapses >= TRICKY ? `<span class="st due" title="Missed ${c.lapses} times">tricky</span>` : ''}</div>
    <div class="cr-acts"><button class="icon-btn" data-edit title="Edit">${icon('edit')}</button><button class="icon-btn danger-hover" data-del title="Delete">${icon('trash')}</button></div></div>`;
}

$('#cb-scope').addEventListener('change', e => { S.cardScope = e.target.value; loadCardList(); });
let searchTimer;
$('#cb-search').addEventListener('input', () => { clearTimeout(searchTimer); searchTimer = setTimeout(loadCardList, 300); });

$('#cb-list').addEventListener('click', async e => {
  const row = e.target.closest('.card-row');
  if (!row) return;
  const id = +row.dataset.id;
  const card = S.cardList.find(c => c.id === id);
  try {
    if (e.target.closest('[data-del]')) {
      if (!await confirmDialog('Delete this card?', card.front, { ok: 'Delete', danger: true })) return;
      await api(`/cards/${id}`, { method: 'DELETE' });
      row.remove();
    } else if (e.target.closest('[data-edit]')) {
      row.classList.add('editing');
      row.innerHTML = `<textarea rows="2" class="e-front">${esc(card.front)}</textarea><textarea rows="2" class="e-back">${esc(card.back)}</textarea>
        <textarea rows="2" class="e-extra" placeholder="Extra">${esc(card.extra)}</textarea>
        <div class="row"><select class="e-type"><option value="vocab">Vocab</option><option value="verb">Verb</option><option value="phrase">Phrase</option><option value="cloze">Cloze</option><option value="fix">Fix the mistake</option></select>
        <button class="small" data-save>${icon('check')}Save</button><button class="ghost small" data-cancel>Cancel</button></div>`;
      $('.e-type', row).value = card.type;
    } else if (e.target.closest('[data-save]')) {
      await api(`/cards/${id}`, { method: 'PUT', body: { front: $('.e-front', row).value, back: $('.e-back', row).value, extra: $('.e-extra', row).value, type: $('.e-type', row).value } });
      loadCardList();
    } else if (e.target.closest('[data-cancel]')) {
      loadCardList();
    }
  } catch (err) { toast(err.message, 'error'); }
});

$('#cb-generate').addEventListener('click', e => {
  const v = $('#cb-scope').value;
  if (!v || v.startsWith('b')) return toast('Pick a single chapter in the list first', 'error');
  busy(e.currentTarget, 'Making cards...', async () => {
    const r = await api(`/chapters/${v}/cards`, { method: 'POST', body: { count: +$('#cb-count').value, focus: $('#cb-focus').value } });
    await loadCardList(r.added);
    refreshNav();
  });
});

// ---------- words from a chapter (offline dictionary, no AI) ----------
$('#cb-words').addEventListener('click', e => {
  const v = $('#cb-scope').value;
  if (!v || v.startsWith('b')) return toast('Pick a single chapter in the list first', 'error');
  const box = $('#cb-words-box');
  if (!box.classList.contains('hidden') && box.dataset.chapter === v) { box.classList.add('hidden'); return; }
  busy(e.currentTarget, 'Reading the chapter...', async () => {
    const r = await api(`/chapters/${v}/words`);
    box.dataset.chapter = v;
    box.classList.remove('hidden');
    renderWords(r.words);
  });
});

function renderWords(words) {
  const box = $('#cb-words-box');
  if (!words.length) {
    box.innerHTML = '<p class="muted small">No German words found in this chapter (it may be mostly English explanations or pictures).</p>';
    return;
  }
  const fresh = words.filter(w => !w.have).length;
  box.innerHTML = `<div class="w-head"><b>${words.length} words in this chapter</b>
      <span class="muted small">${fresh} not in your cards yet · in the order they appear · very common words left out</span>
      <span class="grow"></span><button type="button" class="link-btn" data-wsel="all">Select all</button><button type="button" class="link-btn" data-wsel="none">None</button></div>
    <div class="w-list">${words.map((w, i) => `<label class="w-row ${w.have ? 'have' : ''}">
      <input type="checkbox" data-w="${i}" ${w.have ? 'disabled' : 'checked'}>
      <span class="w-word ${w.article ? 'g-' + w.article : ''}">${esc([w.article, w.word].filter(Boolean).join(' '))}</span>
      <span class="muted small">${esc(w.pos === 'noun' && w.plural ? 'die ' + w.plural : w.forms || w.pos_name)}</span>
      <span class="w-mean small">${esc(w.meaning)}</span>${w.have ? '<span class="chip">have it</span>' : ''}</label>`).join('')}</div>
    <div class="row"><button id="cb-words-add"><span>Add the selected as cards</span></button>
      <span class="muted small">Meanings come from Wiktionary, in English. Example sentences come from your book.</span></div>`;
  $('#cb-words-add').insertAdjacentHTML('afterbegin', icon('plus'));
  box.onclick = ev => {
    const s = ev.target.closest('[data-wsel]');
    if (s) $$('input[data-w]:not(:disabled)', box).forEach(c => { c.checked = s.dataset.wsel === 'all'; });
  };
  $('#cb-words-add').addEventListener('click', ev => {
    const picked = $$('input[data-w]:checked', box).map(c => words[+c.dataset.w]);
    if (!picked.length) return toast('Tick some words first', 'error');
    busy(ev.currentTarget, 'Adding...', async () => {
      const r = await api(`/chapters/${box.dataset.chapter}/words/cards`, { method: 'POST', body: { words: picked } });
      toast(`${r.added} card${r.added === 1 ? '' : 's'} added`);
      box.classList.add('hidden');
      await loadCardList(r.added);
      refreshNav();
    });
  });
}

// ---------- Anki ----------
$('#anki-download').addEventListener('click', () => {
  window.location.href = '/api/anki/export?' + queryString(scopeParams($('#anki-scope').value));
});
$('#anki-push').addEventListener('click', e => busy(e.currentTarget, 'Sending...', async () => {
  const r = await api('/anki/push', { method: 'POST', body: scopeParams($('#anki-scope').value) });
  toast(`Sent ${r.added} cards to Anki${r.skipped ? ` (${r.skipped} were already there)` : ''}`);
}));
