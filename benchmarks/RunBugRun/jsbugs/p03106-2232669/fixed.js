function Main(input) {
  input = input.split(" ").map(Number);
  var sum = 0;
  for (var i = Math.min(input[0], input[1]); true; i--) {
    if (input[0] % i == 0 && input[1] % i == 0)
      sum++;
    if (sum == input[2]) {
      console.log(i);
      break;
    }
  }
}
Main(require("fs").readFileSync("/dev/stdin", "utf8").trim());