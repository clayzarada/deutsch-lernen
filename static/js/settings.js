// Resources and Settings pages.
import { $, S, api, esc, icon, toast, registerView, confirmDialog, emptyState, updateNavStatus, playClip, setNavLayout } from './core.js';
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
  ui_language: 's-ui-lang', nav_layout: 's-nav', model: 's-model', quick_model: 's-quick-model', effort: 's-effort', level: 's-level', native_language: 's-native', daily_minutes: 's-minutes',
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
  $('#s-key').placeholder = s.own_key ? 'Saved. Paste a new key to replace it.' : 'Paste your key from console.anthropic.com';
  $('#key-state').innerHTML = keyPill(s.own_key);
  // Plus picks the models; the choice only applies to your own API key.
  $('#plus-models').hidden = !s.plus_mode;
  $('#model-choice').hidden = !!s.plus_mode;
  $('#quick-choice').hidden = !!s.plus_mode;
  $('#quick-note').hidden = !!s.plus_mode;
  $('#s-gkey').value = '';
  $('#s-gkey').placeholder = s.has_gemini_key ? 'Saved. Paste a new key to replace it.' : 'Paste your key from aistudio.google.com/apikey';
  $('#gkey-state').innerHTML = keyPill(s.has_gemini_key);
  loadAccount().catch(() => {});
  loadUsage().catch(() => {});
  loadBackups().catch(() => {});
  $('#about-version').textContent = s.version ? `${s.version}${s.build_name ? ` “${s.build_name}”` : ''}` : '';
  if (s.credits) {
    $('#about-author').textContent = s.credits.author;
    $('#about-copyright').textContent = s.credits.copyright;
  }
}

// ---------- account (Plus) ----------
const ACC = { email: '', codeSent: false };

async function loadAccount(refresh) {
  renderAccount(await api('/account' + (refresh ? '?refresh=true' : '')));
}

// ---------- cloud backup (Plus) ----------
const when = iso => new Date(iso).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
const kb = n => n == null ? '' : n < 1048576 ? `${Math.max(1, Math.round(n / 1024))} KB` : `${(n / 1048576).toFixed(1)} MB`;

async function loadCloud() {
  const box = $('#cloud-box');
  if (!box) return;
  try { renderCloud(await api('/cloud?full=true')); }
  catch (err) { box.innerHTML = `<h3>Cloud backup</h3><p class="muted small">${esc(err.message)}</p>`; }
}

function renderCloud(c) {
  const box = $('#cloud-box');
  if (!box) return;
  const list = c.backups || [];
  box.innerHTML = `
    <h3>Cloud backup</h3>
    <label class="check"><input type="checkbox" id="cloud-on" ${c.enabled ? 'checked' : ''}> Back up my study data to the cloud every day</label>
    <p class="muted small">Your progress, flashcards, answers and notes, kept safe on our server and restorable on any computer where you sign in. Book files (PDFs) stay on this computer. The newest ${c.keep} backups are kept.</p>
    <div class="btnrow"><button type="button" class="ghost small" id="cloud-now">Back up now</button></div>
    ${list.length ? `<div class="cloud-list">${list.map(b => `<div class="backup-row"><span><b>${esc(when(b.created))}</b> <span class="muted small">${kb(b.size)}</span></span>
        <button type="button" class="ghost small" data-cloud-restore="${esc(b.name)}">Restore</button></div>`).join('')}</div>`
      : '<p class="muted small">No cloud backups yet.</p>'}`;
}

$('#account-box').addEventListener('change', async e => {
  if (e.target.id !== 'cloud-on') return;
  try {
    await api('/cloud', { method: 'PUT', body: { enabled: e.target.checked } });
    toast(e.target.checked ? 'Daily cloud backup is on' : 'Daily cloud backup is off');
    if (e.target.checked) setTimeout(loadCloud, 4000);  // the first backup runs in the background
  } catch (err) { toast(err.message, 'error'); e.target.checked = !e.target.checked; }
});

