// Listening page: AI-made audio episodes per chapter (and imported audio), with a synced transcript.
import {
  $, $$, S, api, esc, icon, busy, loading, emptyState, toast, loadBooks, chapterOptions, registerView,
  confirmDialog, promptDialog, hearButton,
} from './core.js';
import { openNotebookBridge } from './notebook.js';

const STYLE_LABEL = { dialogue: 'Dialogue', podcast: 'Podcast', story: 'Story', imported: 'Imported' };
const L = { media: null, played: 0, lastTime: 0 };

registerView('listening', loadListening);

async function loadListening() {
  await loadBooks();
  $('#l-chapter').innerHTML = chapterOptions(S.listenChapter) || '<option value="">Import a book first</option>';
  $('#l-generate').disabled = !S.books.length;
  const list = await loadList();
  const want = S.listenMedia || L.media?.id;
  S.listenMedia = null;
  S.listenChapter = null;
  if (want && list.some(m => m.id === want)) openMedia(want);
  else if (!L.media) {
    $('#l-player').innerHTML = emptyState('headphones', 'Make your first episode',
      'Pick a chapter and a style. You get a German dialogue, podcast or story at your level, voiced by two natural speakers, with a transcript, translation and vocabulary list.');
  }
}

function fmt(sec) {
  if (!sec) return '';
  const m = Math.floor(sec / 60), s = Math.round(sec % 60);
  return `${m}:${String(s).padStart(2, '0')}`;
}

async function loadList() {
  const list = await api('/media');
  $('#l-list').innerHTML = list.length ? list.map(m => `
    <div class="set-item ${L.media?.id === m.id ? 'active' : ''}" data-id="${m.id}">
      <span class="res-icon small">${icon(m.source === 'imported' ? 'upload' : 'headphones')}</span>
      <div class="grow"><div class="set-title">${esc(m.title)}</div>
        <div class="muted small">${STYLE_LABEL[m.source] || ''}${m.seconds ? ' · ' + fmt(m.seconds) : ''}${m.chapter ? ' · ' + esc(m.chapter) : ''}${m.listens ? ` · ${icon('check')}${m.listens}×` : ''}</div></div>
    </div>`).join('') : '<p class="muted small">No audio yet.</p>';
  return list;
}

$('#l-list').addEventListener('click', e => {
  const item = e.target.closest('.set-item');
  if (item) openMedia(+item.dataset.id);
});

$('#l-generate').addEventListener('click', e => {
  const id = +$('#l-chapter').value;
  if (!id) return toast('Pick a chapter first', 'error');
  if (!S.settings.has_gemini_key) return toast('Add a Google Gemini API key in Settings first (it voices the episode)', 'error');
  const before = $('#l-player').innerHTML;
  const minutes = +$('#l-minutes').value;
  $('#l-player').innerHTML = loading(`Writing the script and recording it. A ${minutes}-minute episode takes about ${Math.max(1, Math.round(minutes / 2))}-${minutes} minutes...`);
  busy(e.currentTarget, 'Making episode...', async () => {
    try {
      const m = await api(`/chapters/${id}/episode`, { method: 'POST', body: {
        minutes, style: $('input[name=l-style]:checked').value, focus: $('#l-focus').value,
      } });
      await loadList();
      openMedia(m.id);
      toast('Episode ready');
    } catch (err) { $('#l-player').innerHTML = before; throw err; }
  });
});

$('#l-import').addEventListener('click', () => openNotebookBridge(+$('#l-chapter').value || null, 'audio'));

// ---------- player ----------
async function openMedia(id) {
  try { renderPlayer(await api(`/media/${id}`)); loadList(); }
  catch (err) { toast(err.message, 'error'); }
}

