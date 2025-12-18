'use strict'
let x = parseInt(require('fs').readFileSync('/dev/stdin', 'utf-8'));
console.log(x + x * x + x * x * x);
