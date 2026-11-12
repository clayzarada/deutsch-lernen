// Gemini Notebook bridge: send a chapter to Gemini Notebook, give it good prompts, and import what it makes.
import { $, $$, S, api, esc, icon, busy, toast, loadBooks, chapterOptions, findChapter, show } from './core.js';

const KIND_HELP = {
  cards: 'Paste a table or list of words, or Gemini Notebook\'s flashcards. Tables (German | meaning) are imported as-is; anything else is tidied into cards by Claude.',
  exercises: 'Paste a quiz or list of questions. Claude turns it into a practice set you can answer and get graded on here.',
  audio: 'In Gemini Notebook, open the Audio Overview\'s ⋮ menu and choose Download. Then choose that file here.',
};

function prompts(chapter) {
  const lang = S.settings.native_language;
  const learner = `${S.settings.level.startsWith('A') ? 'an' : 'a'} ${S.settings.level} learner of German`;
  return [
    { title: 'Flashcards', tip: 'Paste the answer into step 3 as Flashcards',
      text: `Make 30 flashcards for ${learner} from the most useful vocabulary and phrases in "${chapter}". Give them as a table with three columns: German (nouns with article and plural, e.g. "der Tisch, -e") | ${lang} meaning | short German example sentence.` },
    { title: 'Practice quiz', tip: 'Paste the answer into step 3 as Practice questions',
      text: `Write 15 practice questions for ${learner} on the grammar and vocabulary of "${chapter}". Mix fill-in-the-gap, multiple choice and translation questions. After each question, give the correct answer and a one-sentence explanation.` },
    { title: 'Audio Overview (Customize box)', tip: 'Set the output language to Deutsch first, then download the audio and import it in step 3',
      text: `This is for ${learner}. Speak in simple, slow, clear German. Focus on the vocabulary and grammar of this chapter, use them often, and briefly explain difficult words in ${lang}.` },
    { title: 'Study guide', tip: 'Read it in Gemini Notebook, or paste it into step 3 as Flashcards',
      text: `Create a study guide for "${chapter}" for ${learner}: key vocabulary with articles and plurals, each grammar rule with two examples, and the most common mistakes learners make.` },
  ];
}

export async function openNotebookBridge(chapterId, kind = 'cards') {
  await loadBooks();
  if (!S.books.length) return toast('Import a book first', 'error');
  const dlg = $('#nb-dialog');
  $('#nb-chapter').innerHTML = chapterOptions(chapterId || S.books[0].chapters[0]?.id);
  $(`input[name=nb-kind][value=${kind}]`).checked = true;
  $('#nb-text').value = '';
  $('#nb-title').value = '';
  $('#nb-file').value = '';
  $('#nb-file-name').textContent = 'Or choose a file';
  $('#nb-result').innerHTML = '';
  renderPrompts();
  updateKind();
  dlg.showModal();
}

function renderPrompts() {
  const c = findChapter(+$('#nb-chapter').value)?.chapter;
  $('#nb-prompts').innerHTML = prompts(c?.title || 'this chapter').map((p, i) => `
    <div class="prompt-card"><div class="row"><b class="grow">${esc(p.title)}</b>
      <button class="ghost small" data-copy="${i}">${icon('page')}Copy</button></div>
      <p>${esc(p.text)}</p><span class="muted small">${esc(p.tip)}</span></div>`).join('');
  $('#nb-prompts').dataset.texts = JSON.stringify(prompts(c?.title || 'this chapter').map(p => p.text));
}

function updateKind() {
  const kind = $('input[name=nb-kind]:checked').value;
  $('#nb-kind-help').textContent = KIND_HELP[kind];
  $('#nb-text').classList.toggle('hidden', kind === 'audio');
  $('#nb-file').accept = kind === 'audio' ? 'audio/*,.mp3,.m4a,.wav,.ogg,.webm' : '.txt,.md,.csv,.tsv,.json,.pdf,.html';
}

$('#nb-chapter').addEventListener('change', renderPrompts);
$$('input[name=nb-kind]').forEach(r => r.addEventListener('change', updateKind));
$('#nb-close').addEventListener('click', () => $('#nb-dialog').close());
$('#nb-pdf').addEventListener('click', () => { window.location.href = `/api/chapters/${$('#nb-chapter').value}/pdf`; });
$('#nb-file').addEventListener('change', e => { $('#nb-file-name').textContent = e.target.files[0]?.name || 'Or choose a file'; });

$('#nb-prompts').addEventListener('click', async e => {
  const b = e.target.closest('[data-copy]');
  if (!b) return;
  await navigator.clipboard.writeText(JSON.parse($('#nb-prompts').dataset.texts)[+b.dataset.copy]);
  b.innerHTML = icon('check') + 'Copied';
  setTimeout(() => { b.innerHTML = icon('page') + 'Copy'; }, 1800);
});

$('#nb-import').addEventListener('click', e => {
  const kind = $('input[name=nb-kind]:checked').value;
  const file = $('#nb-file').files[0];
  const text = $('#nb-text').value.trim();
  if (!file && (kind === 'audio' || !text)) return toast(kind === 'audio' ? 'Choose an audio file first' : 'Paste something or choose a file first', 'error');
  const chapterId = +$('#nb-chapter').value;
  const fd = new FormData();
  fd.append('chapter_id', chapterId);
  fd.append('kind', kind);
  fd.append('text', kind === 'audio' ? '' : text);
  fd.append('title', $('#nb-title').value);
  if (file) fd.append('file', file);
  busy(e.currentTarget, kind === 'audio' ? 'Uploading...' : 'Importing...', async () => {
    const r = await api('/import', { method: 'POST', body: fd });
    const go = {
      cards: [`Added ${r.added} flashcards`, 'Open flashcards', () => { S.cardTab = 'browse'; S.cardScope = String(chapterId); show('cards'); }],
      exercises: [`Added a practice set with ${r.added} questions`, 'Open practice set', () => { S.currentSet = { id: r.set_id }; show('practice'); }],
      audio: ['Audio added', 'Open in Listening', () => { S.listenMedia = r.media_id; show('listening'); }],
    }[r.kind];
    $('#nb-result').innerHTML = `<div class="result perfect">${icon('check')}<b>${go[0]}</b><button class="small">${go[1]}</button></div>`;
    $('#nb-result button').addEventListener('click', () => { $('#nb-dialog').close(); go[2](); });
    $('#nb-text').value = '';
    $('#nb-file').value = '';
    $('#nb-file-name').textContent = 'Or choose a file';
  });
});
