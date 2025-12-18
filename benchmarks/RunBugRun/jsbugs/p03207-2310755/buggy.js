a = k = 0;
require('fs')
    .readFileSync('/dev/stdin', 'utf8')
    .split("\n")
    .shift()
    .forEach((j) => {
      a = a > ~~j ? a : j;
      k += ~~j
    });
k = k - a / 2;
console.log(k);