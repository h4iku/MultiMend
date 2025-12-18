function Main(input) {
  input = input.split("\n");
  tmp = input[0].split(" ");
  var a = tmp[0];
  var b = tmp[1];
  var s;
  if (a != "H") {
    if (b == "H") {
      s = "D";
    } else {
      s = "H";
    }
  } else {
    s = b;
  }
  console.log('%s', s);
}
Main(require("fs").readFileSync("/dev/stdin", "utf8"));