function Main(input) {
  input = input.split(" ");
  var a = input[0];
  var b = input[1];
  console.log(math.max(a + b, a - b, a * b));
}

Main(require("fs").readFileSync("/dev/stdin", "utf8"));