// Reader page: PDF rendering, writing on pages (type / pen / highlight / erase),
// word lookups, AI marking of a page, and reading-time tracking.
import {
  $, $$, S, api, esc, icon, md, toast, busy, loading, emptyState, store,
  loadBooks, registerView, show, isActive, cardEditor, playClip, hearButton,
} from './core.js';
import { openNotebookBridge } from './notebook.js';

pdfjsLib.GlobalWorkerOptions.workerSrc = '/static/vendor/pdf.worker.min.js';

const COLORS = ['#1d4ed8', '#dc2626', '#15803d', '#111827'];
const TEXT_SIZE = 10; // PDF points; about the size of typical textbook body text
const R = { book: null, doc: null, page: 1, zoom: 1, tool: 'select', color: COLORS[0], annots: [], history: [], renderToken: 0, pending: 0 };

registerView('reader', () => openReader());

export function forgetBook(id) {
  if (R.book?.id === id) { R.book = null; R.doc = null; }
}

export async function openReader(bookId, page) {
  await loadBooks();
  show('reader', { load: false });
  const book = S.books.find(b => b.id === bookId) || S.books.find(b => b.id === R.book?.id) || S.books[0];
  $('#r-empty').classList.toggle('hidden', !!book);
  $('#r-pagewrap').classList.toggle('hidden', !book);
  if (!book) {
    R.book = null;
    $('#r-empty').innerHTML = emptyState('reader', 'Nothing to read yet', '<a href="#" data-go="library">Import a PDF</a> to get started.');
    return;
  }
  if (R.book?.id !== book.id || !R.doc) {
    $('#r-pagewrap').classList.add('loading-page');
    R.doc = await pdfjsLib.getDocument(`/api/books/${book.id}/file`).promise;
    R.page = book.last_page || 1;
    R.history = [];
    $('#r-assist').innerHTML = '<p class="muted small">In <b>Read</b> mode, double-click a word or select a sentence to look it up, get it explained, or turn it into a flashcard.</p>';
    $('#r-check-out').innerHTML = '';
  }
  R.book = book;
  if (page) R.page = page;
  $('#r-book').innerHTML = S.books.map(b => `<option value="${b.id}" ${b.id === book.id ? 'selected' : ''}>${esc(b.title)}</option>`).join('');
  $('#r-chapter').innerHTML = book.chapters.map(c => `<option value="${c.id}">${esc(c.title)}</option>`).join('');
  setTool(R.tool);
  await renderPage();
}

function currentChapter() {
  return R.book?.chapters.find(c => R.page >= c.start_page && R.page <= c.end_page) || null;
}

let lastPageSave;
async function goPage(n) {
  if (!R.doc) return;
  n = Math.max(1, Math.min(n, R.doc.numPages));
  if (n === R.page) return;
  await flushSaves();
  R.page = n;
  $('#r-check-out').innerHTML = '';
  $('#r-scroll').scrollTop = 0;
  renderPage();
  clearTimeout(lastPageSave);
  lastPageSave = setTimeout(() => api(`/books/${R.book.id}`, { method: 'PUT', body: { last_page: R.page } }).catch(() => {}), 800);
}

