'use strict';
(function(input) {
input = input.trim().sprit(/\s+/).map(x => x - 0);
console.log(Math.floor((3 * input[0] + input[1]) / 2));
})(require('fs').readFileSync('/dev/stdin', 'utf8'));