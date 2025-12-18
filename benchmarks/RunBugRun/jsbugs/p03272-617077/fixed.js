'use strict';

function main(arg) { console.log((arg.split(" ")[0] - arg.split(" ")[1]) + 1) }

main(require('fs').readFileSync('/dev/stdin', 'utf8'));