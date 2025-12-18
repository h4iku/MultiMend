a = k = 0;
l = require('fs').readFileSync('/dev/stdin', 'utf8').split("\n");
l.shift();
l.forEach(j => {
  a = a > ~~j ? a : j;
  k += ~~j
});
k = k - a / 2;
console.log(k);