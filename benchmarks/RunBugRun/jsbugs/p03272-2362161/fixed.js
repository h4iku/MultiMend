function main(input) {
  var args = input.split(" ");
  var n = parseInt(args[0], 10);
  var i = parseInt(args[1], 10);
  console.log(n - i + 1);
}
main(require("fs").readFileSync("/dev/stdin", "utf8"));