async function renderPage() {
  if (!R.doc) return;
  const token = ++R.renderToken;
  R.page = Math.max(1, Math.min(R.page, R.doc.numPages));
  $('#r-page').value = R.page;
  $('#r-count').textContent = R.doc.numPages;
  $('#r-prev').disabled = R.page <= 1;
  $('#r-next').disabled = R.page >= R.doc.numPages;
  $('#r-zoom').textContent = Math.round(R.zoom * 100) + '%';
  const ch = currentChapter();
  if (ch) $('#r-chapter').value = ch.id;
  $('#r-chap-info').innerHTML = ch
    ? `<b>${esc(ch.title)}</b><p class="muted small">Pages ${ch.start_page}–${ch.end_page} · you're on ${R.page - ch.start_page + 1} of ${ch.end_page - ch.start_page + 1}</p>`
    : '<p class="muted small">No chapter covers this page. Edit chapters in the Library.</p>';
  $('#r-gen-ex').disabled = $('#r-gen-cards').disabled = $('#r-gen-audio').disabled = !ch;

  const page = await R.doc.getPage(R.page);
  if (token !== R.renderToken) return;
  const base = page.getViewport({ scale: 1 });
  const avail = Math.max(300, $('#r-scroll').clientWidth - 64); // padding + room for a scrollbar
  const scale = Math.max(0.3, (avail / base.width) * R.zoom);
  const vp = page.getViewport({ scale });
  const dpr = window.devicePixelRatio || 1;

  // Render off-screen first so turning pages doesn't flash white.
  const off = document.createElement('canvas');
  off.width = Math.floor(vp.width * dpr);
  off.height = Math.floor(vp.height * dpr);
  const task = page.render({ canvasContext: off.getContext('2d'), viewport: vp, transform: dpr !== 1 ? [dpr, 0, 0, dpr, 0, 0] : null });
  try { await task.promise; } catch (e) { if (e?.name === 'RenderingCancelledException') return; throw e; }
  if (token !== R.renderToken) return;

  R.scale = scale;
  R.vp = vp;
  const canvas = $('#r-canvas');
  canvas.width = off.width;
  canvas.height = off.height;
  canvas.style.width = vp.width + 'px';
  canvas.style.height = vp.height + 'px';
  canvas.getContext('2d').drawImage(off, 0, 0);
  const wrap = $('#r-pagewrap');
  wrap.style.width = vp.width + 'px';
  wrap.style.height = vp.height + 'px';
  wrap.classList.remove('loading-page');

  const tl = $('#r-text');
  tl.innerHTML = '';
  tl.style.setProperty('--scale-factor', scale);
  const tc = await page.getTextContent();
  if (token !== R.renderToken) return;
  R.pageText = tc.items.map(i => i.str + (i.hasEOL ? '\n' : '')).join(' ').replace(/ +/g, ' ');
  pdfjsLib.renderTextLayer({ textContentSource: tc, container: tl, viewport: vp, textDivs: [] });

  const annots = await api(`/books/${R.book.id}/annotations?page=${R.page}`);
  if (token !== R.renderToken) return;
  R.annots = annots;
  drawAnnots();
  updateStatus();
}

// ---------- writing on the page ----------
const NS = 'http://www.w3.org/2000/svg';

function updateStatus() {
  const el = $('#r-status');
  if (R.pending > 0) { el.innerHTML = '<span class="spin small"></span>Saving'; el.className = 'save-status'; }
  else if (R.annots.length) { el.innerHTML = icon('check') + 'Saved'; el.className = 'save-status ok'; }
  else el.innerHTML = '';
}

function drawAnnots() {
  const layer = $('#r-annot'), svg = $('#r-ink');
  $$('.tbox', layer).forEach(n => n.remove());
  svg.innerHTML = '';
  svg.setAttribute('viewBox', `0 0 ${R.vp.width} ${R.vp.height}`);
  for (const a of R.annots) a.kind === 'ink' ? drawInk(a) : drawTextBox(a);
}

function inkPoints(pts) {
  return pts.map(([x, y]) => `${(x * R.vp.width).toFixed(1)},${(y * R.vp.height).toFixed(1)}`).join(' ');
}

function drawInk(a) {
  const g = document.createElementNS(NS, 'g');
  g.dataset.id = a.id;
  const pts = inkPoints(a.data.points);
  const line = document.createElementNS(NS, 'polyline');
  line.setAttribute('class', 'ink' + ((a.data.opacity ?? 1) < 1 ? ' hl' : ''));
  line.setAttribute('points', pts);
  line.setAttribute('stroke', a.data.color);
  line.setAttribute('stroke-width', a.data.width * R.scale);
  line.setAttribute('stroke-opacity', a.data.opacity ?? 1);
  const hit = document.createElementNS(NS, 'polyline');
  hit.setAttribute('class', 'ink-hit');
  hit.setAttribute('points', pts);
  hit.setAttribute('stroke-width', Math.max(14, a.data.width * R.scale + 8));
  g.append(line, hit);
  $('#r-ink').append(g);
  return g;
}

function drawTextBox(a) {
  const el = document.createElement('div');
  el.className = 'tbox';
  el.style.left = a.x * 100 + '%';
  el.style.top = a.y * 100 + '%';
  el.style.fontSize = a.data.size * R.scale + 'px';
  el.style.color = a.data.color;
  el.innerHTML = '<span class="grip" title="Drag to move">⠿</span><div class="tbox-text" contenteditable="true" spellcheck="false"></div>';
  const txt = $('.tbox-text', el);
  txt.textContent = a.data.text;
  $('#r-annot').append(el);
  txt.addEventListener('input', () => { a.data.text = txt.innerText.replace(/\n$/, ''); saveAnnotSoon(a); });
  txt.addEventListener('blur', () => {
    if (!R.annots.includes(a)) return;
    if (!a.data.text.trim()) removeAnnot(a); else saveAnnot(a);
  });
  txt.addEventListener('keydown', e => { e.stopPropagation(); if (e.key === 'Escape') txt.blur(); });
  txt.addEventListener('pointerdown', e => { if (R.tool === 'erase') { e.preventDefault(); removeAnnot(a); } });
  $('.grip', el).addEventListener('pointerdown', e => startDrag(e, a, el));
  return txt;
}

