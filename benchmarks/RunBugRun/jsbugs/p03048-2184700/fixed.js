// inputに入力データ全体が入る
function Main(input) {
  input = input.trim();
  input = input.split(" ");
  var R = input[0];
  var G = input[1];
  var B = input[2];
  var N = input[3];
  var tmpR;
  var tmpG;
  var count = 0;

  for (var i = 0; i < N / R + 1; i++) {
    tmpR = N - R * i;
    if (tmpR >= 0) {
      for (var j = 0; j < tmpR / G + 1; j++) {
        tmpG = tmpR - G * j;
        if (tmpG >= 0 && tmpG % B == 0) {
          count++;
        }
      }
    }
  }

  console.log(count);
}
//*この行以降は編集しないでください（標準入出力から一度に読み込み、Mainを呼び出します）
Main(require("fs").readFileSync("/dev/stdin", "utf8"));