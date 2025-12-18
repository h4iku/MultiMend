a = [], m = l = n = c = 0;
require("fs")
    .readFileSync("/dev/stdin", "utf8")
    .trim()
    .split(' ')
    .map(function(i) {
      a[i] ? ++a[i] > m ? m = a[n = i] : 0 : a[i] = 1;
      (t = i.length) > l ? (c = i, l = t) : 0
    });
console.log(n + ' ' + c)