$('#account-box').addEventListener('click', async e => {
  if (e.target.closest('#cloud-now')) {
    const b = e.target.closest('#cloud-now');
    b.disabled = true; b.textContent = 'Backing up…';
    try { renderCloud(await api('/cloud/backup', { method: 'POST' })); toast('Backed up to the cloud'); }
    catch (err) { toast(err.message, 'error'); b.disabled = false; b.textContent = 'Back up now'; }
    return;
  }
  const r = e.target.closest('[data-cloud-restore]');
  if (!r) return;
  const at = r.closest('.backup-row').querySelector('b').textContent;
  if (!await confirmDialog(`Restore the cloud backup from ${at}?`, 'Your study data on this computer (answers, cards, progress) is replaced by the backup. What you have now is backed up on this computer first, so you can switch back under Backups.', { ok: 'Restore', danger: true })) return;
  try {
    await api('/cloud/restore', { method: 'POST', body: { name: r.dataset.cloudRestore } });
    toast('Cloud backup restored. Reloading...');
    setTimeout(() => location.reload(), 900);
  } catch (err) { toast(err.message, 'error'); }
});

function renderAccount(a) {
  const box = $('#account-box');
  if (!a.signed_in) {
    box.innerHTML = `
      <p class="small">Sign in to use <b>Plus</b>: AI features without an API key of your own. Free features never need an account.</p>
      <div class="acct-row"><input id="acct-email" type="email" placeholder="you@example.com" value="${esc(ACC.email)}" autocomplete="email">
        <button type="button" class="ghost" id="acct-send">${ACC.codeSent ? 'Send again' : 'Email me a sign-in link'}</button></div>
      ${ACC.codeSent ? `<div class="acct-row"><input id="acct-code" inputmode="numeric" autocomplete="one-time-code" placeholder="Code from the email" maxlength="12">
        <button type="button" id="acct-verify">Sign in</button></div>
        <p class="muted small">We emailed ${esc(ACC.email)}. Click the link in the email on this computer, or type the code if the email has one. It may take a minute; check spam too.</p>` : ''}`;
    return;
  }
  const plus = a.plus;
  const pct = a.used_pct || 0;
  box.innerHTML = `
    <p>Signed in as <b>${esc(a.email || '')}</b> · ${plus ? `<span class="pill ok">${icon('check')}Plus</span>` : '<span class="pill">Free</span>'}</p>
    ${plus ? `<div class="meter"><div class="meter-bar ${pct >= 90 ? 'bad' : pct >= 70 ? 'mid' : ''}"><span style="width:${pct}%"></span></div><span>${pct}% of this month's AI allowance used</span></div>
      <p class="muted small">${S.settings.own_key ? 'Your own API key is saved, so the app uses it instead of Plus. Use “Remove API key” at the bottom of Settings to switch to Plus.' : 'AI features run through Plus. No API key needed.'}</p>`
      : !a.sales_open ? `<p class="small" style="margin-top:8px"><b>Plus is coming soon:</b> AI features with no API key of your own, plus cloud backup. You'll be able to upgrade right here.</p>`
      : `<p class="small" style="margin-top:8px">Get <b>Plus</b> for AI features with no API key of your own. Cancel any time.</p>
        <div class="btnrow"><button type="button" id="acct-buy-yearly">Upgrade: $79 / year</button>
          <button type="button" class="ghost" id="acct-buy-monthly">$9.99 / month</button></div>
        <p class="muted small">Checkout opens in your browser. When you're done, come back and press Refresh.</p>`}
    ${plus ? '<div id="cloud-box" class="cloud-box"><p class="muted small">Loading cloud backup…</p></div>' : ''}
    ${a.offline ? '<p class="muted small">Offline: showing the last known status.</p>' : ''}
    <div class="btnrow">${plus ? '<button type="button" class="ghost small" id="acct-manage">Manage subscription</button>' : ''}<button type="button" class="ghost small" id="acct-refresh">Refresh</button>
      <button type="button" class="ghost small" id="acct-out">Sign out</button>
      <button type="button" class="ghost small danger-hover" id="acct-delete">Delete account</button></div>`;
  if (plus) loadCloud();
}

$('#account-box').addEventListener('click', async e => {
  const id = e.target.closest('button')?.id;
  if (!id) return;
  try {
    if (id === 'acct-send') {
      ACC.email = $('#acct-email').value.trim();
      await api('/account/code', { method: 'POST', body: { email: ACC.email } });
      ACC.codeSent = true;
      renderAccount({ signed_in: false });
      $('#acct-code')?.focus();
      toast('Email sent');
    } else if (id === 'acct-verify') {
      if (ACC.verifying) return;  // a double click would send the code twice; the second try always fails
      ACC.verifying = true;
      try {
        const a = await api('/account/verify', { method: 'POST', body: { email: ACC.email, code: $('#acct-code').value } });
        ACC.codeSent = false;
        await refreshAfterAccount(a);
        toast('Signed in');
      } catch (err) {
        const a = await api('/account').catch(() => ({}));
        if (!a.signed_in) throw err;  // a real failure; if we're signed in anyway, say nothing
        ACC.codeSent = false;
        await refreshAfterAccount(a);
      } finally { ACC.verifying = false; }
    } else if (id === 'acct-buy-yearly' || id === 'acct-buy-monthly') {
      const { url } = await api('/account/checkout', { method: 'POST', body: { plan: id.endsWith('yearly') ? 'yearly' : 'monthly' } });
      window.open(url, '_blank', 'noopener');
      watchForPlus();
    } else if (id === 'acct-manage') {
      const { url } = await api('/account/portal', { method: 'POST' });
      window.open(url, '_blank', 'noopener');
    } else if (id === 'acct-refresh') {
      await refreshAfterAccount(await api('/account?refresh=true'));
    } else if (id === 'acct-out') {
      await refreshAfterAccount(await api('/account/signout', { method: 'POST' }));
      toast('Signed out');
    } else if (id === 'acct-delete') {
      if (!await confirmDialog('Delete your account?', 'This cancels any Plus subscription right away and removes your sign-in, Plus status, usage records and cloud backups from our server. Your study data on this computer is not touched.', { ok: 'Delete account', danger: true })) return;
      await refreshAfterAccount(await api('/account/delete', { method: 'POST' }));
      toast('Account deleted');
    }
  } catch (err) { toast(err.message, 'error'); }
});

// After opening checkout, check every 10 seconds for up to 10 minutes so Plus shows up without pressing Refresh.
let plusWatch = null;
function watchForPlus() {
  clearInterval(plusWatch);
  let tries = 0;
  plusWatch = setInterval(async () => {
    if (++tries > 60) return clearInterval(plusWatch);
    try {
      const a = await api('/account?refresh=true');
      if (a.plus) { clearInterval(plusWatch); await refreshAfterAccount(a); toast('Plus is active. Thank you!'); }
    } catch { /* offline: try again next time */ }
  }, 10000);
}

// Enter in the code box signs in (instead of submitting the whole Settings form).
$('#account-box').addEventListener('keydown', e => {
  if (e.key !== 'Enter' || !e.target.matches('#acct-code, #acct-email')) return;
  e.preventDefault();
  $(e.target.id === 'acct-code' ? '#acct-verify' : '#acct-send')?.click();
});

async function refreshAfterAccount(a) {
  S.settings = await api('/settings');
  renderAccount(a);
  updateNavStatus();
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

$('#backup-save').addEventListener('click', () => { window.location.href = '/api/backups/export'; });
$('#backup-load').addEventListener('click', () => $('#backup-load-file').click());
$('#backup-load-file').addEventListener('change', async e => {
  const f = e.target.files[0];
  e.target.value = '';
  if (!f) return;
  if (!await confirmDialog('Load this backup file?', 'Your progress, cards and answers are replaced by the ones in the file, and its books and audio are added. What you have now is backed up first, so you can switch back under Backups.', { ok: 'Load backup', danger: true })) return;
  const fd = new FormData();
  fd.append('file', f);
  try {
    toast('Loading the backup...');
    await api('/backups/import', { method: 'POST', body: fd });
    toast('Backup loaded. Reloading...');
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
  setNavLayout(S.settings.nav_layout);
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

// The beginner course switch and the welcome flow.
import('./welcome.js').then(({ startWelcome }) => {
  $('#s-welcome').addEventListener('click', startWelcome);
});
$('#s-course').addEventListener('change', async e => {
  S.settings = await api('/settings', { method: 'PUT', body: { use_course: e.target.checked ? '1' : '0' } });
});
document.addEventListener('viewchange', e => { if (e.detail === 'settings') $('#s-course').checked = S.settings?.use_course === '1'; });