function renderPlayer(m) {
  L.media = m;
  L.played = 0;
  const sc = m.script;
  const speakers = sc ? sc.speakers.map(s => s.name) : [];
  $('#l-player').innerHTML = `
    <div class="player-head">
      <div class="grow"><span class="chip">${icon(m.source === 'imported' ? 'upload' : 'headphones')}${STYLE_LABEL[m.source] || 'Audio'}</span>
        <h2>${esc(m.title)}</h2>
        <p class="muted small">${sc?.summary ? esc(sc.summary) + ' · ' : ''}${m.seconds ? fmt(m.seconds) : ''}${m.listens ? ` · listened ${m.listens}×` : ''}</p></div>
      <div class="row"><button class="icon-btn" id="l-rename" title="Rename">${icon('edit')}</button>
        <button class="icon-btn danger-hover" id="l-delete" title="Delete">${icon('trash')}</button></div>
    </div>
    <audio id="l-audio" controls preload="metadata" src="/api/media/${m.id}/file"></audio>
    <div class="row wrap player-opts">
      <div class="speed" id="l-speed">${[0.75, 0.9, 1].map(r => `<button class="${r === 1 ? 'active' : ''}" data-rate="${r}">${r}×</button>`).join('')}</div>
      ${sc ? `<label class="check"><input type="checkbox" id="l-show-text"> Show transcript</label>
        <label class="check"><input type="checkbox" id="l-show-tr"> Show translation</label>` : ''}
    </div>
    ${sc ? `
      <p class="muted small tip-line">${icon('sparkles')}Tip: listen once without the transcript, then again while reading, then pause after each line and repeat it out loud.</p>
      <div class="transcript hidden" id="l-transcript">${sc.turns.map((t, i) => `
        <div class="turn" data-i="${i}"><b class="spk spk-${Math.max(0, speakers.indexOf(t.speaker))}">${esc(t.speaker)}</b>
          <div class="grow"><p>${esc(t.text)}</p><p class="tr">${esc(t.translation)}</p></div>${hearButton(t.text)}</div>`).join('')}</div>
      <div class="two-col">
        <div><h3>Vocabulary</h3><ul class="vocab">${sc.vocabulary.map(v => `<li>${hearButton(v.german, 'tiny')}<b>${esc(v.german)}</b><span>${esc(v.meaning)}</span></li>`).join('')}</ul></div>
        <div><h3>Did you understand?</h3>${sc.questions.map(q => `<details class="q"><summary>${esc(q.question)}</summary><p>${esc(q.answer)}</p></details>`).join('')}</div>
      </div>` : '<p class="muted small">This audio has no transcript.</p>'}`;

  const audio = $('#l-audio');
  $('#l-speed').addEventListener('click', e => {
    const b = e.target.closest('[data-rate]');
    if (!b) return;
    audio.playbackRate = +b.dataset.rate;
    $$('#l-speed button').forEach(x => x.classList.toggle('active', x === b));
  });
  $('#l-show-text')?.addEventListener('change', e => $('#l-transcript').classList.toggle('hidden', !e.target.checked));
  $('#l-show-tr')?.addEventListener('change', e => $('#l-transcript').classList.toggle('with-tr', e.target.checked));
  $('#l-rename').addEventListener('click', async () => {
    const title = await promptDialog('Rename audio', m.title);
    if (title) { renderPlayer(await api(`/media/${m.id}`, { method: 'PUT', body: { title } })); loadList(); }
  });
  $('#l-delete').addEventListener('click', async () => {
    if (!await confirmDialog(`Delete "${m.title}"?`, 'The audio file is removed from the app.', { ok: 'Delete', danger: true })) return;
    await api(`/media/${m.id}`, { method: 'DELETE' });
    L.media = null;
    loadListening();
  });

  // Highlight the line being spoken. There are no timestamps, so estimate from each line's length.
  if (sc) {
    const lens = sc.turns.map(t => t.text.length + 20);
    const total = lens.reduce((a, b) => a + b, 0);
    const starts = lens.map((_, i) => lens.slice(0, i).reduce((a, b) => a + b, 0) / total);
    const turns = $$('.turn', $('#l-player'));
    audio.addEventListener('timeupdate', () => {
      if (!audio.duration) return;
      const pos = audio.currentTime / audio.duration;
      let cur = starts.findLastIndex(s => s <= pos);
      turns.forEach((t, i) => t.classList.toggle('current', i === cur && !audio.paused));
    });
    $('#l-transcript').addEventListener('click', e => {
      const t = e.target.closest('.turn');
      if (!t || e.target.closest('[data-hear]') || !audio.duration) return;
      audio.currentTime = starts[+t.dataset.i] * audio.duration;
      audio.play();
    });
  }

  // Listening time counts toward today's study minutes.
  audio.addEventListener('timeupdate', () => {
    const d = audio.currentTime - L.lastTime;
    L.lastTime = audio.currentTime;
    if (!audio.paused && d > 0 && d < 2) L.played += d;
    if (L.played >= 15) {
      api('/activity', { method: 'POST', body: { kind: 'listening', seconds: 15 } }).catch(() => {});
      L.played -= 15;
    }
  });
  audio.addEventListener('ended', () => {
    api(`/media/${m.id}/listened`, { method: 'POST' }).then(loadList).catch(() => {});
    toast('Nice listening! Try it again with the transcript, or shadow the speakers.');
  });
}

document.addEventListener('viewchange', e => { if (e.detail !== 'listening') $('#l-audio')?.pause(); });
