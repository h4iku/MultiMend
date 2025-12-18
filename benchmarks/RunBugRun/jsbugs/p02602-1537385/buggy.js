// inputに入力データ全体が入る
function Main(input) {

  input = input.split("\n");

  line1 = input[0].split(" ");
  let N = parseInt(line1[0], 10);
  let K = parseInt(line1[1], 10);

  line2 = input[1].split(" ");

  let ans = '';
  let pre = 0;
  let cur = 0;

  for (let i = K; i < N; i++) {
    pre = parseInt(line2[i - K], 10);
    cur = parseInt(line2[i], 10);

    console.log("%d %d", pre, cur);
    if (pre < cur) {
      ans = ans + "Yes\n";
    } else {
      ans = ans + "No\n";
    }
  }

  console.log(ans);
}

Main(require("fs").readFileSync("/dev/stdin", "utf8"));