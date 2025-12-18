function Main(input) {
  var line = input.trim().split(' ');
  var A = Number(line[0]);
  var P = Number(line[1]);
  P += A * 3;
  console.log(Math.floor(P / 2));
}

Main(require("fs").readFileSync("/dev/stdin", "utf8"));
