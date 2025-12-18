'use strict'
let x = require('fs').readFileSync('/dev/stdin', 'utf-8');
console.log(x + x * x + x * x * x);
