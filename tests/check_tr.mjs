// Used by tests/test_tr_js.py: loads static/i18n/tr.js as a module (like the browser) and lists repeated keys.
import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

const path = process.argv[2];
const src = readFileSync(path, 'utf8');
const seen = new Map();
for (const m of src.matchAll(/^\s*('(?:[^'\\]|\\.)*'|"(?:[^"\\]|\\.)*")\s*:/gm)) seen.set(m[1], (seen.get(m[1]) || 0) + 1);
const mod = await import(pathToFileURL(path).href);
console.log(JSON.stringify({ n: Object.keys(mod.default).length, dupes: [...seen].filter(([, n]) => n > 1).map(([k]) => k) }));
