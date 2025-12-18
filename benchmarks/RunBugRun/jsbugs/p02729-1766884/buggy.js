function Main(input) {
  var str = input;
  var ans = 0;
  var str = str.split("\n")[0];
  var num = str.split(" ");
  var n = Number(num[0]);
  var m = Number(num[1]);

  if (n > 1) {
    n = n * (n - 1) / 2;
  }
  if (m > 1) {
    m = m * (m - 1) / 2;
  }
  ans = n + m;
  console.log(ans);
}
Main(require("fs").readFileSync("/dev/stdin", "utf8"));