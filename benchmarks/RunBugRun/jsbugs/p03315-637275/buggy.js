// inputに入力データ全体が入る
function Main(input) {
  // 1行目がinput[0], 2行目がinput[1], …に入る
  // input = input.split("\n");
  ans = 0
  input = input.split("");
  input.forEach(function(i) {
    if (i === '-') {
      ans--
    } else {
      ans++
    }
  })

  // s = input[0].split(' ').map((n) => (parseInt(n)))[1]
  // input = input[1].split(' ').map((n) => (parseInt(n)))
  // ans = input.filter((n) => (s <= n)).length

  //出力
  console.log(ans)
}
//*この行以降は編集しないでください（標準入出力から一度に読み込み、Mainを呼び出します）
Main(require("fs").readFileSync("/dev/stdin", "utf8"));
// Main(require('fs').readFileSync('./input.txt', 'utf-8'));