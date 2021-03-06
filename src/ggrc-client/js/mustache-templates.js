/*
    Copyright (C) 2019 Google Inc.
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

GGRC.Templates = GGRC.Templates || {};
GGRC.mustache_path = '/static/mustache';

let mustacheTemplates = require.context('./mustache/', true, /\.mustache/);

let prefix = './';
let postfix = '.mustache';

mustacheTemplates.keys().forEach((key) => {
  let prefixPos = key.indexOf(prefix);
  let postfixPos = key.lastIndexOf(postfix);

  let newKey = key.slice(prefixPos + prefix.length, postfixPos);

  GGRC.Templates[newKey] = mustacheTemplates(key);
});
