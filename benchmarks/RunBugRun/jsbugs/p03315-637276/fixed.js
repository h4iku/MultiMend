// inputに入力データ全体が入る
function Main(input) {
  // 1行目がinput[0], 2行目がinput[1], …に入る
  // input = input.split("\n");
  ans = 0
  input = input.trim().split("");
  input.forEach(function(i) {
    if (i === '-') {
      ans--
    } else {
      ans++
    }
  })

  //出力
  console.log(ans + "" +
              '\n')
}
Main(require("fs").readFileSync("/dev/stdin", "utf8"));
// Main(require('fs').readFileSync('./input.txt', 'utf-8'));