// Saves one annotation (creating it the first time). Errors are shown, never thrown.
async function saveAnnot(a) {
  clearTimeout(a._t);
  a._t = null;
  R.pending++;
  updateStatus();
  try {
    if (a._creating) await a._creating;
    if (a.kind === 'text' && !a.data.text.trim()) {
      if (a.id !== 'new') await api(`/annotations/${a.id}`, { method: 'DELETE' });
      return;
    }
    const body = { book_id: a.book_id, page: a.page, kind: a.kind, x: a.x, y: a.y, data: a.data };
    if (a.id === 'new') {
      a._creating = api('/annotations', { method: 'POST', body }).then(r => { a.id = r.id; });
      try { await a._creating; } finally { a._creating = null; }
    } else {
      await api(`/annotations/${a.id}`, { method: 'PUT', body });
    }
  } catch (err) {
    toast('Couldn\'t save your writing: ' + err.message, 'error');
  } finally {
    R.pending--;
    updateStatus();
  }
}

function saveAnnotSoon(a) {
  clearTimeout(a._t);
  a._t = setTimeout(() => saveAnnot(a), 600);
  $('#r-status').innerHTML = '<span class="spin small"></span>Saving';
}

async function flushSaves() {
  await Promise.all(R.annots.filter(a => a._t || a._creating).map(saveAnnot));
}

async function removeAnnot(a) {
  if (!a) return;
  R.annots = R.annots.filter(x => x !== a);
  R.history = R.history.filter(x => x !== a);
  clearTimeout(a._t);
  drawAnnots();
  try {
    if (a._creating) await a._creating;
    if (a.id !== 'new') await api(`/annotations/${a.id}`, { method: 'DELETE' });
  } catch (err) { toast(err.message, 'error'); }
  updateStatus();
}

function layerPoint(e) {
  const r = $('#r-annot').getBoundingClientRect();
  return [+((e.clientX - r.left) / r.width).toFixed(4), +((e.clientY - r.top) / r.height).toFixed(4)];
}

function createTextAt(e) {
  const [x, y] = layerPoint(e);
  const size = TEXT_SIZE;
  const a = { id: 'new', book_id: R.book.id, page: R.page, kind: 'text', x, y: Math.max(0, y - (size * 0.6) / R.vp.height), data: { text: '', size, color: R.color } };
  R.annots.push(a);
  R.history.push(a);
  const txt = drawTextBox(a);
  setTimeout(() => txt.focus(), 0);
}

function startDrag(e, a, el) {
  e.preventDefault();
  e.stopPropagation();
  const r = $('#r-annot').getBoundingClientRect();
  const ox = e.clientX - a.x * r.width, oy = e.clientY - a.y * r.height;
  const move = ev => {
    a.x = Math.min(0.98, Math.max(0, (ev.clientX - ox) / r.width));
    a.y = Math.min(0.98, Math.max(0, (ev.clientY - oy) / r.height));
    el.style.left = a.x * 100 + '%';
    el.style.top = a.y * 100 + '%';
  };
  const up = () => {
    window.removeEventListener('pointermove', move);
    window.removeEventListener('pointerup', up);
    saveAnnot(a);
  };
  window.addEventListener('pointermove', move);
  window.addEventListener('pointerup', up);
}

function startStroke(e) {
  e.preventDefault();
  const layer = $('#r-annot');
  const hl = R.tool === 'highlight';
  const a = {
    id: 'new', book_id: R.book.id, page: R.page, kind: 'ink', x: 0, y: 0,
    data: { points: [layerPoint(e)], color: hl ? '#facc15' : R.color, width: hl ? 11 : 1.6, opacity: hl ? 0.4 : 1 },
  };
  const g = drawInk(a);
  layer.setPointerCapture(e.pointerId);
  const move = ev => {
    for (const c of (ev.getCoalescedEvents?.() || [ev])) {
      const p = layerPoint(c), last = a.data.points.at(-1);
      if (Math.abs(p[0] - last[0]) + Math.abs(p[1] - last[1]) > 0.0012) a.data.points.push(p);
    }
    const pts = inkPoints(a.data.points);
    g.querySelectorAll('polyline').forEach(pl => pl.setAttribute('points', pts));
  };
  const up = () => {
    layer.removeEventListener('pointermove', move);
    layer.removeEventListener('pointerup', up);
    layer.removeEventListener('pointercancel', up);
    if (a.data.points.length < 2) a.data.points.push([a.data.points[0][0] + 0.001, a.data.points[0][1]]);
    R.annots.push(a);
    R.history.push(a);
    saveAnnot(a).then(() => { g.dataset.id = a.id; });
  };
  layer.addEventListener('pointermove', move);
  layer.addEventListener('pointerup', up);
  layer.addEventListener('pointercancel', up);
}

