function Main(input) {
  // 1行目がinput[0], 2行目がinput[1], …に入る
  tmp = input.split("\n");
  N = tmp[0];
  p = tmp.slice(1, N + 1);
  p = p.map(Number);
  M = Math.max.apply(null, p);
  answer = 0;
  for (i = 0; i < N; i++) {
    answer += p[i];
  }

  console.log(Number(answer) - 0.5 * M);
}
//*この行以降は編集しないでください（標準入出力から一度に読み込み、Mainを呼び出します）
Main(require("fs").readFileSync("/dev/stdin", "utf8"));
