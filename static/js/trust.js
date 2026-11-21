// Settings → Backups: the one-click "Export all my data" download (the flashcard retention choice is saved with
// the rest of the Settings form).
import { $, toast } from './core.js';

// The server builds the zip in a temporary file and streams it; the browser saves it like any download.
$('#export-all').addEventListener('click', () => {
  toast('Preparing your data. With many books this can take a moment...');
  window.location.href = '/api/export/all';
});
