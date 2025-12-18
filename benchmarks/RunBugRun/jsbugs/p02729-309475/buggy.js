function Main(input) {
  var tmp = input.split(" ");
  var N = parseInt(tmp[0], 10);
  var M = parseInt(tmp[1], 10);

  //組み合わせの考え方
  //偶数＋偶数＝偶数(1)
  //奇数＋偶数＝奇数(2)
  //奇数＋奇数＝偶数(3)
  //であるため
  //(1)=N*(N-1),(3)=M*(M-1)の和が
  // N+Mのボールから任意の2のボールを取るときの偶数となる場合の数となる。

  console.log(N * (N - 1) + M * (M - 1) / 2);
}
//*この行以降は編集しないでください（標準入出力から一度に読み込み、Mainを呼び出します）
Main(require("fs").readFileSync("/dev/stdin", "utf8"));
