function Main(str) {
  var splited = [];
  var goukei = 0;
  splited = str.split("");
  console.log(splited);
  for (var i = 0; i < splited.length - 1; i++) {
    if (splited[i] == '+') {
      goukei = goukei + 1;
    }
    if (splited[i] == '-') {
      goukei = goukei - 1;
    }
  }
  console.log(goukei);
}
Main(require("fs").readFileSync("/dev/stdin", "utf8"));