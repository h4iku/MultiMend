
function Main(arg) {
  var N = arg.split("\n")[0].split(" ")[0] - 0;
  var T = arg.split("\n")[0].split(" ")[1] - 0;
  var t = arg.split("\n")[1].split(" ").map(Number);

  var ans = 0;
  for (var i = 1; i < N; i++) {
    if (t[i] - t[i - 1] < T) {
      ans += t[i] - t[i - 1];
    } else {
      ans += T;
    }
  }

  console.log(ans + T);
  return;
}

Main(require("fs").readFileSync("/dev/stdin", "utf8"));