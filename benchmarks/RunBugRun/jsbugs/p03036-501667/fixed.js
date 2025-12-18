function Main(input) {
  input = input.split(' ');
  var r = input[0];
  var D = input[1];
  var x2000 = input[2];
  current = x2000
  for (var i = 0; i < 10; i++) {
    current = r * current - D;
    console.log(current);
  }
}
Main(require("fs").readFileSync("/dev/stdin", "utf8"));