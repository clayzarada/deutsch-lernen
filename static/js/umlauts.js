// Umlaut helper: a small ä ö ü ß bar next to any text field you're typing in,
// plus shortcuts: Alt+A/O/U/S → ä ö ü ß, and Alt+Shift+A/O/U → Ä Ö Ü.

const CHARS = ['ä', 'ö', 'ü', 'ß', 'Ä', 'Ö', 'Ü'];
const KEYS = { a: 'ä', o: 'ö', u: 'ü', s: 'ß' };
const TEXT_INPUTS = ['text', 'search', ''];

const bar = document.createElement('div');
bar.id = 'umlaut-bar';
bar.className = 'umlaut-bar hidden';
bar.innerHTML = CHARS.map(c => {
  const key = Object.keys(KEYS).find(k => KEYS[k] === c.toLowerCase());
  const hint = key ? `Alt+${c === c.toLowerCase() ? '' : 'Shift+'}${key.toUpperCase()}` : '';
  return `<button type="button" data-ch="${c}" title="${hint}">${c}</button>`;
}).join('');
document.body.append(bar);

let target = null;

function editable(el) {
  if (!el) return false;
  if (el.isContentEditable) return true;
  if (el.tagName === 'TEXTAREA') return !el.readOnly;
  return el.tagName === 'INPUT' && TEXT_INPUTS.includes(el.getAttribute('type') || '') && !el.readOnly;
}

function insert(ch) {
  if (!target) return;
  target.focus();
  // insertText keeps the browser's undo history and fires the normal input events.
  if (!document.execCommand('insertText', false, ch) && 'setRangeText' in target) {
    target.setRangeText(ch, target.selectionStart, target.selectionEnd, 'end');
    target.dispatchEvent(new Event('input', { bubbles: true }));
  }
}

function place() {
  if (!target) return;
  const r = target.getBoundingClientRect();
  const h = bar.offsetHeight || 34;
  const below = r.bottom + 6 + h < window.innerHeight;
  bar.style.top = (below ? r.bottom + 6 : r.top - h - 6) + 'px';
  bar.style.left = Math.max(8, Math.min(r.left, window.innerWidth - bar.offsetWidth - 8)) + 'px';
}

document.addEventListener('focusin', e => {
  if (!editable(e.target)) return;
  target = e.target;
  bar.classList.remove('hidden');
  place();
});
document.addEventListener('focusout', e => {
  if (e.target !== target) return;
  setTimeout(() => {
    if (document.activeElement !== target) { bar.classList.add('hidden'); target = null; }
  }, 0);
});
window.addEventListener('scroll', place, true);
window.addEventListener('resize', place);
document.addEventListener('input', () => requestAnimationFrame(place));

// Keep focus in the field when a button is pressed (a blur would, e.g., remove an empty answer box).
bar.addEventListener('pointerdown', e => e.preventDefault());
bar.addEventListener('click', e => {
  const b = e.target.closest('[data-ch]');
  if (b) insert(b.dataset.ch);
});

document.addEventListener('keydown', e => {
  if (!e.altKey || e.ctrlKey || e.metaKey || !editable(e.target)) return;
  const ch = KEYS[e.code.replace('Key', '').toLowerCase()];
  if (!ch) return;
  e.preventDefault();
  target = e.target;
  insert(e.shiftKey && ch !== 'ß' ? ch.toUpperCase() : ch);
}, true);
