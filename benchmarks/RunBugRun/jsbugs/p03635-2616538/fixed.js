function Main(input) {
  input = input.split(" ");
  var m = Number(input[0]);
  var n = Number(input[1]);
  var a = ((n + 1) * (m + 1));
  console.log(a - ((((n + 1) * 2) + ((m + 1) * 2)) - 4))
}
Main(require("fs").readFileSync("/dev/stdin", "utf8"));