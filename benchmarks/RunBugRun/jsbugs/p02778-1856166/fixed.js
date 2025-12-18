function Main(input) {
  input = input.trim();
  var str = '';
  for (i = 0; i < input.length; i++) {
    str += 'x';
  }
  console.log(str);
}

Main(require("fs").readFileSync("/dev/stdin", "utf8"));