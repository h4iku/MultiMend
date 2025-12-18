// inputに入力データ全体が入る
function Main(input) {

  // 1行目がinput[0], 2行目がinput[1], …に入る
  input = input.split("\n");

  line = input[0].split(" ");

  var r;

  r = line[0] + line[1]

      if (r >= 10)
  r = "error"

  console.log(r);
}

//*この行以降は編集しないでください（標準入出力から一度に読み込み、Mainを呼び出します）
Main(require("fs").readFileSync("/dev/stdin", "utf8"));