function Main(input) {
  var ans = input * input;
  console.log(input);
}
Main(require("fs").readFileSync("/dev/stdin", "utf8"));