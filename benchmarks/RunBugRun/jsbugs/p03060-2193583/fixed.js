function Main(input) {
  input = input.split("\n");
  var n = parseInt(input[0], 10);
  var v = input[1].split(" ");
  var c = input[2].split(" ");
  var t = [];
  var a = 0;
  for (var i = 0; i < n; i++) {
    t.push(v[i] - c[i]);
  }
  t.sort(function(a, b) { return (a < b ? 1 : -1); });
  for (var i = 0; i < n; i++) {
    if (t[i] > 0) {
      a += t[i];
    }
  }
  console.log('%d', a);
}
//*この行以降は編集しないでください（標準入出力から一度に読み込み、Mainを呼び出します）
Main(require("fs").readFileSync("/dev/stdin", "utf8"));