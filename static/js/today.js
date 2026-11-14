// Today page: stats, weekly chart, weak topics and the coach's daily plan.
import { $, S, api, esc, icon, md, busy, loading, registerView, show, updateNavStatus } from './core.js';
import { openReader } from './reader.js';
import { kittySvg, hopliteKittySvg } from './declensions.js';

const KIND = {
  reader: { label: 'Textbook', icon: 'reader' }, practice: { label: 'Practice', icon: 'practice' },
  flashcards: { label: 'Flashcards', icon: 'cards' }, mistakes: { label: 'Mistakes', icon: 'mistake' },
  declensions: { label: 'Declensions', icon: 'rocket' }, verbs: { label: 'Verbs', icon: 'spear' },
  video: { label: 'Video', icon: 'play' },
  listening: { label: 'Listening', icon: 'headphones' }, speaking: { label: 'Speaking', icon: 'mic' },
  writing: { label: 'Writing', icon: 'edit' }, other: { label: 'Activity', icon: 'target' },
};
const IN_APP = ['reader', 'practice', 'flashcards', 'mistakes', 'declensions', 'verbs', 'writing'];
const inApp = b => IN_APP.includes(b.kind) || !!b.media_id;

registerView('today', loadToday);

async function loadToday() {
  const hour = new Date().getHours();
  $('#today-greeting').textContent = hour < 4 ? 'Gute Nacht!' : hour < 11 ? 'Guten Morgen!' : hour < 18 ? 'Guten Tag!' : 'Guten Abend!';
  if (!$('#plan-minutes').value) $('#plan-minutes').value = S.settings.daily_minutes;
  const [st, plan] = await Promise.all([api('/stats'), api('/plan/today')]);
  // The study day (it runs until 4am), not the calendar date.
  $('#today-date').textContent = new Date(st.today.date + 'T12:00').toLocaleDateString(undefined, { weekday: 'long', day: 'numeric', month: 'long' });
  updateNavStatus(st);
  S.homeStats = st;
  renderSetup(plan);
  renderTiles(st);
  renderWeek(st.week);
  renderJourney(st.journey, st.verbs_journey);
  renderCalendar(st.calendar);
  renderWeak(st.weak_topics);
  renderPlan(plan);
}

function renderSetup(plan) {
  const steps = [
    { done: S.settings.has_key, title: 'Turn on AI features (optional)', text: 'Practice sets, marking, AI flashcards and the coach need a Claude API key. The dictionary, drills, flashcard packs and quick plans work without one.', go: 'settings', btn: 'Open Settings' },
    { done: S.books.length > 0, title: 'Import a textbook', text: 'Any PDF. Chapters are detected from its bookmarks.', go: 'library', btn: 'Go to Library' },
    { done: !!plan, title: 'Plan your first day', text: 'Use the form below.' },
  ];
  // Only for a brand-new copy: once there's a book, cards or a plan, Home's own cards say what to do next.
  if ((steps[0].done && steps[1].done) || S.books.length || S.homeStats?.cards.total || plan) { $('#setup').innerHTML = ''; return; }
  $('#setup').innerHTML = `<div class="panel setup"><h2>Get started</h2><ol>${steps.map(s => `
    <li class="${s.done ? 'done' : ''}"><span class="step-mark">${s.done ? icon('check') : ''}</span>
      <div><b>${s.title}</b><p class="muted small">${s.text}</p></div>
      ${!s.done && s.go ? `<button class="ghost small" data-go="${s.go}">${s.btn}</button>` : ''}</li>`).join('')}</ol></div>`;
}

function renderTiles(st) {
  const t = st.today, c = st.cards;
  const tile = (ic, v, label, sub = '') => `<div class="tile">${icon(ic)}<div><b>${v}</b><span>${label}</span>${sub ? `<small>${sub}</small>` : ''}</div></div>`;
  $('#stat-tiles').innerHTML =
    tile('clock', t.minutes, 'minutes studied', `${t.reading_minutes} read · ${t.practice_minutes} practice · ${t.listening_minutes} listen · ${t.flashcard_minutes} cards`) +
    tile('page', t.pages_read, 'pages read') +
    tile('practice', t.questions, 'questions answered', t.accuracy != null ? `${t.accuracy}% right` : '') +
    tile('cards', c.due + c.new_available, 'cards waiting', `${t.cards_reviewed} reviewed today`);
}

