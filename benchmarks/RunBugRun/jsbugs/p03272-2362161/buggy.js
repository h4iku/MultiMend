function main(input) {
  var args = input.split(" ");
  var n = args[0];
  var i = args[0];
  console.log(n - i + 1);
}
main(require("fs").readFileSync("/dev/stdin", "utf8"));
