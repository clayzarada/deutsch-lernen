// Resources and Settings pages.
import { $, S, api, esc, icon, toast, registerView, confirmDialog, emptyState, updateNavStatus, playClip } from './core.js';
import { setLanguage } from './i18n.js';

// ---------- resources ----------
const KIND_ICON = { video: 'play', podcast: 'headphones', course: 'library', reading: 'page', app: 'cards', speaking: 'mic', other: 'resources' };

registerView('resources', async () => renderResources(await api('/resources')));

function renderResources(list) {
  $('#res-list').innerHTML = list.length ? list.map(r => {
    const host = r.url ? r.url.replace(/^https?:\/\/(www\.)?/, '').split('/')[0] : '';
    return `<div class="res">
      <span class="res-icon">${icon(KIND_ICON[r.kind] || 'resources')}</span>
      <div class="grow"><b>${r.url ? `<a href="${esc(r.url)}" target="_blank" rel="noopener">${esc(r.title)}</a>` : esc(r.title)}</b>
        <div class="muted small">${esc(r.kind)}${host ? ' · ' + esc(host) : ''}</div>
        ${r.notes ? `<p class="small">${esc(r.notes)}</p>` : ''}</div>
      <button class="icon-btn danger-hover" data-del="${r.id}" title="Remove">${icon('trash')}</button></div>`;
  }).join('') : emptyState('resources', 'No resources yet', 'Add channels, podcasts and sites you like.');
}

$('#res-form').addEventListener('submit', async e => {
  e.preventDefault();
  renderResources(await api('/resources', { method: 'POST', body: { title: $('#res-title').value, url: $('#res-url').value, kind: $('#res-kind').value, notes: $('#res-notes').value } }));
  e.target.reset();
  toast('Resource added');
});
$('#res-list').addEventListener('click', async e => {
  const d = e.target.closest('[data-del]');
  if (d) renderResources(await api(`/resources/${d.dataset.del}`, { method: 'DELETE' }));
});

// ---------- settings ----------
const FIELDS = {
  ui_language: 's-ui-lang', model: 's-model', effort: 's-effort', level: 's-level', native_language: 's-native', daily_minutes: 's-minutes',
  goal: 's-goal', exam_date: 's-exam', new_cards_per_day: 's-newcards', monthly_budget: 's-budget', tts_model: 's-tts-model', voice_a: 's-voice-a', voice_b: 's-voice-b',
};

registerView('settings', loadSettings);

const keyPill = has => has ? `<span class="pill ok">${icon('check')}saved</span>` : '<span class="pill bad">not set</span>';

function loadSettings() {
  const s = S.settings;
  const voices = s.voices.map(v => `<option>${v}</option>`).join('');
  $('#s-voice-a').innerHTML = voices;
  $('#s-voice-b').innerHTML = voices;
  for (const [k, id] of Object.entries(FIELDS)) $('#' + id).value = s[k] ?? '';
  $('#s-web').checked = s.web_search === '1';
  $('#s-key').value = '';
  $('#s-key').placeholder = s.has_key ? 'Saved. Paste a new key to replace it.' : 'Paste your key from console.anthropic.com';
  $('#key-state').innerHTML = keyPill(s.has_key);
  $('#s-gkey').value = '';
  $('#s-gkey').placeholder = s.has_gemini_key ? 'Saved. Paste a new key to replace it.' : 'Paste your key from aistudio.google.com/apikey';
  $('#gkey-state').innerHTML = keyPill(s.has_gemini_key);
  loadUsage().catch(() => {});
  loadBackups().catch(() => {});
  $('#about-version').textContent = s.version ? `${s.version}${s.build_name ? ` “${s.build_name}”` : ''}` : '';
  if (s.credits) {
    $('#about-author').textContent = s.credits.author;
    $('#about-copyright').textContent = s.credits.copyright;
  }
}

const money = v => v < 0.01 && v > 0 ? '< $0.01' : '$' + v.toFixed(2);

