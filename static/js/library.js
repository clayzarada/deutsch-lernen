// Library page: importing PDFs, editing chapters, renaming and deleting books.
import { $, $$, S, api, esc, icon, toast, loadBooks, registerView, confirmDialog, promptDialog, emptyState } from './core.js';
import { openReader, forgetBook } from './reader.js';
import { openNotebookBridge } from './notebook.js';

registerView('library', loadLibrary);

async function loadLibrary() {
  await loadBooks();
  const list = $('#book-list');
  if (!S.books.length) {
    list.innerHTML = emptyState('library', 'No books yet', 'Press <b>Import PDF</b> or drag a PDF here to add your first textbook.');
    return;
  }
  list.innerHTML = S.books.map(b => {
    const pct = Math.round((100 * b.pages_read) / b.page_count);
    return `<article class="book" data-id="${b.id}">
      <button class="cover" data-act="open" title="Open in reader"><img src="/api/books/${b.id}/thumb" alt="" loading="lazy"></button>
      <div class="book-info">
        <h2>${esc(b.title)}</h2>
        <p class="muted small">${b.page_count} pages · ${b.chapters.length} chapter${b.chapters.length === 1 ? '' : 's'}</p>
        <div class="meter"><div class="meter-bar"><span style="width:${pct}%"></span></div><span>${pct}% read</span></div>
        <button data-act="open" class="small">${icon('reader')}${b.last_page > 1 ? `Continue at p. ${b.last_page}` : 'Start reading'}</button>
        <div class="book-actions">
          <button class="icon-btn" data-act="chapters" title="Edit chapters">${icon('list')}</button>
          <button class="icon-btn" data-act="notebook" title="Send to / import from Gemini Notebook">${icon('sparkles')}</button>
          <button class="icon-btn" data-act="rename" title="Rename">${icon('edit')}</button>
          <a class="icon-btn" href="/api/books/${b.id}/export" title="Download with your answers written in">${icon('download')}</a>
          <button class="icon-btn danger-hover" data-act="delete" title="Delete">${icon('trash')}</button>
        </div>
      </div></article>`;
  }).join('');
}

$('#book-list').addEventListener('click', async e => {
  const btn = e.target.closest('[data-act]');
  if (!btn) return;
  const id = +btn.closest('.book').dataset.id;
  const book = S.books.find(b => b.id === id);
  try {
    switch (btn.dataset.act) {
      case 'open': return openReader(id);
      case 'chapters': return openChapterDialog(book);
      case 'notebook': return openNotebookBridge(book.chapters[0]?.id);
      case 'rename': {
        const title = await promptDialog('Rename book', book.title);
        if (title) { await api(`/books/${id}`, { method: 'PUT', body: { title } }); loadLibrary(); }
        return;
      }
      case 'delete': {
        const ok = await confirmDialog(`Delete "${book.title}"?`, 'Your writing on it and its practice sets are deleted too. Flashcards are kept.', { ok: 'Delete', danger: true });
        if (!ok) return;
        await api(`/books/${id}`, { method: 'DELETE' });
        forgetBook(id);
        toast('Book deleted');
        return loadLibrary();
      }
    }
  } catch (err) { toast(err.message, 'error'); }
});

async function importPdf(file) {
  if (!file) return;
  if (!/\.(pdf|html?|md|txt)$/i.test(file.name)) return toast(`Can't import ${file.name}: use PDF, HTML, Markdown or text`, 'error');
  const fd = new FormData();
  fd.append('file', file);
  const list = $('#book-list');
  if (!S.books.length) list.innerHTML = '';
  list.insertAdjacentHTML('afterbegin', `<article class="book importing"><div class="cover"><span class="spin"></span></div><div class="book-info"><h2>${esc(file.name)}</h2><p class="muted small">Importing...</p></div></article>`);
  try {
    const book = await api('/books', { method: 'POST', body: fd });
    toast(`Imported "${book.title}" with ${book.chapters.length} chapter(s)`);
    await loadLibrary();
    if (/\.pdf$/i.test(file.name)) openChapterDialog(S.books.find(b => b.id === book.id));
  } catch (err) { toast(err.message, 'error'); loadLibrary(); }
}

$('#pdf-input').addEventListener('change', async e => {
  const files = [...e.target.files];
  e.target.value = '';
  for (const f of files) await importPdf(f);
});

const libView = $('#view-library');
libView.addEventListener('dragover', e => { e.preventDefault(); libView.classList.add('dragging'); });
libView.addEventListener('dragleave', e => { if (!libView.contains(e.relatedTarget)) libView.classList.remove('dragging'); });
libView.addEventListener('drop', async e => {
  e.preventDefault();
  libView.classList.remove('dragging');
  for (const f of [...e.dataTransfer.files]) await importPdf(f);
});

// ---------- chapter editor ----------
function chapterRow(c = {}) {
  return `<div class="ch-row" data-id="${c.id || ''}">
    <input class="ch-title" value="${esc(c.title || '')}" placeholder="Chapter title">
    <input class="ch-start" type="number" min="1" value="${c.start_page || ''}">
    <input class="ch-end" type="number" min="1" value="${c.end_page || ''}">
    <button class="icon-btn ch-del" title="Remove">${icon('x')}</button></div>`;
}

function openChapterDialog(book) {
  const dlg = $('#chapter-dialog');
  dlg.dataset.book = book.id;
  $('#ch-rows').innerHTML = book.chapters.map(chapterRow).join('');
  dlg.showModal();
}

$('#ch-rows').addEventListener('click', e => { if (e.target.closest('.ch-del')) e.target.closest('.ch-row').remove(); });
$('#ch-add').addEventListener('click', () => {
  const rows = $$('#ch-rows .ch-row');
  const lastEnd = rows.length ? +$('.ch-end', rows.at(-1)).value || 0 : 0;
  $('#ch-rows').insertAdjacentHTML('beforeend', chapterRow({ start_page: lastEnd + 1 }));
  $('#ch-rows .ch-row:last-child .ch-title').focus();
});
$('#ch-cancel').addEventListener('click', () => $('#chapter-dialog').close());
$('#ch-save').addEventListener('click', async () => {
  const dlg = $('#chapter-dialog');
  const chapters = $$('#ch-rows .ch-row').map(r => ({
    id: r.dataset.id ? +r.dataset.id : null, title: $('.ch-title', r).value.trim() || 'Untitled',
    start_page: +$('.ch-start', r).value, end_page: +$('.ch-end', r).value,
  }));
  try {
    await api(`/books/${dlg.dataset.book}/chapters`, { method: 'PUT', body: { chapters } });
    dlg.close();
    toast('Chapters saved');
    loadLibrary();
  } catch (err) { toast(err.message, 'error'); }
});
