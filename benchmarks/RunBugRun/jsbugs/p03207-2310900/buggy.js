// inputに入力データ全体が入る
function Main(input) {
  var N = input.split('\n')[0];
  var p = input.split('\n');
  p.shift();
  p = p.map(v => parseInt(v));
  var max = Math.max(...p);
  p.splice(p.indexOf(max), 1);
  var sum = 0;
  p.forEach(v => sum += v);
  sum += max / 2;
  console.log(sum);
}

// ※この行以降は編集しない (標準入力から一度に読み込みMainを呼び出します)
Main(require("fs").readFileSync("/dev/stdin", "utf8"));