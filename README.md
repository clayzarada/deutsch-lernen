# Deutsch lernen

**Made by Clay Zarada · © 2026 Zarada Holdings Group. All rights reserved.** See [LICENSE](LICENSE).

A local study app for German textbooks: read your PDFs, write answers on the pages, get them marked, generate practice sets and flashcards per chapter, and let an AI coach plan your study days.

## Start it

Double-click the **Deutsch lernen** icon on your Desktop (it's also in the Start menu; right-click it there to pin it to the taskbar). The app opens in its own window; closing the window stops the app.

If the icon is missing or you moved the folder, right-click `make_shortcut.ps1` → **Run with PowerShell** to recreate it.

**`start.bat`** still works too. Use it after updates (it installs any new Python packages) or if something goes wrong, since its black window shows error messages. With start.bat the app opens in your normal browser at http://127.0.0.1:8777, and you close the black window to stop it.

Then:
1. **Settings**: paste your Claude API key (from https://console.anthropic.com), set your level and goal.
2. **Library**: Import PDF. Check the chapter page ranges; they're read from the PDF's bookmarks when it has them.
3. **Today**: press **Plan my day**.

## What's where

| Page | What it does |
|---|---|
| Today | Today's stats, the coach's plan with live progress bars, your weak topics |
| Library | Import PDFs, edit chapters, export a PDF with your answers written in |
| Reader | Read the book. Tools: **Read** (select a word to look it up, explain or make a card), **Type** (click to type an answer on the page), **Pen** (write by hand, works with a stylus), **Highlight**, **Erase**. **Check answers on this page** sends the page with your writing to Claude for marking |
| Practice | AI-written exercise sets per chapter, graded with explanations |
| Flashcards | Spaced-repetition review in the app, browse/edit cards, generate cards per chapter, export to Anki |
| Listening | German dialogues, podcasts or stories made from a chapter at your level (Claude writes, Google Gemini voices), with transcript, translation, vocabulary and questions. Also holds audio you import |
| Declensions | A guided course for cases and endings, laid out as a space map: eleven planets unlocked in order (Nominativ, Akkusativ, Dativ, two-way prepositions, ein-words, Genitiv, three adjective stages, pronouns, final mix). Each planet has a briefing, charts to fill in, a drill, a reading with gaps, flashcards and a checkpoint; passing the checkpoint unlocks the next planet, and you can take it straight away to test out. Free practice has the smart drill, 60-second sprints and every table. Rule-based, so it is instant and needs no API key (only freshly written readings use Claude) |
| Verbs | A guided course for verb forms on a map of Alexander's march: Präsens (Hellas), Perfekt (Anatolien), Futur I (Phönizien), modal verbs (Ägypten), Präteritum (Syrien), Plusquamperfekt (Persien), Konjunktiv II (Baktrien), Futur II (Indus), then an endless mixed stop (Babylon). Same steps as Declensions. Free practice drills about 180 common verbs: conjugation, sentences with a time word, haben or sein, Partizip II and principal parts, with tables for every tense and strong verbs grouped by vowel pattern. A Word order tab builds sentences from word tiles (verb second, inversion, the verb bracket, separable verbs, verb last after weil/dass, questions). Rule-based, instant, no API key needed |
| Writing | Exam-style writing tasks (B1, B2, C1), the writing task from today's plan, or your own topic. Claude marks the text like the Goethe writing paper (task, coherence, vocabulary, grammar), marks every error in your text, and adds the corrections to the Mistake Book |
| Mistakes | Your *Fehlerheft*: every wrong answer from practice sets and checked pages, grouped by topic and counted when repeated. Select some to get a fresh drill on the same rules, turn them into "fix the mistake" flashcards, or mark them learned |
| Coach | Chat with your study coach. It sees all your progress data, including your Mistake Book |
| Resources | Your favorite channels, podcasts and sites. The coach uses them when planning |

**Umlauts:** whenever you type anywhere in the app (including answers on a PDF page), a small **ä ö ü ß Ä Ö Ü** bar appears under the field. Or use **Alt+A / Alt+O / Alt+U / Alt+S** for ä ö ü ß, and add **Shift** for capitals.

Reader keyboard shortcuts: ←/→ change page, R/T/P/H/E switch tools, Ctrl+Z undo your last writing.

**Hear it:** with a Google Gemini key, select text in the Reader and press *Hear it*, or press the speaker icon on flashcards, vocabulary and transcript lines.

## Gemini Notebook

The ✨ button on a book (Library) or **Gemini Notebook** in the Reader's chapter panel opens a 3-step helper:
1. Download the chapter as a PDF and add it to a notebook in Gemini Notebook.
2. Copy ready-made prompts (flashcards, quiz, Audio Overview, study guide) tuned to your level.
3. Paste or upload what Gemini Notebook made: flashcards and quizzes become cards and practice sets here, and downloaded Audio Overviews go to Listening.

To bring documents *out* of Gemini Notebook, get the originals from Google Drive or your computer, or export everything with Google Takeout (choose NotebookLM). Takeout gives the sources as HTML text, which the Library imports and turns into PDFs.

## How progress is tracked

- **Pages read**: time spent on a page with the reader open and you active (20 seconds or more counts as read).
- **Questions**: every practice answer and every answer marked by "Check answers on this page".
- **Cards**: every flashcard review.

When you press **Start** on a plan block, its progress bars count everything you do from then on.

## Your data

Everything stays on this computer, in the `data` folder: `study.db` holds your progress, cards and writing, and `books` holds the PDFs. Back up that folder to keep your work. The API key is stored in `.env`.

## How the code is organized

| Folder / file | What's in it |
|---|---|
| `app/main.py` | The web server: every `/api/...` route |
| `app/ai.py` | All Claude API calls and their prompts |
| `app/tts.py` | Google Gemini text-to-speech (listening episodes, "hear it") |
| `app/planner.py` | Stats, streaks, and the coach's daily plans |
| `app/pdfs.py` | Chapter detection, page text, cover thumbnails, exporting your answers into a PDF |
| `app/srs.py` | Flashcard scheduling |
| `app/anki.py` | Anki export |
| `app/db.py` | Database tables and settings |
| `static/js/` | One file per page (`today.js`, `reader.js`, ...) plus `core.js` with shared helpers |
| `static/style.css` | All styling. Colors are defined at the top. The app follows your system's light/dark mode |

## Costs

AI features use your Claude API key and are billed per use. Generating a practice set or a set of cards for one chapter costs a few cents on the default model. You can pick a cheaper model in Settings.

## Free practice without AI
A built-in German dictionary (from Wiktionary, about 78,000 words, works offline) powers practice that costs nothing:
- **Reader look-ups**: select a word for its gender, plural, forms and meanings instantly. "Explain it in this sentence"
  asks the AI only when you want it.
- **Practice > Gap-fills from the book**: real sentences from a chapter with an article, adjective ending or verb form
  to fill in, marked against what the book printed.
- **Flashcards > Words from the chapter**: the chapter's vocabulary in order, with gender, plural and an example
  sentence from the book, turned into cards in one click.
- **Declensions > Free practice > Nouns**: der/die/das and plurals for the 8,500 most common nouns, most common first.
- **Declensions > Free practice > Numbers**: numbers, clock times, dates, prices and years, read and written, with an
  optional listening mode that uses the computer's own German voice.
- **Flashcards > Library**: ready-made packs (everyday phrases, the 1,000 most common nouns, core verbs and
  adjectives, ten topics, irregular verbs, dative verbs, verbs with prepositions, prepositions by case, false friends).
- **Flashcards > Anki > Import from Anki**: .apkg and .colpkg decks (old and new Anki formats) and Anki's plain-text
  export. Text and cloze cards come across, and learned cards keep their Anki intervals.
- **Learn > Course**: a built-in beginner course (A1, 12 lessons so far). Each lesson has new words, a short
  dialogue, one grammar point and a quiz, and its words can go straight into your flashcards. The lessons live in
  `app/lessons_data.py`.
- **Welcome setup**: on first start the app asks your level, how you want to learn (the course, your own textbook
  or both), a daily goal and which starter flashcards you want. No API key or textbook is needed to begin.
- **Today > Quick plan**: an instant daily plan built from your flashcards, mistakes, book and grammar courses by
  simple rules, with the same live progress as the coach's plan.

The dictionary is rebuilt with `python tools/make_dictionary.py <kaikki German .jsonl.gz> <de_50k.txt>`
(sources and license in `static/vendor/dict/SOURCES.txt`).

## Costs and backups
Settings shows an estimate of what the AI features cost this month, by feature, and lets you set a monthly budget that pauses Claude features once it's reached. The app also backs up your data once a day (the last 14 are kept in `data/backups`); Settings lists them and can restore one. "Save backup file" puts everything (progress, cards, answers, books and audio, but never your API keys) into one .zip to keep or move to another computer; "Load backup file" brings it back.

## Releases
Publishing a GitHub release (`gh release create vX.Y.Z --title ... --notes ...`, no files) starts `.github/workflows/release.yml`: it runs the tests, then builds and attaches the Windows app, the Mac installer kit and the ready-made Mac apps. `version.json` must already say X.Y.Z with a current fingerprint. The tests (`python -m pytest tests`, needs `requirements-dev.txt`) also run on every push.

## License

© 2026 Zarada Holdings Group. Created by Clay Zarada. All rights reserved: you may use the released app for personal learning, but not copy, modify, redistribute or sell it without written permission. See [LICENSE](LICENSE).
