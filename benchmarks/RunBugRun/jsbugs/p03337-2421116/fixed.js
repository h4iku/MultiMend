function Main(s) {
  s = s.split(/\n|\s/);
  s.forEach(function(e, i, a) { a[i] = Number(a[i]); });
  var a = s[0] + s[1];
  var b = s[0] - s[1];
  var c = s[0] * s[1];
  a = a > b ? a : b;
  a = a > c ? a : c;

  console.log(a | 0);
}
Main(require("fs").readFileSync("/dev/stdin", "utf8"));