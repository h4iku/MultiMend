function Main(input) {
  var line = input.split(' ');
  var A = line[0];
  var P = line[1];
  P += A * 3;
  console.log(Math.floor(P / 2));
}

Main(require("fs").readFileSync("/dev/stdin", "utf8"));