function renderWeek(week) {
  const goal = +S.settings.daily_minutes || 30;
  const max = Math.max(goal, ...week.map(d => d.minutes));
  const goalPx = Math.round((goal / max) * 100); // bar tracks are 100px tall
  $('#week-chart').innerHTML = `<div class="bars" style="--goal:${goalPx}px">${week.map((d, i) => {
    const day = new Date(d.date + 'T12:00');
    const h = d.minutes ? Math.max(4, (d.minutes / max) * 100) : 0;
    return `<div class="bar ${i === week.length - 1 ? 'today' : ''} ${d.minutes >= goal ? 'met' : ''}" title="${d.minutes} min on ${day.toLocaleDateString(undefined, { weekday: 'long' })}">
      <div class="bar-track"><span style="height:${h}%"></span></div><small>${day.toLocaleDateString(undefined, { weekday: 'narrow' })}</small></div>`;
  }).join('')}<div class="goal-line"><span>${goal} min goal</span></div></div>
  <p class="muted small">${week.reduce((a, d) => a + d.minutes, 0)} minutes in the last 7 days</p>`;
}

// One card per grammar course: where you are on the journey and what's next.
function journeyCard(j, { view, title, avatar, box, unit, label }) {
  return `<button class="journey-card" data-journey="${view}" title="${title}">
    <svg viewBox="${box}" class="dj-avatar">${avatar}</svg>
    <span class="grow"><small>${label} · ${j.planets_done} of ${j.planets_total} ${unit}</small>
      <b>${j.finished ? 'Mission complete' : esc(view === 'verbs' ? `${j.planet}: ${j.title}` : j.title)}</b>
      <span class="meter"><span class="meter-bar"><span style="width:${j.finished ? 100 : (100 * j.steps_done) / j.steps_total}%"></span></span>
        <span>${j.finished ? `★ ${j.stars}/${j.max_stars}` : j.next_step ? `next: ${j.next_step.toLowerCase()}` : ''}</span></span></span>${icon('right')}</button>`;
}

function renderJourney(j, v) {
  $('#today-journey').innerHTML = journeyCard(j, { view: 'decl', title: 'Open the Declensions map', avatar: kittySvg(), box: '-34 -27 68 60', unit: 'planets', label: 'Declensions' })
    + (v ? journeyCard(v, { view: 'verbs', title: 'Open the Verbs map', avatar: hopliteKittySvg(), box: '-36 -42 72 76', unit: 'regions', label: 'Verbs' }) : '');
}

// Twelve weeks of study days, one column per week (Monday at the top).
function renderCalendar(cal) {
  const goal = +S.settings.daily_minutes || 30;
  const level = d => !d.active ? 0 : d.minutes >= goal ? 4 : d.minutes >= goal * .6 ? 3 : d.minutes >= goal * .25 ? 2 : 1;
  const pad = (new Date(cal[0].date + 'T12:00').getDay() + 6) % 7;
  const cells = Array(pad).fill('<i class="pad"></i>').concat(cal.map((d, i) =>
    `<i class="l${level(d)} ${i === cal.length - 1 ? 'today' : ''}" title="${new Date(d.date + 'T12:00').toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'short' })}: ${d.minutes} min"></i>`));
  const days = cal.filter(d => d.active).length;
  $('#today-cal').innerHTML = `<div class="cal-grid">${cells.join('')}</div>
    <div class="cal-foot"><span class="muted small">${days} study day${days === 1 ? '' : 's'}</span>
      <span class="cal-legend muted small">less<i class="l1"></i><i class="l2"></i><i class="l3"></i><i class="l4"></i>goal met</span></div>`;
}

function renderWeak(topics) {
  $('#weak-topics').innerHTML = topics.length
    ? topics.map(w => `<button class="topic" data-mk-topic="${esc(w.topic)}" title="See these mistakes"><div class="topic-top"><span>${esc(w.topic)}</span><b>${w.accuracy}%</b></div>
        <div class="meter-bar ${w.accuracy < 60 ? 'bad' : w.accuracy < 80 ? 'mid' : ''}"><span style="width:${w.accuracy}%"></span></div></button>`).join('')
      + '<button class="link-btn" data-go="mistakes">Open Mistake Book →</button>'
    : '<p class="muted small">Answer some questions and the topics you struggle with show up here.</p>';
}