$('#r-annot').addEventListener('pointerdown', e => {
  if (!R.book) return;
  if (R.tool === 'text') {
    if (e.target.closest('.tbox')) return;
    e.preventDefault();
    createTextAt(e);
  } else if (R.tool === 'pen' || R.tool === 'highlight') {
    startStroke(e);
  } else if (R.tool === 'erase') {
    const g = e.target.closest('g[data-id]');
    if (g) removeAnnot(R.annots.find(a => String(a.id) === g.dataset.id));
  }
});

function setTool(t) {
  R.tool = t;
  $('#r-pagewrap').classList.remove('tool-select', 'tool-text', 'tool-pen', 'tool-highlight', 'tool-erase');
  $('#r-pagewrap').classList.add('tool-' + t);
  $$('[data-tool]').forEach(b => b.classList.toggle('active', b.dataset.tool === t));
  if (t !== 'select') window.getSelection()?.removeAllRanges();
  hideSelPop();
}
$$('[data-tool]').forEach(b => b.addEventListener('click', () => setTool(b.dataset.tool)));

$('#r-swatches').innerHTML = COLORS.map(c => `<button class="swatch ${c === R.color ? 'active' : ''}" data-color="${c}" style="--c:${c}" title="Ink color"></button>`).join('');
$('#r-swatches').addEventListener('click', e => {
  const b = e.target.closest('[data-color]');
  if (!b) return;
  R.color = b.dataset.color;
  $$('.swatch').forEach(s => s.classList.toggle('active', s === b));
  if (R.tool === 'select' || R.tool === 'erase') setTool('pen');
});

// ---------- toolbar ----------
$('#r-book').addEventListener('change', e => openReader(+e.target.value));
$('#r-prev').addEventListener('click', () => goPage(R.page - 1));
$('#r-next').addEventListener('click', () => goPage(R.page + 1));
$('#r-page').addEventListener('change', e => goPage(+e.target.value));
$('#r-chapter').addEventListener('change', e => {
  const c = R.book.chapters.find(c => c.id === +e.target.value);
  if (c) goPage(c.start_page);
});
$('#r-zoom-in').addEventListener('click', () => { R.zoom = Math.min(3, R.zoom * 1.15); renderPage(); });
$('#r-zoom-out').addEventListener('click', () => { R.zoom = Math.max(0.4, R.zoom / 1.15); renderPage(); });
$('#r-fit').addEventListener('click', () => { R.zoom = 1; renderPage(); });
$('#r-export').addEventListener('click', async () => {
  if (!R.book) return;
  await flushSaves();
  window.location.href = `/api/books/${R.book.id}/export`;
});
$('#r-side-toggle').addEventListener('click', () => {
  const hidden = $('#r-body').classList.toggle('side-hidden');
  store.set('readerSide', hidden ? 'hidden' : '');
  renderPage();
});
if (store.get('readerSide') === 'hidden') $('#r-body').classList.add('side-hidden');

$('#r-gen-ex').addEventListener('click', () => { const c = currentChapter(); if (c) { S.practiceChapter = c.id; show('practice'); } });
$('#r-gen-cards').addEventListener('click', () => {
  const c = currentChapter();
  if (c) { S.cardTab = 'browse'; S.cardScope = String(c.id); show('cards'); }
});
$('#r-gen-audio').addEventListener('click', () => { const c = currentChapter(); if (c) { S.listenChapter = c.id; show('listening'); } });
$('#r-notebook').addEventListener('click', () => openNotebookBridge(currentChapter()?.id));

let resizeTimer;
window.addEventListener('resize', () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => { if (S.view === 'reader') renderPage(); }, 200);
});

