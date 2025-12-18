// inputに入力データ全体が入る
function Main(input) {
  input = input.split("\n");
  N = Number(input[0]);
  　input.shift();
  P = input
  var max = 0;
  var x;
  var sum = 0;
  for (i of P) {
    if (max < i) {
      x = i / 2
      max = i;
    }
    sum += Number(i)
  }
  sum -= x
  console.log(sum)
}
//*この行以降は編集しないでください（標準入出力から一度に読み込み、Mainを呼び出します）
Main(require("fs").readFileSync("/dev/stdin", "utf8"));