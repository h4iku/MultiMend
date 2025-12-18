function Main(input) {
  input = input.split(" ");
  var a = Number(input[0]);
  var b = Number(input[1]);
  console.log(Math.max(a + b, a - b, a * b));
}

Main(require("fs").readFileSync("/dev/stdin", "utf8"));