function Main(input) {
  input = input.split(" ");
  var a = parseInt(input[0], 10), b = parseInt(input[1], 10)
  console.log(Math.max(a + b, a * b, a - b))
}
Main(require("fs").readFileSync("/dev/stdin", "utf8"));