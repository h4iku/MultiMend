function Main(s) {
  s = s.split(/\s/);
  s.forEach(function(e, i, a) { a[i] = Number(a[i]); });
  var a = s[0] + s[1];
  var b = s[0] - s[1];
  var c = s[0] * s[1];
  a = a > b ? a : b;
  a = a > c ? a : c;
}
Main(require("fs").readFileSync("/dev/stdin", "utf8"));