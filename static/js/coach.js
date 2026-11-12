// Coach page: chat with the study coach, and its notes about you.
import { $, S, api, esc, icon, md, toast, registerView, confirmDialog } from './core.js';

const IDEAS = ['How did my week go?', 'What should I focus on this week?', 'Find me a good video on this chapter\'s grammar', 'Make a plan to reach my goal'];

registerView('coach', loadCoach);

async function loadCoach() {
  api('/progress').then(renderProgress).catch(() => {});
  renderChat(await api('/coach/messages'));
  $('#coach-notes').value = S.settings.coach_notes || '';
}

function miniBars(title, weeks, get, show) {
  const vals = weeks.map(get);
  const max = Math.max(1, ...vals.map(v => v || 0));
  const last = vals[vals.length - 1];
  return `<div class="pg-chart"><h3>${title}</h3><p><b>${last == null ? '–' : show(last)}</b> <small class="muted">this week</small></p>
    <div class="bars mini">${weeks.map((w, i) => `<div class="bar ${i === weeks.length - 1 ? 'today' : ''}" title="Week of ${new Date(w.start + 'T12:00').toLocaleDateString(undefined, { day: 'numeric', month: 'short' })}: ${vals[i] == null ? 'nothing yet' : show(vals[i])}">
      <div class="bar-track"><span style="height:${vals[i] ? Math.max(6, (100 * vals[i]) / max) : 0}%"></span></div></div>`).join('')}</div></div>`;
}

// Eight weeks at a glance, so the coach's advice can be checked against the numbers.
function renderProgress(p) {
  const j = p.journey;
  $('#coach-progress').innerHTML = `<div class="pg-grid">
    ${miniBars('Minutes', p.weeks, w => w.minutes, v => v + ' min')}
    ${miniBars('Accuracy', p.weeks, w => w.accuracy, v => v + '%')}
    ${miniBars('Cards reviewed', p.weeks, w => w.cards, v => v)}
    ${miniBars('Study days', p.weeks, w => w.days, v => v + ' of 7')}
  </div>
  <p class="muted small pg-foot">${icon('flame')}${p.streak.days} day streak &nbsp;·&nbsp; ${icon('rocket')}Declensions: ${j.planets_done} of ${j.planets_total} planets, now on ${esc(j.title)} &nbsp;·&nbsp; bars show the last 8 weeks</p>`;
}

function bubble(m) {
  return m.role === 'user'
    ? `<div class="msg user">${esc(m.content)}</div>`
    : `<div class="msg assistant"><span class="avatar">${icon('sparkles')}</span><div class="msg-body">${md(m.content)}</div></div>`;
}

function renderChat(msgs, pending) {
  const log = $('#coach-log');
  if (!msgs.length && !pending) {
    log.innerHTML = bubble({ role: 'assistant', content: 'Hallo! I\'m your study coach. I can see your reading, practice results and flashcards, so ask me anything. For a full session plan, press **Plan my day** on the Today page.' })
      + `<div class="suggest">${IDEAS.map(i => `<button class="chip-btn" data-suggest>${esc(i)}</button>`).join('')}</div>`;
    return;
  }
  log.innerHTML = msgs.map(bubble).join('')
    + (pending ? `<div class="msg user">${esc(pending)}</div><div class="msg assistant"><span class="avatar">${icon('sparkles')}</span><div class="msg-body typing"><i></i><i></i><i></i></div></div>` : '');
  log.lastElementChild?.scrollIntoView({ block: 'end', behavior: 'smooth' });
}

async function send(text) {
  text = text.trim();
  if (!text) return;
  const prev = await api('/coach/messages');
  renderChat(prev, text);
  const input = $('#coach-input');
  input.value = '';
  autosize();
  try { renderChat(await api('/coach/chat', { method: 'POST', body: { message: text } })); }
  catch (err) { toast(err.message, 'error'); renderChat(prev); input.value = text; autosize(); }
}

function autosize() {
  const t = $('#coach-input');
  t.style.height = 'auto';
  t.style.height = Math.min(t.scrollHeight, 200) + 'px';
}

$('#coach-form').addEventListener('submit', e => { e.preventDefault(); send($('#coach-input').value); });
$('#coach-input').addEventListener('input', autosize);
$('#coach-input').addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(e.target.value); } });
$('#coach-log').addEventListener('click', e => { const b = e.target.closest('[data-suggest]'); if (b) send(b.textContent); });
$('#coach-clear').addEventListener('click', async () => {
  if (!await confirmDialog('Clear the chat?', 'The coach\'s notes about you are kept.', { ok: 'Clear chat', danger: true })) return;
  await api('/coach/messages', { method: 'DELETE' });
  loadCoach();
});
$('#coach-notes-save').addEventListener('click', async () => {
  S.settings = await api('/settings', { method: 'PUT', body: { coach_notes: $('#coach-notes').value } });
  toast('Notes saved');
});
