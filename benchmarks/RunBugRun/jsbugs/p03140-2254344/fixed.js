// inputに入力データ全体が入る
function Main(input) {
  input = input.split("\n");
  N = parseInt(input[0]);
  answer = 0;
  moto_word = [];
  for (i = 0; i < N; i++) {
    answer += new Set([ input[1][i], input[2][i], input[3][i] ]).size - 1
  }
  console.log('%d', answer);
}
//*この行以降は編集しないでください（標準入出力から一度に読み込み、Mainを呼び出します）
Main(require("fs").readFileSync("/dev/stdin", "utf8"));
