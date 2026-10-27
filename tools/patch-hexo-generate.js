#!/usr/bin/env node
'use strict';

/**
 * Node 14+ (including Node 24) compatibility patch for Hexo 3.9.
 *
 * Hexo 3.9's generate command defines its own CacheStream.destroy() that clears
 * the buffered output. Node's stream autoDestroy calls that method before
 * generate.js reads the buffer, so every generated file is written as 0 bytes.
 *
 * This script renames the custom destructor to destroyCache() and updates the
 * explicit call site, leaving the native stream destroy() untouched.
 *
 * It is idempotent and safe to run from npm's postinstall hook.
 */

const fs = require('fs');
const path = require('path');

const file = path.join(
  __dirname,
  '..',
  'node_modules',
  'hexo',
  'lib',
  'plugins',
  'console',
  'generate.js'
);

const OLD_PROTOTYPE = [
  'CacheStream.prototype.destroy = function() {',
  '  this._cache.length = 0;',
  '};'
].join('\n');

const NEW_PROTOTYPE = [
  'CacheStream.prototype.destroyCache = function() {',
  '  this._cache.length = 0;',
  '};'
].join('\n');

const OLD_CALL = 'cacheStream.destroy();';
const NEW_CALL = 'cacheStream.destroyCache();';

if (!fs.existsSync(file)) {
  console.warn('[patch-hexo-generate] hexo is not installed, skipping.');
  process.exit(0);
}

let source = fs.readFileSync(file, 'utf8');
let changed = false;

if (source.includes(OLD_PROTOTYPE)) {
  source = source.replace(OLD_PROTOTYPE, NEW_PROTOTYPE);
  changed = true;
} else if (!source.includes(NEW_PROTOTYPE)) {
  console.warn(
    '[patch-hexo-generate] Expected Hexo 3.9 CacheStream code was not found; ' +
    'skipping. Check whether the installed Hexo version already fixes this.'
  );
  process.exit(0);
}

if (source.includes(OLD_CALL)) {
  source = source.replace(OLD_CALL, NEW_CALL);
  changed = true;
}

if (!changed) {
  console.log('[patch-hexo-generate] Already patched.');
  process.exit(0);
}

fs.writeFileSync(file, source);
console.log('[patch-hexo-generate] Patched Hexo 3.9 generate for Node 14+ stream autoDestroy.');
