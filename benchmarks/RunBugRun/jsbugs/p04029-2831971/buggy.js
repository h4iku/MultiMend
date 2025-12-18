// inputに入力データ全体が入る
function Main(input) {
  input = input.split(" ");
  //文字列から10進数に変換するときはparseIntを使います
  var a = parseInt(input[0], 10);
  var half = a / 2;
  var roundHalf = Math.round(half);
  var total = 0;
  //出力
  if (parseInt(half, 10) === half) {
    total = (1 + a) * half;
    console.log(total);
  } else {
    total = (1 + a) * (roundHalf - 1);
    total += roundHalf;
  }
  console.log(total);
}
//*この行以降は編集しないでください（標準入出力から一度に読み込み、Mainを呼び出します）
Main(require("fs").readFileSync("/dev/stdin", "utf8"));