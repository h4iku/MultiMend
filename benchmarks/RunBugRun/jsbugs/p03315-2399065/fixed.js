function Main(input) {
  var s = 0;
  var result = input.split('');

  for (var i = 0; i < 4; i++) {
    if (result[i] === '+') {
      s++;
    } else if (result[i] === '-') {
      s--;
    }
  }
  console.log(s);
}

Main(require("fs").readFileSync("/dev/stdin", "utf8"));
