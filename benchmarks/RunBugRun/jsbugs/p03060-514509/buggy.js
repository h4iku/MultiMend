function Main(input) {
  input = input.split("\n");
  var a = input[1].split(" ").map(Number);
  var b = input[2].split(" ").map(Number);
  var sum = 0;
  for (var i = 0; i < input.length; i++) {
    if ((a[i] - b[i]) > 0)
      sum += (a[i] - b[i]);
  }
  console.log(sum);
}
Main(require("fs").readFileSync("/dev/stdin", "utf8").trim());