a = [], m = l = 0, n = c = '';
require("fs")
    .readFileSync("/dev/stdin", "utf8")
    .trim()
    .split(' ')
    .some(function(i) {
      a[i] ? (++a[i] > m ? m = a[n = i] : 0) : a[i] = 1;
      (t = i.length) > l ? (c = j, l = t) : 0
    });
console.log(n + ' ' + c)