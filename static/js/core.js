// Shared helpers, app state and navigation used by every page.

export const $ = (s, el = document) => el.querySelector(s);
export const $$ = (s, el = document) => [...el.querySelectorAll(s)];
export const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

export const S = { settings: null, books: [], view: null, lastActive: Date.now() };

// ---------- server calls ----------
export async function api(path, opts = {}) {
  const o = { ...opts, headers: { ...(opts.headers || {}) } };
  if (o.body && !(o.body instanceof FormData) && typeof o.body !== 'string') {
    o.body = JSON.stringify(o.body);
    o.headers['Content-Type'] = 'application/json';
  }
  const r = await fetch('/api' + path, o);
  if (!r.ok) {
    let msg = r.statusText;
    try { const j = await r.json(); msg = typeof j.detail === 'string' ? j.detail : JSON.stringify(j.detail); } catch { /* not json */ }
    throw new Error(msg);
  }
  return (r.headers.get('content-type') || '').includes('json') ? r.json() : r;
}

export async function loadBooks() { S.books = await api('/books'); return S.books; }

export const store = {
  get(k) { try { return localStorage.getItem(k); } catch { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch { /* storage unavailable */ } },
};

// ---------- icons (Lucide-style line icons) ----------
const ICONS = {
  today: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M6.3 17.7l-1.4 1.4M19.1 4.9l-1.4 1.4"/>',
  library: '<path d="M4 19.5V5a2 2 0 0 1 2-2h13v18H6.5A2.5 2.5 0 0 1 4 18.5zM4 18.5A2.5 2.5 0 0 1 6.5 16H19"/>',
  reader: '<path d="M2 4h6a4 4 0 0 1 4 4v13a3 3 0 0 0-3-3H2zM22 4h-6a4 4 0 0 0-4 4v13a3 3 0 0 1 3-3h7z"/>',
  practice: '<path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>',
  cards: '<path d="M12 2 2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>',
  coach: '<path d="M21 11.5a8.4 8.4 0 0 1-9 8.4 8.4 8.4 0 0 1-3.8-.9L3 21l1.9-5.7a8.4 8.4 0 0 1-.9-3.8 8.5 8.5 0 0 1 8.5-8.5 8.5 8.5 0 0 1 8.5 8.5z"/>',
  resources: '<path d="M10 13a5 5 0 0 0 7.5.5l3-3a5 5 0 0 0-7-7l-1.7 1.7M14 11a5 5 0 0 0-7.5-.5l-3 3a5 5 0 0 0 7 7l1.7-1.7"/>',
  settings: '<path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M1 14h6M9 8h6M17 16h6"/>',
  select: '<path d="M4 3l7 17 2.5-7.5L21 10z"/>',
  text: '<path d="M4 7V4h16v3M9 20h6M12 4v16"/>',
  pen: '<path d="M12 20h9M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/>',
  highlight: '<path d="M9 11l-6 6v3h9l3-3"/><path d="M22 12l-4.6 4.6a2 2 0 0 1-2.8 0l-5.2-5.2a2 2 0 0 1 0-2.8L14 4"/>',
  erase: '<path d="M20 20H8l-4.3-4.3a1 1 0 0 1 0-1.4l10-10a1 1 0 0 1 1.4 0l5.6 5.6a1 1 0 0 1 0 1.4L13 19.6M8.5 9.5l6 6"/>',
  left: '<path d="M15 18l-6-6 6-6"/>',
  right: '<path d="M9 18l6-6-6-6"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  minus: '<path d="M5 12h14"/>',
  fit: '<path d="M8 3H5a2 2 0 0 0-2 2v3M21 8V5a2 2 0 0 0-2-2h-3M3 16v3a2 2 0 0 0 2 2h3M16 21h3a2 2 0 0 0 2-2v-3"/>',
  download: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/>',
  upload: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/>',
  sparkles: '<path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9zM19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z"/>',
  check: '<path d="M20 6 9 17l-5-5"/>',
  x: '<path d="M18 6 6 18M6 6l12 12"/>',
  trash: '<path d="M3 6h18M8 6V4h8v2M19 6l-1 14H6L5 6"/>',
  edit: '<path d="M12 20h9M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/>',
  flame: '<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.4-.5-2-1-3-1.1-2.1-.2-4 2-6 .5 2.5 2 4.9 4 6.5s3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.2.4-2.3 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  panel: '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M15 3v18"/>',
  external: '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14 21 3"/>',
  play: '<path d="M6 4l14 8-14 8z"/>',
  page: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8zM14 2v6h6M8 13h8M8 17h5"/>',
  target: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
  list: '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
  undo: '<path d="M3 7v6h6"/><path d="M21 17a9 9 0 0 0-15-6.7L3 13"/>',
  send: '<path d="M22 2 11 13M22 2l-7 20-4-9-9-4z"/>',
  book: '<path d="M4 19.5V5a2 2 0 0 1 2-2h13v18H6.5A2.5 2.5 0 0 1 4 18.5z"/>',
  mic: '<rect x="9" y="2" width="6" height="12" rx="3"/><path d="M5 10a7 7 0 0 0 14 0M12 17v5"/>',
  headphones: '<path d="M3 18v-6a9 9 0 0 1 18 0v6"/><path d="M21 19a2 2 0 0 1-2 2h-1v-6h3zM3 19a2 2 0 0 0 2 2h1v-6H3z"/>',
  key: '<circle cx="7.5" cy="15.5" r="4.5"/><path d="m21 2-9.6 9.6M15.5 7.5l3 3L22 7l-3-3"/>',
  volume: '<path d="M11 5 6 9H2v6h4l5 4z"/><path d="M15.5 8.5a5 5 0 0 1 0 7M19 5a10 10 0 0 1 0 14"/>',
  pause: '<path d="M7 4h3v16H7zM14 4h3v16h-3z"/>',
  mistake: '<path d="M6 3h9l4 4v14H6z"/><path d="M15 3v4h4"/><path d="m10 11 4 4M14 11l-4 4"/>',
  grid: '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M3 15h18M9 3v18M15 3v18"/>',
  rocket: '<path d="M4.5 16.5c-1.5 1.3-2 5-2 5s3.7-.5 5-2c.7-.8.7-2.1-.1-2.9a2.2 2.2 0 0 0-2.9-.1zM12 15l-3-3a22 22 0 0 1 2-4A12.9 12.9 0 0 1 22 2c0 2.7-.8 7.5-6 11a22.4 22.4 0 0 1-4 2zM9 12H4s.6-3 2-4c1.6-1.1 5 0 5 0M12 15v5s3-.6 4-2c1.1-1.6 0-5 0-5"/>',
  star: '<path d="M12 2l3.1 6.3 6.9 1-5 4.9 1.2 6.8L12 17.8 5.8 21l1.2-6.8-5-4.9 6.9-1z"/>',
  moon: '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/>',
};

// ---------- pronunciation: Gemini reads a short German text aloud ----------
let clip;
export async function playClip(text, btn) {
  if (!S.settings?.has_gemini_key) return toast('Add a Google Gemini API key in Settings to hear pronunciation', 'error');
  clip?.pause();
  btn?.classList.add('playing');
  try {
    const r = await api('/speak', { method: 'POST', body: { text } });
    clip = new Audio(URL.createObjectURL(await r.blob()));
    clip.onended = () => btn?.classList.remove('playing');
    await clip.play();
  } catch (e) {
    btn?.classList.remove('playing');
    toast(e.message, 'error');
  }
}

export function hearButton(text, cls = '') {
  return `<button class="icon-btn hear ${cls}" data-hear="${esc(text)}" title="Hear it">${icon('volume')}</button>`;
}

document.addEventListener('click', e => {
  const b = e.target.closest('[data-hear]');
  if (b) { e.stopPropagation(); playClip(b.dataset.hear, b); }
});

export function icon(name, cls = '') {
  return `<svg class="icon ${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[name] || ''}</svg>`;
}

export function fillIcons(root = document) {
  $$('[data-icon]', root).forEach(el => el.insertAdjacentHTML('afterbegin', icon(el.dataset.icon)));
}

// ---------- feedback: toasts, busy buttons, loading ----------
export function toast(msg, kind = 'info') {
  const el = document.createElement('div');
  el.className = 'toast ' + kind;
  el.innerHTML = icon(kind === 'error' ? 'x' : 'check') + `<span>${esc(msg)}</span>`;
  $('#toast').append(el);
  setTimeout(() => el.classList.add('out'), kind === 'error' ? 7000 : 3500);
  setTimeout(() => el.remove(), kind === 'error' ? 7400 : 3900);
}

// Show a spinner on a button while an async action runs, and report errors as toasts.
export async function busy(btn, label, fn) {
  const old = btn?.innerHTML;
  if (btn) { btn.disabled = true; btn.innerHTML = `<span class="spin"></span>${esc(label)}`; }
  try { return await fn(); }
  catch (e) { toast(e.message, 'error'); }
  finally { if (btn && btn.isConnected) { btn.disabled = false; btn.innerHTML = old; } }
}

export function loading(text) {
  return `<div class="loading"><span class="spin"></span>${esc(text)}</div>`;
}

export function emptyState(iconName, title, text = '') {
  return `<div class="empty">${icon(iconName)}<b>${esc(title)}</b>${text ? `<p>${text}</p>` : ''}</div>`;
}

// ---------- modal dialogs (replace the browser's confirm/prompt) ----------
function openModal(html, onReady) {
  const dlg = $('#modal');
  dlg.innerHTML = html;
  dlg.returnValue = '';
  dlg.showModal();
  onReady?.(dlg);
  return new Promise(res => { dlg.onclose = () => res(dlg.returnValue); });
}

export async function confirmDialog(title, text = '', { ok = 'OK', danger = false } = {}) {
  const r = await openModal(`<form method="dialog"><h2>${esc(title)}</h2>${text ? `<p class="muted">${esc(text)}</p>` : ''}
    <div class="modal-actions"><button value="ok" class="${danger ? 'danger' : ''}">${esc(ok)}</button><button value="cancel" class="ghost">Cancel</button></div></form>`);
  return r === 'ok';
}

export async function promptDialog(title, value = '') {
  let input;
  const r = await openModal(`<form method="dialog"><h2>${esc(title)}</h2><input name="v" value="${esc(value)}">
    <div class="modal-actions"><button value="ok">Save</button><button value="cancel" class="ghost" formnovalidate>Cancel</button></div></form>`,
    d => { input = $('input', d); input.select(); });
  return r === 'ok' ? input.value.trim() : null;
}

// ---------- tiny Markdown renderer for AI text ----------
export function md(src) {
  const inline = s => esc(s)
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>')
    .replace(/(^|[^*])\*([^*\s][^*]*)\*/g, '$1<i>$2</i>')
    .replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
  let out = '', list = null;
  for (const line of String(src || '').split('\n')) {
    const m = line.match(/^\s*([-*•]|\d+\.)\s+(.*)/);
    if (m) {
      const t = /\d/.test(m[1]) ? 'ol' : 'ul';
      if (list !== t) { if (list) out += `</${list}>`; out += `<${t}>`; list = t; }
      out += `<li>${inline(m[2])}</li>`;
      continue;
    }
    if (list) { out += `</${list}>`; list = null; }
    const h = line.match(/^#{1,4}\s+(.*)/);
    if (h) out += `<h4>${inline(h[1])}</h4>`;
    else if (line.trim()) out += `<p>${inline(line)}</p>`;
  }
  if (list) out += `</${list}>`;
  return `<div class="md">${out}</div>`;
}

// ---------- navigation ----------
const views = {};
export function registerView(name, load) { views[name] = load; }

export function show(view, { load = true } = {}) {
  S.view = view;
  $$('.view').forEach(v => v.classList.toggle('hidden', v.id !== 'view-' + view));
  $$('#nav a[data-view]').forEach(a => a.classList.toggle('active', a.dataset.view === view));
  store.set('view', view);
  document.dispatchEvent(new CustomEvent('viewchange', { detail: view }));
  if (load) Promise.resolve(views[view]?.()).catch(e => toast(e.message, 'error'));
}

export function hasView(name) { return name in views; }

export function setBadge(view, n) {
  const b = $(`#nav a[data-view="${view}"] .badge`);
  if (b) { b.textContent = n > 99 ? '99+' : n; b.classList.toggle('hidden', !n); }
}

export function updateNavStatus(stats) {
  if (stats) {
    setBadge('cards', stats.cards.due + stats.cards.new_available);
    const st = stats.streak;
    $('#nav-streak').innerHTML = st.days ? `${icon('flame')}<span><b>${st.days}</b> day${st.days === 1 ? '' : 's'} streak</span>` : '';
    $('#nav-streak').classList.toggle('lit', st.today_done);
  }
  const ok = S.settings?.has_key;
  $('#nav-ai').innerHTML = `<i class="dot ${ok ? 'on' : ''}"></i><span>${ok ? 'AI ready' : 'Add API key'}</span>`;
  const v = S.settings?.version;
  $('#nav-version').textContent = v ? `v${v}${S.settings.build_name ? ' · ' + S.settings.build_name : ''}` : '';
  const c = S.settings?.credits;
  if (c) $('#nav-credit').textContent = `by ${c.author}`;
}

export async function refreshNav() {
  try { updateNavStatus(await api('/stats')); } catch { /* not critical */ }
}

// True when the user has touched the page recently and it's visible (used for time tracking).
// Three minutes of grace covers reading a long page or thinking over a task without touching anything.
export const IDLE_MS = 180000;
export function isActive() {
  return document.visibilityState === 'visible' && Date.now() - S.lastActive < IDLE_MS;
}

// ---------- books & chapters ----------
export function findChapter(id) {
  for (const b of S.books) for (const c of b.chapters) if (c.id === id) return { book: b, chapter: c };
  return null;
}

export function chapterOptions(selected, { all = false } = {}) {
  let h = all ? '<option value="">All cards</option>' : '';
  for (const b of S.books) {
    h += `<optgroup label="${esc(b.title)}">`;
    if (all) h += `<option value="b${b.id}" ${selected === 'b' + b.id ? 'selected' : ''}>${esc(b.title)} (whole book)</option>`;
    for (const c of b.chapters) {
      h += `<option value="${c.id}" ${String(c.id) === String(selected) ? 'selected' : ''}>${esc(c.title)} (p. ${c.start_page}–${c.end_page})</option>`;
    }
    h += '</optgroup>';
  }
  return h;
}

// Turns a chapterOptions value ('' / 'b3' / '12') into {book_id, chapter_id} filters.
export function scopeParams(v) {
  if (!v) return {};
  return v.startsWith('b') ? { book_id: +v.slice(1) } : { chapter_id: +v, book_id: findChapter(+v)?.book.id };
}

export function queryString(params) {
  return new URLSearchParams(Object.entries(params).filter(([, v]) => v != null && v !== '')).toString();
}

// ---------- shared flashcard form ----------
// context() returns {book_id, chapter_id} at save time; onSaved runs after a successful save.
export function cardEditor(pre = {}, { collapsed = false, context = () => ({}), onSaved } = {}) {
  const wrap = document.createElement(collapsed ? 'details' : 'div');
  wrap.className = 'card-editor';
  wrap.innerHTML = `${collapsed ? '<summary>Make a flashcard</summary>' : ''}
    <input class="ce-front" placeholder="Front, e.g. der Tisch, -e" value="${esc(pre.front || '')}">
    <textarea class="ce-back" rows="2" placeholder="Back, e.g. table">${esc(pre.back || '')}</textarea>
    <textarea class="ce-extra" rows="2" placeholder="Extra: example sentence, notes (optional)">${esc(pre.extra || '')}</textarea>
    <div class="row"><select class="ce-type"><option value="vocab">Vocab</option><option value="verb">Verb</option><option value="phrase">Phrase</option><option value="cloze">Cloze</option><option value="fix">Fix the mistake</option></select>
    <button class="ce-save" type="button">${icon('plus')}Add card</button></div>`;
  $('.ce-type', wrap).value = pre.type || 'vocab';
  $('.ce-save', wrap).addEventListener('click', async () => {
    const front = $('.ce-front', wrap).value.trim(), back = $('.ce-back', wrap).value.trim();
    if (!front || !back) return toast('Fill in the front and back first', 'error');
    try {
      await api('/cards', { method: 'POST', body: { front, back, extra: $('.ce-extra', wrap).value.trim(), type: $('.ce-type', wrap).value, ...context() } });
      toast('Card added');
      if (onSaved) onSaved(wrap); else wrap.remove();
      refreshNav();
    } catch (err) { toast(err.message, 'error'); }
  });
  return wrap;
}
