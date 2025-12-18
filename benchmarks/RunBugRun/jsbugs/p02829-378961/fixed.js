// inputに入力データ全体が入る
function Main(input) {
  // 1行目がinput[0], 2行目がinput[1], …に入る
  input = input.split("\n");
  //文字列から10進数に変換するときはparseIntを使います
  var a = parseInt(input[0], 10);
  var b = parseInt(input[1], 10);
  if (a == 1 && b == 2) {
    console.log(3);
  } else if (a == 2 && b == 1) {
    console.log(3);
  } else if (a == 3 && b == 1) {
    console.log(2);
  } else if (a == 1 && b == 3) {
    console.log(2);
  } else {
    console.log(1);
  }
}
//*この行以降は編集しないでください（標準入出力から一度に読み込み、Mainを呼び出します）
Main(require("fs").readFileSync("/dev/stdin", "utf8"));