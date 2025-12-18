
function Main(input) {
  var S = input[0];
  var length = S.length - 2;

  var F = S.charAt(0);
  var L = S.charAt(S.length - 1);
  console.log(F + length + L);
}

Main(require("fs").readFileSync("/dev/stdin", "utf8").trim().split(/\n|\s/));