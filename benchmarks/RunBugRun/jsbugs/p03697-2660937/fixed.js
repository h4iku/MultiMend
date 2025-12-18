function Main(input) {

  var r;

  input = input.split("\n");

  var line = input[0].split(" ");

  r = parseInt(line[0], 10) + parseInt(line[1], 10)

  if (r >= 10)
  r = "error"

  console.log(r);
}

//*この行以降は編集しないでください（標準入出力から一度に読み込み、Mainを呼び出します）
Main(require("fs").readFileSync("/dev/stdin", "utf8"));