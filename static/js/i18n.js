// App language (English / Turkish).
//
// The app is written in English. When Turkish is picked, every piece of English text that appears on screen
// (static HTML, anything the pages render later, toasts, tooltips and placeholders) is swapped for its Turkish
// version from i18n/tr.js. A MutationObserver catches text as it is added, so page code doesn't need changes.
//
// Dictionary keys are the English text exactly as it appears in one text node (whitespace collapsed).
// "{}" in a key matches any text; the translation can put it back with {1}, {2}, ... in any order.
// Text without an entry stays English, so a missing translation never breaks anything.
import TR from '../i18n/tr.js';

const DICTS = { tr: TR };
const KEY = 'ui_lang';
const ATTRS = ['title', 'placeholder', 'aria-label'];
// Never translate the textbook, things the learner typed, or code.
const SKIP = 'script, style, textarea, code, pre, [contenteditable], [data-no-i18n], .textLayer, .tbox';

function stored() { try { return localStorage.getItem(KEY); } catch { return null; } }

export const lang = DICTS[stored()] ? stored() : 'en';

/** Switch language (saved in the browser for an instant start) and reload so everything is redrawn. */
export function setLanguage(l) {
  try { localStorage.setItem(KEY, DICTS[l] ? l : 'en'); } catch { /* storage unavailable */ }
  location.reload();
}

/** Call once settings are loaded: the server's setting wins if it differs from the browser's copy. */
export function syncLanguage(serverLang) {
  const l = DICTS[serverLang] ? serverLang : 'en';
  if (l !== lang) setLanguage(l);
}

const dict = DICTS[lang];
const exact = new Map();
const patterns = [];
if (dict) {
  const norm = s => s.replace(/\s+/g, ' ').trim();
  for (const [k, v] of Object.entries(dict)) {
    const key = norm(k);
    if (!key.includes('{}')) { exact.set(key, v); continue; }
    const re = key.split('{}').map(p => p.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('(.*?)');
    patterns.push([new RegExp('^' + re + '$', 's'), v, key.replace(/\{\}/g, '').length]);
  }
  patterns.sort((a, b) => b[2] - a[2]);  // most specific (most literal text) first
}

/** Translate one string. Returns it unchanged when there's no entry. */
export function t(s) {
  if (!dict || s == null) return s;
  const str = String(s);
  const core = str.replace(/\s+/g, ' ').trim();
  if (!core || !/[A-Za-z]/.test(core)) return str;
  let out = exact.get(core);
  if (out === undefined) {
    for (const [re, v] of patterns) {
      const m = core.match(re);
      if (m) { out = v.replace(/\{(\d)\}/g, (_, i) => m[+i] ?? ''); break; }
    }
  }
  if (out === undefined) return str;
  const lead = str.match(/^\s*/)[0], trail = str.match(/\s*$/)[0];
  return lead + out + trail;
}

function skip(el) { return el && el.closest && el.closest(SKIP); }
// A text box's own placeholder/tooltip is app text even though what's typed inside it is not.
const SKIP_ATTRS = '[contenteditable], [data-no-i18n], .textLayer, .tbox';

function doText(node) {
  if (skip(node.parentElement)) return;
  const v = t(node.nodeValue);
  if (v !== node.nodeValue) node.nodeValue = v;
}

function doAttrs(el) {
  if (el.closest(SKIP_ATTRS)) return;
  for (const a of ATTRS) {
    const v = el.getAttribute(a);
    if (v) { const n = t(v); if (n !== v) el.setAttribute(a, n); }
  }
}

function walk(root) {
  if (root.nodeType === 3) return doText(root);
  if (root.nodeType !== 1) return;
  doAttrs(root);
  if (skip(root)) return;
  const it = document.createTreeWalker(root, NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT);
  for (let n = it.nextNode(); n; n = it.nextNode()) {
    if (n.nodeType === 3) doText(n); else doAttrs(n);
  }
}

if (dict) {
  document.documentElement.lang = lang;
  // Dates and times follow the app language too (pages call toLocale...String(undefined, ...)).
  const loc = { tr: 'tr-TR' }[lang];
  for (const fn of ['toLocaleDateString', 'toLocaleTimeString', 'toLocaleString']) {
    const orig = Date.prototype[fn];
    Date.prototype[fn] = function (l, o) { return orig.call(this, l ?? loc, o); };
  }
  const start = () => {
    walk(document.body);
    document.title = t(document.title);
    new MutationObserver(muts => {
      for (const m of muts) {
        if (m.type === 'characterData') doText(m.target);
        else if (m.type === 'attributes') doAttrs(m.target);
        else m.addedNodes.forEach(walk);
      }
    }).observe(document.body, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ATTRS });
  };
  if (document.body) start(); else document.addEventListener('DOMContentLoaded', start);
}
