// Day/night toggle. The starting theme is set in index.html before the page draws;
// until you click the button, the app follows your system's light/dark setting.
import { $, icon, store } from './core.js';

const root = document.documentElement;
const btn = $('#theme-toggle');

function showIcon() {
  const dark = root.dataset.theme === 'dark';
  btn.innerHTML = icon(dark ? 'today' : 'moon');
  btn.title = dark ? 'Switch to day mode' : 'Switch to night mode';
}

function apply(theme) {
  root.classList.add('theme-switching');
  root.dataset.theme = theme;
  showIcon();
  setTimeout(() => root.classList.remove('theme-switching'), 300);
}

btn.addEventListener('click', () => {
  const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
  store.set('theme', next);
  apply(next);
});

matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
  if (!store.get('theme')) apply(e.matches ? 'dark' : 'light');
});

showIcon();