document.addEventListener('keydown', e => {
  if (S.view !== 'reader' || e.target.closest('input, textarea, select, [contenteditable]')) return;
  if (e.key === 'ArrowRight' || e.key === 'PageDown') { e.preventDefault(); goPage(R.page + 1); }
  else if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); goPage(R.page - 1); }
  else if ((e.ctrlKey || e.metaKey) && e.key === 'z') { e.preventDefault(); removeAnnot(R.history.at(-1)); }
  else if (!e.ctrlKey && !e.metaKey && !e.altKey) {
    const tool = { r: 'select', t: 'text', p: 'pen', h: 'highlight', e: 'erase' }[e.key.toLowerCase()];
    if (tool) setTool(tool);
  }
});

// Reading time: every 15 s while the reader is open and you're active.
setInterval(() => {
  if (S.view === 'reader' && R.book && isActive()) {
    api('/reading', { method: 'POST', body: { book_id: R.book.id, page: R.page, seconds: 15 } }).catch(() => {});
  }
}, 15000);

// ---------- selection popup: look up / explain / make card ----------
function hideSelPop() { $('#sel-pop').classList.add('hidden'); }
document.addEventListener('viewchange', hideSelPop);

function sentenceAround(text) {
  const t = R.pageText || '';
  const i = t.indexOf(text);
  if (i < 0) return '';
  const start = Math.max(t.lastIndexOf('.', i), t.lastIndexOf('!', i), t.lastIndexOf('?', i), t.lastIndexOf('\n', i)) + 1;
  const rest = t.slice(i + text.length).search(/[.!?\n]/);
  const end = rest < 0 ? t.length : i + text.length + rest + 1;
  return t.slice(start, end).trim().slice(0, 400);
}

$('#r-text').addEventListener('mouseup', () => setTimeout(() => {
  const sel = window.getSelection();
  const text = sel.toString().replace(/\s+/g, ' ').trim();
  if (!text || R.tool !== 'select' || !sel.rangeCount) return hideSelPop();
  const rect = sel.getRangeAt(0).getBoundingClientRect();
  const pop = $('#sel-pop');
  pop.style.left = rect.left + rect.width / 2 + 'px';
  pop.style.top = Math.max(60, rect.top - 8) + 'px';
  pop.classList.remove('hidden');
  R.selection = { text, sentence: sentenceAround(text) };
}, 10));
document.addEventListener('pointerdown', e => { if (!e.target.closest('#sel-pop')) hideSelPop(); });

$('#sel-pop').addEventListener('click', e => {
  const act = e.target.closest('button')?.dataset.act;
  if (!act || !R.selection) return;
  hideSelPop();
  const { text, sentence } = R.selection;
  if (act === 'hear') return playClip(text);
  showSide();
  if (act === 'lookup' && text.split(' ').length <= 5) doLookup(text, sentence);
  else if (act === 'card') {
    const out = $('#r-assist');
    out.innerHTML = '';
    out.append(cardEditor({ front: text }, { context: cardContext }));
    $('.ce-back', out)?.focus();
  } else doExplain(text);
});

function showSide() {
  if ($('#r-body').classList.contains('side-hidden')) $('#r-side-toggle').click();
}

function cardContext() {
  return { book_id: R.book?.id, chapter_id: currentChapter()?.id };
}

async function doLookup(text, sentence) {
  const out = $('#r-assist');
  out.innerHTML = loading(`Looking up “${text}”...`);
  try {
    const r = await api('/lookup', { method: 'POST', body: { word: text, sentence } });
    const head = [r.article, r.lemma].filter(Boolean).join(' ') + (r.plural ? `, ${r.plural}` : '');
    out.innerHTML = `<div class="lookup">
      <div class="lk-head"><span class="lk-word ${r.article ? 'g-' + r.article : ''}">${esc(head)}</span>${hearButton([r.article, r.lemma].filter(Boolean).join(' '), 'tiny')}<span class="chip">${esc(r.part_of_speech)}</span></div>
      <p class="lk-meaning">${esc(r.meaning)}</p>
      ${r.meaning_in_context ? `<p class="small"><b>Here:</b> ${esc(r.meaning_in_context)}</p>` : ''}
      ${r.forms ? `<p class="small"><b>Forms:</b> ${esc(r.forms)}</p>` : ''}
      ${r.example ? `<blockquote>${hearButton(r.example, 'tiny float')}${esc(r.example)}<span>${esc(r.example_translation)}</span></blockquote>` : ''}
      ${r.note ? `<p class="small tip">${icon('sparkles')}${esc(r.note)}</p>` : ''}</div>`;
    out.append(cardEditor({
      front: head, back: r.meaning + (r.forms ? `\n${r.forms}` : ''),
      extra: r.example ? `${r.example}\n${r.example_translation}` : '',
      type: /verb/i.test(r.part_of_speech) ? 'verb' : 'vocab',
    }, { collapsed: true, context: cardContext }));
  } catch (err) { out.innerHTML = `<p class="error">${esc(err.message)}</p>`; }
}

