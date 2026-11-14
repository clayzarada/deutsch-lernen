// Entry point: loads every page module, wires up navigation and starts the app.
import { syncLanguage } from './i18n.js';  // first, so text is translated as soon as it appears
import { $$, S, api, store, toast, show, showSection, hasView, fillIcons, loadBooks, refreshNav } from './core.js';
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
import './settings.js';
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
    toast('Could not reach the app server. Is the start.bat window still open? ' + err.message, 'error');
    return;
  }
  refreshNav();
  const start = store.get('view');
  show(hasView(start) ? start : 'today');
})();
