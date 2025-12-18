// inputに入力データ全体が入る
function Main(input) {
  // 1行目がinput[0], 2行目がinput[1], …に入る
  input = input.split("\n");
  var line1 = input[0].split(" ");
  var n = line1[0], k = line1[1];
  var h = input[1].split(" ");
  var count = 0;
  h.forEach((x) => {
    if (x >= k)
      count++;
  });
  //出力
  console.log(count);
}
//*この行以降は編集しないでください（標準入出力から一度に読み込み、Mainを呼び出します）
Main(require("fs").readFileSync("/dev/stdin", "utf8"));