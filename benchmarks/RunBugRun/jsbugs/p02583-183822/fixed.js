'use strict';
function isGoodTriangle(l) {
  l.sort((a, b) => b - a);
  return l[0] - l[1] < l[2] && l[0] !== l[1] && l[1] !== l[2];
}

function Main(inputs) {
  // 1行目がinput[0], 2行目がinput[1], …に入る
  const input = inputs.split("\n");
  const n = Number(input[0]);
  const l = input[1].split(' ').map(Number);

  let num = 0;
  for (let a = 0; a < n; a++) {
    for (let b = a + 1; b < n; b++) {
      for (let c = b + 1; c < n; c++) {
        if (isGoodTriangle([ l[a], l[b], l[c] ])) {
          num++;
        }
      }
    }
  }
  console.log(num);
}
//*この行以降は編集しないでください（標準入出力から一度に読み込み、Mainを呼び出します）
Main(require("fs").readFileSync("/dev/stdin", "utf8"));
