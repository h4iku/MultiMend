function Main(input) {
  var splited = [];
  var goukei = 0;
  splited = input.split("");
  for (var i = 0; i < 4; i++) {
    if (splited[i] == '+')
      goukei = goukei + 1;
    if (splited[i] == '-')
      goukei = goukei - 1;
  }
  console.log(goukei);
}
Main(require("fs").readFileSync("/dev/stdin", "utf8"));