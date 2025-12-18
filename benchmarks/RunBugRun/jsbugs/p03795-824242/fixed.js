function Main(input) {
  input = parseInt(input.trim().split(" "));
  var x = 800 * input;
  var y = 200 * Math.floor(input / 15);
  console.log(x - y);
}

Main(require("fs").readFileSync("/dev/stdin", "utf8"));
