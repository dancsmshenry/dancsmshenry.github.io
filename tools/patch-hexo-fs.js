#!/usr/bin/env node
'use strict';

/**
 * Node 24 compatibility patch for hexo-fs 1.x.
 *
 * hexo-fs passes its options object as the `mode` argument to fs.copyFile:
 *
 *   copyFile(src, dest, options)
 *
 * Node 24 validates that argument and throws:
 *
 *   TypeError: mode must be int32 or null/undefined
 *
 * This breaks `hexo deploy` while copying public/ into .deploy_git, leaving
 * the deploy directory empty. Normalize non-numeric mode values to 0.
 *
 * The script is idempotent and safe to run from npm's postinstall hook.
 */

const fs = require('fs');
const path = require('path');

const file = path.join(__dirname, '..', 'node_modules', 'hexo-fs', 'lib', 'fs.js');

const OLD = [
  'function copyFile(src, dest, flags, callback) {',
  "  if (!src) throw new TypeError('src is required!');",
  "  if (!dest) throw new TypeError('dest is required!');",
  '  if (typeof flags === \'function\') {',
  '    callback = flags;',
  '  }',
  '',
  '  return checkParent(dest).then(() => _copyFile(src, dest, flags)).asCallback(callback);',
  '}'
].join('\n');

const NEW = [
  'function copyFile(src, dest, flags, callback) {',
  "  if (!src) throw new TypeError('src is required!');",
  "  if (!dest) throw new TypeError('dest is required!');",
  '  if (typeof flags === \'function\') {',
  '    callback = flags;',
  '    flags = 0;',
  '  } else if (flags && typeof flags === \'object\') {',
  '    // Node 24: hexo-fs passes an options object as the copy mode.',
  '    flags = 0;',
  '  }',
  '',
  '  return checkParent(dest).then(() => _copyFile(src, dest, flags)).asCallback(callback);',
  '}'
].join('\n');

if (!fs.existsSync(file)) {
  console.warn('[patch-hexo-fs] hexo-fs is not installed, skipping.');
  process.exit(0);
}

const source = fs.readFileSync(file, 'utf8');

if (source.includes('Node 24: hexo-fs passes an options object as the copy mode.')) {
  console.log('[patch-hexo-fs] Already patched.');
  process.exit(0);
}

if (!source.includes(OLD)) {
  console.warn('[patch-hexo-fs] Expected hexo-fs copyFile code was not found; skipping.');
  process.exit(0);
}

fs.writeFileSync(file, source.replace(OLD, NEW));
console.log('[patch-hexo-fs] Patched hexo-fs copyFile for Node 24.');
