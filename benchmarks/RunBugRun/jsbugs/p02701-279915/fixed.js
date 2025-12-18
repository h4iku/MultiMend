const main = input => new Set(input.trim().split("\n").slice(1)).size

console.log(main(require('fs').readFileSync('/dev/stdin', 'utf8')));