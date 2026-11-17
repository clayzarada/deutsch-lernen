// In-app questions from the developer: a (!) "Quick question" link in the sidebar opens a small dialog.
// Answering or skipping removes it; the question is never asked again on this computer.
import { $, S, api, esc, toast, setNavLayout } from './core.js';

// An option can preview itself live behind the dialog: "try": "nav:side" switches the navigation layout.
function tryOut(spec) {
  const [what, value] = String(spec || '').split(':');
  if (what === 'nav') setNavLayout(value);
}
function undoTry() { setNavLayout(S.settings.nav_layout); }

let open = [];

async function refresh() {
  try { open = await api('/surveys'); } catch { open = []; }
  $('#nav-survey')?.classList.toggle('hidden', !open.length);
}

function close() { $('.survey-back')?.remove(); undoTry(); }

function render(s) {
  close();
  const imgs = s.kind === 'image_choice';
  const opts = s.kind === 'rating'
    ? `<div class="survey-rating">${[1, 2, 3, 4, 5].map(n => `<button type="button" class="survey-opt" data-v="${n}">${n}</button>`).join('')}</div>`
    : s.kind === 'text' ? ''
    : `<div class="survey-opts ${imgs ? 'images' : ''}">${(s.options || []).map(o => `
        <button type="button" class="survey-opt" data-v="${esc(o.id)}" title="${o.try ? 'Click to see it behind this box' : ''}">
          ${imgs && o.image ? `<img src="${esc(o.image)}" alt="" loading="lazy">` : ''}<span>${esc(o.label)}</span></button>`).join('')}</div>`;
  const back = document.createElement('div');
  back.className = 'survey-back';
  back.innerHTML = `<div class="survey" role="dialog" aria-modal="true" aria-label="${esc(s.title)}">
      <h2>${esc(s.title)}</h2><p class="q">${esc(s.question)}</p>${opts}
      ${(s.options || []).some(o => o.try) ? '<p class="muted small">Click an option to see it in the app behind this box.</p>' : ''}
      ${s.kind === 'text' || s.allow_comment ? `<textarea id="survey-comment" placeholder="${s.kind === 'text' ? '' : 'Anything else? (optional)'}"></textarea>` : ''}
      <div class="btnrow"><button type="button" class="ghost" data-skip>Skip</button><button type="button" data-send ${s.kind === 'text' ? '' : 'disabled'}>Send</button></div>
    </div>`;
  document.body.append(back);
  let picked = null;
  back.addEventListener('click', async e => {
    if (e.target === back) return close();
    const o = e.target.closest('.survey-opt');
    if (o) {
      picked = o.dataset.v;
      tryOut((s.options || []).find(x => String(x.id) === picked)?.try);
      back.querySelectorAll('.survey-opt').forEach(b => b.classList.toggle('on', b === o));
      back.querySelector('[data-send]').disabled = false;
      return;
    }
    const skip = !!e.target.closest('[data-skip]');
    if (!skip && !e.target.closest('[data-send]')) return;
    try {
      const r = await api(`/surveys/${encodeURIComponent(s.id)}`, { method: 'POST',
        body: { answer: picked, comment: $('#survey-comment')?.value || '', skipped: skip } });
      open = r.pending || [];
      close();
      $('#nav-survey')?.classList.toggle('hidden', !open.length);
      if (!skip) toast('Thanks for answering!');
    } catch (err) { toast(err.message, 'error'); }
  });
  document.addEventListener('keydown', function esc_(e) { if (e.key === 'Escape') { close(); document.removeEventListener('keydown', esc_); } });
}

$('#nav-survey')?.addEventListener('click', e => { e.preventDefault(); if (open.length) render(open[0]); });
refresh();
setInterval(refresh, 30 * 60 * 1000);  // new questions show up without restarting the app