async function doExplain(text) {
  const out = $('#r-assist');
  out.innerHTML = loading('Explaining...');
  try {
    const r = await api('/explain', { method: 'POST', body: { text, book_id: R.book.id, page: R.page } });
    out.innerHTML = `<blockquote>${esc(text.slice(0, 300))}</blockquote>${md(r.text)}`;
    out.append(cardEditor({ front: text.slice(0, 200) }, { collapsed: true, context: cardContext }));
  } catch (err) { out.innerHTML = `<p class="error">${esc(err.message)}</p>`; }
}

// ---------- AI marking of answers written on the page ----------
// Draws the page plus your writing into one image for Claude to read.
function composePage() {
  const src = $('#r-canvas');
  const k = Math.min(1, 1600 / src.width);
  const c = document.createElement('canvas');
  c.width = Math.round(src.width * k);
  c.height = Math.round(src.height * k);
  const ctx = c.getContext('2d');
  ctx.fillStyle = '#fff';
  ctx.fillRect(0, 0, c.width, c.height);
  ctx.drawImage(src, 0, 0, c.width, c.height);
  const W = c.width, H = c.height, px = W / R.vp.width;
  for (const a of R.annots) {
    ctx.save();
    if (a.kind === 'ink') {
      ctx.globalAlpha = a.data.opacity ?? 1;
      ctx.strokeStyle = a.data.color;
      ctx.lineWidth = a.data.width * R.scale * px;
      ctx.lineCap = ctx.lineJoin = 'round';
      ctx.beginPath();
      a.data.points.forEach(([x, y], i) => (i ? ctx.lineTo(x * W, y * H) : ctx.moveTo(x * W, y * H)));
      ctx.stroke();
    } else if (a.data.text?.trim()) {
      const fs = a.data.size * R.scale * px;
      ctx.fillStyle = a.data.color;
      ctx.font = `${fs}px Arial, sans-serif`;
      ctx.textBaseline = 'top';
      a.data.text.split('\n').forEach((line, i) => ctx.fillText(line, a.x * W, a.y * H + i * fs * 1.2));
    }
    ctx.restore();
  }
  return c.toDataURL('image/jpeg', 0.85);
}

const VERDICT_ICON = { correct: 'check', incorrect: 'x', partly: 'minus', unclear: 'minus' };

$('#r-check').addEventListener('click', e => {
  if (!R.book) return;
  if (!R.annots.length) return toast('Write some answers on this page first (Type or Pen)', 'error');
  const out = $('#r-check-out');
  out.innerHTML = loading('Marking your answers...');
  busy(e.currentTarget, 'Checking...', async () => {
    await flushSaves();
    try {
      const r = await api(`/books/${R.book.id}/check_page`, { method: 'POST', body: { page: R.page, image: composePage() } });
      const right = r.items.filter(i => i.verdict === 'correct').length;
      if (r.new_mistakes) toast(`${r.new_mistakes} mistake${r.new_mistakes === 1 ? '' : 's'} saved to your Mistake Book`);
      out.innerHTML = (r.items.length ? `<div class="score">${right}/${r.items.length} correct</div>` : '') + md(r.summary)
        + (r.reused ? `<p class="muted small">${r.reused === 1 ? '1 answer hadn’t changed since your last check and kept its mark.' : `${r.reused} answers hadn’t changed since your last check and kept their marks.`}</p>` : '')
        + (r.items.length ? r.items.map(i => `
          <div class="check-item ${i.verdict}">
            <div class="ci-head">${icon(VERDICT_ICON[i.verdict])}<b>${esc(i.exercise)}</b><span class="verdict">${esc(i.verdict)}</span></div>
            <div class="small">You wrote: <i>${esc(i.student_answer)}</i></div>
            ${i.verdict !== 'correct' ? `<div class="small">Correct: <b>${esc(i.correction)}</b></div>` : ''}
            <div class="muted small">${esc(i.explanation)}</div></div>`).join('') : '<p class="muted small">No answers found on this page.</p>');
    } catch (err) { out.innerHTML = ''; throw err; }
  });
});
