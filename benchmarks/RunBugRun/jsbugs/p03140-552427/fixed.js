function Main(input) {
  input = input.split("\n");
  var a = input[1].split("");
  var b = input[2].split("");
  var c = input[3].split("");
  var sum = a.length * 2;
  for (var i = 0; i < a.length; i++) {
    var x = 0;
    if (a[i] == b[i])
      x++;
    if (c[i] == b[i])
      x++;
    if (a[i] == c[i])
      x++;
    if (x == 3)
      sum -= 2;
    else if (x == 1)
      sum--;
  }
  console.log(sum);
}
Main(require("fs").readFileSync("/dev/stdin", "utf8").trim());