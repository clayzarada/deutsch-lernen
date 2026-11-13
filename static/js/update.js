// Updates: a banner when a newer version of the app has been released, with "Update now" (the app installs it
// itself, see app/update.py), and the "Check for updates" button in Settings > About.
// The server checks GitHub at most once a day.
import { $, api, esc, icon, store } from './core.js';

const DISMISS_KEY = 'update_dismissed';  // "Later" hides the banner until an even newer version comes out

// Release notes are Markdown; show the bullet points as plain text.
function noteLines(md) {
  return (md || '').split('\n').map(l => l.trim()).filter(l => /^[-*] /.test(l)).slice(0, 5)
    .map(l => l.slice(2).replace(/\*\*|__|`/g, '').replace(/\*([^*]+)\*/g, '$1'));
}

function showBanner(u) {
  if (!u?.newer || store.get(DISMISS_KEY) === u.latest || $('#update-banner')) return;
  const notes = noteLines(u.notes);
  const auto = u.install && u.install !== 'manual';
  const el = document.createElement('div');
  el.id = 'update-banner';
  el.className = 'update-banner';
  el.innerHTML = `${icon('download')}
    <div class="grow"><b>Version ${esc(u.latest)} is available</b>
      <p class="small" data-ustatus>You have ${esc(u.current)}. Your progress, cards and keys are kept when you update.</p>
      <div class="update-bar hidden"><i></i></div>
      ${notes.length ? `<details class="small"><summary>What's new</summary><ul>${notes.map(n => `<li>${esc(n)}</li>`).join('')}</ul></details>` : ''}</div>
    ${auto ? '<button type="button" class="small" data-install>Update now</button>'
      : `<a class="button small" href="${esc(u.download)}" target="_blank" rel="noopener">Download update</a>`}
    <button type="button" class="ghost small" data-later>Later</button>`;
  el.querySelector('[data-later]').addEventListener('click', () => { store.set(DISMISS_KEY, u.latest); el.remove(); });
  el.querySelector('[data-install]')?.addEventListener('click', () => install(el));
  $('main').prepend(el);
}

async function install(el) {
  const status = el.querySelector('[data-ustatus]'), bar = el.querySelector('.update-bar');
  const btn = el.querySelector('[data-install]'), later = el.querySelector('[data-later]');
  btn.disabled = true; later.disabled = true;
  bar.classList.remove('hidden');
  const say = t => { status.textContent = t; };
  try {
    let p = await api('/update/install', { method: 'POST' });
    while (['downloading', 'unpacking', 'pulling'].includes(p.stage)) {
      say(p.stage === 'downloading' ? `Downloading... ${p.pct || 0}%` : p.stage === 'unpacking' ? 'Unpacking...' : (p.message || 'Updating...'));
      bar.firstElementChild.style.width = `${p.stage === 'downloading' ? p.pct || 0 : 100}%`;
      await new Promise(r => setTimeout(r, 500));
      p = await api('/update/progress');
    }
    if (p.stage === 'error') throw new Error(p.message);
    bar.firstElementChild.style.width = '100%';
    if (p.stage === 'ready') {  // Windows app: restart to swap in the new version
      say('Restarting... the app opens again in a few seconds.');
      await api('/update/restart', { method: 'POST' });
      document.body.insertAdjacentHTML('beforeend', `<div class="update-overlay"><div>${icon('download')}<b>Updating to ${esc(p.latest)}</b><p>The app closes and opens again by itself in a few seconds.</p></div></div>`);
      return;
    }
    say(p.message);  // git copy: done, reopen to load it
    btn.remove(); later.disabled = false; later.textContent = 'OK';
  } catch (err) {
    say(err.message);
    btn.disabled = false; later.disabled = false;
    bar.classList.add('hidden');
  }
}

export async function checkForUpdate(force = false) {
  const u = await api('/update' + (force ? '?force=true' : ''));
  if (force) store.set(DISMISS_KEY, '');  // asking explicitly brings the banner back
  showBanner(u);
  return u;
}

// After the app has loaded, quietly in the background. Never shows an error.
setTimeout(() => checkForUpdate().catch(() => {}), 3000);

// Settings > About
document.addEventListener('click', async e => {
  const b = e.target.closest('#check-update');
  if (!b) return;
  const out = $('#update-status');
  b.disabled = true;
  out.textContent = 'Checking...';
  try {
    const u = await checkForUpdate(true);
    out.textContent = !u.ok ? "Couldn't reach the update server. Check your internet connection."
      : u.newer ? `Version ${u.latest} is available.` : `You have the newest version (${u.current}).`;
  } catch {
    out.textContent = "Couldn't reach the update server. Check your internet connection.";
  } finally {
    b.disabled = false;
  }
});
