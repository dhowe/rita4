#!/usr/bin/env node
/**
 * Generates JS-module-format dict files for js/ and java/ from the canonical
 * shared/rita_dict.json. Run after updating shared/rita_dict.json.
 *
 *   node scripts/gen-dicts.js
 */

import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { join, dirname } from 'path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const data = JSON.parse(readFileSync(join(root, 'shared', 'rita_dict.json'), 'utf8'));
const body = JSON.stringify(data, null, 2);

const targets = [
  {
    path: join(root, 'js', 'src', 'rita_dict.js'),
    content: `/** @type {object} */\nexport default ${body};\n`,
  },
  {
    path: join(root, 'java', 'src', 'main', 'resources', 'rita', 'rita_dict.js'),
    content: `export default ${body};\n`,
  },
];

for (const { path, content } of targets) {
  writeFileSync(path, content, 'utf8');
  console.log(`Written: ${path}`);
}