async function loadUsage() {
  const u = await api('/usage');
  const max = Math.max(0.01, ...u.months.map(m => m.cost));
  const pct = u.budget ? Math.min(100, (100 * u.month) / u.budget) : 0;
  $('#usage-box').innerHTML = `
    <div class="usage-top"><div><b>${money(u.month)}</b><span>this month${u.budget ? ` of ${money(u.budget)}` : ''}</span><small>${money(u.today)} today</small></div>
      ${u.months.length > 1 ? `<div class="bars mini usage-bars">${u.months.map(m => `<div class="bar" title="${m.month}: ${money(m.cost)}"><div class="bar-track"><span style="height:${Math.max(4, (100 * m.cost) / max)}%"></span></div><small>${new Date(m.month + '-15').toLocaleDateString(undefined, { month: 'narrow' })}</small></div>`).join('')}</div>` : ''}</div>
    ${u.budget ? `<div class="meter ${pct >= 100 ? '' : ''}"><div class="meter-bar ${pct >= 90 ? 'bad' : pct >= 70 ? 'mid' : ''}"><span style="width:${pct}%"></span></div><span>${Math.round(pct)}% of the budget</span></div>` : ''}
    ${u.features.length ? `<table class="usage-table"><tbody>${u.features.map(f => `<tr><td>${esc(f.label)}</td><td class="muted">${f.calls} call${f.calls === 1 ? '' : 's'}</td><td>${f.provider === 'gemini' ? '<span class="muted">not priced</span>' : money(f.cost)}</td></tr>`).join('')}</tbody></table>`
      : '<p class="muted small">No AI calls this month yet.</p>'}
    <p class="muted small">Estimated from Anthropic's list prices${u.since ? `, counted since ${new Date(u.since).toLocaleDateString()}` : ''}. Your actual bill is at console.anthropic.com, and includes anyone else using the same key.</p>`;
}

async function loadBackups(list) {
  const r = list ? { backups: list } : await api('/backups');
  const label = { auto: 'Daily backup', manual: 'Made by hand', 'before-restore': 'Before a restore' };
  $('#backup-box').innerHTML = `<div class="backup-list">${r.backups.slice(0, 20).map(b => `<div class="backup-row">
      <span class="grow"><b>${new Date(b.created).toLocaleString(undefined, { weekday: 'short', day: 'numeric', month: 'short', hour: 'numeric', minute: '2-digit' })}</b>
      <small class="muted">${label[b.kind]} · ${(b.size / 1048576).toFixed(1)} MB</small></span>
      <button type="button" class="ghost small" data-restore="${esc(b.name)}">Restore</button></div>`).join('') || '<p class="muted small">No backups yet.</p>'}</div>
    <button type="button" class="ghost small" id="backup-now">${icon('download')}Back up now</button>`;
}

$('#backup-box').addEventListener('click', async e => {
  if (e.target.closest('#backup-now')) {
    const r = await api('/backups', { method: 'POST' });
    toast('Backup made');
    return loadBackups(r.backups);
  }
  const b = e.target.closest('[data-restore]');
  if (!b) return;
  const when = b.closest('.backup-row').querySelector('b').textContent;
  if (!await confirmDialog(`Restore the backup from ${when}?`, 'Everything since then (answers, cards, progress) is replaced by the backup. What you have now is backed up first, so you can switch back.', { ok: 'Restore', danger: true })) return;
  try {
    await api('/backups/restore', { method: 'POST', body: { name: b.dataset.restore } });
    toast('Backup restored. Reloading...');
    setTimeout(() => location.reload(), 900);
  } catch (err) { toast(err.message, 'error'); }
});

$('#s-voice-test').addEventListener('click', async e => {
  if ($('#s-voice-a').value !== S.settings.voice_a) await saveSettings(true);
  playClip('Hallo! Schön, dass du da bist. Heute lernen wir zusammen Deutsch.', e.currentTarget);
});

async function saveSettings(quiet = false) {
  const body = { web_search: $('#s-web').checked ? '1' : '0' };
  for (const [k, id] of Object.entries(FIELDS)) body[k] = $('#' + id).value;
  if ($('#s-key').value.trim()) body.api_key = $('#s-key').value.trim();
  if ($('#s-gkey').value.trim()) body.gemini_key = $('#s-gkey').value.trim();
  const langChanged = body.ui_language !== (S.settings.ui_language || 'en');
  if (langChanged) {
    // The AI explains things in the learner's language, so follow the app language unless it was set to something else.
    const native = body.native_language.trim().toLowerCase();
    if (body.ui_language === 'tr' && (!native || native === 'english')) body.native_language = 'Turkish';
    if (body.ui_language === 'en' && (native === 'turkish' || native === 'türkçe')) body.native_language = 'English';
  }
  S.settings = await api('/settings', { method: 'PUT', body });
  if (langChanged) { setLanguage(S.settings.ui_language); return; }  // reloads the page in the new language
  loadSettings();
  updateNavStatus();
  if (!quiet) toast('Settings saved');
}

$('#settings-form').addEventListener('submit', async e => {
  e.preventDefault();
  try { await saveSettings(); } catch (err) { toast(err.message, 'error'); }
});

$('#s-remove-key').addEventListener('click', async () => {
  if (!await confirmDialog('Remove the saved Claude API key?', 'AI features stop working until you add a key again.', { ok: 'Remove', danger: true })) return;
  S.settings = await api('/settings', { method: 'PUT', body: { api_key: '' } });
  loadSettings();
  updateNavStatus();
});
