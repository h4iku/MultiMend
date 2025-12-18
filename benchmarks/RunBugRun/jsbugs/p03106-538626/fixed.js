'use strict'
// inputに入力データ全体が入る
function Main(input) {
  let inAry = input.split(" ");
  let a = inAry[0];
  let b = inAry[1];
  let k = inAry[2];

  let ayaku = [];
  let byaku = [];
  for (let i = 1; i <= a; i++) {
    if (a % i === 0) {
      ayaku.push(i);
    }
  }
  for (let i = 1; i <= b; i++) {
    if (b % i === 0) {
      byaku.push(i);
    }
  }

  let kouyakusu = ayaku.filter((value) => { return byaku.indexOf(value) >= 0; })

  kouyakusu = byaku.filter((value) => { return ayaku.indexOf(value) >= 0; })

  kouyakusu.sort((a, b) => { return a - b; });
  console.log(kouyakusu[kouyakusu.length - k]);
}
//*この行以降は編集しないでください（標準入出力から一度に読み込み、Mainを呼び出します）
Main(require("fs").readFileSync("/dev/stdin", "utf8"));