// ---------- plan ----------
function meter(label, v, t) {
  const pct = Math.min(100, Math.round(100 * v / t));
  return `<div class="meter ${pct >= 100 ? 'full' : ''}"><div class="meter-bar"><span style="width:${pct}%"></span></div><span>${v}/${t} ${label}</span></div>`;
}

function linkFor(b) {
  if (b.url) return `<a href="${esc(b.url)}" target="_blank" rel="noopener" class="ext">${icon('external')}${esc(b.url.replace(/^https?:\/\/(www\.)?/, '').slice(0, 60))}</a>`;
  if (!b.search_query) return '';
  const base = ['video', 'listening'].includes(b.kind) ? 'https://www.youtube.com/results?search_query=' : 'https://www.google.com/search?q=';
  return `<a href="${base + encodeURIComponent(b.search_query)}" target="_blank" rel="noopener" class="ext">${icon('external')}Search: ${esc(b.search_query)}</a>`;
}

function blockHtml(b, i) {
  const k = KIND[b.kind] || KIND.other;
  const p = b.progress || {};
  const meters = [
    b.target_pages && meter('pages', p.pages || 0, b.target_pages),
    b.target_questions && meter('questions', p.questions || 0, b.target_questions),
    b.target_cards && meter('cards', p.cards || 0, b.target_cards),
    b.minutes && meter('min', p.minutes || 0, b.minutes),
  ].filter(Boolean);
  const targets = [b.target_pages && `${b.target_pages} pages`, b.target_questions && `${b.target_questions} questions`, b.target_cards && `${b.target_cards} cards`].filter(Boolean);
  let actions;
  if (b.status === 'done' || b.status === 'skipped') actions = `<button data-act="reset" class="ghost small">${icon('undo')}Undo</button>`;
  else if (b.status === 'active') actions = `${inApp(b) ?`<button data-act="open" class="small">Continue</button>` : ''}<button data-act="done" class="small">${icon('check')}Done</button><button data-act="skip" class="link-btn">Skip</button>`;
  else actions = `<button data-act="start" class="small">${icon('play')}Start</button><button data-act="done" class="link-btn">Mark done</button><button data-act="skip" class="link-btn">Skip</button>`;
  return `<li class="block ${b.status} kind-${b.kind}" data-idx="${i}">
    <div class="block-mark">${b.status === 'done' ? icon('check') : i + 1}</div>
    <div class="block-main">
      <div class="block-head"><span class="chip">${icon(k.icon)}${k.label}</span>${b.auto_done ? `<span class="chip auto-done" title="All its targets were reached, so it was ticked off for you">${icon('check')}target reached</span>` : ''}<span class="muted small">${b.minutes} min${targets.length ? ' · ' + targets.join(' · ') : ''}</span></div>
      <h3>${esc(b.title)}</h3>
      <div class="block-body">${md(b.instructions)}${linkFor(b)}${b.why ? `<p class="why">${esc(b.why)}</p>` : ''}</div>
      ${b.progress && b.status !== 'skipped' ? `<div class="meters">${meters.join('')}</div>` : ''}
    </div>
    <div class="block-actions">${actions}</div></li>`;
}

