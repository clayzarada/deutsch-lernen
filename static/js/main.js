// Entry point: loads every page module, wires up navigation and starts the app.
import { syncLanguage } from './i18n.js';  // first, so text is translated as soon as it appears
import { $$, S, api, store, toast, show, showSection, hasView, fillIcons, loadBooks, refreshNav, setNavLayout } from './core.js';
import './today.js';
import './library.js';
import './reader.js';
import './practice.js';
import './declensions.js';
import './writing.js';
import './cards.js';
import './listening.js';
import './notebook.js';
import './mistakes.js';
import './umlauts.js';
import './theme.js';
import './coach.js';
import './progress.js';
import './settings.js';
import './course.js';
import { startWelcome } from './welcome.js';
import './update.js';

fillIcons();

$$('#nav a[data-section]').forEach(a => a.addEventListener('click', () => showSection(a.dataset.section)));
document.addEventListener('click', e => {
  const g = e.target.closest('[data-go]');
  if (g) { e.preventDefault(); show(g.dataset.go); }
});
// Any sign of use counts: mouse, keys, scrolling (also inside panels), typing and touch.
['pointermove', 'keydown', 'wheel', 'pointerdown', 'input', 'touchstart', 'scroll'].forEach(ev =>
  document.addEventListener(ev, () => { S.lastActive = Date.now(); }, { passive: true, capture: true }));

(async function init() {
  try {
    S.settings = await api('/settings');
    syncLanguage(S.settings.ui_language);
    await loadBooks();
  } catch (err) {
    toast('Could not reach the app. Close Deutsch lernen and open it again. ' + err.message, 'error');
    return;
  }
  refreshNav();
  setNavLayout(new URLSearchParams(location.search).get('nav') || S.settings.nav_layout);
  // Sidebar links have no address, so give them a tab stop and a label (labels also show as tooltips when the sidebar is icons only).
  document.querySelectorAll('#nav a:not([href])').forEach(a => {
    a.tabIndex = 0; a.setAttribute('role', 'button');
    const label = a.querySelector('span')?.textContent.trim();
    if (label && !a.title) { a.title = label; a.setAttribute('aria-label', label); }
  });
  matchMedia('(max-width: 860px)').addEventListener('change', () => setNavLayout(S.settings.nav_layout));
  const start = store.get('view');
  show(hasView(start) && S.settings.onboarded ? start : 'today');
  if (!S.settings.onboarded) startWelcome();
})();
import('./survey.js');
import('./needsai.js');
document.addEventListener('keydown', e => {
  if ((e.key === 'Enter' || e.key === ' ') && e.target.matches?.('a[role=button]')) { e.preventDefault(); e.target.click(); }
});
