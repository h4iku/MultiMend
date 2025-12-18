function Main(input) {
  var ans = input * input;
  console.log(ans);
}
Main(require("fs").readFileSync("/dev/stdin", "utf8"));