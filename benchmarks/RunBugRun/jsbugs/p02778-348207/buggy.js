function Main(input) {
  input = input.split("");
  let result = "";
  for (let i = 0; i < input.length; i++) {
    result += "x";
  }

  console.log(result);
}
//*この行以降は編集しないでください（標準入出力から一度に読み込み、Mainを呼び出します）
Main(require("fs").readFileSync("/dev/stdin", "utf8"));