// The top of Home: how far today's goal is, the next thing to do and one button that starts it.
function renderHero() {
  const st = S.homeStats, plan = S.plan;
  if (!st) return;
  const goal = +S.settings.daily_minutes || 30, done = st.today.minutes;
  const R = 26, C = 2 * Math.PI * R, part = Math.min(1, done / goal);
  const ring = `<svg class="goal-ring ${part >= 1 ? 'met' : ''}" viewBox="0 0 64 64" role="img" aria-label="${done} of ${goal} minutes">
    <circle cx="32" cy="32" r="${R}" class="track"/><circle cx="32" cy="32" r="${R}" class="fill" stroke-dasharray="${(C * part).toFixed(1)} ${C.toFixed(1)}" transform="rotate(-90 32 32)"/>
    <text x="32" y="37" text-anchor="middle">${done}</text></svg>`;
  const idx = plan ? plan.blocks.findIndex(b => b.status === 'active') : -1;
  const next = plan ? (idx >= 0 ? idx : plan.blocks.findIndex(b => b.status === 'todo')) : -1;
  let eyebrow = `Today · ${done} of ${goal} minutes`, title, text, btn;
  if (!plan) {
    title = 'Start today\'s session';
    text = 'A plan is put together from your flashcards, mistakes, book and courses.';
    btn = `<button id="hero-go" data-hero="plan">${icon('play')}<span>Start</span></button>`;
  } else if (next < 0) {
    title = 'Alles erledigt!';
    text = part >= 1 ? 'Today\'s plan is done and your goal is met.' : 'Today\'s plan is done. Anything extra is a bonus.';
    btn = `<button id="hero-go" class="ghost" data-hero="more">${icon('cards')}<span>Practice more</span></button>`;
  } else {
    const b = plan.blocks[next], k = KIND[b.kind] || KIND.other;
    eyebrow += ` · step ${next + 1} of ${plan.blocks.length}`;
    title = b.title;
    text = `${k.label} · ${b.minutes} min`;
    btn = `<button id="hero-go" data-hero="block" data-idx="${next}">${icon('play')}<span>${b.status === 'active' || next > 0 ? 'Continue' : 'Start'}</span></button>`;
  }
  $('#home-hero').innerHTML = `<div class="hero">${ring}<div class="grow"><p class="hero-eyebrow">${eyebrow}</p><h2>${esc(title)}</h2><p class="muted">${esc(text)}</p></div>${btn}</div>`;

  const c = st.cards, j = st.journey, bk = st.book;
  const card = (go, ic, t, sub) => `<button class="next-card" data-next="${go}">${icon(ic)}<span><b>${esc(t)}</b><small>${esc(sub)}</small></span></button>`;
  const waiting = c.due + c.new_available;
  $('#home-next').innerHTML =
    card('cards', 'cards', waiting ? `${waiting} cards waiting` : 'Flashcards', waiting ? `About ${Math.max(1, Math.round(waiting / 4))} min` : (c.total ? 'Nothing due right now' : 'Add a pack from the Library tab'))
    + card('decl', 'rocket', j.finished ? 'Declensions' : j.title, j.finished ? 'Course finished · free practice' : `Declensions · step ${Math.min(j.steps_done + 1, j.steps_total)} of ${j.steps_total}`)
    + (bk ? card('book', 'reader', bk.title, `Read on from page ${bk.page}`) : card('library', 'library', 'Add a textbook', 'Any PDF, read and practice inside the app'));
}

$('#home-hero').addEventListener('click', async e => {
  const b = e.target.closest('[data-hero]');
  if (!b) return;
  if (b.dataset.hero === 'more') { S.cardTab = 'review'; return show('cards'); }
  await busy(b, '', async () => {
    let plan = S.plan, idx = +b.dataset.idx;
    if (b.dataset.hero === 'plan') {
      plan = await api('/plan/quick', { method: 'POST', body: { minutes: +$('#plan-minutes').value || +S.settings.daily_minutes || 30 } });
      idx = plan.blocks.findIndex(x => x.status === 'todo');
      renderPlan(plan);
      if (idx < 0) return;
    }
    const bl = plan.blocks[idx];
    if (bl.status !== 'active') renderPlan(await api(`/plan/${plan.id}/blocks/${idx}`, { method: 'POST', body: { action: 'start' } }));
    openBlock(bl);
  });
});

$('#home-next').addEventListener('click', e => {
  const n = e.target.closest('[data-next]')?.dataset.next;
  if (!n) return;
  if (n === 'book') return openReader(S.homeStats.book.id, S.homeStats.book.page);
  if (n === 'cards') S.cardTab = 'review';
  if (n === 'decl') S.declTab = 'journey';
  show(n);
});

