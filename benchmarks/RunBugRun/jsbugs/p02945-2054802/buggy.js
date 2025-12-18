function Main(input) {
  input = input.split(" ");
  var a = input[0], b = input[1]
  console.log(Math.max(a + b, a * b, a - b))
}
Main(require("fs").readFileSync("/dev/stdin", "utf8"));