function renderPlan(plan) {
  S.plan = plan;
  renderHero();
  $('#plan-form button[type=submit] span').textContent = plan ? 'New plan' : 'Plan my day';
  if (!plan) {
    $('#plan-meta').textContent = 'A session built from your progress, weak spots and flashcards.';
    $('#plan').innerHTML = `<div class="plan-empty">${icon('sparkles')}<p>No plan yet today. Set your time and press <b>Plan my day</b>, or <b>Quick plan</b> for an instant one without AI.</p></div>`;
    return;
  }
  const done = plan.blocks.filter(b => b.status === 'done').length;
  const total = plan.blocks.reduce((a, b) => a + (b.minutes || 0), 0);
  const left = plan.blocks.filter(b => !['done', 'skipped'].includes(b.status)).reduce((a, b) => a + (b.minutes || 0), 0);
  $('#plan-meta').innerHTML = `${plan.quick ? '<span class="chip">Quick plan · no AI</span> ' : ''}${total} min · ${done} of ${plan.blocks.length} done${left && left < total ? ` · <b>${left} min left</b>` : ''}`;
  $('#plan').innerHTML = `<div class="plan-progress"><span style="width:${(100 * done) / plan.blocks.length}%"></span></div>
    <div class="plan-summary">${md(plan.summary)}</div>
    <ol class="blocks">${plan.blocks.map(blockHtml).join('')}</ol>
    ${done === plan.blocks.length ? `<div class="plan-done">${icon('check')}<b>Alles erledigt!</b> Everything on today's plan is done. Sehr gut!</div>` : ''}`;
}

$('#weak-topics').addEventListener('click', e => {
  const t = e.target.closest('[data-mk-topic]');
  if (!t) return;
  if (t.dataset.mkTopic.startsWith('Declensions')) { S.declTab = 'free'; return show('decl'); }
  if (t.dataset.mkTopic.startsWith('Verbs')) { S.verbsTab = 'free'; return show('verbs'); }
  S.mistakeTopic = t.dataset.mkTopic;
  show('mistakes');
});

$('#today-journey').addEventListener('click', e => {
  const c = e.target.closest('[data-journey]');
  if (c) { const view = c.dataset.journey || 'decl'; S[view + 'Tab'] = 'journey'; show(view); }
});

$('#plan').addEventListener('click', async e => {
  const btn = e.target.closest('button[data-act]');
  if (!btn) return;
  const idx = +btn.closest('.block').dataset.idx;
  const act = btn.dataset.act;
  const b = S.plan.blocks[idx];
  if (act === 'open') return openBlock(b);
  await busy(btn, '', async () => {
    renderPlan(await api(`/plan/${S.plan.id}/blocks/${idx}`, { method: 'POST', body: { action: act } }));
    if (act === 'start') openBlock(b);
  });
});

function openBlock(b) {
  if (b.sub === 'gaps') { S.practiceTabWant = 'gaps'; S.gapChapterWant = b.chapter_id ? String(b.chapter_id) : null; return show('practice'); }
  if (b.kind === 'declensions' && b.sub) { S.declSub = b.sub === 'free' ? 'drill' : b.sub; return show('decl'); }
  if (b.kind === 'verbs' && b.sub) { S.verbsTab = 'free'; return show('verbs'); }
  if (b.kind === 'reader') openReader(b.book_id, b.start_page || null);
  else if (b.kind === 'practice') { S.practiceChapter = b.chapter_id; show('practice'); }
  else if (b.kind === 'flashcards') { S.cardTab = 'review'; show('cards'); }
  else if (b.kind === 'mistakes') show('mistakes');
  else if (b.kind === 'declensions') show('decl');
  else if (b.kind === 'verbs') show('verbs');
  else if (b.kind === 'writing') { S.writingTask = { id: 'plan-' + S.plan.id, title: b.title, kind: 'From your plan', task: b.instructions, level: S.settings.level }; show('writing'); }
  else if (b.media_id) { S.listenMedia = b.media_id; show('listening'); }
  else if (b.url) window.open(b.url, '_blank', 'noopener');
}

$('#plan-quick').addEventListener('click', e => busy(e.currentTarget, 'Planning...', async () => {
  renderPlan(await api('/plan/quick', { method: 'POST', body: { minutes: +$('#plan-minutes').value } }));
}));

$('#plan-form').addEventListener('submit', e => {
  e.preventDefault();
  $('#plan').innerHTML = loading('Your coach is looking at your progress and planning today. This can take up to a minute...');
  busy($('#plan-form button[type=submit]'), 'Planning...', async () => {
    try {
      renderPlan(await api('/plan/generate', { method: 'POST', body: { minutes: +$('#plan-minutes').value, note: $('#plan-note').value } }));
      $('#plan-note').value = '';
    } catch (err) { renderPlan(S.plan); throw err; }
  });
});
